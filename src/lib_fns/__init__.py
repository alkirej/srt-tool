# lib_fns package for srt-tool

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
