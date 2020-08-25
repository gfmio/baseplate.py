from enum import Enum
from enum import unique
from typing import Callable
from typing import Optional

from schedule import CancelJob

from baseplate.lib.threaded_scheduler import ThreadedScheduler


@unique
class TimerState(Enum):
    Running = "Running"
    Stopped = "Stopped"


class Timer:
    def __init__(
        self,
        function: Callable[[], None],
        interval: float,
        scheduler_interval: Optional[float] = None,
        is_repeating: bool = False,
    ) -> None:
        self.function = function
        self.interval = interval
        self.scheduler_interval = scheduler_interval if scheduler_interval is not None else interval
        self.is_repeating = is_repeating
        self.state = TimerState.Stopped
        self.scheduler = ThreadedScheduler()

    def start(self) -> None:
        if self.state == TimerState.Running:
            return
        self.state = TimerState.Running
        self.scheduler.every(self.interval).seconds.do(self._invoke)
        self.scheduler.run_continuously(self.scheduler_interval)

    def stop(self) -> None:
        self.scheduler.cancel_job(self._invoke)
        self.state = TimerState.Stopped
        self.scheduler.cease_continuous_run()

    def _invoke(self):
        self.function()
        if self.is_repeating:
            return None
        else:
            self.stop()
            return CancelJob

    def is_running(self):
        return self.state == TimerState.Running

    def __del__(self):
        self.stop()