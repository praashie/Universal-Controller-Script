
from controlsurfaces.eventpatterns import BasicPattern, ForwardedPattern
from controlsurfaces.valuestrategies import (
    ButtonData2Strategy,
    ForwardedStrategy
)
from controlsurfaces import (
    DirectionUp,
    DirectionDown,
    DirectionLeft,
    DirectionRight,
)
from .. import ColorInControlSurface, GrayscaleInControlSurface
from ...colors.mk3 import COLORS
from ...colors.greyscale import COLORS as GRAYSCALE


class MiniMk3DirectionUp(ColorInControlSurface, DirectionUp):
    def __init__(self) -> None:
        ColorInControlSurface.__init__(
            self,
            0x0,
            0x68,
            COLORS,
        )
        DirectionUp.__init__(
            self,
            ForwardedPattern(2, BasicPattern(0xB0, 0x68, ...)),
            ForwardedStrategy(ButtonData2Strategy())
        )


class MiniMk3DirectionDown(ColorInControlSurface, DirectionDown):
    def __init__(self) -> None:
        ColorInControlSurface.__init__(
            self,
            0x0,
            0x69,
            COLORS,
        )
        DirectionDown.__init__(
            self,
            ForwardedPattern(2, BasicPattern(0xB0, 0x69, ...)),
            ForwardedStrategy(ButtonData2Strategy())
        )


class Mk3DirectionUp(ColorInControlSurface, DirectionUp):
    def __init__(self) -> None:
        ColorInControlSurface.__init__(
            self,
            0x0,
            0x6A,
            COLORS,
        )
        DirectionUp.__init__(
            self,
            ForwardedPattern(2, BasicPattern(0xBF, 0x6A, ...)),
            ForwardedStrategy(ButtonData2Strategy())
        )


class Mk3DirectionDown(ColorInControlSurface, DirectionDown):
    def __init__(self) -> None:
        ColorInControlSurface.__init__(
            self,
            0x0,
            0x6B,
            COLORS,
        )
        DirectionDown.__init__(
            self,
            ForwardedPattern(2, BasicPattern(0xBF, 0x6B, ...)),
            ForwardedStrategy(ButtonData2Strategy())
        )


class Mk3DirectionLeft(GrayscaleInControlSurface, DirectionLeft):
    def __init__(self) -> None:
        GrayscaleInControlSurface.__init__(
            self,
            0xF,
            0x67,
            GRAYSCALE,
        )
        DirectionLeft.__init__(
            self,
            ForwardedPattern(2, BasicPattern(0xBF, 0x67, ...)),
            ForwardedStrategy(ButtonData2Strategy())
        )


class Mk3DirectionRight(GrayscaleInControlSurface, DirectionRight):
    def __init__(self) -> None:
        GrayscaleInControlSurface.__init__(
            self,
            0xF,
            0x66,
            GRAYSCALE,
        )
        DirectionRight.__init__(
            self,
            ForwardedPattern(2, BasicPattern(0xBF, 0x66, ...)),
            ForwardedStrategy(ButtonData2Strategy())
        )
