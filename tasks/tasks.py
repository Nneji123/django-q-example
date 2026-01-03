import time
from datetime import datetime
from loguru import logger
from .decorators import shared_task


@shared_task
def sample_task(message: str, delay: int = 2) -> dict:
    logger.info(f"Task started with message: {message}")
    time.sleep(delay)
    result = {
        "status": "completed",
        "message": f"Processed: {message}",
        "delay": delay,
    }
    logger.success(f"Task completed: {result}")
    return result


@shared_task
def scheduled_task() -> dict:
    timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    result = {
        "status": "completed",
        "message": f"Scheduled task executed at {timestamp}",
        "timestamp": timestamp,
    }
    logger.info(f"[SCHEDULED TASK] {result['message']}")
    return result
