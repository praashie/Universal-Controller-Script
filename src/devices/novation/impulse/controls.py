"""
devices > novation > impulse > controls

MIDI control message definitions

Authors:
* Praash [praashie@gmail.com, Praash#0846]

This code is licensed under the GPL v3 license. Refer to the LICENSE file for
more details.
"""

from typing import Optional, Sequence
from fl_classes import FlMidiMsg
from control_surfaces import (
    ControlEvent,
    ControlSurface,
    DrumPad,
    Fader,
    Encoder,
    GenericFaderButton,
    MasterFader,
    MasterGenericFaderButton,
    RewindButton,
    FastForwardButton,
    StopButton,
    PlayButton,
    LoopButton,
    RecordButton,
    TransportButton,
    DirectionNext,
    DirectionPrevious
)

from control_surfaces.event_patterns import BasicPattern, NotePattern
from control_surfaces.matchers import IControlMatcher
from control_surfaces.value_strategies import (
    Data2Strategy, NoteStrategy, TwosComplimentDeltaStrategy
)
from control_surfaces.managers import IValueManager

from .util import ImpulseAnnotationValueManager, ImpulseEncoderValueStrategy, ImpulseFaderButtonManager, ImpulseFakeAnnotationManager

from .templates import DrumPad as TemplateDrumPad


class ImpulseDrumPad(DrumPad):
    ...


class ImpulseDrumpadMatcher(IControlMatcher):
    def __init__(self):
        self._drum_pads: list[DrumPad] = makeDrumpads()

    def loadTemplatePads(self, template_pads: list[TemplateDrumPad]):
        for i, template_pad in enumerate(template_pads):
            channel = template_pad.midi_channel_port & 0x0F
            self._drum_pads[i]._ControlSurface__pattern = NotePattern(template_pad.note, channel)

    def matchEvent(self, event: FlMidiMsg) -> Optional[ControlEvent]:
        for pad in self._drum_pads:
            if (m := pad.match(event)) is not None:
                return m
        return None

    def getControls(self) -> Sequence[ControlSurface]:
        return self._drum_pads

    def tick(self, thorough: bool) -> None:
        pass


def makeDrumpads() -> list[DrumPad]:
    """
    Create a default set of drum pads. This assumes drum pads on channel 9 (10 on controllers)

    This won't work with some the default templates (such as "BascMIDI"),
    because the drum pads are assigned to the same channel as the keyboard.
    """

    drum_notes = [45, 47, 50, 46, 36, 38, 40, 42]
    drum_pads = []
    for i, note in enumerate(drum_notes):
        coordinate = ((i // 4), i % 4)
        drum_pads.append(makeDrumpadControl(note, 9, coordinate))
    return drum_pads


def makeDrumpadControl(note: int, channel: int, coordinate: tuple[int, int]) -> DrumPad:
    return DrumPad(
        NotePattern(note, channel),
        NoteStrategy(),
        coordinate
    )


def makeMixerControls() -> tuple[list[Fader], list[GenericFaderButton]]:
    faders = []
    buttons = []
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
        faders.append(fader)
        buttons.append(button)

    faders.append(ImpulseFader(MasterFader, 8))
    buttons.append(ImpulseFaderButton(MasterGenericFaderButton, 8))

    return faders, buttons


def makeEncoders() -> list[Encoder]:
    encoders = []
    for i in range(8):
        encoder = ImpulseEncoder(
            control_class=Encoder,
            index=i,
            coordinate=(i // 4, i % 4)
        )
        encoders.append(encoder)
    return encoders


def makeTransportButtons() -> list[TransportButton]:
    buttons = []
    controlTypes: list[tuple[ type[TransportButton], int ]] = [
        (DirectionPrevious, 0x26),
        (DirectionNext, 0x25),
        (RewindButton, 0x1B),
        (FastForwardButton, 0x1C),
        (StopButton, 0x1D),
        (PlayButton, 0x1E),
        (LoopButton, 0x1F),
        (RecordButton, 0x20)
    ]

    for cType, cc in controlTypes:
        button = cType(
            event_pattern=BasicPattern(0xB0, cc, ...),
            value_strategy=Data2Strategy(),
        )
        button.isPress = impulse_button_isPress
        buttons.append(button)

    return buttons


def impulse_button_isPress(value: float):
    return value != 0.0


def ImpulseFaderButton(
    control_class: type[ControlSurface], track_index: int,
    coordinate: tuple[int, int] = (0, 0)
) -> ControlSurface:

    cc = 0x9 + track_index
    manager = ImpulseFaderButtonManager(
        channel=0, cc=cc, annotation_group=1, annotation_slot=track_index)

    button = control_class(
        event_pattern=BasicPattern(0xB0, cc, ...),
        value_strategy=Data2Strategy(),
        coordinate=coordinate,
        value_manager=manager,
        annotation_manager=manager,
        color_manager=manager
    )

    button.isPress = impulse_button_isPress
    return button


def ImpulseFader(
    control_class: type[ControlSurface], track_index: int,
    coordinate: tuple[int, int] = (0, 0)
) -> ControlSurface:

    manager = ImpulseAnnotationValueManager(
        channel=0, cc=track_index, annotation_group=0, annotation_slot=track_index)

    return control_class(
        event_pattern=BasicPattern(0xB0, track_index, ...),
        value_strategy=Data2Strategy(),
        coordinate=coordinate,
        value_manager=manager,
        annotation_manager=manager
    )


def ImpulseEncoder(
    control_class: type[ControlSurface], index: int,
    coordinate: tuple[int, int] = (0, 0)
) -> ControlSurface:

    manager = ImpulseAnnotationValueManager(
        channel=1, cc=index, annotation_group=2, annotation_slot=index
    )

    return control_class(
        event_pattern=BasicPattern(0xB1, index, ...),
        coordinate=coordinate,
        value_strategy=ImpulseEncoderValueStrategy(),
        annotation_manager=manager,
        value_manager=manager
    )