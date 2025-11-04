# utils/observed.py

import os
import logging
from datetime import datetime, timezone
from typing import Any, Optional, Dict
import jwt

# This utility assumes a 'kafka.py' file with a singleton 'kafka_logger'
# is available in the same directory or a reachable path.
from .kafka import kafka_logger

logger = logging.getLogger(__name__)

# --- Reusable Constants ---
# The separator used to split the JWT from the encrypted payload.
CUSTOM_TOKEN_SEPARATOR = "$YashUnified2025$"

# --- Pre-computed Environment Variables (Read once at startup for efficiency) ---
MODEL_NAME = os.getenv("MODEL_NAME")
AGENT_NAME = os.getenv("AGENT_NAME")
SERVER_NAME = os.getenv("SERVER_NAME")

# --- Actionable Startup Checks ---
# Provides clear guidance if the environment is not configured correctly.
if not MODEL_NAME:
    logger.warning(
        "Environment variable 'MODEL_NAME' is not set. The Kafka payload will use 'N/A'. Please set this in your .env file."
    )
if not AGENT_NAME:
    logger.info(
        "Environment variable 'AGENT_NAME' is not set. The Kafka payload will derive it from the 'context' parameter."
    )
if not SERVER_NAME:
    logger.warning(
        "Environment variable 'SERVER_NAME' is not set. The Kafka payload will use 'Unknown Server'. Please set this in your .env file."
    )


def observe_token_usage(
    result: Any, auth_token: Optional[str], context: str = "Operation"
) -> None:
    """
    Observes LLM token usage from a result object, constructs a detailed payload,
    and sends it to a Kafka topic.

    This function is designed to be "plug and play" and is hardened against
    common failures. It will not crash the parent application if Kafka is
    unavailable, the auth token is missing/malformed, or the result object
    lacks token data.

    **Required Environment Variables:**
      - KAFKA_BOOTSTRAP_SERVERS: Comma-separated list of Kafka brokers.
      - KAFKA_TOPIC_NAME: The Kafka topic to send logs to.
      - MODEL_NAME: The name of the model being used.
      - AGENT_NAME: A constant name for the agent running the task.
      - SERVER_NAME: The name of the backend server.

    **Usage Example (in your main application logic):**
    ```python
    from utils.observed import observe_token_usage

    # After getting a result from a CrewAI kickoff...
    # 'crew_result' is the object returned by crew.kickoff()
    # 'authorization_header' is the full token from the request
    observe_token_usage(
        result=crew_result,
        auth_token=authorization_header,
        context="CodeReviewTask"
    )
    ```

    Args:
        result: The result object from an LLM call (e.g., from crew.kickoff()).
                Expected to have a 'token_usage' attribute.
        auth_token: The full authorization string from the request header.
                    Can be a JWT or a JWT combined with an encrypted payload,
                    and may include the "Bearer " prefix.
        context: A descriptive string for the operation being logged. Used as a
                 fallback if AGENT_NAME is not set.
    """
    try:
        # --- 1. Safely Extract Token Usage ---
        usage_info = getattr(result, "token_usage", None)
        if not usage_info:
            logger.debug(
                f"No token usage information found for context '{context}'. Skipping Kafka log."
            )
            return

        # Ensure usage_info is a dictionary for consistent access.
        if not isinstance(usage_info, dict):
            if hasattr(usage_info, "__dict__"):
                usage_info = usage_info.__dict__
            else:
                logger.warning(
                    f"Token usage info for context '{context}' is not a parsable object or dictionary. Skipping log."
                )
                return

        # --- 2. Robustly Parse Authentication Token ---
        user_email, encrypted_payload = "N/A", "N/A"
        if not auth_token:
            logger.warning(
                f"The 'auth_token' provided for context '{context}' was None or empty."
            )
        else:
            # Separate the JWT from the encrypted payload.
            jwt_part = auth_token
            if CUSTOM_TOKEN_SEPARATOR in auth_token:
                jwt_part, encrypted_payload = auth_token.split(
                    CUSTOM_TOKEN_SEPARATOR, 1
                )

            # Clean the "Bearer " prefix, a common source of decoding errors.
            if jwt_part.lower().startswith("bearer "):
                jwt_part = jwt_part[7:]

            # Decode the JWT to find the user's email.
            try:
                decoded_token = jwt.decode(
                    jwt_part, options={"verify_signature": False}
                )
                custom_data = decoded_token.get("custom-data", {})

                # Check multiple common claims to find the email address.
                user_email = (
                    custom_data.get("user_email")
                    or decoded_token.get("email")
                    or decoded_token.get("upn")  # User Principal Name
                    or decoded_token.get("preferred_username")
                    or decoded_token.get("unique_name")
                    or decoded_token.get("sub")  # Subject claim
                    or "N/A"
                )
            except jwt.PyJWTError as e:
                logger.error(
                    f"JWT Decoding Failed for context '{context}': {e}. The token part may be malformed."
                )

        # --- 3. Assemble the Final Kafka Payload ---
        final_log = {
            # --- Fields from Auth Token ---
            "encrypted_payload": encrypted_payload,
            "user_email": user_email,
            # --- Fields from LLM Result ---
            "prompt_tokens": usage_info.get("prompt_tokens", 0),
            "completion_tokens": usage_info.get("completion_tokens", 0),
            "total_tokens": usage_info.get("total_tokens", 0),
            "thoughts_token_count": usage_info.get("total_tokens", 0)
            - (
                usage_info.get("prompt_tokens", 0)
                + usage_info.get("completion_tokens", 0)
            ),  # Not available, set to 0 as required
            # --- Fields from Environment ---
            "model_name": MODEL_NAME or "N/A",
            "agent_name_constant": AGENT_NAME or f"Unknown Agent ({context})",
            "server_name": SERVER_NAME or "Unknown Server",
        }

        # --- 4. Asynchronously Send to Kafka ---
        kafka_logger.log(final_log)

    except Exception as e:
        # Catch-all to ensure this utility never crashes the main application.
        logger.error(
            f"A critical error occurred in observe_token_usage for context '{context}': {e}",
            exc_info=True,
        )
