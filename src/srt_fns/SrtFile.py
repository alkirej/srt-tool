# **********************************
# PYTHON LIBRARY IMPORTS
# **********************************
import logging as log
from pathlib import Path
import os
import sys
from typing import Self

# **********************************
# add project src dir to import path
# **********************************
new_path: str = str(Path(__file__).resolve().parent.parent)
if new_path not in sys.path:
    sys.path.append(new_path)
# **********************************
 

# **********************************
# CURRENT PROJECT LIBRARY IMPORTS
# **********************************
import srt_fns as sfn
import time_fns as tfn

SRT_SEPARATOR: str = " --> "


class SrtFile:
    def __init__(self, 
                 file_path: str = ""
                 ):
        if len(file_path) > 0:
            # Ensure file is not actually a directory. If so, bad news.
            if os.path.isdir(file_path):
                log.error(f"{file_path} (a directory) cannot be a .srt file.")
                raise Exception(f"{file_path} (a directory) cannot be a .srt file.")

        # Save the filename to read from (if supplied)
        self.file_name = file_path

        # If a filename is supplied, read in the subtitles.
        self.st_blocks: [sfn.SubtitleBlock] = self._load_from_file()

        # from -- read srt file

    def supply_subtitle_list(self, subt_list: [sfn.SubtitleBlock]) -> Self:
        self.st_blocks = subt_list
        return self

    def _load_from_file(self) -> [sfn.SubtitleBlock]:
        return_block_list: [sfn.SubtitleBlock] = []

        if len(self.file_name) == 0:
            return return_block_list

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

            new_block: sfn.SubtitleBlock = sfn.SubtitleBlock(index, time_block, subtitle_text)
            return_block_list.append(new_block)

            ln_nbr += 1

        return return_block_list

    def find_block_at(self, time: str | float) -> sfn.SubtitleBlock | None:
        secs: float = tfn.convert_to_secs(time)

        for block in self.st_blocks:
            if block.tb.start <= secs <= block.tb.stop:
                return block

        return None

    def is_subtitle_here(self, time: str | float) -> bool:
        looking: sfn.SubtitleBlock | None = self.find_block_at(time)

        return looking is not None

    def write_to_file(self, file_name: str,
                      reindex_blocks: bool = False
                      ) -> Self:
        block_index: int = 0
        if os.path.exists(file_name):
            log.error(f"{file_name} already exists. Quiting")
            raise Exception(f"{file_name} already exists. Quiting")

        with open(file_name, "w") as srt_file:
            for block in self.st_blocks:
                if reindex_blocks:
                    block_index += 1
                    block.idx = block_index
                srt_file.write(sfn.srt_block_output(block))

        log.info(f"Saved subtitle file {file_name} with {len(self.st_blocks)} entries.")
        return self

    def write_to_stdout(self, reindex_blocks: bool = False) -> Self:
        print(reindex_blocks)
        block_index = 0
        for block in self.st_blocks:
            if reindex_blocks:
                block_index += 1
                block.idx = block_index
            print(sfn.srt_block_output(block))
        return self

    def end_of_last_subtitle(self) -> float:
        last_time: float = 0.0
        for b in self.st_blocks:
            if b.tb.stop > last_time:
                last_time = b.tb.stop
        return last_time

    def to_string(self) -> str:
        return "".join(sfn.srt_block_output(b) for b in self.st_blocks)

    def get_subtitles_from(self, 
                           tb: tfn.TimeBlock, 
                           include_overlaps: bool = False
                           ) -> [tfn.TimeBlock]:
        if include_overlaps:
            sub_include_fn: function = tb.contains_overlap
        else:
            sub_include_fn: function = tb.contains_duration

        included_subtitles: [tfn.TimeBlock] = []

        for bl in self.st_blocks:
            if sub_include_fn(bl.tb):
                included_subtitles.append(bl)

        return included_subtitles

    # *****************************************************
    # REMOVE ONE SUBTITLE FROM THE FILE
    # remove_me parameter can be the index of the block (int)
    #           or a single subtitle that will be found and removed.
    # The deleted subtitle information is returned if one was
    #           found and deleted. None is returned if no match
    #           was found
    # *****************************************************
    def remove_one_subtitle(self,
                            remove_me: sfn.SubtitleBlock | int
                            ) -> sfn.SubtitleBlock:
        if type(remove_me) is sfn.SubtitleBlock:
            idx: int = remove_me.idx
        else:
            idx: int = int(remove_me)

        for subt in self.st_blocks:
            if idx == subt.idx:
                self.st_blocks.remove(subt)
                return subt

        return None

    def remove_subtitles_by_time(self,
                                 time_range: tfn.TimeBlock,
                                 shrink_overlaps: bool = False
                                 ) -> int:
        removed_blocks: [sfn.SubtitleBlock] = []
        to_remove: [sfn.SubtitleBlock] = self.get_subtitles_from(time_range, include_overlaps=True)

        for subt in to_remove:
            if shrink_overlaps:
                if subt.tb.cut_to(time_range) is False:
                    deleted: sfn.SubtitleBlock = self.remove_one_subtitle(subt)
                    if deleted is not None:
                        removed_blocks.append(subt)
            else:
                deleted: sfn.SubtitleBlock = self.remove_one_subtitle(subt)
                if deleted is not None:
                    removed_blocks.append(subt)

        return len(removed_blocks)
