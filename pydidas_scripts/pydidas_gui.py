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
The main_gui module includes a function to run the GUI.
"""

__author__ = "Malte Storm"
__copyright__ = "Copyright 2021-2022, Malte Storm, Helmholtz-Zentrum Hereon"
__license__ = "GPL-3.0"
__maintainer__ = "Malte Storm"
__status__ = "Development"
__all__ = ["run_gui"]

import sys
import warnings
import multiprocessing as mp

from qtpy import QtWidgets

from pydidas.gui import MainWindow
from pydidas.gui.frames import (
    DataBrowsingFrame,
    WorkflowEditFrame,
    PyfaiCalibFrame,
    HomeFrame,
    SetupExperimentFrame,
    SetupScanFrame,
    WorkflowRunFrame,
    CompositeCreatorFrame,
    DirectorySpyFrame,
    ViewResultsFrame,
    WorkflowTestFrame,
)


def run_gui(app=None):
    """
    Run the GUI application with the generic pydidas layout.

    Parameters
    ----------
    app : Union[QtCore.QApplication, None]
        The main Qt application.
    """
    if mp.get_start_method() != "spawn":
        try:
            mp.set_start_method("spawn", force=True)
        except RuntimeError:
            warnings.warn(
                "Could not set the multiprocessing Process startup method to "
                '"spawn". Multiprocessing with OpenGL will not work in Linux. '
                "To solve this issue, restart the kernel and import pydidas "
                "before starting any multiprocessing."
            )

    if app is None:
        app = QtWidgets.QApplication(sys.argv)
    gui = MainWindow()
    gui.register_frame(HomeFrame)
    gui.register_frame(DataBrowsingFrame)
    gui.register_frame(PyfaiCalibFrame)
    gui.register_frame(CompositeCreatorFrame)
    gui.register_frame(DirectorySpyFrame)
    gui.register_frame(
        "ProcessingFrame",
        title="Workflow processing",
        menu_entry="Workflow processing",
        icon="qta::mdi.cogs",
    )
    gui.register_frame(SetupExperimentFrame)
    gui.register_frame(SetupScanFrame)
    gui.register_frame(WorkflowEditFrame)
    gui.register_frame(WorkflowTestFrame)
    gui.register_frame(WorkflowRunFrame)
    gui.register_frame(ViewResultsFrame)
    gui.raise_()
    gui.show()
    _ = app.exec_()
    gui.deleteLater()
    app.quit()
    sys.exit()


if __name__ == "__main__":
    app = QtWidgets.QApplication(sys.argv)
    run_gui(app)
