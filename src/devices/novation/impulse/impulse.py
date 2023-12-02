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

from consts import getVersionString as getUcsVersionString
from control_surfaces.event_patterns import BasicPattern, NotePattern
from common.logger import log
from common.extension_manager import ExtensionManager
from control_surfaces.matchers import (
    BasicControlMatcher,
    IndexedMatcher,
    NoteMatcher,
)
from control_surfaces.value_strategies import Data2Strategy, NoteStrategy
from control_surfaces import (
    ChannelAfterTouch,
    ControlSurface,
    DrumPad,
    Fader,
    MasterFader,
    MasterGenericFaderButton,
    ModWheel,
    MuteButton,
    NullControl,
    GenericFaderButton,
    StandardModWheel,
    StandardPitchWheel,
    SustainPedal,
)

import device
from fl_classes import FlMidiMsg
import ui

from . import controls
from . import impulse_sysex
from .templates import ImpulseTemplateDumpMatcher, ImpulseTemplateData


class Impulse49_61(Device):
    """
    Novation Impulse 49/61 keyboard controller.
    """

    def __init__(self):
        self.matcher = BasicControlMatcher()

        self.drum_pads = controls.makeDrumpads()
        self.faders, self.fader_buttons = controls.makeMixerControls()
        self.encoders = controls.makeEncoders()
        self.transport_buttons = controls.makeTransportButtons()

        for control_set in (
            self.drum_pads, self.faders, self.fader_buttons,
            self.encoders, self.transport_buttons
        ):
            self.matcher.addControls(control_set)

        self.matcher.addSubMatcher(NoteMatcher())

        # In the advanced control mode, the modwheel is set to
        # channel 3 to avoid conflicts
        self.matcher.addControl(ModWheel(
            BasicPattern(0xB2, 0x1, ...),
            Data2Strategy(),
        ))
        self.matcher.addControl(StandardPitchWheel.create())
        self.matcher.addControl(SustainPedal.create())
        self.matcher.addControl(ChannelAfterTouch.fromChannel([0, 15]))

        # Soft-ignore the response from initialization
        self.matcher.addControl(NullControl(
            BasicPattern([
                0xF0, 0x00, 0x20, 0x29, 0x67, 0x07, ...
            ])
        ))

        self.matcher.addSubMatcher(ImpulseTemplateDumpMatcher(self.onTemplateDumped))

        super().__init__(self.matcher)

    @staticmethod
    def getId():
        return "Novation.Impulse.49_61"

    @staticmethod
    def getSupportedIds():
        return ("Novation.Impulse.49_61",)

    def initialize(self):
        self.deinitialize()
        impulse_sysex.initialize()

        log('general', 'Triggering template dump...')
        impulse_sysex.triggerTemplateDump()

        impulse_sysex.setLcdText(f"Universal Controller Script {getUcsVersionString()}")
        impulse_sysex.setLcdTinyText("UCS")
        log('device.impulse.init', 'Initialization message sent.')

    def deinitialize(self):
        log('device.impulse.init', 'Deinitialization message sent.')

    def onTemplateDumped(self, sysex_data: bytes):
        template = ImpulseTemplateData.parse(sysex_data)
        log('device.impulse.template', 'Received template data:')
        log('device.impulse.template', repr(template))

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


ExtensionManager.devices.register(Impulse49_61)
