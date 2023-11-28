import device
from common.types import Color

from common.util.misc import clamp
from fl_classes import FlMidiMsg, isMidiMsgStandard
from control_surfaces.managers import IValueManager, IAnnotationManager, IColorManager
from control_surfaces.value_strategies import IValueStrategy

from . import impulse_sysex


class ImpulseAnnotationValueManager(IValueManager, IAnnotationManager):
    """
    Provide feedback and LCD annotations for faders, fader buttons,
    and encoders.
    """
    def __init__(self, channel: int, cc: int, annotation_group: int, annotation_slot: int):
        self.channel = channel
        self.cc = cc
        self.annotation_group = annotation_group
        self.annotation_slot = annotation_slot

    def onValueChange(self, new_value: float) -> None:
        value_byte = round(max(0, min(255, 255 * new_value)))
        device.midiOutMsg((0xB0 + self.channel) + (self.cc << 8) + (value_byte << 16))

    def onAnnotationChange(self, new_annotation: str) -> None:
        impulse_sysex.setControlAnnotationText(self.annotation_group, self.annotation_slot, new_annotation)

    def tick(self) -> None:
        # Used for basic control feedback - the Impulse is expected to memorize these.
        pass


class ImpulseFaderButtonManager(ImpulseAnnotationValueManager, IColorManager):
    def onValueChange(self, new_value: float) -> None:
        # Ignore this functionality; we only care about the mute status
        # communicated by color objects
        pass

    def onColorChange(self, new_color: Color) -> None:
        value_byte = new_color.enabled
        device.midiOutMsg( (0xB0 + self.channel) + (self.cc << 8) + (value_byte << 16) )


class ImpulseFakeAnnotationManager(IAnnotationManager, IValueManager):
    """
    Provide 'annotations' for controls by explicitly displaying a UCS annotation
    whenever this control is moved.
    """
    def __init__(self):
        self._annotation = ''

    def onAnnotationChange(self, new_annotation: str):
        self._annotation = new_annotation
        print(f'New annotation: {new_annotation!r}')

    def onValueChange(self, new_value: float):
        impulse_sysex.setLcdText(self._annotation)

    def tick(self):
        pass


class ImpulseEncoderValueStrategy(IValueStrategy):
    """
    Value strategy used in Impulse encoders.
    """
    def __init__(self, scaling: float = 1.0) -> None:
        """
        * `scaling` (`float`, optional): amount to scale deltas by. Defaults to
          `1.0`.
        """
        self.__scaling = scaling

    def getValueFromEvent(self, event: FlMidiMsg, value: float) -> float:
        assert isMidiMsgStandard(event)
        delta = event.data2 - 0x40
        return clamp((delta / 32.0) * self.__scaling + value, 0.0, 1.0)

    def getChannelFromEvent(self, event: FlMidiMsg) -> int:
        assert isMidiMsgStandard(event)
        return event.status & 0xF
