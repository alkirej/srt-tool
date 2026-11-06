from pathlib import Path
import sys

# **********************************
# add project src dir to import path
# **********************************
new_path: str = str(Path(__file__).resolve().parent.parent)
if new_path not in sys.path:
    sys.path.append(new_path)
# **********************************

FIELD_SEP = " | "


class ComskipTimeBlock:
    def __init__(self, comskip_log_line: str):
        self.log_line: str = comskip_log_line
        self.block_nbr: int
        self.note_list: [str] = []
        self.commercial: bool | None
        self.refer: bool | None
        self.black_frame_count: int
        self.black_frames_at_start: int
        self.black_frames_at_end: int
        self.start_frame: int
        self.stop_frame: int
        self.start_time: float
        self.stop_time: float
        self.time_length: float
        self.score: float
        self.scene_change_rate: float
        self.combination_count: int
        self.aspect_ratio: float
        self.cut_reasons: str     # !!! May want to change to some dictionary of bools
        self.brightness: int
        self.brightness_dir: str
        self.logo_percent: float
        self.volume: int
        self.volume_dir: str
        self.silence: int
        self.silence_dir: str
        self.corr: float  # --> what is it?
        self.std_dev: int
        self.captions: str

        data: [str] = comskip_log_line.split()

        # 1st characters have format 1:++
        # where the 1 is the block # (0 indexed)
        #     and ++ means non-commercial video
        #         -- means commercial video (to delete)
        # (int, str)
        (block_nbr, plus_minus) = data[0].split(":")
        self.block_nbr = int(block_nbr)

        # First +/- indicates if block is commercial
        if "+" == plus_minus[0]:
            self.commercial = False
        elif "-" == plus_minus[0]:
            self.commercial = True
        else:
            self.commercial = None

        # Second +/- indicates something about reference frames.
        if "+" == plus_minus[1]:
            self.refer = False
        elif "-" == plus_minus[1]:
            self.refer = True
        else:
            self.refer = None

        # sbf   bs   be
        self.black_frame_count = int(data[1])
        self.black_frames_at_start = int(data[2])
        self.black_frames_at_end = int(data[3])

        # fs  fe
        self.start_frame = int(data[4])
        self.stop_frame = int(data[5])

        # ts  te
        self.start_time = float(data[6][:-1])
        self.stop_time = float(data[7][:-1])

        # len
        self.time_length = float(data[8][:-1])
        # sc  = scoring to determine if block is in commercial
        self.score = float(data[9])

        # scr  cmb    ar
        self.scene_change_rate = float(data[10])
        self.combination_count = int(data[11])
        self.aspect_ratio = float(data[12])

        current_idx: int = 13
        cut_reason: [str] = []
        while data[current_idx][-1:] not in "+-0":
            cut_reason.append(data[current_idx])
            current_idx += 1
        self.cut_reasons = "".join(cut_reason)

        # bri
        self.brightness = int(data[current_idx][:-1])
        self.brightness_dir = data[current_idx][-1:]
        current_idx += 1

        # logo
        self.logo_percent = float(data[current_idx])
        current_idx += 1

        # vol
        self.volume = int(data[current_idx][:-1])
        self.volume_dir = data[current_idx][-1:]
        current_idx += 1

        # sil
        self.silence = int(data[current_idx][:-1])
        self.silence_dir = data[current_idx][-1:]
        current_idx += 1

        # corr stdev
        self.corr = float(data[current_idx])
        current_idx += 1
        self.std_dev = int(data[current_idx])
        current_idx += 1

        try:
            self.captions = data[current_idx]
        except IndexError:
            self.captions = ""

    @staticmethod
    def print_header() -> str:
        headers: [str] = [
            f"{'# ?':>5}",
            f"{'frame #s':^15}",
            f"{'times (in sec)':^15}",
            f"{'length':>7}",
            f"{'score':>6}",
            f"{'scr':^3}",         # scene change rate
            f"{'cbn':>3}",         # combined blocks
            f"{'a/r':>4}",         # aspect ration
            f"{'reason':>8}",      # reason the frame was cut
            f"{'lo%':>2}",         # logo percentage
            f"{'bright':6}",       # brightness
            f"{'volu':6}",         # volume
            f"{'silen':5}",        # silence
            ""
        ]

        return FIELD_SEP.join(headers)

    # BLACK FRAME COUNT (TOTAL, AT START, & AT END)
    # ARE NOT DISPLAYED AT THIS TIME (FOR SPACE)
    def __str__(self) -> str:
        return self.to_str()

    def to_str(self, include_notes: bool = False) -> str:
        if self.commercial is None:
            comm_str: str = "?"
        elif self.commercial is True:
            comm_str: str = "+"
        else:
            comm_str: str = " "

        if not include_notes or len(self.note_list) == 0:
            notes: str = ""
        else:
            notes: str = "\n    " + "\n    ".join(self.note_list)

        values: [str] = [
            f"{self.block_nbr:3} {comm_str}",
            f"{self.start_frame:7,}-{self.stop_frame:7,}",
            f"{self.start_time:7,.1f}-{self.stop_time:7,.1f}",
            f"{self.time_length:7.1f}",
            f"{self.score:6.2f}",
            f"{int(self.scene_change_rate*100):3}",
            f"{self.combination_count:3}",
            f"{self.aspect_ratio:>4.2f}",
            f"{self.cut_reasons:.>8}",
            f"{int(100*self.logo_percent):3}",
            f"{self.brightness:4} {self.brightness_dir:1}",
            f"{self.volume:4} {self.volume_dir:1}",
            f"{self.silence:3} {self.silence_dir:1}",
            f"{notes}"
            ""
        ]
        return FIELD_SEP.join(values)

    def add_note(self, note_text: str) -> None:
        self.note_list.append(note_text.strip())
