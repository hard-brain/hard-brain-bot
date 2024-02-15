import asyncio
from typing import Callable


class AsyncTimer:
    def __init__(self, timer_timeout: float, callback: Callable, *args, **kwargs) -> None:
        """
        A simple timeout object that imitates `threading.Timer()` while supporting async callbacks.
        :param timer_timeout: Timeout time to wait in seconds
        :param callback: Function or coroutine to be called after timeout.
        """
        self.loop = asyncio.get_event_loop()
        self.callback = callback
        self.args = args
        self.kwargs = kwargs
        self.timer_timeout = timer_timeout
        self.task: asyncio.Task | None = None
        self._is_executed = False

    def _is_started(self) -> bool:
        return isinstance(self.task, asyncio.Task)

    async def _job(self) -> None:
        await asyncio.sleep(self.timer_timeout)
        await self.callback(*self.args, **self.kwargs)
        self._is_executed = True

    def start(self) -> None:
        if self._is_started():
            raise RuntimeError("Tried to start an in-progress AsyncTimer")
        if self.task and self.task.done():
            raise RuntimeError("Tried to start a finished AsyncTimer")
        self.task = self.loop.create_task(self._job())

    def cancel(self) -> None:
        if not self._is_started():
            raise RuntimeError(
                "Tried to cancel a AsyncTimer that is not running a task"
            )
        if self.task and self.task.done():
            raise RuntimeError("Tried to cancel a finished AsyncTimer")
        self.task.cancel()


class CancellableTask:
    def __init__(self, callback: Callable, *args, **kwargs) -> None:
        self.loop = asyncio.get_event_loop()
        self.callback = callback
        self.args = args
        self.kwargs = kwargs
        self.task: asyncio.Task | None = None

    def start(self) -> None:
        if isinstance(self.task, asyncio.Task):
            self.task = self.loop.create_task(self.callback(*self.args, **self.kwargs))

    def cancel(self) -> None:
        if isinstance(self.task, asyncio.Task):
            self.task.cancel()
