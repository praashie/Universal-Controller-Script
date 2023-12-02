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
from control_surfaces.matchers import BasicControlMatcher
from control_surfaces.value_strategies import (
    Data2Strategy, NoteStrategy, TwosComplimentDeltaStrategy
)
from control_surfaces.managers import IValueManager

from .util import ImpulseAnnotationValueManager, ImpulseEncoderValueStrategy, ImpulseFaderButtonManager, ImpulseFakeAnnotationManager


def makeDrumpads() -> list[DrumPad]:
    # TODO: Documentation: Drum pads must be assigned to MIDI channel 16!
    # Default note layout starts from bottom left, C3 (60)

    drum_notes = [60, 62, 64, 65, 67, 69, 71, 72]
    drum_pads = []
    for i, note in enumerate(drum_notes):
        coordinate = (1 - (i // 4), i % 4)
        drum_pads.append(makeDrumpadControl(note, coordinate))
    return drum_pads


def makeDrumpadControl(note: int, coordinate: tuple[int, int]) -> DrumPad:
    return DrumPad(
        NotePattern(note, 15),
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