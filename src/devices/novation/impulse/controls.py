"""
devices > novation > impulse > controls

MIDI control message definitions

Authors:
* Praash [praashie@gmail.com, Praash#0846]

This code is licensed under the GPL v3 license. Refer to the LICENSE file for
more details.
"""

from control_surfaces.controls import (
    ControlSurface,
    DrumPad,
    Fader,
    GenericFaderButton,
    MasterFader,
    MasterGenericFaderButton,
)
from control_surfaces.event_patterns import BasicPattern, NotePattern
from control_surfaces.matchers import BasicControlMatcher
from control_surfaces.value_strategies import (
    Data2Strategy, NoteStrategy, TwosComplimentDeltaStrategy
)
from control_surfaces.managers import IValueManager

from .sysex import SYX_MSG_TEXT, SYX_MSG_TEXT2

import device


def setLcdText(msg: str):
    text_bytes = msg.encode("ascii", errors="ignore")
    device.midiOutSysex(SYX_MSG_TEXT + text_bytes)


def setLcdTinyText(msg: str):
    text_bytes = msg.encode("ascii", errors="ignore")
    device.midiOutSysex(SYX_MSG_TEXT2 + text_bytes)


def registerImpulseControls(matcher: BasicControlMatcher):
    registerDrumpads(matcher)
    registerMixerControls(matcher)


def registerDrumpads(matcher: BasicControlMatcher):
    # TODO: Documentation: Drum pads must be assigned to MIDI channel 16!
    # Default note layout starts from bottom left, C3 (60)

    drum_notes = [60, 62, 64, 65, 67, 69, 71, 72]
    for i, note in enumerate(drum_notes):
        coordinate = (1 - (i // 4), i % 4)
        pad = makeDrumpadControl(note, coordinate)
        matcher.addControl(pad)


def makeDrumpadControl(note: int, coordinate: tuple[int, int]) -> DrumPad:
    return DrumPad(
        NotePattern(note, 15),
        NoteStrategy(),
        coordinate
    )


def registerMixerControls(matcher: BasicControlMatcher):
    for i in range(8):
        fader = ImpulseFader(
            control_class=Fader,
            track_index=i,
            coordinate=(0, i)
        )
        button = ImpulseFaderButton(
            control_class=GenericFaderButton,
            track_index=i,
            coordinate=(0, i)
        )
        matcher.addControl(fader)
        matcher.addControl(button)


    matcher.addControl(ImpulseFader(MasterFader, 8))
    matcher.addControl(ImpulseFaderButton(MasterGenericFaderButton, 8))


class MidiCCValueManager(IValueManager):
    def __init__(self, channel: int, cc: int):
        self.channel = channel
        self.cc = cc

    def onValueChange(self, new_value: float) -> None:
        value_byte = round(max(0, min(255, 255 * new_value)))
        device.midiOutMsg((0xB0 + self.channel) + (self.cc << 8) + (value_byte << 16))

    def tick(self) -> None:
        # Used for basic control feedback - the Impulse is expected to memorize these.
        pass


def impulse_button_isPress(value: float):
    return value != 0.0


def ImpulseFaderButton(
    control_class: type[ControlSurface], track_index: int,
    coordinate: tuple[int, int] = (0, 0)
) -> ControlSurface:
    cc = 0x9 + track_index
    button = control_class(
        event_pattern=BasicPattern(0xB0, cc, ...),
        value_strategy=Data2Strategy(),
        coordinate=coordinate,
        value_manager=MidiCCValueManager(channel=0, cc=cc)
    )

    button.isPress = impulse_button_isPress
    return button


def ImpulseFader(
    control_class: type[ControlSurface], track_index: int,
    coordinate: tuple[int, int] = (0, 0)
) -> ControlSurface:
    return control_class(
        event_pattern=BasicPattern(0xB0, track_index, ...),
        value_strategy=Data2Strategy(),
        coordinate=coordinate,
        value_manager=MidiCCValueManager(channel=0, cc=track_index)
    )