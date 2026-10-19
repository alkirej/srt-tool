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

    def contains_time_point(self, time_pt: float|int|str) -> bool:
        num_time_pt: float = tfn.convert_to_secs(time_pt)
        return num_time_pt >= self.start and num_time_pt <= self.stop
    
    def contains_duration(self, duration) -> bool:
        start_time_inside: bool = self.contains_time_point(duration.start)
        stop_time_inside: bool = self.contains_time_point(duration.stop)

        return start_time_inside and stop_time_inside

    def overlap_end(self, duration) -> bool:
        start_time_inside: bool = self.contains_time_point(duration.start)
        stop_time_inside: bool = self.contains_time_point(duration.stop)
        return start_time_inside and not stop_time_inside

    def overlap_start(self, duration) -> bool:
        start_time_inside: bool = self.contains_time_point(duration.start)
        stop_time_inside: bool = self.contains_time_point(duration.stop)
        return stop_time_inside and not start_time_inside

    def contains_overlap(self, duration) -> bool:
        start_time_inside: bool = self.contains_time_point(duration.start)
        stop_time_inside: bool = self.contains_time_point(duration.stop)

        overlap_one_boundary: bool = start_time_inside ^ stop_time_inside
        complete_overlap: bool = (duration.start < self.start and duration.stop  > self.stop) \
                                     or self.contains_duration(duration)

        return overlap_one_boundary or complete_overlap

