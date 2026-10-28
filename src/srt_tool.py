import argparse as ap
import logging as log
import os as os
import sys
import typing

import edl_fns as edlfn
import lib_fns as libfn
import srt_fns as srtfn
import time_fns as timefn


# DETERMINE THE START AND STOP LOCATIONS SUPPLIED ON THE
# COMMAND LINE
def determine_gap(args: ap.Namespace) -> timefn.TimeBlock:
    return timefn.TimeBlock(args.start_at, args.stop_at)


def process_results(args: ap.Namespace,
                    subs: srtfn.SrtFile
                    ) -> None:
    if libfn.has_meaningful_value(args.save_as):
        subs.write_to_file(args.save_as, args.reindex)
    else:
        subs.write_to_stdout(args.reindex)


# READ AND ECHO THE SRT INFORMATION
def read(args: ap.Namespace) -> srtfn.SrtFile:
    if not libfn.has_meaningful_value(args.from_file):
        log.error(f"Cannot find file to read things from.")
        print(f"Cannot find file to read things from.")
        sys.exit(5)

    return srtfn.SrtFile(args.from_file)


# PRINT THE SRT FILE OUT TO STDOUT
def show(args: ap.Namespace) -> srtfn.SrtFile:
    subs: srtfn.SrtFile = srtfn.SrtFile(args.from_file)

    gap: timefn.TimeBlock = determine_gap(args)
    if gap.stop == 0.0:
        gap.stop = subs.end_of_last_subtitle()

    print(srtfn.srt_time_output(gap))
    return subs


# DISPLAY THE SUBTITLE FROM A SPECIFIC TIME
def display_subtitle_at(args: ap.Namespace) -> srtfn.SrtFile:
    if not libfn.has_meaningful_value(args.from_file):
        log.error(f"Cannot find file to read things from.")
        print(f"Cannot find file to read things from.")
        sys.exit(6)

    subtitle_info: srtfn.SrtFile = srtfn.SrtFile(args.from_file)
    print(subtitle_info.is_subtitle_here(args.at))
    if subtitle_info.is_subtitle_here(args.at):
        blck: srtfn.SubtitleBlock = subtitle_info.find_block_at(args.at)
        print(blck.to_display)

    return subtitle_info


# REMOVE ALL SUBTITLES IN THE GIVEN BLOCK. AT THE SAME TIME,
# TRIM ANY SUBTITLES THAT OVERLAP INTO THE BLOCK TO BE 1 MILLI-
# SECOND OUT OF THE RANGE.  FINALLY SUBTRACT THE DURATION OF
# THE GAP FROM ALL ENTRIES AFTER THE GAP.
def remove_one_gap(args: ap.Namespace) -> srtfn.SrtFile:
    if not libfn.has_meaningful_value(args.from_file):
        log.error(f"missing --from-file parameter")
        print(f"missing --from-file parameter")
        sys.exit(3)

    start_file: srtfn.SrtFile = read(args)
    start_file.file_name = ""

    try:
        del_gap: timefn.TimeBlock | None = determine_gap(args)
    except timefn.TimeException:
        del_gap: timefn.TimeBlock | None = None

    start_file.remove_subtitles_by_time([del_gap], shrink_overlaps=True)
    process_results(args, start_file)

    return start_file


def remove_edl(args: ap.Namespace) -> srtfn.SrtFile:
    if not libfn.has_meaningful_value(args.from_file):
        log.error(f"missing --from-file parameter")
        print(f"missing --from-file parameter")
        sys.exit(12)
    if not libfn.has_meaningful_value(args.edl_file):
        log.error(f"missing --edl-file parameter.")
        print(f"missing --edl-file parameter.")
        sys.exit(13)

    start_file: srtfn.SrtFile = read(args)
    start_file.file_name = ""

    edl_del_times: [timefn.TimeBlock] = edlfn.read_deletes_in_edl_file(args.edl_file)
    start_file.remove_subtitles_by_time(edl_del_times, shrink_overlaps=True)
    process_results(args, start_file)

    return start_file


# SAVE RESULTS TO AN SRT FILE
def save_as_srt(args: ap.Namespace) -> srtfn.SrtFile:
    if not libfn.has_meaningful_value(args.save_as):
        log.error(f"No file name specified for saving. (use --save-as)")
        print(f" file name specified for saving. (use --save-as)")
        sys.exit(8)

    subs_file: srtfn.SrtFile = read(args)
    subs_file.write_to_file(args.save_as)
    return subs_file


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
SRT_COMMANDS = {"remove-gap": remove_one_gap,
                "remove-edl": remove_edl,
                "read": read,
                "save": save_as_srt,
                "show": show,
                "show-subtitle": display_subtitle_at,
                }


# *******************************************************
# *******************************************************
# *******************************************************

def srt_command_check(command: str) -> typing.Callable[[ap.Namespace], None]:
    try:
        return SRT_COMMANDS[command]

    except KeyError as ke:
        log.exception(ke)
        log.error(f"{command} is not a valid command.")
        print(f"\n{command} is not a valid command. Try one of these:")
        print(f"     {libfn.str_from_dict_keys(SRT_COMMANDS)}")
        sys.exit(1)


def new_file_name_check(file_name: str) -> str:
    if not os.path.exists(file_name):
        return file_name
    else:
        log.error(f"{file_name} already exists.")
        print(f"{file_name} already exists.")
        sys.exit(7)


def file_name_check(file_name: str) -> str:
    if os.path.isfile(file_name):
        return file_name
    else:
        log.error(f"{file_name} is not a readable file.")
        print(f"{file_name} is not a readable file.")
        sys.exit(2)


def timestamp_check(time_str: str) -> float:
    return timefn.hmsm_dur_to_secs(time_str)


def main():
    log.info(f'Command line params: {" ".join(sys.argv)}')
    parser: ap.ArgumentParser = ap.ArgumentParser(
        prog="srt-tool",
        description="SubRip Text (srt) tool"
    )

    parser.add_argument("command",
                        type=srt_command_check,
                        help="What to do. (Valid options: remove)"
                        )
    parser.add_argument("--from-file",
                        type=file_name_check
                        )
    parser.add_argument("--edl-file",
                        type=file_name_check
                        )
    parser.add_argument("--start-at",
                        type=timestamp_check
                        )
    parser.add_argument("--stop-at",
                        type=timestamp_check
                        )
    parser.add_argument("--edl-times",
                        type=file_name_check
                        )
    parser.add_argument("--at",
                        type=timestamp_check
                        )
    parser.add_argument("--save-as",
                        type=new_file_name_check
                        )
    parser.add_argument("--clean-escape-seq",
                        default=False,
                        action="store_true"
                        )
    parser.add_argument("--reindex",
                        default=False,
                        action="store_true"
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
