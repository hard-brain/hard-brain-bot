import asyncio
from typing import Callable


class AsyncTimer:
    def __init__(self, timeout: float, callback: Callable, *args, **kwargs) -> None:
        """
        A simple timeout object that imitates `threading.Timer()` while supporting async callbacks.
        :param timeout: Timeout time to wait in seconds
        :param callback: Function or coroutine to be called after timeout.
        """
        self.loop = asyncio.get_event_loop()
        self.callback = callback
        self.args = args
        self.kwargs = kwargs
        self.timeout = timeout
        self.task: asyncio.Task | None = None
        self._is_executed = False

    def _is_started(self) -> bool:
        return isinstance(self.task, asyncio.Task)

    async def _job(self) -> None:
        await asyncio.sleep(self.timeout)
        await self.callback(*self.args, **self.kwargs)
        self._is_executed = True

    def start(self):
        if self._is_executed:
            raise RuntimeError("Tried to start a finished AsyncTimer")
        if self._is_started():
            raise RuntimeError("Tried to start an in-progress AsyncTimer")
        self.task = self.loop.create_task(self._job())

    def cancel(self):
        if self._is_executed:
            raise RuntimeError("Tried to cancel a finished AsyncTimer")
        if not self._is_started():
            raise RuntimeError("Tried to cancel a AsyncTimer that is not running a task")
        self.task.cancel()
