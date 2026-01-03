from django.apps import AppConfig
from django.conf import settings
from loguru import logger


class TasksConfig(AppConfig):
    default_auto_field = "django.db.models.BigAutoField"
    name = "tasks"

    def ready(self):
        """
        Auto-create the scheduled task when the app is ready.
        This only runs if AUTO_CREATE_SCHEDULED_TASK is True in settings.
        """
        if (
            hasattr(settings, "AUTO_CREATE_SCHEDULED_TASK")
            and settings.AUTO_CREATE_SCHEDULED_TASK
        ):
            try:
                from django_q.models import Schedule
                from django_q.tasks import schedule

                if not Schedule.objects.filter(name="scheduled_task_5s").exists():
                    schedule(
                        "tasks.tasks.scheduled_task",
                        name="scheduled_task_5s",
                        schedule_type=Schedule.SECONDS,
                        seconds=5,
                        repeats=-1,
                    )
                    logger.info("Auto-created scheduled task (runs every 5 seconds)")
            except Exception as e:
                logger.warning(f"Could not auto-create scheduled task: {e}")
