from rest_framework import serializers


class TaskRequestSerializer(serializers.Serializer):
    message = serializers.CharField(
        required=True, help_text="Message to process in the task"
    )
    delay = serializers.IntegerField(
        default=2,
        min_value=0,
        max_value=300,
        help_text="Delay in seconds to simulate work (0-300)",
    )


class TaskResponseSerializer(serializers.Serializer):
    task_id = serializers.CharField(help_text="Unique task identifier")
    status = serializers.CharField(help_text="Task status")
    message = serializers.CharField(help_text="Response message")
    input = serializers.DictField(help_text="Input parameters")


class TaskResultSerializer(serializers.Serializer):
    task_id = serializers.CharField(help_text="Task identifier")
    status = serializers.CharField(help_text="Result status")
    result = serializers.DictField(help_text="Task execution result")


class ScheduledTaskStatusSerializer(serializers.Serializer):
    exists = serializers.BooleanField(help_text="Whether the scheduled task exists")
    name = serializers.CharField(required=False, help_text="Schedule name")
    next_run = serializers.DateTimeField(
        required=False, help_text="Next scheduled run time"
    )
    schedule_type = serializers.CharField(
        required=False, help_text="Schedule type description"
    )
    repeats = serializers.IntegerField(
        required=False, help_text="Number of repeats (-1 for infinite)"
    )
    success_count = serializers.IntegerField(
        required=False, help_text="Number of successful runs"
    )
    last_run = serializers.DateTimeField(
        required=False, help_text="Last execution time"
    )
    message = serializers.CharField(required=False, help_text="Status message")


class ScheduledTaskResponseSerializer(serializers.Serializer):
    status = serializers.CharField(help_text="Operation status")
    message = serializers.CharField(help_text="Response message")
    schedule_id = serializers.IntegerField(
        required=False, help_text="Schedule identifier"
    )
    next_run = serializers.DateTimeField(
        required=False, help_text="Next scheduled run time"
    )
    schedule_type = serializers.CharField(
        required=False, help_text="Schedule type description"
    )


class EmailRequestSerializer(serializers.Serializer):
    subject = serializers.CharField(required=True, help_text="Email subject")
    html_template_path = serializers.CharField(required=True, help_text="Path to HTML template")
    to_email = serializers.ListField(
        child=serializers.EmailField(),
        required=True,
        help_text="List of recipient email addresses",
    )
    context = serializers.DictField(
        required=True, help_text="Context data for rendering the email template"
    )
    service_type = serializers.CharField(
        required=False, allow_null=True, help_text="Deprecated: Email service type"
    )


class EmailResponseSerializer(serializers.Serializer):
    task_id = serializers.CharField(help_text="Task identifier")
    status = serializers.CharField(help_text="Task status")
    message = serializers.CharField(help_text="Response message")
