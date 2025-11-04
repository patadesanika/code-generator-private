# utils/event_messages.py

"""
Centralized event message constants for consistent messaging across the Code Generator Backend.
These constants ensure uniform event messages across all servers and environments.
"""


class EventMessages:
    """Standardized event message constants."""

    # System events
    SYSTEM_STARTING = "Code Generator Backend is starting up..."
    SYSTEM_READY = "Code Generator Backend is ready to process requests"
    SYSTEM_SHUTTING_DOWN = "Code Generator Backend is shutting down..."

    # Agent events
    AGENT_INITIALIZING = "AI agent is initializing..."
    AGENT_THINKING = "AI agent is thinking..."
    AGENT_PROCESSING = "AI agent is processing your request..."
    AGENT_READY = "AI agent is ready for your request"

    # Task events
    TASK_RECEIVED = "Code generation task received"
    TASK_STARTING = "Starting code generation process..."
    TASK_IN_PROGRESS = "Code generation in progress..."
    TASK_COMPLETED = "Code generation completed successfully"
    TASK_FAILED = "Code generation task failed"

    # Code generation specific events
    CODE_ANALYSIS_STARTING = "Analyzing code requirements..."
    CODE_GENERATION_STARTING = "Starting code generation..."
    CODE_REVIEW_STARTING = "Reviewing generated code..."
    CODE_OPTIMIZATION_STARTING = "Optimizing generated code..."

    # Success events
    SUCCESS_CODE_GENERATED = "Code generated successfully"
    SUCCESS_TASK_COMPLETED = "Task completed successfully"
    SUCCESS_VALIDATION_PASSED = "Code validation passed"

    # Error events
    ERROR_INVALID_REQUEST = "Invalid request parameters"
    ERROR_GENERATION_FAILED = "Code generation failed"
    ERROR_TASK_FAILED = "Task execution failed"
    ERROR_SYSTEM_ERROR = "System error occurred"
    ERROR_TIMEOUT = "Request timeout occurred"

    # Progress events with dynamic content
    PROGRESS_AGENTS_INITIALIZING = "Initializing code generation agents..."
    PROGRESS_AGENTS_STARTED = "Code generation agents started successfully"
    PROGRESS_CREW_EXECUTING = "CrewAI agents are working on your code..."
    PROGRESS_FINALIZING = "Finalizing generated code..."


class EventTypes:
    """Event type constants for categorization."""

    SYSTEM = "system"
    AGENT = "agent"
    TASK = "task"
    SUCCESS = "success"
    ERROR = "error"
    PROGRESS = "progress"


class EventPriority:
    """Event priority levels."""

    LOW = "low"
    NORMAL = "normal"
    HIGH = "high"
    CRITICAL = "critical"
