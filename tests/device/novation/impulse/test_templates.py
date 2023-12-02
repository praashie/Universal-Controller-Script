"""
tests > device > novation > impulse > test_templates

Tests for parsing and patching Novation Impulse SysEx template data.

Authors:
* Praash [praashie@gmail.com, Praash#0846]

This code is licensed under the GPL v3 license. Refer to the LICENSE file for
more details.
"""

import pytest

from devices.novation.impulse.templates import (
    DrumPad,
    ImpulseTemplateData,
    KeyboardZone,
    TEMPLATE_SYSEX_PREFIX_BYTES
)

h = bytes.fromhex

# My personal template for use with FL Studio.
# Drum pads are assigned to separate MIDI channels, just so that
# we could get individual pad pressures as aftertouch data separately.
# Additionally, the first fader button is assigned to mimic a sustain pedal
SAMPLE_TEMPLATE = h(
    "F0 00 20 29 43 00 00 46 4C 53 74 75 64 69 6F 00 03 03 01 40 0B 00 24 3B 40 00 00 3C 60 40 01 00 24 54 40 10 04 24 54 40 10 04 09 15 7F 00 10 08 01 09 16 7F 00 10 08 01 09 17 7F 00 10 08 01 09 18 7F 00 10 08 01 09 19 7F 00 10 08 01 09 1A 7F 00 10 08 01 09 1B 7F 00 10 08 01 09 1C 7F 00 10 08 01 08 43 7F 00 08 08 01 08 45 7F 00 09 08 01 08 47 7F 00 0A 08 01 08 48 7F 00 0B 08 01 08 3C 7F 00 0C 08 01 08 3E 7F 00 0D 08 01 08 40 7F 00 0E 08 01 08 41 7F 00 0F 08 01 09 29 7F 00 0F 08 01 09 2A 7F 00 0F 08 01 09 2B 7F 00 0F 08 01 09 2C 7F 00 0F 08 01 09 2D 7F 00 0F 08 01 09 2E 7F 00 0F 08 01 09 2F 7F 00 0F 08 01 09 30 7F 00 0F 08 01 09 07 7F 00 0F 08 01 11 40 7F 00 02 08 01 11 42 7F 00 02 08 01 11 43 7F 00 02 08 01 11 36 7F 00 10 08 01 11 37 7F 00 10 08 01 11 38 7F 00 10 08 01 11 39 7D 00 10 08 01 11 3A 7F 00 10 08 01 11 3B 7F 00 10 08 01 09 01 7F 00 10 08 01 F7"
)

FACTORY_TEMPLATE_BASIC = h(
    "F0 00 20 29 43 00 00 42 61 73 63 4D 49 44 49 00 03 02 01 40 0B 00 24 3B 40 00 00 3C 60 40 01 00 24 54 40 10 04 24 54 40 10 04 09 15 7F 00 10 08 01 09 16 7F 00 10 08 01 09 17 7F 00 10 08 01 09 18 7F 00 10 08 01 09 19 7F 00 10 08 01 09 1A 7F 00 10 08 01 09 1B 7F 00 10 08 01 09 1C 7F 00 10 08 01 08 43 7F 00 10 08 01 08 45 7F 00 10 08 01 08 47 7F 00 10 08 01 08 48 7F 00 10 08 01 08 3C 7F 00 10 08 01 08 3E 7F 00 10 08 01 08 40 7F 00 10 08 01 08 41 7F 00 10 08 01 09 29 7F 00 10 08 01 09 2A 7F 00 10 08 01 09 2B 7F 00 10 08 01 09 2C 7F 00 10 08 01 09 2D 7F 00 10 08 01 09 2E 7F 00 10 08 01 09 2F 7F 00 10 08 01 09 30 7F 00 10 08 01 09 31 7F 00 10 08 01 11 33 7F 00 10 08 01 11 34 7F 00 10 08 01 11 35 7F 00 10 08 01 11 36 7F 00 10 08 01 11 37 7F 00 10 08 01 11 38 7F 00 10 08 01 11 39 7F 00 10 08 01 11 3A 7F 00 10 08 01 11 3B 7F 00 10 08 01 09 01 7F 00 10 08 01 F7"
)

MSG_TYPE_NOTE = 0x08
SAMPLE_DRUM_PADS: list[DrumPad] = [
    DrumPad(MSG_TYPE_NOTE, 67, 127, 0, 8, 8, 1),
    DrumPad(MSG_TYPE_NOTE, 69, 127, 0, 9, 8, 1),
    DrumPad(MSG_TYPE_NOTE, 71, 127, 0, 10, 8, 1),
    DrumPad(MSG_TYPE_NOTE, 72, 127, 0, 11, 8, 1),
    DrumPad(MSG_TYPE_NOTE, 60, 127, 0, 12, 8, 1),
    DrumPad(MSG_TYPE_NOTE, 62, 127, 0, 13, 8, 1),
    DrumPad(MSG_TYPE_NOTE, 64, 127, 0, 14, 8, 1),
    DrumPad(MSG_TYPE_NOTE, 65, 127, 0, 15, 8, 1),
]


@pytest.fixture
def result():
    return ImpulseTemplateData(SAMPLE_TEMPLATE)


def test_invalid_prefix():
    data = bytes([0xF0, 0x00, 0x20, 0x29, 0x67, 0x07, 0x3D, 0xF7])
    with pytest.raises(AssertionError):
        result = ImpulseTemplateData(data)


def test_template_basics(result: ImpulseTemplateData):
    assert result.name == 'FLStudio'
    assert result.keyboard_channel == 0
    assert result.keyboard_port == 3
    assert result.keyboard_velocity_curve == 3
    assert result.aftertouch == True
    assert result.octave == 0
    assert result.transpose == 0


def test_template_zones(result: ImpulseTemplateData):
    assert result.keyboard_zones_enabled == False
    assert result.keyboard_zones == [
        KeyboardZone(36, 59, 0, 0, 0),
        KeyboardZone(60, 96, 0, 1, 0),
        KeyboardZone(36, 84, 0, 16, 4),
        KeyboardZone(36, 84, 0, 16, 4),
    ]


def test_template_drum_pads(result: ImpulseTemplateData):
    assert result.drum_pads == SAMPLE_DRUM_PADS


def test_template_apply_patch():
    basic_template = ImpulseTemplateData(FACTORY_TEMPLATE_BASIC)

    basic_template.name = 'UnitTest'
    basic_template.octave = 2

    modified_zones: list[KeyboardZone] = [
        KeyboardZone(20, 31, 64, 3, 0),
        KeyboardZone(32, 43, 62, 4, 0),
        KeyboardZone(44, 55, 64, 5, 0),
        KeyboardZone(56, 127, 61, 6, 0),
    ]

    basic_template.drum_pads = [
        DrumPad(*pad.dump())
        for pad in SAMPLE_DRUM_PADS
    ]

    basic_template.keyboard_zones = modified_zones

    patched_data = basic_template.apply_patch(FACTORY_TEMPLATE_BASIC)
    parsed_template = ImpulseTemplateData(patched_data)

    assert parsed_template == basic_template
