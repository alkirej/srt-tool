import time_fns as tfn

class TimeBlock:
    def __init__(self, start: float|int|str, stop: None|float|int|str = None):
        self.start: float = tfn.convert_to_secs(start)
        self.stop: float = tfn.convert_to_secs(stop)

    def get_block_start_in_secs(self) -> float:
        return self.start

    def get_block_stop_in_secs(self) -> float:
        return self.stop

    def get_block_times(self) -> (float,float):
        return (self.start, self.stop)

