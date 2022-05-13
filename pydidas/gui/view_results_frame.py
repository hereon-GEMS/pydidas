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
Module with the ViewResultsFrame which allows to visualize results from
running the pydidas WorkflowTree.
"""

__author__ = "Malte Storm"
__copyright__ = "Copyright 2021-2022, Malte Storm, Helmholtz-Zentrum Hereon"
__license__ = "GPL-3.0"
__maintainer__ = "Malte Storm"
__status__ = "Development"
__all__ = ["ViewResultsFrame"]

from qtpy import QtCore

from ..core import get_generic_param_collection
from ..workflow import WorkflowResults
from .builders.view_results_frame_builder import ViewResultsFrameBuilder
from .mixins import ViewResultsMixin

RESULTS = WorkflowResults()


class ViewResultsFrame(ViewResultsFrameBuilder, ViewResultsMixin):
    """
    The ViewResultsFrame is used to visualize the results from running the
    WorkflowTree.
    """

    menu_icon = "qta::mdi.monitor-eye"
    menu_title = "View workflow results"
    menu_entry = "Workflow processing/View workflow results"

    default_params = get_generic_param_collection(
        "selected_results", "saving_format", "enable_overwrite"
    )
    params_not_to_restore = ["selected_results"]

    def __init__(self, parent=None, **kwargs):
        ViewResultsFrameBuilder.__init__(self, parent, **kwargs)
        self.set_default_params()

    def finalize_ui(self):
        """
        Connect the export functions to the results widget data.
        """
        ViewResultsMixin.__init__(self)

    @QtCore.Slot(int)
    def frame_activated(self, index):
        """
        Received a signal that a new frame has been selected.

        This method checks whether the selected frame is the current class
        and if yes, it will call some updates.

        Parameters
        ----------
        index : int
            The index of the newly activated frame.
        """
        super().frame_activated(index)
        if index == self.frame_index:
            self._update_choices_of_selected_results()
            self._update_export_button_activation()
        self._config["frame_active"] = index == self.frame_index
