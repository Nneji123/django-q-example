"""
Task functions for django-q2
"""

import time
from datetime import datetime

from loguru import logger


def sample_task(message: str, delay: int = 2) -> dict:
    """
    A sample task that simulates some work.

    Args:
        message: A message to process
        delay: Number of seconds to simulate work

    Returns:
        dict: Result of the task execution
    """
    logger.info(f"Task started with message: {message}")
    time.sleep(delay)
    result = {
        "status": "completed",
        "message": f"Processed: {message}",
        "delay": delay,
    }
    logger.success(f"Task completed: {result}")
    return result


def scheduled_task() -> dict:
    """
    A scheduled task that runs periodically (every 5 seconds).
    This task demonstrates that scheduled tasks run in worker processes
    and do NOT block the main Django server.

    Returns:
        dict: Result of the scheduled task execution
    """
    timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    result = {
        "status": "completed",
        "message": f"Scheduled task executed at {timestamp}",
        "timestamp": timestamp,
    }
    logger.info(f"[SCHEDULED TASK] {result['message']}")
    return result
