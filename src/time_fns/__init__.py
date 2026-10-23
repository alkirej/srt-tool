# time_fns package for srt-tool

import logging as log

from .TimeBlock import TimeBlock
from .TimeException import TimeException

HOUR: int = 3600   # 3,600 seconds in an hour
MINUTE: int = 60   # 60 seconds in a minute
SECOND: int = 1    # 1 second in a second
MILLI: int = 1000  # 1,000 millis in a second

# *****************************************************
# Hour:Minute:Second,millis format 
# in_str of "00:01:04,500" returns 64.5
#     because 0 hours, 1 minute, 4 seconds and 500/1000 of a second
#     is a total of 64.5 seconds.
# *****************************************************


def hmsm_dur_to_secs(in_str: str) -> float:
    # time_stamp and milliseconds return as str
    parts: [str] = in_str.split(",")
    time_stamp: str = parts[0]
    if len(parts) <= 1:
        milliseconds: str = '0'
    elif parts[1] == '':
        milliseconds: str = '0'
    else:
        milliseconds: str = parts[1]

    millis: float = int(milliseconds) / 1000.0
    if millis >= 1.0:
        log.error(f"{milliseconds} is too many millis. Setting to max (999)")
        millis = 0.999

    split_time: [str] = time_stamp.split(":")
    if len(split_time) > 3:
        log.error(f"{in_str} is an invalid timestamp. (hh:mm:ss,mmm)")
        return 0

    total_secs = 0.0
    for idx, num in enumerate(split_time):
        if '' == num:
            num_val = 0
        else:
            try:
                num_val = int(num)
            except TimeException:
                log.error(f"{num} from {in_str} is an invalid. (hh:mm:ss,mmm)")
                num_val = 0

        place = (len(split_time)-idx-1)
        place_val = 60**place
        total_secs = total_secs + num_val*place_val

    return total_secs + millis


# *****************************************************
# Receive an input and convert into a count of the seconds
# in the input. The routine should hand any kinds of input
# and give 0.0 in the event the type cannot convert to time.
#
# for strings assume HH:MM:SS,mmmm format
# for int and float return the number as the result
# other types get to be 0.
# *****************************************************
def convert_to_secs(num_seconds: str | float | int) -> float:
    if type(num_seconds) is str:
        return hmsm_dur_to_secs(num_seconds.strip())
    if type(num_seconds) is int:
        return float(num_seconds)
    if type(num_seconds) is float:
        return num_seconds

    return 0.0


# *****************************************************
# Given a number of seconds, return the duration in the
# HH:MM:SS,mmmm format.
# *****************************************************
def secs_to_hmsm_dur(secs: float) -> str:
    i_secs: int = int(secs)
    millis: float = secs - i_secs  # fractions of a second
    millis = millis * MILLI             # convert to milli secs
    i_millis: int = int(millis)         # remove and excess fraction
    (hrs, secs_left) = divmod(i_secs, HOUR)
    (mins, secs_left) = divmod(secs_left, MINUTE)

    return "{0}:{1}:{2},{3}" \
              .format(num_as_two_digits(hrs),
                      num_as_two_digits(mins),
                      num_as_two_digits(secs_left),
                      str(i_millis)
                      )


# *****************************************************
# Make numbers into text strings of exactly 2 chars
# to work properly in HH:MM:SS,mmmm format.
# *****************************************************
def num_as_two_digits(num: int | float) -> str:
    i_num = int(num)
    if i_num > 99 or i_num < 0:
        raise TimeException(f"{num} cannot be converted to a 2 digit number")

    if i_num < 10:
        return "0" + str(i_num)
    return str(i_num)
