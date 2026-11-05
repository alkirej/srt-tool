import logging as log
from pathlib import Path
import sys

# **********************************
# add project src dir to import path
# **********************************
new_path: str = str(Path(__file__).resolve().parent.parent)
if new_path not in sys.path:
    sys.path.append(new_path)
# **********************************

from .ComskipTimeBlock import ComskipTimeBlock


class ComskipBlockList:
    def __init__(self, comskip_log_file: str):
        self.file_name = comskip_log_file
        self.blocks: [ComskipTimeBlock] = []
        self.notes: [str] = []

        self._load_blocks_from_log(comskip_log_file)

    def __getitem__(self, idx: int) -> ComskipTimeBlock:
        return self.blocks[idx]

    def _add_note(self, line_of_text: str) -> None:
        line_of_text = line_of_text.strip()
        bl_start: int = 0
        bl_end: int = 0
        words: [str] = line_of_text.split()

        if line_of_text.startswith("Block "):
            bl_start = int(words[1])
            bl_end = bl_start

        elif line_of_text.startswith("Combining Blocks "):
            bl_start = int(words[2])
            bl_end = int(words[4])

        elif words[1] in ["Added", "Deleting"] and words[2] == "cblock":
            bl_start = int(words[3])
            bl_end = bl_start

        else:
            self.notes.append(line_of_text)

        for bl in self.blocks:
            if bl_start <= bl.block_nbr <= bl_end:
                bl.add_note(line_of_text)

    def _load_blocks_from_log(self, comskip_log_file: str) -> None:
        if len(comskip_log_file) == 0:
            # log error and raise exception
            print(f"Cannot find {comskip_log_file}. Exiting.")
            log.error(f"Cannot find {comskip_log_file}. Exiting.")

        with open(self.file_name, "r", encoding="utf-8", errors="replace") as log_file:
            block_lines: [str] = log_file.readlines()

        # Search log file for desired data.
        log_file_iter: iter = iter(block_lines)

        try:
            # Read post weighing block data.
            arrived_to_block_list: bool = False
            bl_line: str = ""
            while not arrived_to_block_list:
                bl_line = next(log_file_iter)

                # SKIP UNTIL BLOCK LIST LINES ARE FOUND
                if "Block list after weighing" in bl_line:
                    arrived_to_block_list = True
                    # skip 3 lines
                    next(log_file_iter)    # ---- dashes
                    next(log_file_iter)    # # sbf ... header line
                    bl_line = next(log_file_iter)    # data starts here

            # Read in the blocks.
            while len(bl_line.strip()) > 0:
                next_bl: ComskipTimeBlock = ComskipTimeBlock(bl_line)
                self.blocks.append(next_bl)
                bl_line = next(log_file_iter)

        except Exception as e:
            print(e)
            sys.exit(1)

        # ----------------------------------------
        # ADD NOTES FROM FUZZY LOGIC TO THE BLOCKS
        # ----------------------------------------
        # Search from top of log file again.
        # Notes come to us before the weighted blocks.
        log_file_iter: iter = iter(block_lines)

        arrived_at_fuzzy_line: bool = False
        fuzzy_line: str = ""
        while not arrived_at_fuzzy_line:
            fuzzy_line = next(log_file_iter)
            if "Fuzzy scoring of the blocks" in fuzzy_line:
                arrived_at_fuzzy_line = True
                # skip the ----- line
                next(log_file_iter)
                fuzzy_line = next(log_file_iter)  # "Notes" start here

        while len(fuzzy_line.strip()) > 0:
            self._add_note(fuzzy_line)
            fuzzy_line = next(log_file_iter)
