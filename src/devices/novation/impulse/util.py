import device
from control_surfaces.managers import IValueManager, IAnnotationManager
from . import impulse_sysex


class ImpulseAnnotationValueManager(IValueManager):
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

