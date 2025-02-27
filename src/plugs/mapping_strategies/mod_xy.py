"""
plugs > mapping_strategies > mod_xy

Mappings for ModX and ModY control

Authors:
* Miguel Guthridge [hdsq@outlook.com.au, HDSQ#2154]

This code is licensed under the GPL v3 license. Refer to the LICENSE file for
more details.
"""

from common.param import Param, PluginParameter
from common.plug_indexes import PluginIndex
from control_surfaces import ModX, ModY
from control_surfaces import ControlShadow, ControlShadowEvent
from devices.device_shadow import DeviceShadow
from plugs.event_filters.index import toPluginIndex
from . import IMappingStrategy


class ModXYStrategy(IMappingStrategy):
    """
    Maps mod-x and mod-y controls to the given parameters
    """
    def __init__(self, x_param: int, y_param: int) -> None:
        """
        Create a mapping for mod-x and mod-y controls, given the param indexes
        for each value

        ### Args:
        * `x_param` (`int`): mod-x param index

        * `y_param` (`int`): mod-y param-index
        """
        self._x = Param(x_param)
        self._y = Param(y_param)

    def apply(self, shadow: DeviceShadow) -> None:
        shadow.bindMatch(ModX, self.event, self.tick, (self._x,))
        shadow.bindMatch(ModY, self.event, self.tick, (self._y,))

    @toPluginIndex()
    def event(
        self,
        control: ControlShadowEvent,
        index: PluginIndex,
        param: type[PluginParameter],
        *args,
    ) -> bool:
        param(index).value = control.value
        return True

    @toPluginIndex()
    def tick(
        self,
        control: ControlShadow,
        index: PluginIndex,
        param: type[PluginParameter],
        *args,
    ):
        # Update value
        control.value = param(index).value
        # Update annotations
        control.annotation = param(index).name
