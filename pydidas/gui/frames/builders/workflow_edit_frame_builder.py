# This file is part of pydidas.
#
# pydidas is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
#
# Pydidas is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE. See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with Pydidas. If not, see <http://www.gnu.org/licenses/>.

"""
Module with the WorkflowEditFrameBuilder class which is used to populate the
WorkflowEditFrame with widgets.
"""

__author__ = "Malte Storm"
__copyright__ = "Copyright 2021-2022, Malte Storm, Helmholtz-Zentrum Hereon"
__license__ = "GPL-3.0"
__maintainer__ = "Malte Storm"
__status__ = "Development"
__all__ = ["WorkflowEditFrameBuilder"]

from ....core.constants import EXP_EXP_POLICY
from ....core.utils import update_size_policy
from ....widgets import ScrollArea, BaseFrame
from ....widgets.parameter_config import EditPluginParametersWidget
from ....widgets.workflow_edit import WorkflowTreeCanvas, PluginCollectionBrowser


class WorkflowEditFrameBuilder(BaseFrame):
    """
    Mix-in class which includes the build_self method to populate the
    base class's UI and initialize all widgets.
    """

    def __init__(self, parent=None, **kwargs):
        BaseFrame.__init__(self, parent, **kwargs)

    def build_frame(self):
        """
        Create all widgets and initialize their state.
        """
        self._widgets["workflow_canvas"] = WorkflowTreeCanvas()

        self.create_any_widget(
            "workflow_area",
            ScrollArea,
            minimumHeight=500,
            widget=self._widgets["workflow_canvas"],
            gridPos=(0, 0, 1, 1),
        )
        self.create_any_widget(
            "plugin_collection", PluginCollectionBrowser, gridPos=(1, 0, 3, 1)
        )
        self._widgets["plugin_edit_canvas"] = EditPluginParametersWidget()
        self.create_any_widget(
            "plugin_edit_area",
            ScrollArea,
            minimumHeight=500,
            widget=self._widgets["plugin_edit_canvas"],
            fixedWidth=400,
            sizePolicy=EXP_EXP_POLICY,
            gridPos=(0, 1, 2, 1),
        )
        self.create_button(
            "but_load",
            "Import workflow from file",
            gridPos=(2, 1, 1, 1),
            icon=self.style().standardIcon(42),
        )
        self.create_button(
            "but_save",
            "Export workflow to file",
            gridPos=(3, 1, 1, 1),
            icon=self.style().standardIcon(43),
        )

        update_size_policy(self._widgets["workflow_area"], verticalStretch=2)
        update_size_policy(self._widgets["plugin_collection"], verticalStretch=1)
