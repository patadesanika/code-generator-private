#!/usr/bin/env python3
"""
Test script for the simplified KafkaEventLogger in the Code Generator Backend.
This script tests the same 3-field event structure: encrypted_payload, timestamp, message.
"""

import os
import sys

# Add the current directory to Python path so we can import utils
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from utils.kafka import create_event_logger
from utils.event_messages import EventMessages


def test_simplified_event_logger():
    """Test the simplified event logger with minimal 3-field structure."""

    print("🧪 Testing Simplified KafkaEventLogger for Code Generator Backend...")
    print("=" * 60)

    # Create event logger instance
    event_logger = create_event_logger()

    # Mock JWT token with encrypted payload (same format as a2a-server)
    mock_auth_token = "Bearer eyJ0eXAiOiJKV1QiLCJhbGciOiJIUzI1NiJ9$YashUnified2025$mock-encrypted-payload-backend-xyz789"

    print("📡 Testing Event Logger Methods...")
    print("-" * 40)

    # Test 1: Basic event logging
    print("1️⃣ Testing log_event...")
    event_logger.log_event(EventMessages.TASK_RECEIVED, mock_auth_token)

    # Test 2: Progress logging
    print("2️⃣ Testing log_progress...")
    event_logger.log_progress(
        EventMessages.PROGRESS_AGENTS_INITIALIZING, auth_token=mock_auth_token
    )
    event_logger.log_progress("Code generation in progress", 25, mock_auth_token)
    event_logger.log_progress("Code generation in progress", 75, mock_auth_token)

    # Test 3: LLM interaction logging
    print("3️⃣ Testing log_llm_interaction...")
    event_logger.log_llm_interaction(EventMessages.AGENT_THINKING, mock_auth_token)

    # Test 4: Success logging
    print("4️⃣ Testing log_success...")
    event_logger.log_success(EventMessages.SUCCESS_CODE_GENERATED, mock_auth_token)

    # Test 5: Error logging
    print("5️⃣ Testing log_error...")
    event_logger.log_error(
        EventMessages.ERROR_GENERATION_FAILED, "Mock error details", mock_auth_token
    )

    # Test 6: Events without auth token (fallback)
    print("6️⃣ Testing events without auth token...")
    event_logger.log_event("System event without auth token")

    print("-" * 40)
    print("✅ All event logger tests completed!")
    print("📡 Events sent to topic: agent-event-notification")
    print("🏷️ Session ID: test-session-backend-123")
    print("👤 User: backend-test@example.com")
    print("🖥️ Agent: CODE_GENERATOR")
    print("🌐 Server: CODE_GENERATOR_BACKEND")
    print("=" * 60)


if __name__ == "__main__":
    # Set up test environment variables
    os.environ.setdefault("AGENT_NAME", "CODE_GENERATOR")
    os.environ.setdefault("SERVER_NAME", "CODE_GENERATOR_BACKEND")
    os.environ.setdefault("KAFKA_BOOTSTRAP_SERVERS", "localhost:9092")

    test_simplified_event_logger()
