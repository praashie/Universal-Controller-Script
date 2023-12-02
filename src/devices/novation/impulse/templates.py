from typing import Callable, Optional as O, Sequence

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
    def __init__(self, template_callback: 'Callable[[bytes], None]'):
        super().__init__()

        self._control = NullControl(BasicPattern(TEMPLATE_SYSEX_PREFIX_BYTES))
        self.template_callback = template_callback

    def matchEvent(self, event: FlMidiMsg) -> 'O[ControlEvent]':
        if not isMidiMsgSysex(event):
            return None

        result = self._control.match(event)
        if result:
            self.template_callback(event.sysex)
            return result
        return None


    def getControls(self) -> Sequence[ControlSurface]:
        return []

    def tick(self, thorough: bool) -> None:
        return


class KeyboardZone:
    def __init__(self, start: int, end: int, octave: int, channel: int, port: int):
        self.start = start
        self.end = end
        self.octave = octave
        self.channel = channel
        self.port = port

    @staticmethod
    def parse(start: int, end: int, octave_byte: int, channel: int, port: int) -> 'KeyboardZone':
        return KeyboardZone(start, end, octave_byte - 64, channel, port)

    def dump(self) -> bytes:
        return bytes((self.start, self.end, self.octave + 64, self.channel, self.port))

    def __repr__(self):
        return f'KeyboardZone(start={self.start}, end={self.end}, octave={self.octave}, channel={self.channel}, port={self.port})'

    def __eq__(self, other: 'KeyboardZone') -> bool:
        return self.dump() == other.dump()


class DrumPad:
    def __init__(self, message_type: int, note: int, max_value: int, min_value: int, midi_channel_port: int, rpn_lsb: int, rpn_msb: int):
        self.message_type = message_type
        self.note = note
        self.max_value = max_value
        self.min_value = min_value
        self.midi_channel_port = midi_channel_port
        self.rpn_lsb = rpn_lsb
        self.rpn_msb = rpn_msb

    def dump(self) -> bytes:
        return bytes((self.message_type, self.note, self.max_value, self.min_value, self.midi_channel_port, self.rpn_lsb, self.rpn_msb))

    def __eq__(self, other: 'DrumPad') -> bool:
        return self.dump() == other.dump()

    def __repr__(self) -> str:
        return (
            "DrumPad("
            f"message_type={self.message_type},"
            f"note={self.note}, "
            f"max_value={self.max_value}), "
            f"min_value={self.min_value}), "
            f"midi_channel_port={self.midi_channel_port}), "
            f"rpn_lsb={self.rpn_lsb}), "
            f"rpn_msb={self.rpn_msb}), "
        )


OFFSET_NAME = slice(7, 15)
OFFSET_KBD_ZONES = 22
OFFSET_DRUM_PADS = 98


class ImpulseTemplateData:
    """
    Data structure for parsing an Impulse template SysEx dump.
    The parsing is not exhaustive.
    """
    def __init__(self, dump: bytes):
        prefix = dump[0:7]
        assert prefix == bytes(TEMPLATE_SYSEX_PREFIX_BYTES)

        self.name = dump[OFFSET_NAME].decode(errors='replace')

        self.keyboard_channel = dump[15]
        self.keyboard_port = dump[16]
        self.keyboard_velocity_curve = dump[17]
        self.aftertouch = bool(dump[18])
        self.octave = dump[19] - 64
        self.transpose = dump[20] - 11
        self.keyboard_zones_enabled = bool(dump[21])

        self.keyboard_zones: list[KeyboardZone] = []
        for i in range(4):
            offset = OFFSET_KBD_ZONES + i * 5
            zone_data = dump[offset:offset+5]
            self.keyboard_zones.append(KeyboardZone.parse(*zone_data))

        self.drum_pads: list[DrumPad] = []
        for i in range(8):
            offset = OFFSET_DRUM_PADS + i * 7
            pad_data = dump[offset:offset+7]
            self.drum_pads.append(DrumPad(*pad_data))

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
            data[offset:offset+7] = self.drum_pads[i].dump()

        return bytes(data)

    def __eq__(self, other: 'ImpulseTemplateData') -> bool:
        return (
            self.name == other.name and
            self.keyboard_channel == other.keyboard_channel and
            self.keyboard_port == other.keyboard_port and
            self.keyboard_velocity_curve == other.keyboard_velocity_curve and
            self.aftertouch == other.aftertouch and
            self.octave == other.octave and
            self.transpose == other.transpose and
            self.keyboard_zones_enabled == other.keyboard_zones_enabled and
            self.keyboard_zones == other.keyboard_zones and
            self.drum_pads == other.drum_pads
        )

    def __repr__(self) -> str:
        fields = [
            'name', 'keyboard_channel', 'keyboard_port', 'keyboard_velocity_curve',
            'aftertouch', 'octave', 'transpose', 'keyboard_zones_enabled',
            'keyboard_zones', 'drum_pads'
        ]

        return 'ImpulseTemplateData<' + ', '.join([f'{fieldname}={getattr(self, fieldname)!r}' for fieldname in fields]) + '>'


def patch_template_for_ucs(template: ImpulseTemplateData):
    pass
