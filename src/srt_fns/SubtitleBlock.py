# **********************************
# add project src dir to import path
# **********************************
import sys
from pathlib import Path
new_path: Path = str(Path(__file__).resolve().parent.parent)
if new_path not in sys.path:
    sys.path.append(new_path)
# **********************************

# **********************************
# PYTHON LIBRARY IMPORTS 
# **********************************

# **********************************
# CURRENT PROJECT LIBRARY IMPORTS
# **********************************
import time_fns as tfn

class SubtitleBlock:

    # **********************************
    # index = srt file index line (often ignored by video display apps)
    # times = TimeBlock indicating when the subtitle should begin and end
    #                its display on the screen.
    # text  = what to display on the screen subtitle line
    # **********************************
    def __init__(self, 
                 index: int, 
                 times: tfn.TimeBlock, 
                 text: str
                ):
        self.idx: int = index
        self.tb: TimeBlock = times
        self.to_display: str = text

