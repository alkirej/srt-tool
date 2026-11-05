import argparse as ap
import logging as log
import sys
import typing

import edl_fns as edl
import lib_fns as lib
import time_fns as time


def range_check(cmd_line_val: str) -> (int, int):
    print(cmd_line_val)
    try:
        val = int(cmd_line_val)
        return (val, val)
    except ValueError:
        pass

    as_str: [str] = cmd_line_val.split("-")
    return int(as_str[0]), int(as_str[1])

def display_edl_time_info(args: ap.Namespace):
    delete_times: [time.TimeBlock] \
            = edl.read_deletes_in_edl_file(args.file)

    print()
    print("--------------------------------")
    print(f"EDL File: {args.file}")
    print("--------------------------------")
    print()
    print(f"Commercial locations in video:")
    for index, item in enumerate(delete_times, start=1):
        pretty_start: str = time.secs_to_hmsm_dur(item.start, True)
        pretty_stop: str = time.secs_to_hmsm_dur(item.stop, True)
        print(f"{index:4}  {item.start:10,.2f} - {item.stop:10,.2f}  ===  {pretty_start} - {pretty_stop}")

    print()
    print(f"Locations of removed commercials:")
    prev_end: None | float = None
    next_start_time: float = 0.0

    for index, item in enumerate(delete_times, start=1):
        if prev_end is None:
            if item.start <= 0.1:
                prev_end = item.stop
                continue
            else:
                prev_end = 0.0

        pretty_orig_time: str = time.secs_to_hmsm_dur(item.start, True)
        regular_video_dur: float = item.start - prev_end
        next_start_time += regular_video_dur
        pretty_new_time: str = time.secs_to_hmsm_dur(next_start_time)
        print(f"    {item.start:10,.2f}   {pretty_orig_time}  -->  {next_start_time:10,.2f}  {pretty_new_time}")

        prev_end = item.stop


def display_weighted_block_info(args: ap.Namespace) -> None:
    blocks: edl.ComskipBlockList = edl.ComskipBlockList(args.file)

    print(edl.ComskipTimeBlock.print_header())
    if args.blocks is None:
        # bl: ComskipTimeBlock
        for bl in blocks:
            print(bl.to_str(args.notes))

    else:
        for bl in blocks:
            if args.blocks[0] <= bl.block_nbr <= args.blocks[1]:
                print(bl.to_str(args.notes))

    if len(blocks.notes) > 0 and args.notes:
        print(f"\n{len(blocks.notes)} general notes:")
        for n in blocks.notes:
            print(f"    {n}")

# *******************************************************
# *******************************************************
# *******************************************************
# Each dictionary item has a key supplied as the command
#     from the command line and a value that is a function
#     that takes exactly 1 parameter that is a argparse
#     Namespace object.
# *******************************************************
# *******************************************************
# *******************************************************
EDL_COMMANDS = {"show": display_edl_time_info,
                "block-info": display_weighted_block_info
                }


def edl_command_check(command: str) -> typing.Callable[[ap.Namespace], None]:
    try:
        return EDL_COMMANDS[command]

    except KeyError as ke:
        log.exception(ke)
        log.error(f"{command} is not a valid command.")
        print(f"\n{command} is not a valid command. Try one of these:")
        print(f"     {lib.str_from_dict_keys(EDL_COMMANDS)}")
        sys.exit(1)


def main():
    log.info(f'Command line params: {" ".join(sys.argv)}')
    parser: ap.ArgumentParser = ap.ArgumentParser(
        prog="edl-tool",
        description="Reads and works with .edl video split file format."
    )

    parser.add_argument("command",
                        type=edl_command_check,
                        help="What to do. (Valid options: show, block-info)"
                        )
    parser.add_argument("--file",
                        type=lib.file_name_check,
                        help="Name of file to process."
                        )
    parser.add_argument("--notes",
                        default=False,
                        action="store_true",
                        help="use --notes to display notes for each block"
                        )
    parser.add_argument("--blocks",
                        type=range_check,
                        help="block number (e.g. 45) or range (e.g. 40-48) to display."
                        )

    try:
        args = parser.parse_args()
    except Exception as e:
        print(e)
        print(type(e))
        sys.exit()

    args.command(args)


if "__main__" == __name__:
    # SETUP LOGGER BEFORE IMPORTS SO THEY CAN USE THESE SETTINGS
    log.basicConfig(filename="srt-tool.log",
                    filemode="a",
                    format="%(asctime)s %(filename)15.15s %(funcName)15.15s %(levelname)5.5s %(lineno)4.4s %(message)s",
                    datefmt="%Y%m%d-%H:%M:%S"
                    )
    log.getLogger().setLevel(log.DEBUG)

    main()
