# edl_fns package for srt-tool

# **********************************
# add project src dir to import path
# **********************************
import sys
from pathlib import Path
new_path: str = str(Path(__file__).resolve().parent.parent)
if new_path not in sys.path:
    sys.path.append(new_path)

import time_fns as time

from .ComskipTimeBlock import ComskipTimeBlock
from .ComskipBlockList import ComskipBlockList


EDL_ACTION_DELETE: int = 3

EDL_FIELD_START: int = 0
EDL_FIELD_STOP: int = 1
EDL_FIELD_ACTION: int = 2


def read_deletes_in_edl_file(file_name: str) -> [time.TimeBlock]:
    time_blocks: [time.TimeBlock] = []

    with open(file_name, "r") as edl_file:
        lines: [str] = edl_file.readlines()

    for ln in lines:
        # skip blank lines
        if len(ln.strip()) == 0:
            continue
        data: [str] = ln.split()
        start: float = float(data[EDL_FIELD_START])

        if int(data[EDL_FIELD_ACTION]) == EDL_ACTION_DELETE:
            tb: time.TimeBlock = time.TimeBlock(
                                     start,
                                     float(data[EDL_FIELD_STOP])
                                 )
            time_blocks.append(tb)

    time_blocks.sort(key=lambda tbl: tbl.start)
    return time_blocks


def write_deletes_to_edl_file(times: [time.TimeBlock], file_name: str) -> None:
    with open(file_name, "w") as edl_file:
        for t in times:
            start = time.convert_to_secs(t.start)
            stop = time.convert_to_secs(t.stop)
            edl_file.write(f"{start}\t{stop}\t{EDL_ACTION_DELETE}\n")


def read_comskip_log_weighted_block_info(file_name: str) -> ComskipBlockList:
    return ComskipBlockList(file_name)
