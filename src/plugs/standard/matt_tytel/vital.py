"""
plugs > standard > matt_tytel > vital

Authors:
* Miguel Guthridge [hdsq@outlook.com.au, HDSQ#2154]

This code is licensed under the GPL v3 license. Refer to the LICENSE file for
more details.
"""
from typing import Any
from common.plug_indexes import GeneratorIndex
from common.types import Color
from common.param import Param
from devices import DeviceShadow
from common import ExtensionManager
from control_surfaces import PitchWheel, ControlShadowEvent, ControlShadow
from plugs.mapping_strategies import IMappingStrategy, SimpleFaders
from plugs import StandardPlugin, event_filters, tick_filters

MACRO_START = 211
VITAL_COLOR = Color.fromInteger(0xAA88FF)

# The pitch wheel appears to be broken for vital, so link to the parameter
# instead
VitalPitch = Param(464)


@ExtensionManager.plugins.register
class Vital(StandardPlugin):
    """
    Matt Tytel's Vital plugin
    """

    def __init__(self, shadow: DeviceShadow) -> None:
        mappings: list[IMappingStrategy] = []
        mappings.append(SimpleFaders(
            [MACRO_START + i for i in range(4)],
            colors=VITAL_COLOR,
        ))
        pitch = shadow.bindMatch(
            PitchWheel,
            self.ePitchWheel,
            self.tPitchWheel,
        )
        if pitch is not None:
            pitch.annotation = 'Pitch'
            pitch.color = VITAL_COLOR

        super().__init__(shadow, mappings)

    @event_filters.toGeneratorIndex()
    def ePitchWheel(
        self,
        control: ControlShadowEvent,
        index: GeneratorIndex,
        *args: Any,
    ) -> bool:
        VitalPitch(index).value = control.value
        return True

    @tick_filters.toGeneratorIndex()
    def tPitchWheel(
        self,
        control: ControlShadow,
        index: GeneratorIndex,
        *args,
    ) -> bool:
        control.value = VitalPitch(index).value
        return True

    @classmethod
    def create(cls, shadow: DeviceShadow) -> 'StandardPlugin':
        return cls(shadow)

    @classmethod
    def getPlugIds(cls) -> tuple[str, ...]:
        return ('Vital',)
