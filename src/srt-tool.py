# import datetime as dt                                                                 
import argparse as ap
import logging as log
# import os
# import shutil
import typing as t

# REMOVE TIME FROM SBT FILE SUPPLIED AND OUTPUTING UPDATED INFO
def remove( args: ap.Namespace ) -> None:
    pass

SBT_COMMANDS = {"remove-time": remove
               }

def sbt_command_check(command: str) -> t.Callable[ap.Namespace, None]:
    return SBT_COMMANDS[command]

def file_name_check(file_name: str) -> [str]:
    return file_name 

def timestamp(time: str) -> (int,int):
    time.strptime('01:01:09,000', '%H:%M:%S,%f')

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
                        required=True,
                        type=file_name_check
                        )
    parser.add_argument("--start-time", 
                        type=timestamp
                        )
    parser.add_argument("--stop-time", 
                        type=timestamp
                        )

    args = parser.parse_args()

    print( type(args) )
    print(dir(args))
    print(args.command)
    print(args.test)


print("uncomment to allow main() to be entered.")
# if "__main__" == __name__:
#    main()

import time_fns as t
import sys

timestp=sys.argv[1]
total_secs = t.to_secs(timestp)
print(f"Number seconds in {timestp} = {total_secs}")

