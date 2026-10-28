import logging as log
import sys

import edl_fns as edl
import time_fns as time

import srt_fns as srt


def main():
    log.info(f'Command line params: {" ".join(sys.argv)}')

    delete_times: [time.TimeBlock] \
            = edl.read_deletes_in_edl_file(sys.argv[1])

    total_to_del: float = 0.0
    for item in delete_times:
        new_start: str = time.secs_to_hmsm_dur(item.start - total_to_del)

        current_dur: float = item.get_block_duration()
        total_to_del += current_dur
        new_stop: str = time.secs_to_hmsm_dur(item.stop - total_to_del)

        pretty_start: str = time.secs_to_hmsm_dur(item.start)
        pretty_stop: str = time.secs_to_hmsm_dur(item.stop)
        print(f"{pretty_start} to {pretty_stop}  ({current_dur:.3f} secs) ({total_to_del:.3f} tot)")
        print(f"    becomes:  {new_start} to {new_stop}")

        print()

    print()
    pretty_time: str = time.secs_to_hmsm_dur(total_to_del)
    print(f"Total time to remove: {pretty_time}")

    subt: srt.SrtFile = srt.SrtFile("Best Medicine (2026) - S02E04 - No Place Like Om.p1.svc01.srt")
    subt.remove_subtitles_by_time(delete_times)
    subt.write_to_file("jeff-test.srt", False)


if "__main__" == __name__:
    # SETUP LOGGER BEFORE IMPORTS SO THEY CAN USE THESE SETTINGS
    log.basicConfig(filename="srt-tool.log",
                    filemode="a",
                    format="%(asctime)s %(filename)15.15s %(funcName)15.15s %(levelname)5.5s %(lineno)4.4s %(message)s",
                    datefmt="%Y%m%d-%H:%M:%S"
                    )
    log.getLogger().setLevel(log.DEBUG)

    main()
