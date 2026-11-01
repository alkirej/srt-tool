import logging as log
import sys

import edl_fns as edl
import time_fns as time


def main():
    log.info(f'Command line params: {" ".join(sys.argv)}')
    file_name: str = sys.argv[1]

    delete_times: [time.TimeBlock] \
            = edl.read_deletes_in_edl_file(file_name)

    print()
    print(f"EDL File: {file_name}")
    print()
    print()
    print(f"Commercial locations in video:")
    for index, item in enumerate(delete_times, start=1):
        print(f"{index:4}  {item.start:10,.2f} - {item.stop:10,.2f}")

    print()
    print(f"Locations of removed commercials:")
    prev_end: None | float = None

    for index, item in enumerate(delete_times, start=1):
        if prev_end is None:
            if item.start <= 0.1:
                prev_end = item.stop
                continue
            else:
                prev_end = 0.0

        pretty_time: str = time.secs_to_hmsm_dur(item.start, True)
        print(f"    {item.start:10,.2f}   {pretty_time}")
        prev_end = item.stop
        # regular_video_dur: float = item.start - prev_end




if "__main__" == __name__:
    # SETUP LOGGER BEFORE IMPORTS SO THEY CAN USE THESE SETTINGS
    log.basicConfig(filename="srt-tool.log",
                    filemode="a",
                    format="%(asctime)s %(filename)15.15s %(funcName)15.15s %(levelname)5.5s %(lineno)4.4s %(message)s",
                    datefmt="%Y%m%d-%H:%M:%S"
                    )
    log.getLogger().setLevel(log.DEBUG)

    main()
