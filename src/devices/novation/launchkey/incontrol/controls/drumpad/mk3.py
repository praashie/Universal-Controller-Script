
from .drumpad import LkDrumPad
from ...colors.mk3 import COLORS

DRUM_PADS = [
    [0x60, 0x61, 0x62, 0x63, 0x64, 0x65, 0x66, 0x67],
    [0x70, 0x71, 0x72, 0x73, 0x74, 0x75, 0x76, 0x77],
]


class LkMk3DrumPad(LkDrumPad):

    def __init__(self, row: int, col: int) -> None:
        super().__init__(
            (row, col),
            0x0,
            DRUM_PADS[row][col],
            COLORS,
        )

    @classmethod
    def create(cls, row: int, col: int) -> 'LkMk3DrumPad':
        return LkMk3DrumPad(row, col)
