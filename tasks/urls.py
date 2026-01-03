"""
URL configuration for tasks app
"""

from django.urls import path

from .views import ScheduledTaskView, TaskResultView, TaskView

app_name = "tasks"

urlpatterns = [
    path("task/", TaskView.as_view(), name="task"),
    path("task/result/", TaskResultView.as_view(), name="task_result"),
    path("scheduled-task/", ScheduledTaskView.as_view(), name="scheduled_task"),
]
