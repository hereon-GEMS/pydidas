# This file is part of pydidas.
#
# Copyright 2023, Helmholtz-Zentrum Hereon
# SPDX-License-Identifier: GPL-3.0-only
#
# pydidas is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License version 3 as
# published by the Free Software Foundation.
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
__copyright__ = "Copyright 2023, Helmholtz-Zentrum Hereon"
__license__ = "GPL-3.0-only"
__maintainer__ = "Malte Storm"
__status__ = "Production"
__all__ = ["WorkflowEditFrameBuilder"]


from qtpy.QtWidgets import QAbstractScrollArea, QApplication

from ....core import constants
from ....core.utils import update_size_policy
from ....core.constants import PARAM_EDIT_ASPECT_RATIO
from ....widgets import ScrollArea
from ....widgets.framework import BaseFrame
from ....widgets.parameter_config import EditPluginParametersWidget
from ....widgets.workflow_edit import PluginCollectionBrowser, WorkflowTreeCanvas


class WorkflowEditFrameBuilder:
    """
    Builder for the WorkflowEditFrame.
    """

    @classmethod
    def populate_frame(cls, frame: BaseFrame):
        """
        Build the frame by creating all required widgets and placing them in the layout.

        Parameters
        ----------
        frame : BaseFrame
            The frame instance.
        """
        frame._widgets["workflow_canvas"] = WorkflowTreeCanvas()

        frame.create_label(
            "label_title",
            "Workflow tree editor",
            fontsize_offset=4,
            bold=True,
            fixedWidth=250,
            gridPos=(0, 0, 1, 3),
        )
        frame.create_any_widget(
            "workflow_area",
            ScrollArea,
            minimumHeight=450,
            widget=frame._widgets["workflow_canvas"],
            alignment=constants.ALIGN_TOP_CENTER,
            sizePolicy=constants.POLICY_EXP_EXP,
            sizeAdjustPolicy=QAbstractScrollArea.AdjustToContents,
            gridPos=(1, 0, 3, 2),
        )
        frame.create_label(
            "plugin_title",
            "Available plugins:",
            fontsize_offset=3,
            underline=True,
            gridPos=(4, 0, 1, 2),
        )
        frame.create_any_widget(
            "plugin_collection", PluginCollectionBrowser, gridPos=(5, 0, 1, 2)
        )
        frame._widgets["plugin_edit_canvas"] = EditPluginParametersWidget()
        frame.create_any_widget(
            "plugin_edit_area",
            ScrollArea,
            minimumHeight=450,
            fixedWidth=int(
                QApplication.instance().standard_font_height * PARAM_EDIT_ASPECT_RATIO
                + 25
            ),
            widget=frame._widgets["plugin_edit_canvas"],
            sizePolicy=constants.POLICY_EXP_EXP,
            gridPos=(1, 2, 5, 1),
        )
        frame.create_button(
            "but_load",
            "Import workflow from file",
            icon="qt-std::SP_DialogOpenButton",
            gridPos=(1, 0, 1, 1),
        )
        frame.create_button(
            "but_save",
            "Export workflow to file",
            icon="qt-std::SP_DialogSaveButton",
            gridPos=(2, 0, 1, 1),
        )

        update_size_policy(frame._widgets["workflow_area"], verticalStretch=2)
        update_size_policy(frame._widgets["plugin_collection"], verticalStretch=1)
        frame.layout().setRowStretch(3, 10)
        frame.layout().setRowStretch(5, 5)
        frame.layout().setColumnStretch(1, 10)
