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
import logging as log
import os 
import sys

# **********************************
# CURRENT PROJECT LIBRARY IMPORTS
# **********************************
import srt_fns as sfn
import time_fns as tfn

SRT_SEPARATOR: str = " --> "

class SrtFile:
    def __init__(self, 
                 file_path: str = None
                ):
        # Ensure file is not actually a directory. If so, bad news.
        if os.path.isdir(file_path):
            log.error(f"{file_path} (a directory) cannot be a .srt file.")
            raise Error(f"{file_path} (a directory) cannot be a .srt file.")

        # Save the filename to read from (if supplied)
        self.file_name = file_path

        # If a filename is supplied, read in the subtitles.
        self.st_blocks: [sfn.SubtitleBlock] = self._load_from_file()

        # from -- read srt file

    def _load_from_file(self) -> [sfn.SubtitleBlock]:
        return_block_list: [sfn.SubtitleBlock] = []

        with open(self.file_name, "r") as srt_file:
            lines: [str] = srt_file.readlines()

        line_count: int = len(lines) 
        ln_nbr: int = 0

        while ln_nbr < line_count:
            index: int = int(lines[ln_nbr])
            ln_nbr += 1
            (start_index, stop_index) = lines[ln_nbr].split(SRT_SEPARATOR)
            time_block: tfn.TimeBlock = tfn.TimeBlock(start_index, stop_index)

            ln_nbr += 1
            subtitle_text: str = ""
            while len(lines[ln_nbr].strip()) > 0:
                subtitle_text += lines[ln_nbr]
                ln_nbr += 1

            new_block: sfn.SubtitleBlock = sfn.SubtitleBlock(index,time_block,subtitle_text)
            return_block_list.append(new_block)

            ln_nbr += 1

        return return_block_list

    def find_block_at(self, time: str|float) -> sfn.SubtitleBlock|None:
        secs: float = tfn.convert_to_secs(time)

        for block in self.st_blocks:
            if secs >= block.tb.start and secs <= block.tb.stop:
                return block

        return None

    def is_subtitle_here(self, time: str|float) -> bool:
        looking: sfn.SubtitleBlock|None = self.find_block_at(time)

        return looking != None

    def write_to_file(self, file_name: str) -> None:
        if os.path.exists(file_name):
            log.error(f"{file_name} already exists. Quiting")
            raise Exception(f"{file_name} already exists. Quiting")

        with open(file_name, "w") as srt_file:
            for block in self.st_blocks:
                srt_file.write( sfn.srt_block_output(block) )

        log.info(f"Saved subtitle file {file_name} with {len(self.st_blocks)} entries.")

    def end_of_last_subtitle(self) -> float:
        last_time: float = 0.0
        for b in self.st_blocks:
            if b.tb.stop > last_time:
                last_time = b.tb.stop
        return last_time

    def to_string(self) -> str:
        return "".join( sfn.srt_block_output(b) for b in self.st_blocks)

    def get_subtitles_from(self, 
                           tb: tfn.TimeBlock, 
                           include_overlaps: bool = False
                           ) -> [tfn.TimeBlock]:
        if include_overlaps:
            sub_include_fn: function = tb.contains_overlap
            print(f"overlap: yes -> {sub_include_fn}")
        else:
            sub_include_fn: function = tb.contains_duration
            print(f"overlap: no -> {sub_include_fn}")

        included_subtitles: [tfn.TimeBlock] = []

        for bl in self.st_blocks:
            if sub_include_fn(bl.tb):
                included_subtitles.append(bl)

        return included_subtitles


