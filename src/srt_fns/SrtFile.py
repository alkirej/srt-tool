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
        self.st_blocks.sort(key=lambda bl: bl.tb.start)
        self.clean()

    def supply_subtitle_list(self, subt_list: [sfn.SubtitleBlock]) -> Self:
        self.st_blocks = subt_list
        self.st_blocks.sort(key=lambda bl: bl.tb.start)

        return self

    def _load_from_file(self) -> [sfn.SubtitleBlock]:
        return_block_list: [sfn.SubtitleBlock] = []

        if len(self.file_name) == 0:
            return return_block_list

        with open(self.file_name, "r", encoding="latin-1") as srt_file:
            lines: [str] = srt_file.readlines()

        line_count: int = len(lines) 
        ln_nbr: int = 0
        valid_times: bool = True

        while ln_nbr < line_count:
            time_block: tfn.TimeBlock | None = None
            index: int = int(lines[ln_nbr])
            ln_nbr += 1
            (start_index, stop_index) = lines[ln_nbr].split(SRT_SEPARATOR)
            try:
                time_block: tfn.TimeBlock = tfn.TimeBlock(start_index, stop_index)
            except tfn.TimeException:
                valid_times = False

            ln_nbr += 1
            subtitle_text: str = ""
            while len(lines[ln_nbr].strip()) > 0:
                subtitle_text += f"{lines[ln_nbr].strip()}\n"
                ln_nbr += 1

            if time_block is not None and valid_times:
                new_block: sfn.SubtitleBlock = sfn.SubtitleBlock(index, time_block, subtitle_text)
                return_block_list.append(new_block)
            else:
                valid_times = True

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

    def write_to_file(self,
                      file_name: str,
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

                try:
                    srt_file.write(sfn.srt_block_output(block))
                except tfn.TimeException:
                    # sometimes the broadcast sends bad subtitle timestamps
                    # that end before the start. Let's ignore these.
                    block_index -= 1
                    pass

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
                                 dlt_tm_blks: [tfn.TimeBlock],
                                 shrink_overlaps: bool = False
                                 ) -> int:
        dlt_tm_blks.sort(key=lambda bl: bl.start)
        removed_time: float = 0.0
        del_block_iter = iter(dlt_tm_blks)
        try:
            current_block: tfn.TimeBlock = next(del_block_iter)
        # nothing found to delete
        except StopIteration:
            return 0
        first_block: tfn.TimeBlockj = current_block
        blocks_to_delete: [sfn.SubtitleBlock] = []
        no_more_blocks: bool = False

        # loop through all subtitle entries in collection/file
        for subt in self.st_blocks:
            # Is this subtitle entry inside a block of time to be deleted?
            block: tfn.TimeBlock = subt.tb
            after_time_block: bool = block.start > current_block.stop

            # Handle special case of moving out of a deletion block.
            if after_time_block and not no_more_blocks:
                removed_time += current_block.get_block_duration()
                try:
                    current_block = next(del_block_iter)
                except StopIteration:
                    # indicates we are past the last section to delete.
                    # Noting will match the current block for the rest
                    # of the loop and this is what we want, so no
                    # concerns.
                    no_more_blocks = True

            now_in_time_block: bool = current_block.contains_overlap(block)
            # Handle deletion of some or all of subtitle entry
            if now_in_time_block:
                # truncate the current subtitle time range if part of
                # it is deleted, but not all of it.
                # returning false from cut_to method means entry needs to
                # be completely deleted.
                if shrink_overlaps and subt.tb.cut_to(current_block):
                    # When we remove only a portion of a subtitle display entry,
                    # we must be careful to remove the correct amount of time
                    # to keep things in sink
                    if first_block is current_block:
                        current_block_dur: float = 0.0

                    # crossing the start of a delete time block
                    # delete previously deleted time, but not this block.
                    elif subt.tb.stop < current_block.start:
                        current_block_dur: float = 0.0

                    # crossing the end of a delete time block
                    # delete previously deleted time AND the time in
                    # the current block.
                    else:
                        current_block_dur: float = current_block.get_block_duration()

                    subt.tb.start -= (removed_time + current_block_dur)
                    subt.tb.stop -= (removed_time + current_block_dur)
                else:
                    blocks_to_delete.append(subt)

            # we are not inside a deletion block. Only need to adjust the
            # times by the currently deleted amount.
            else:
                subt.tb.start -= removed_time
                subt.tb.stop -= removed_time

        for subt in blocks_to_delete:
            self.st_blocks.remove(subt)

        return len(blocks_to_delete)

    def clean(self) -> None:
        overlap_count: int = 0
        previous_end_time: float = 0.0
        for st in self.st_blocks:
            start_time: float = st.tb.start

            if start_time < previous_end_time:
                overlap_count += 1
                st.tb.start = previous_end_time
                st.tb.add_minimum_to_block()

            previous_end_time = st.tb.stop

        log.info(f"Found {overlap_count} overlapping subtitles in '{self.file_name}'.")
