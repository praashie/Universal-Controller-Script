import device

h = bytes.fromhex
SYX_NOVATION_HEADER = h("F0 00 20 29")
SYX_IMPULSE_HEADER = SYX_NOVATION_HEADER + h("67")

# The "Automap" initialization message has these three "parameter" bytes.
# Most scripts would set all three to 01.

# After some fiddling, I've determined that setting the third byte to 00
# allows the faders and encoders to be assigned individual "names".
# When a control is tweaked, Impulse will automatically update its LCD to reflect this
# name, or displays "No Ctrl" if none is assigned.
SYX_MSG_INIT = SYX_IMPULSE_HEADER + h("06 01 01 00")
SYX_MSG_DEINIT = SYX_IMPULSE_HEADER + h("06 00 00 00")

# This is the "control annotation" message I discovered through monitoring
# the USB traffic used by Automap. It behaves like writing into a text buffer,
# as if we had a long LCD text display divided into sections.
SYX_CONTROL_ANNOTATION = SYX_IMPULSE_HEADER + h("05")

SYX_MSG_TEXT = SYX_IMPULSE_HEADER + h("08")
SYX_MSG_TEXT2 = SYX_IMPULSE_HEADER + h("09")

SYX_SIMULATION = SYX_NOVATION_HEADER + h("03 05 12 00 00 00 66")

BUTTON_SETUP = 1
BUTTON_MINUS = 7
BUTTON_PLUS = 8
BUTTON_ENTER = 34


def initialize():
    device.midiOutSysex(SYX_MSG_INIT)


def deinitialize():
    device.midiOutSysex(SYX_MSG_DEINIT)


def setLcdText(msg: str):
    text_bytes = msg.encode("ascii", errors="ignore")
    device.midiOutSysex(SYX_MSG_TEXT + text_bytes)


def setLcdTinyText(msg: str):
    text_bytes = msg.encode("ascii", errors="ignore")
    device.midiOutSysex(SYX_MSG_TEXT2 + text_bytes)


def setControlAnnotationText(group: int, slot: int, msg: str):
    """
    Set an annotation for an Impulse control.

    group:
    - 0 = faders
    - 1 = fader buttons
    - 2 = encoders

    slot: index of the control within the group
    """
    # This appears to be internally implemented as a simple text buffer.

    if msg:
        msg_bytes = msg[:8].encode(errors='ignore')
        device.midiOutSysex(SYX_CONTROL_ANNOTATION + bytes([group, slot * 9, 0]) + msg_bytes + bytes([0]))
    else:
        device.midiOutSysex(SYX_CONTROL_ANNOTATION + bytes([group, slot * 9, 0]))


def simulateButton(button_index: int, value: bool):
    """
    Tell Impulse to mock a physical button press. Dark magic!
    This message is documented in the Novation SL MKII MIDI programmer's manual.
    The button numbers themselves are unique to Impulse, and were discovered through
    trial and error.
    """
    device.midiOutSysex(SYX_SIMULATION + bytes([0x01, button_index, value]))


def simulateButtonHit(button_index: int):
    simulateButton(button_index, True)
    simulateButton(button_index, False)


def triggerTemplateDump():
    """
    As there is no full documentation available on all of Novation Impulse's
    MIDI messages, this is a really hacky way to force the keyboard to dump its currently
    active template data.

    The implementation instructs Impulse to mock physical button presses,
    resulting in the currently active Impulse template dumped through SysEx.
    This would be normally done by the user, but here, we *become* the user.
    """

    sequence = [
        # Starting from normal operation mode
        BUTTON_SETUP,
        # Menu: Transport
        BUTTON_PLUS,
        # Menu: PadCurve
        BUTTON_PLUS,
        # Menu: Tempo
        BUTTON_PLUS,
        # Menu: ClockSrc
        BUTTON_PLUS,
        # Menu: DIN From
        BUTTON_PLUS,
        # Menu: DumpSYX?
        BUTTON_ENTER, # Template gets dumped here
        # Menu: DumpSYX?
        BUTTON_SETUP
        # Back to normal operation
    ]
    for button in sequence:
        simulateButtonHit(button)
