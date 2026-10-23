import logging as log
from pathlib import Path
import sys
from typing import Self

# **********************************
# add project src dir to import path
# **********************************
new_path: str = str(Path(__file__).resolve().parent.parent)
if new_path not in sys.path:
    sys.path.append(new_path)
# **********************************

import time_fns as tfn


class TimeBlock:
    def __init__(self,
                 start: float | int | str,
                 stop: None | float | int | str = None
                 ):
        self._start: float = tfn.convert_to_secs(start)
        self._stop: float = tfn.convert_to_secs(stop)

        self._verify_time_block()

    def _verify_time_block(self):
        if self._start < 0.0 or self._stop < 0.0:
            log.warning(f"Times cannot be negative. ({self._start}, {self._stop})")
            raise tfn.TimeException(f"Times cannot be negative. ({self._start}, {self._stop})")

        if self._stop <= self._start:
            log.info(f"Invalid time block. start {self._start} cannot be before stop {self._stop}")
            raise tfn.TimeException(f"Invalid time block. start {self._start} cannot be before stop {self._stop}")

    @property
    def start(self) -> float:
        return self._start

    @start.setter
    def start(self, value: float | str) -> None:
        self._start = tfn.convert_to_secs(value)
        self._verify_time_block()

    @property
    def stop(self) -> float:
        return self._stop

    @stop.setter
    def stop(self, value: float | str) -> None:
        self._stop = tfn.convert_to_secs(value)
        self._verify_time_block()

    def get_block_start_in_secs(self) -> float:
        return self._start

    def get_block_stop_in_secs(self) -> float:
        return self._stop

    def get_block_times(self) -> (float, float):
        return self._start, self._stop

    def get_block_duration(self) -> float:
        return self._stop - self._start

    def contains_time_point(self, time_pt: float | int | str) -> bool:
        num_time_pt: float = tfn.convert_to_secs(time_pt)
        return self._start <= num_time_pt <= self._stop

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

    def contains_overlap(self, duration: Self) -> bool:
        start_time_inside: bool = self.contains_time_point(duration._start)
        stop_time_inside: bool = self.contains_time_point(duration._stop)

        overlap_one_boundary: bool = start_time_inside ^ stop_time_inside
        complete_overlap: bool = (duration._start < self._start and duration._stop > self._stop) \
                                     or self.contains_duration(duration)

        return overlap_one_boundary or complete_overlap

    # ************************************************
    # Given the timeframe as a boundary, update the current
    # (self) object to not overlap. So, if our object starts
    # before the boundary and the boundary starts before
    # our object ends, shorten the current object to NOT
    # overlap with the boundary condition (by changing
    # the ending time of the current object)
    #
    # At the end, an overlap is starting the current
    # object at a later time.
    #
    # Note: this is not intended to handle the condition
    # that occurs when one TimeBlock objects starts before
    # and ends after the other. (When one fully contains
    # the other.)
    # ************************************************
    def cut_to(self, timeframe: Self) -> bool:
        if self.overlap_end(timeframe):
            self._stop = timeframe._start - 0.002
            return True
        if self.overlap_start(timeframe):
            self._start = timeframe._stop + 0.002
            return True

        return False
