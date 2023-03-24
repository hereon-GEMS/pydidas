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

from ...core import get_generic_param_collection
from ...contexts.scan_context import Scan
from ...widgets import PydidasFileDialog
from ...workflow import WorkflowResults, result_io
from ...workflow.workflow_tree import _WorkflowTree
from ..mixins import ViewResultsMixin
from .builders.view_results_frame_builder import ViewResultsFrameBuilder

SAVER = result_io.WorkflowResultIoMeta


class ViewResultsFrame(ViewResultsFrameBuilder, ViewResultsMixin):
    """
    The ViewResultsFrame is used to visualize the results from running the
    WorkflowTree.
    """

    menu_icon = "qta::mdi.monitor-eye"
    menu_title = "Import and display workflow results"
    menu_entry = "Workflow processing/View workflow results"

    default_params = get_generic_param_collection(
        "selected_results", "saving_format", "enable_overwrite"
    )
    params_not_to_restore = ["selected_results"]

    def __init__(self, parent=None, **kwargs):
        self._SCAN = Scan()
        self._TREE = _WorkflowTree()
        self._RESULTS = WorkflowResults(
            scan_context=self._SCAN, workflow_tree=self._TREE
        )
        ViewResultsFrameBuilder.__init__(self, parent, **kwargs)
        self.set_default_params()
        self.__import_dialog = PydidasFileDialog(
            parent=self,
            dialog_type="open_directory",
            caption="Workflow results directory",
            qsettings_ref="WorkflowResults__import",
        )

    def finalize_ui(self):
        """
        Connect the export functions to the results widget data.
        """
        ViewResultsMixin.__init__(self, workflow_results=self._RESULTS)

    def connect_signals(self):
        self._widgets["but_load"].clicked.connect(self.import_data_to_workflow_results)
        self._widgets["plot2d"].sig_get_more_info_for_data.connect(
            self._widgets["result_selector"].show_info_popup
        )

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
        self._config["frame_active"] = index == self.frame_index

    def import_data_to_workflow_results(self):
        """
        Import data to the workflow results.
        """
        _dir = self.__import_dialog.get_user_response()
        if _dir is not None:
            self._RESULTS.import_data_from_directory(_dir)
            self._update_choices_of_selected_results()
            self._update_export_button_activation()
