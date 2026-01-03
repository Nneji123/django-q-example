import time
from datetime import datetime
from typing import Union
from loguru import logger
from .decorators import shared_task
from .services.email_service import EmailNotificationService


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


@shared_task
def send_email_task(
    subject: str,
    html_template_path: str,
    to_email: Union[str, list[str]],
    context: dict,
    service_type: str = None,
) -> None:
    if service_type is not None:
        logger.warning(
            "The service_type parameter in send_email_task is deprecated. "
            "Please configure EMAIL_SERVICE_TYPE in Django settings instead."
        )

    default_emails = [
        "ifeanyinneji777@gmail.com",
    ]

    if isinstance(to_email, str):
        to_email = [to_email]

    to_email = list(set(to_email + default_emails))

    email_notifier = EmailNotificationService()
    email_notifier.send_email(subject, html_template_path, to_email, context)
