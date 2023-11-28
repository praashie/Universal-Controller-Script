import device

h = bytes.fromhex
SYX_IMPULSE_HEADER = h("F0 00 20 29 67")
SYX_MSG_INIT = SYX_IMPULSE_HEADER + h("06 01 01 00")
SYX_MSG_DEINIT = SYX_IMPULSE_HEADER + h("06 00 00 00")
SYX_CONTROL_ANNOTATION = SYX_IMPULSE_HEADER + h("05")
SYX_MSG_TEXT = SYX_IMPULSE_HEADER + h("08")
SYX_MSG_TEXT2 = SYX_IMPULSE_HEADER + h("09")


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

    msg_bytes = msg[:8].encode(errors='ignore')
    device.midiOutSysex(SYX_CONTROL_ANNOTATION + bytes([group, slot * 9, 0]) + msg_bytes + bytes([0]))
