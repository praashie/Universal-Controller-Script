"""
control_surfaces > controls > wheel

Contains the definitions for pitch and modulation wheels

Authors:
* Miguel Guthridge [hdsq@outlook.com.au, HDSQ#2154]

This code is licensed under the GPL v3 license. Refer to the LICENSE file for
more details.
"""

from ..event_patterns import IEventPattern, BasicPattern, fromNibbles
from fl_classes import EventData, isEventStandard
from . import ControlSurface
from ..value_strategies import Data2Strategy, IValueStrategy

__all__ = [
    'ModWheel',
    'PitchWheel',
    'StandardModWheel',
    'StandardPitchWheel',
    'Data2PitchWheel',
]


class ModWheel(ControlSurface):
    """
    Represents a modulation wheel
    """
    @staticmethod
    def getControlAssignmentPriorities() -> 'tuple[type[ControlSurface], ...]':
        return tuple()


class StandardModWheel(ModWheel):
    """
    Standard implementation of a mod wheel
    """

    def __init__(self) -> None:
        super().__init__(
            BasicPattern(fromNibbles(0xB, ...), 0x1, ...),
            Data2Strategy(),
        )


class PitchValueStrategy(IValueStrategy):
    """
    Value strategy for standard pitch bends (using 14 bits of information,
    0 - 16384, zero at 8192)
    """

    def getValueFromEvent(self, event: EventData, value: float) -> float:
        """Returns a 14-bit int (0 - 16384)
        Zero value = 8192
        """
        assert isEventStandard(event)
        return (event.data1 + (event.data2 << 7)) / 16383

    def getChannelFromEvent(self, event: EventData) -> int:
        assert isEventStandard(event)
        return event.status & 0xF


class PitchWheel(ControlSurface):
    """
    Represents a pitch bend wheel
    """
    @staticmethod
    def getControlAssignmentPriorities() -> 'tuple[type[ControlSurface], ...]':
        return tuple()

    def __init__(
        self,
        event_pattern: IEventPattern,
        value_strategy: IValueStrategy
    ) -> None:
        super().__init__(event_pattern, value_strategy)


class StandardPitchWheel(PitchWheel):
    """
    Standard implementation of a pitch bend wheel (using 14 bits of
    information)
    """

    def __init__(self) -> None:
        super().__init__(
            BasicPattern(fromNibbles(0xE, ...), ..., ...),
            PitchValueStrategy()
        )


class Data2PitchWheel(PitchWheel):
    """
    Implementation of a pitch wheel using data2 values to determine pitch, as
    some manufacturers don't follow the standard of using 14 bits or precision.
    """

    def __init__(self) -> None:
        super().__init__(
            BasicPattern(fromNibbles(0xE, ...), 0x0, ...),
            Data2Strategy()
        )
