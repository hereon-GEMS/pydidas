# This file is part of pydidas.
#
# Copyright 2024, Helmholtz-Zentrum Hereon
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
The pydidas_gui module includes a function to run the default pydidas processing GUI.
"""

__author__ = "Malte Storm"
__copyright__ = "Copyright 2024, Helmholtz-Zentrum Hereon"
__license__ = "GPL-3.0-only"
__maintainer__ = "Malte Storm"
__status__ = "Production"
__all__ = ["run_gui", "start_pydidas_gui"]


import multiprocessing as mp
import signal
import warnings
from typing import TypeVar


QSplashScreen = TypeVar("QSplashScreen")


def start_pydidas_gui(splash_screen: QSplashScreen, restore_state: str = "None"):
    """
    Start the GUI application with the generic pydidas layout.

    Parameters
    ----------
    splash_screen : QSplashScreen
        The
    restore_state : str, optional
        Flag to restore the state of the pydidas GUI. Flags can be either "None" to
        start fresh, "exit" to restore the exit state or "saved" to restore the last
        saved state.
    """
    from qtpy.QtWidgets import QApplication

    from pydidas.core import UserConfigError
    from pydidas.gui import MainWindow, frames

    _app = QApplication.instance()
    splash_screen.show_aligned_message("Starting QApplication")
    if mp.get_start_method() != "spawn":
        try:
            mp.set_start_method("spawn", force=True)
        except RuntimeError:
            warnings.warn(
                "Could not set the multiprocessing Process startup method to 'spawn'. "
                "Multiprocessing with OpenGL will not work in Linux. To solve this "
                "issue, restart the kernel and import pydidas before starting any "
                "multiprocessing."
            )
    splash_screen.show_aligned_message("Creating objects")
    gui = MainWindow()
    gui.register_frame(frames.HomeFrame)
    gui.register_frame(frames.DataBrowsingFrame)
    gui.register_frame(frames.PyfaiCalibFrame)
    gui.register_frame(frames.ImageMathFrame)
    gui.register_frame(frames.QuickIntegrationFrame)
    gui.register_frame(frames.DefineDiffractionExpFrame)
    gui.register_frame(frames.DefineScanFrame)
    gui.register_frame(frames.WorkflowEditFrame)
    gui.register_frame(frames.WorkflowTestFrame)
    gui.register_frame(frames.WorkflowRunFrame)
    gui.register_frame(frames.ViewResultsFrame)
    gui.register_frame(frames.UtilitiesFrame)
    splash_screen.show_aligned_message("Creating widgets")
    gui.show()
    if restore_state.upper() not in ["NONE", "EXIT", "SAVED"]:
        raise UserConfigError("The restore_state must be 'None', 'saved' or 'exit'.")
    if restore_state.upper() in ["EXIT", "SAVED"]:
        splash_screen.show_aligned_message("Restoring interface state")
        try:
            gui.restore_gui_state(state=restore_state)
        except UserConfigError:
            pass
    splash_screen.finish(gui)
    gui.check_for_updates(auto_check=True)
    gui.raise_()
    return _app.exec_()


def run_gui():
    """Run the pydidas graphical user interface process."""
    # need to import here to prevent crash on Debian
    import pyFAI.azimuthalIntegrator
    from qtpy.QtWidgets import QApplication

    from pydidas_qtcore import PydidasQApplication, PydidasSplashScreen

    signal.signal(signal.SIGINT, signal.SIG_DFL)
    app = QApplication.instance()
    if not isinstance(app, PydidasQApplication):
        app = PydidasQApplication([])
    _splash = PydidasSplashScreen()

    try:
        _ = start_pydidas_gui(_splash, restore_state="exit")
    except Exception:
        _splash.close()
        raise
    app.deleteLater()


if __name__ == "__main__":
    run_gui()
