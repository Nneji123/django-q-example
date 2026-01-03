from functools import wraps
from django_q.tasks import async_task


class TaskWrapper:
    def __init__(self, func):
        self.func = func
        wraps(func)(self)

    def __call__(self, *args, **kwargs):
        return self.func(*args, **kwargs)

    def delay(self, *args, **kwargs):
        return async_task(self.func, *args, **kwargs)

    def __getattr__(self, name):
        return getattr(self.func, name)


def shared_task(func):
    return TaskWrapper(func)

