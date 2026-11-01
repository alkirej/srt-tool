# lib_fns package for srt-tool
import logging as log
import os
import sys


# *******************************************************
# Accept a dictionary and return a comma separated string
# containing each of the keys from the dictionary
# *******************************************************
def str_from_dict_keys(working_dict: dict) -> str:
    return ", ".join(working_dict.keys())


# *******************************************************
# Does the supplied string value contain a "meaningful" value.
# A meaningful value is not a None value and not a string
# of length 0.
# *******************************************************
def has_meaningful_value(value: None | str) -> bool:
    return value is not None and len(value) > 0


# *******************************************************
# If the supplied file name exists, write an error to
# stdout and exit the program.  Do not allow the file
# to be overwritten.
# *******************************************************
def new_file_name_check(file_name: str) -> str:
    if not os.path.exists(file_name):
        return file_name
    else:
        log.error(f"{file_name} already exists.")
        print(f"{file_name} already exists.")
        sys.exit(7)


# *******************************************************
# If the supplied file name does not exists, write an
# error to stdout and exit the program.  Ensure the
# file exists (usually for reading).
# *******************************************************
def file_name_check(file_name: str) -> str:
    if os.path.isfile(file_name):
        return file_name
    else:
        log.error(f"{file_name} is not a readable file.")
        print(f"{file_name} is not a readable file.")
        sys.exit(2)
