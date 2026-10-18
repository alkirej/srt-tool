import time_fns as tfn

class TimeBlock:
    def __init__(self, start: float|int|str, stop: str: None|float|int|str = None):
        self.start: float = convert_to_secs(start)
        self.stop: float = convert_to_secs(stop)

    def sbt_output(self) -> str:
        return ""

