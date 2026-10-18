import argparse as ap
import logging as log
import os as os
import sys
import typing 


import lib_fns as libfn
import time_fns as timefn

# REMOVE TIME FROM SBT FILE SUPPLIED AND OUTPUTING UPDATED INFO
def remove( args: ap.Namespace ) -> None:
    if not libfn.has_meaningful_value(args.from_file):
        log.error(f"Cannot find file to remove things from.")
        print(f"Cannot find file to remove things from.")
        sys.exit(3)

    if not libfn.has_meaningful_value(args.edl_times):
        log.error(f"Cannot find file of blocks of time to remove.")
        print(f"Cannot find file of blocks of time to remove.")
        sys.exit(4)

    print("TIME TO IMPLEMENT REMOVAL OF EDL DATA FROM SRT FILE")


# *******************************************************
# *******************************************************
# *******************************************************
SBT_COMMANDS = {"remove-time": remove,
                "remove": remove
               }
# *******************************************************
# *******************************************************
# *******************************************************

def sbt_command_check(command: str) -> typing.Callable[ap.Namespace, None]:
    try:
        return SBT_COMMANDS[command]

    except KeyError as ke:
        log.exception(ke)
        log.error(f"{command} is not a valid command.")
        print(f"\n{command} is not a valid command. Try one of these:")
        print(f"     {libfn.str_from_dict_keys(SBT_COMMANDS)}")
        sys.exit(1)

def file_name_check(file_name: str) -> str:
    if os.path.isfile(file_name):
        return file_name
    else:
        log.error(f"{file_name} is not a readable file.")
        print(f"{file_name} is not a readable file.")
        sys.exit(2)


def timestamp_check(time_str: str) -> int:
    return hmsm_dur_to_secs(time_str)


def main():
    parser: ArgumentParser = ap.ArgumentParser(
                                 prog="srt-tool",
                                 description="SubRip Text (srt) tool"
                             )

    parser.add_argument("command",
                        type=sbt_command_check,
                        help="What to do. (Valid options: remove)"
                        )
    parser.add_argument("--from-file", 
                        type=file_name_check
                        )
    parser.add_argument("--start-time", 
                        type=timestamp_check
                        )
    parser.add_argument("--stop-time", 
                        type=timestamp_check
                        )
    parser.add_argument("--clean-escape-seq",
                        default=False,
                        action="store_true"
                        )
    parser.add_argument("--edl-times",
                        type=file_name_check
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


