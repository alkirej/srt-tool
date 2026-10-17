
# *****************************************************
# Hour:Minute:Second,millis format 
# in_str of "00:01:04,500" returns 64.5
#     because 0 hours, 1 minute, 4 seconds and 500/1000 of a second
#     is a total of 64.5 seconds.
# *****************************************************

def to_secs(in_str: str) -> float:
    # time_stamp and milliseconds return as str
    parts: [str] = in_str.split(",")
    time_stamp: str = parts[0]
    if len(parts) <= 1:
        milliseconds: str = '0'
    elif parts[1]=='':
        milliseconds: str = '0'
    else:
        milliseconds: str = parts[1]

    millis: float = int(milliseconds) / 1000
    split_time:[str] = time_stamp.split(":")

    if len(split_time)>3:
        raise ValueError(f"{in_str} is an invalid timestamp. (hh:mm:ss,mmm)")

    total_secs = 0.0
    for idx, num in enumerate(split_time):
        if '' == num:
            num_val=0
        else:
            num_val=int(num)

        place=(len(split_time)-idx-1)
        place_val=60**place
        total_secs = total_secs + num_val*place_val

    return total_secs + millis

