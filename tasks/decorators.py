from functools import wraps
from django_q.tasks import async_task


class TaskWrapper:
    def __init__(self, func):
        self.func = func
        self.module_path = f"{func.__module__}.{func.__name__}"
        wraps(func)(self)

    def __call__(self, *args, **kwargs):
        return self.func(*args, **kwargs)

    def delay(self, *args, **kwargs):
        return async_task(self.module_path, *args, **kwargs)

    def __getattr__(self, name):
        return getattr(self.func, name)


def shared_task(func):
    return TaskWrapper(func)

