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
The pydidas_gui module includes a function to run the default pydidas processing GUI.
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

from pydidas.core import UserConfigError, PydidasQApplication
from pydidas.gui import MainWindow, frames


def run_gui(app=None, restore_state="None"):
    """
    Run the GUI application with the generic pydidas layout.

    Parameters
    ----------
    app : Union[QtCore.QApplication, None], optional
        The main Qt application. If None, a new QApplication will be created.
    restore_state : str, optional
        Flag to restore the state of the pydidas GUI. Flags can be either "None" to
        start fresh, "exit" to restore the exit state or "saved" to restore the last
        saved state.
    """
    if mp.get_start_method() != "spawn":
        try:
            mp.set_start_method("spawn", force=True)
        except RuntimeError:
            warnings.warn(
                "Could not set the multiprocessing Process startup method to "
                "'spawn'. Multiprocessing with OpenGL will not work in Linux. "
                "To solve this issue, restart the kernel and import pydidas "
                "before starting any multiprocessing."
            )

    app = QtWidgets.QApplication.instance()
    if app is not None:
        app.quit()
    app = PydidasQApplication(sys.argv)
    gui = MainWindow()
    gui.register_frame(frames.HomeFrame)
    gui.register_frame(frames.DataBrowsingFrame)
    gui.register_frame(frames.PyfaiCalibFrame)
    gui.register_frame(frames.CompositeCreatorFrame)
    gui.register_frame(frames.DirectorySpyFrame)
    gui.register_frame(frames.QuickIntegrationFrame)
    gui.register_frame(frames.DefineDiffractionExpFrame)
    gui.register_frame(frames.DefineScanFrame)
    gui.register_frame(frames.WorkflowEditFrame)
    gui.register_frame(frames.WorkflowTestFrame)
    gui.register_frame(frames.WorkflowRunFrame)
    gui.register_frame(frames.ViewResultsFrame)
    gui.register_frame(frames.UtilitiesFrame)

    if restore_state.upper() not in ["NONE", "EXIT", "SAVED"]:
        raise UserConfigError("The restore_state must be 'None', 'saved' or 'exit'.")
    gui.show()
    gui.raise_()
    if restore_state in ["exit", "saved"]:
        try:
            gui.restore_gui_state(state=restore_state)
        except UserConfigError:
            pass
    return app.exec_()


if __name__ == "__main__":
    _ = run_gui(restore_state="exit")
    app = QtWidgets.QApplication.instance()
    app.quit()
