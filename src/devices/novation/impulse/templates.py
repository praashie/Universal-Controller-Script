from dataclasses import dataclass, astuple
from typing import Optional as O, Sequence


from control_surfaces.event_patterns import (
    BasicPattern,
    fromNibbles,
    ByteMatch,
)
from fl_classes import FlMidiMsg, isMidiMsgSysex
from control_surfaces import ControlEvent, ControlSurface
from control_surfaces.controls import NullControl
from control_surfaces.control_mapping import ControlEvent
from control_surfaces.event_patterns import BasicPattern
from control_surfaces.matchers import IControlMatcher


TEMPLATE_SYSEX_PREFIX_BYTES = [
    0xF0, 0x00, 0x20, 0x29,
    0x43, 0x00, 0x00
]


class ImpulseTemplateDumpMatcher(IControlMatcher):
    """
    Matches a SysEx template dump from Novation Impulse
    """
    def __init__(self):
        super().__init__()

        self._control = NullControl(BasicPattern(TEMPLATE_SYSEX_PREFIX_BYTES))

    def matchEvent(self, event: FlMidiMsg) -> O[ControlEvent]:
        if not isMidiMsgSysex(event):
            return None

        result = self._control.match(event)
        if result:
            print("=" * 100)
            print("HOORAY! WE GOT DUMPED! oh.")
            print("=" * 100)
            return result
        return None


    def getControls(self) -> Sequence[ControlSurface]:
        return []

    def tick(self, thorough: bool) -> None:
        return


@dataclass
class KeyboardZone:
    note_start: int
    note_end: int
    note_octave: int
    midi_channel: int
    midi_port: int

    @staticmethod
    def parse(start: int, end: int, octave: int, channel: int, port: int):
        return KeyboardZone(start, end, octave - 64, channel, port)

    def dump(self) -> bytes:
        return (self.note_start, self.note_end, self.note_octave + 64, self.midi_channel, self.midi_port)


@dataclass
class DrumPad:
    message_type: int
    note: int
    max_value: int
    min_value: int
    midi_channel_port: int
    rpn_lsb: int
    rpn_msb: int

OFFSET_NAME = slice(7, 15)
OFFSET_KBD_ZONES = 22
OFFSET_DRUM_PADS = 98

@dataclass
class ImpulseTemplateData:
    name: str
    keyboard_channel: int
    keyboard_port: int
    keyboard_velocity_curve: int
    aftertouch: bool
    octave: int
    transpose: int
    keyboard_zones_enabled: bool
    keyboard_zones: list[KeyboardZone]
    drum_pads: list[DrumPad]

    @staticmethod
    def parse(dump: bytes) -> 'ImpulseTemplateData':
        """
        Parse an Impulse template SysEx dump.
        The parsing is not exhaustive.
        """
        prefix = dump[0:7]
        assert prefix == bytes(TEMPLATE_SYSEX_PREFIX_BYTES)

        template_name = dump[OFFSET_NAME].decode(errors='replace')

        keyboard_channel = dump[15]
        keyboard_port = dump[16]
        keyboard_velocity_curve = dump[17]
        aftertouch = bool(dump[18])
        octave = dump[19] - 64
        transpose = dump[20] - 11
        keyboard_zones_enabled = bool(dump[21])

        keyboard_zones: list[KeyboardZone] = []
        for i in range(4):
            offset = OFFSET_KBD_ZONES + i * 5
            zone_data = dump[offset:offset+5]
            keyboard_zones.append(KeyboardZone.parse(*zone_data))

        drum_pads: list[DrumPad] = []
        for i in range(8):
            offset = OFFSET_DRUM_PADS + i * 7
            pad_data = dump[offset:offset+7]
            drum_pads.append(DrumPad(*pad_data))

        return ImpulseTemplateData(
            name=template_name,
            keyboard_channel=keyboard_channel,
            keyboard_port=keyboard_port,
            aftertouch=aftertouch,
            keyboard_velocity_curve=keyboard_velocity_curve,
            keyboard_zones_enabled=keyboard_zones_enabled,
            keyboard_zones=keyboard_zones,
            octave=octave,
            transpose=transpose,
            drum_pads=drum_pads
        )

    def apply_patch(self, template: bytes) -> bytes:
        """
        Patch an existing Impulse SysEx dump using the data
        in this template object. This allows uploading modified
        templates back to the Impulse keyboard.
        """

        data = bytearray(template)

        encoded_name = self.name.encode(encoding='ascii', errors='replace')[:8].ljust(8)
        data[OFFSET_NAME] = encoded_name

        data[15] = self.keyboard_channel
        data[16] = self.keyboard_port
        data[17] = self.keyboard_velocity_curve
        data[18] = int(self.aftertouch)
        data[19] = self.octave + 64
        data[20] = self.transpose + 11
        data[21] = int(self.keyboard_zones_enabled)

        for i in range(4):
            offset = OFFSET_KBD_ZONES + i * 5
            data[offset:offset+5] = self.keyboard_zones[i].dump()

        for i in range(8):
            offset = OFFSET_DRUM_PADS + i * 7
            data[offset:offset+7] = astuple(self.drum_pads[i])

        return bytes(data)


def patch_template_for_ucs(template: ImpulseTemplateData):
    ...