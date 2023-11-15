"""
devices > novation > impulse > impulse

Device definitions for Novation Impulse controllers.

Authors:
* Praash [praashie@gmail.com, Praash#0846]

This code is licensed under the GPL v3 license. Refer to the LICENSE file for
more details.
"""

from typing import Optional

from devices import Device

from control_surfaces.event_patterns import BasicPattern, NotePattern
from common.logger import log
from common.extension_manager import ExtensionManager
from control_surfaces.matchers import (
    BasicControlMatcher,
    IndexedMatcher,
    NoteMatcher,
)
from control_surfaces.value_strategies import NoteStrategy
from control_surfaces import (
    ChannelAfterTouch,
    DrumPad,
    NullControl,
    StandardModWheel,
    StandardPitchWheel,
    SustainPedal,
)

import device
from fl_classes import FlMidiMsg



h = bytes.fromhex

SYX_IMPULSE_HEADER = h("F0 00 20 29 67")
SYX_MSG_INIT = SYX_IMPULSE_HEADER + h("06 01 01 01")
SYX_MSG_DEINIT = SYX_IMPULSE_HEADER + h("06 00 00 00")


class Impulse49_61(Device):
    """
    Novation Impulse 49/61 keyboard controller.
    """

    def __init__(self):
        self.matcher = BasicControlMatcher()

        self._registerDrumpads(self.matcher)
        self.matcher.addSubMatcher(NoteMatcher())
        self.matcher.addControl(StandardModWheel.create())
        self.matcher.addControl(StandardPitchWheel.create())
        self.matcher.addControl(ChannelAfterTouch.fromChannel([0, 15]))

        # Soft-ignore the response from initialization
        self.matcher.addControl(NullControl(
            BasicPattern([
                0xF0, 0x00, 0x20, 0x29, 0x67, 0x07, 0x3D
            ])
        ))

        super().__init__(self.matcher)

    def getId(self) -> str:
        return "Novation.Impulse.49_61"

    def getSupportedIds(self):
        return "Novation.Impulse.49_61"

    def initialize(self):
        self.deinitialize()
        device.midiOutSysex(SYX_MSG_INIT)
        log('device.impulse.init', 'Initialization message sent.')

    def deinitialize(self):
        device.midiOutSysex(SYX_MSG_DEINIT)
        log('device.impulse.init', 'Deinitialization message sent.')

    @classmethod
    def create(
        cls,
        event: Optional[FlMidiMsg] = None,
        id: Optional[str] = None
    ) -> Device:
        return cls()

    @classmethod
    def getDrumPadSize(cls):
        return 2, 4

    @staticmethod
    def getUniversalEnquiryResponsePattern():
        return BasicPattern(
            [
                0xF0, 0x7E, 0x7F, 0x06, 0x02,
                0x00, 0x20, 0x29,       # Manufacturer ID
                0x00, 0x1B,             # Device Family
                0x00, 0x1B,             # Device Model
            ]
        )

    @classmethod
    def _registerDrumpads(cls, matcher: BasicControlMatcher):
        # TODO: Documentation: Drum pads must be assigned to MIDI channel 16!
        # Default note layout starts from bottom left, C3 (60)

        drum_notes = [60, 62, 64, 65, 67, 69, 71, 72]
        for i, note in enumerate(drum_notes):
            coordinate = (1 - (i // 4), i % 4)
            pad = cls._makeDrumpadControl(note, coordinate)
            matcher.addControl(pad)

    @classmethod
    def _makeDrumpadControl(cls, note: int, coordinate: tuple[int, int]) -> DrumPad:
        return DrumPad(
            NotePattern(note, 15),
            NoteStrategy(),
            coordinate
        )


ExtensionManager.devices.register(Impulse49_61)
