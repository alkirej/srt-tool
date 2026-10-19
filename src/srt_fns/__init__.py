# **********************************
# add project src dir to import path
# **********************************
import sys
from pathlib import Path
new_path: Path = str(Path(__file__).resolve().parent.parent)
if new_path not in sys.path:
    sys.path.append(new_path)
 

# **********************************
# PYTHON LIBRARY IMPORTS
# **********************************
import logging as log

# **********************************
# CURRENT PROJECT LIBRARY IMPORTS
# **********************************
import time_fns as tfn
from .SubtitleBlock import SubtitleBlock

SRT_SEPARATOR: str = " --> "
BLANK_LINE: str = "\n"

def srt_time_output(tb: tfn.TimeBlock) -> str:
    start_at: str = tfn.secs_to_hmsm_dur(tb.start)
    stop_at: str = tfn.secs_to_hmsm_dur(tb.stop)

    if tb.stop < tb.start:
        log.error(f"Invalid sbt time block ({start_at}-{stop_at})")
        raise Exception(f"Invalid sbt time block ({start_at}-{stop_at})")

    return start_at + SRT_SEPARATOR + stop_at

def srt_block_output(sb: SubtitleBlock) -> str:
    srt_lines: [str] = [ str(sb.idx),
                         srt_time_output(sb.tb),
                         sb.to_display,
                         BLANK_LINE
                        ]
    return "\n".join(srt_lines)


