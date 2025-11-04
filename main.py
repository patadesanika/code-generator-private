from dotenv import load_dotenv

load_dotenv()
from fastapi import FastAPI, HTTPException, Request, Header
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel, Field
from typing import Optional
import os
import asyncio
import logging
import jwt
from crewai import Agent, Task, Crew, Process, LLM
from utils.observed import observe_token_usage
from utils.kafka import create_event_logger, create_response_logger
from utils.event_messages import EventMessages

# --- Configure Loggers ---
log_file_path = os.getenv("LOG_FILE_PATH", "/tmp/app.log")
logging.basicConfig(
    level=logging.INFO,
    filemode="a",
    filename=log_file_path,
    format="%(asctime)s - %(levelname)s - %(filename)s:%(lineno)d - %(funcName)s - %(message)s",
)
logger = logging.getLogger(__name__)

# print(f"GEMINI_API_KEY line 21:{GEMINI_API_KEY}")
app = FastAPI(
    title="CrewAI Developer API",
    description="A FastAPI backend for generating code using CrewAI agents",
    version="1.0.0",
)


class CodeGenerationRequest(BaseModel):
    language: str = Field(
        ..., description="Programming language (e.g., python, java, javascript)"
    )
    query: str = Field(..., description="User query describing what code to generate")
    model: Optional[str] = Field(
        "gemini/gemini-2.5-flash-lite", description="Specific model to use"
    )


class CodeGenerationResponse(BaseModel):
    success: bool
    code: Optional[str] = None
    error: Optional[str] = None
    message: str


# --- Core Logic ---
def get_llm_instance(model: str = "gemini/gemini-2.5-flash-lite"):
    api_key = os.getenv("GEMINI_API_KEY")
    # print(f"GEMINI_API_KEY:{GEMINI_API_KEY}")
    if not api_key:
        raise ValueError("GEMINI_API_KEY not found in environment variables")
    return LLM(api_key=api_key, model=model)


def developer_main(language: str, query: str, llm, auth_token: Optional[str]):
    # Create event logger for this request
    event_logger = create_event_logger()
    # Create response logger for this request
    response_logger = create_response_logger()

    try:
        # Send task progress event
        event_logger.log_event(EventMessages.PROGRESS_AGENTS_INITIALIZING, auth_token)

        coder_agent = Agent(
            role="Code Developer",
            goal=f"Write high-quality, production-ready code in {language} to fulfill the user request: {query}. Focus only on the main implementation code.",
            backstory="You are an experienced developer who writes clean, efficient code without including test cases or examples in the main output.",
            memory=True,
            verbose=True,
            llm=llm,
        )

        reviewer_agent = Agent(
            role="Code Reviewer",
            goal=f"Review the code and tests for {query} in {language}. Provide the final, clean main code only - no test cases, no review comments, just the validated production code.",
            backstory="You are a meticulous reviewer who ensures code quality and returns only the final, clean implementation code.",
            memory=True,
            verbose=True,
            llm=llm,
        )

        coding_task = Task(
            description=f"Write the main implementation code in {language} for: {query}. Provide only the core functionality code, DO NOT INCLUDE ANY DOCSTRINGS, COMMENTS, TESTS, OR EXAMPLES.",
            expected_output="Clean, production-ready main code only.",
            agent=coder_agent,
        )

        reviewing_task = Task(
            description="Review the code, then return ONLY the final main code. Do not include comments about the review, or examples - just the clean, validated main implementation code.",
            expected_output="Final main code only - no tests, no review comments, just the core implementation.",
            agent=reviewer_agent,
        )

        crew = Crew(
            agents=[coder_agent, reviewer_agent],
            tasks=[coding_task, reviewing_task],
            process=Process.sequential,
        )

        # Send progress event before crew execution
        event_logger.log_progress(
            EventMessages.PROGRESS_CREW_EXECUTING, auth_token=auth_token
        )

        result = crew.kickoff(inputs={"language": language, "requirements": query})

        # Log the successful response to the response topic
        success_response = {
            "success": True,
            "language": language,
            "query": query,
            "generated_code": result.raw,
            "crew_result": {
                "token_usage": getattr(result, "token_usage", None),
                "tasks_output": getattr(result, "tasks_output", None),
            },
        }
        response_logger.log_response(success_response, auth_token)

        # Send completion event
        event_logger.log_success(EventMessages.SUCCESS_CODE_GENERATED, auth_token)

        # logger.info("Code generation process completed successfully.", result)
        observe_token_usage(
            result=result,
            auth_token=auth_token,
            context=f"Code generation ({language})",
        )
        return result.raw

    except Exception as e:
        logger.error(f"Error in developer_main: {str(e)}", exc_info=True)

        # Log the error response to the response topic
        error_response = {
            "success": False,
            "error": True,
            "error_message": str(e),
            "error_type": type(e).__name__,
            "language": language,
            "query": query,
        }
        response_logger.log_error_response(error_response, auth_token)

        # Send error event
        event_logger.log_error(
            EventMessages.ERROR_GENERATION_FAILED, str(e), auth_token
        )
        raise


# --- API Endpoint ---
@app.post("/generate-code", response_model=CodeGenerationResponse)
async def generate_code(
    payload: CodeGenerationRequest, authorization: Optional[str] = Header(None)
):
    # Create event logger for this request
    event_logger = create_event_logger()

    try:
        logger.info(
            f"Received code generation request for {payload.language}: {payload.query[:50]}..."
        )

        # Send task started event
        event_logger.log_event(EventMessages.TASK_RECEIVED, authorization)

        if not payload.language.strip() or not payload.query.strip():
            raise HTTPException(
                status_code=400, detail="Language and query cannot be empty"
            )

        # --- Prepare Request State for Observability ---
        # Initialize a list to hold all the provider responses for this request.
        # This list will be populated by the observability handler.
        # request.state.llm_calls = []
        # The ContextVar now just points to this list.
        # observability_data_var.set(request.state.llm_calls)
        # --- End Preparation ---

        llm = get_llm_instance(payload.model)
        generated_code = await asyncio.to_thread(
            developer_main, payload.language, payload.query, llm, authorization
        )

        logger.info("Code generation request successful.")
        # logger.info("here's the final code that is being generated", generated_code)
        return CodeGenerationResponse(
            success=True, code=generated_code, message="Code generated successfully"
        )

    except ValueError as e:
        logger.error(f"Configuration error: {str(e)}")
        # Send error event for configuration errors
        event_logger.log_error(
            EventMessages.ERROR_INVALID_REQUEST,
            f"Configuration error: {str(e)}",
            authorization,
        )
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        logger.error(
            f"Unexpected error during code generation: {str(e)}", exc_info=True
        )
        # Send error event for unexpected errors
        event_logger.log_error(
            EventMessages.ERROR_SYSTEM_ERROR,
            f"Unexpected error: {str(e)}",
            authorization,
        )
        return CodeGenerationResponse(
            success=False, error=str(e), message="Failed to generate code"
        )


if __name__ == "__main__":
    import uvicorn

    port = int(os.getenv("PORT", 2001))
    host = os.getenv("HOST", "0.0.0.0")
    uvicorn.run("main:app", host=host, port=port, log_level="info")
