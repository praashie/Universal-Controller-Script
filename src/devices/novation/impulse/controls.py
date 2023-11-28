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
)
from control_surfaces.event_patterns import BasicPattern, NotePattern
from control_surfaces.matchers import BasicControlMatcher
from control_surfaces.value_strategies import (
    Data2Strategy, NoteStrategy, TwosComplimentDeltaStrategy
)
from control_surfaces.managers import IValueManager

from .util import ImpulseAnnotationValueManager, ImpulseEncoderValueStrategy, ImpulseFaderButtonManager


def registerImpulseControls(matcher: BasicControlMatcher):
    registerDrumpads(matcher)
    registerMixerControls(matcher)
    registerEncoders(matcher)


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


def registerEncoders(matcher: BasicControlMatcher):
    for i in range(8):
        encoder = ImpulseEncoder(
            control_class=Encoder,
            index=i,
            coordinate=(i // 4, i % 4)
        )
        matcher.addControl(encoder)


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