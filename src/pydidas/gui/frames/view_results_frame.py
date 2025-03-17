# This file is part of pydidas.
#
# Copyright 2024 - 2025, Helmholtz-Zentrum Hereon
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
Module with the ViewResultsFrame which allows to visualize results from
running the pydidas WorkflowTree.
"""

__author__ = "Malte Storm"
__copyright__ = "Copyright 2024 - 2025, Helmholtz-Zentrum Hereon"
__license__ = "GPL-3.0-only"
__maintainer__ = "Malte Storm"
__status__ = "Production"
__all__ = ["ViewResultsFrame"]


from qtpy import QtCore

from pydidas.contexts.diff_exp import DiffractionExperiment
from pydidas.contexts.scan import Scan
from pydidas.gui.frames.builders.view_results_frame_builder import (
    get_ViewResultsFrame_build_config,
)
from pydidas.gui.mixins import ViewResultsMixin
from pydidas.widgets import PydidasFileDialog
from pydidas.widgets.framework import BaseFrame
from pydidas.workflow import ProcessingResults, ProcessingTree, result_io


SAVER = result_io.ProcessingResultIoMeta


class ViewResultsFrame(BaseFrame, ViewResultsMixin):
    """
    The ViewResultsFrame is used to import and visualize the pydidas ProcessingResults.
    """

    menu_icon = "pydidas::frame_icon_workflow_results"
    menu_title = "Import and display workflow results"
    menu_entry = "Workflow processing/View workflow results"

    def __init__(self, **kwargs: dict):
        self._SCAN = Scan()
        self._TREE = ProcessingTree()
        self._EXP = DiffractionExperiment()
        BaseFrame.__init__(self, **kwargs)
        ViewResultsMixin.__init__(
            self,
            workflow_results=ProcessingResults(
                diffraction_exp_context=self._EXP,
                scan_context=self._SCAN,
                workflow_tree=self._TREE,
            ),
        )

        self.set_default_params()
        self.__import_dialog = PydidasFileDialog()

    def build_frame(self):
        """
        Build the frame and populate it with widgets.
        """
        for _method, _args, _kwargs in get_ViewResultsFrame_build_config(self):
            _method = getattr(self, _method)
            _method(*_args, **_kwargs)
        self.build_view_results_mixin()

    def connect_signals(self):
        self._widgets["but_load"].clicked.connect(self.import_data_to_workflow_results)
        self.connect_view_results_mixin_signals()

    @QtCore.Slot(int)
    def frame_activated(self, index: int):
        """
        Received a signal that a new frame has been selected.

        This method checks whether the selected frame is the current class
        and if yes, it will call some updates.

        Parameters
        ----------
        index : int
            The index of the newly activated frame.
        """
        BaseFrame.frame_activated(self, index)
        self._config["frame_active"] = index == self.frame_index

    def import_data_to_workflow_results(self):
        """
        Import data to the workflow results.
        """
        _dir = self.__import_dialog.get_existing_directory(
            caption="Workflow results directory",
            qsettings_ref="WorkflowResults__import",
        )
        if _dir is not None:
            self._RESULTS.import_data_from_directory(_dir)
            self._RESULTS._TREE.root.plugin._SCAN = self._RESULTS._SCAN
            self._RESULTS._TREE.root.plugin.update_filename_string()
            self.update_choices_of_selected_results()
            self.update_export_button_activation()
