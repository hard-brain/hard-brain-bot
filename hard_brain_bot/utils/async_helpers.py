import asyncio
from typing import Callable


class AsyncTimer:
    def __init__(
        self, timer_timeout: float, callback: Callable, *args, **kwargs
    ) -> None:
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
        self._event = asyncio.Event()

    def is_started(self) -> bool:
        return isinstance(self.task, asyncio.Task)

    def is_executed(self) -> bool:
        return self._event.is_set()

    async def _job(self) -> None:
        await asyncio.sleep(self.timer_timeout)
        await self.callback(*self.args, **self.kwargs)
        self._is_executed = True
        self._event.set()

    def start(self) -> None:
        if self.is_started():
            raise RuntimeWarning("Tried to start an in-progress AsyncTimer")
        if self.task and self.task.done():
            raise RuntimeWarning("Tried to start a finished AsyncTimer")
        self.task = self.loop.create_task(self._job())

    def cancel(self) -> None:
        if not self.is_started():
            raise RuntimeWarning(
                "Tried to cancel a AsyncTimer that is not running a task"
            )
        if self.task and self.task.done():
            raise RuntimeWarning("Tried to cancel a finished AsyncTimer")
        self.task.cancel()
        self._event.set()

    async def timeout(self) -> None:
        await self._event.wait()
