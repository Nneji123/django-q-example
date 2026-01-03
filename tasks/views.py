from django_q.models import Schedule
from django_q.tasks import result, schedule
from drf_spectacular.utils import extend_schema
from rest_framework import status
from rest_framework.response import Response
from rest_framework.views import APIView

from .serializers import (
    EmailRequestSerializer,
    EmailResponseSerializer,
    ScheduledTaskResponseSerializer,
    ScheduledTaskStatusSerializer,
    TaskRequestSerializer,
    TaskResponseSerializer,
    TaskResultSerializer,
)
from .tasks import sample_task, send_email_task


class TaskView(APIView):
    @extend_schema(
        summary="Run a test task",
        description="Enqueue a sample task using django-q2 and return the task ID",
        request=TaskRequestSerializer,
        responses={200: TaskResponseSerializer, 400: None},
    )
    def post(self, request):
        serializer = TaskRequestSerializer(data=request.data)
        if not serializer.is_valid():
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

        message = serializer.validated_data["message"]
        delay = serializer.validated_data["delay"]

        task_id = sample_task.delay(message, delay)

        response_data = {
            "task_id": task_id,
            "status": "queued",
            "message": "Task has been enqueued",
            "input": {"message": message, "delay": delay},
        }

        response_serializer = TaskResponseSerializer(response_data)
        return Response(response_serializer.data, status=status.HTTP_200_OK)


class TaskResultView(APIView):
    @extend_schema(
        summary="Get task result",
        description="Retrieve the result of a task by its ID",
        responses={200: TaskResultSerializer, 400: None, 404: None},
        parameters=[],
    )
    def get(self, request):
        task_id = request.query_params.get("task_id")

        if not task_id:
            return Response(
                {"error": "task_id query parameter is required"},
                status=status.HTTP_400_BAD_REQUEST,
            )

        task_result = result(task_id)

        if task_result is None:
            return Response(
                {"error": "Task not found or not yet completed"},
                status=status.HTTP_404_NOT_FOUND,
            )

        response_data = {"task_id": task_id, "status": "success", "result": task_result}

        response_serializer = TaskResultSerializer(response_data)
        return Response(response_serializer.data, status=status.HTTP_200_OK)


class ScheduledTaskView(APIView):
    SCHEDULE_NAME = "scheduled_task_5s"

    @extend_schema(
        summary="Create or update scheduled task",
        description="Create a scheduled task that runs every 5 seconds",
        responses={200: ScheduledTaskResponseSerializer},
    )
    def post(self, request):
        existing_schedule = Schedule.objects.filter(name=self.SCHEDULE_NAME).first()

        if existing_schedule:
            existing_schedule.func = "tasks.tasks.scheduled_task"
            existing_schedule.schedule_type = Schedule.MINUTES
            existing_schedule.minutes = 5 / 60
            existing_schedule.repeats = -1
            existing_schedule.save()
            schedule_id = existing_schedule.id
            message = "Scheduled task updated"
        else:
            schedule_id = schedule(
                "tasks.tasks.scheduled_task",
                name=self.SCHEDULE_NAME,
                schedule_type=Schedule.MINUTES,
                minutes=5 / 60,
                repeats=-1,
            )
            message = "Scheduled task created"

        schedule_obj = Schedule.objects.get(id=schedule_id)

        response_data = {
            "status": "success",
            "message": message,
            "schedule_id": schedule_id,
            "next_run": (
                schedule_obj.next_run.isoformat() if schedule_obj.next_run else None
            ),
            "schedule_type": "every 5 seconds",
        }

        response_serializer = ScheduledTaskResponseSerializer(response_data)
        return Response(response_serializer.data, status=status.HTTP_200_OK)

    @extend_schema(
        summary="Get scheduled task status",
        description="Get information about the scheduled task",
        responses={200: ScheduledTaskStatusSerializer},
    )
    def get(self, request):
        schedule_obj = Schedule.objects.filter(name=self.SCHEDULE_NAME).first()

        if not schedule_obj:
            response_data = {
                "exists": False,
                "message": "Scheduled task not found. Use POST /api/scheduled-task/ to create it.",
            }
        else:
            response_data = {
                "exists": True,
                "name": schedule_obj.name,
                "next_run": (
                    schedule_obj.next_run.isoformat() if schedule_obj.next_run else None
                ),
                "schedule_type": f"every {int(schedule_obj.minutes * 60)} seconds",
                "repeats": schedule_obj.repeats,
                "success_count": schedule_obj.success_count,
                "last_run": (
                    schedule_obj.last_run.isoformat() if schedule_obj.last_run else None
                ),
            }

        response_serializer = ScheduledTaskStatusSerializer(response_data)
        return Response(response_serializer.data, status=status.HTTP_200_OK)

    @extend_schema(
        summary="Delete scheduled task",
        description="Delete the scheduled task",
        responses={200: ScheduledTaskResponseSerializer, 404: None},
    )
    def delete(self, request):
        schedule_obj = Schedule.objects.filter(name=self.SCHEDULE_NAME).first()

        if not schedule_obj:
            return Response(
                {"status": "error", "message": "Scheduled task not found"},
                status=status.HTTP_404_NOT_FOUND,
            )

        schedule_obj.delete()

        response_data = {"status": "success", "message": "Scheduled task deleted"}

        response_serializer = ScheduledTaskResponseSerializer(response_data)
        return Response(response_serializer.data, status=status.HTTP_200_OK)


class EmailView(APIView):
    @extend_schema(
        summary="Send email",
        description="Enqueue an email task to send an email using MJML template",
        request=EmailRequestSerializer,
        responses={200: EmailResponseSerializer, 400: None},
    )
    def post(self, request):
        serializer = EmailRequestSerializer(data=request.data)
        if not serializer.is_valid():
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

        subject = serializer.validated_data["subject"]
        html_template_path = serializer.validated_data["html_template_path"]
        to_email = serializer.validated_data["to_email"]
        context = serializer.validated_data["context"]
        service_type = serializer.validated_data.get("service_type")

        task_id = send_email_task.delay(
            subject=subject,
            html_template_path=html_template_path,
            to_email=to_email,
            context=context,
            service_type=service_type,
        )

        response_data = {
            "task_id": task_id,
            "status": "queued",
            "message": "Email task has been enqueued",
        }

        response_serializer = EmailResponseSerializer(response_data)
        return Response(response_serializer.data, status=status.HTTP_200_OK)
