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
The pydidas_gui module includes a function to run the default pydidas processing GUI.
"""

__author__ = "Malte Storm"
__copyright__ = "Copyright 2023, Helmholtz-Zentrum Hereon"
__license__ = "GPL-3.0-only"
__maintainer__ = "Malte Storm"
__status__ = "Production"
__all__ = ["run_gui", "start_pydidas_gui"]


import multiprocessing as mp
import signal
import sys
import warnings
from pathlib import Path
from typing import Union

from qtpy import QtCore, QtGui, QtWidgets
from qtpy.QtWidgets import QApplication, QSplashScreen


def _get_icon_pixmap():
    """
    Get the path for loading the icon and set the icon.

    Returns
    -------
    None.

    """
    for _path in sys.path:
        _p = Path(_path).joinpath("pydidas", "resources", "images", "splash_image.png")
        if _p.is_file():
            _iconpath = str(_p)
            break
    if _iconpath is None:
        raise ModuleNotFoundError(
            "Cannot find the required files for the startup window"
        )
    return QtGui.QPixmap(_iconpath)


class PydidasSplashScreen(QtWidgets.QSplashScreen):
    """
    A splash screen which allows to show centered messages and with the pydidas icon.
    """

    def __init__(self, pixmap=None, f=QtCore.Qt.WindowStaysOnTopHint):
        if pixmap is None:
            pixmap = _get_icon_pixmap()
        QtWidgets.QSplashScreen.__init__(self, pixmap, f)
        self.show_aligned_message("Importing packages")
        self.show()
        QtWidgets.QApplication.instance().processEvents()

    def show_aligned_message(self, message: str):
        """
        Show a message aligned bottom / center.

        Parameters
        ----------
        message : str
            The message to be displayes.
        """
        self.showMessage(message, QtCore.Qt.AlignHCenter | QtCore.Qt.AlignBottom)


def start_pydidas_gui(
    splash_screen: QSplashScreen,
    app: Union[None, QApplication] = None,
    restore_state: str = "None",
):
    """
    Start the GUI application with the generic pydidas layout.

    Parameters
    ----------
    splash_screen :
    app : Union[QtCore.QApplication, None], optional
        The main Qt application. If None, a new QApplication will be created.
    restore_state : str, optional
        Flag to restore the state of the pydidas GUI. Flags can be either "None" to
        start fresh, "exit" to restore the exit state or "saved" to restore the last
        saved state.
    """
    from pydidas.core import PydidasQApplication, UserConfigError
    from pydidas.gui import MainWindow, frames

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
    app = PydidasQApplication(sys.argv)
    gui = MainWindow()
    gui.register_frame(frames.HomeFrame)
    gui.register_frame(frames.DataBrowsingFrame)
    gui.register_frame(frames.PyfaiCalibFrame)
    gui.register_frame(frames.DirectorySpyFrame)
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
    if restore_state in ["exit", "saved"]:
        splash_screen.show_aligned_message("Restoring interface state")
        try:
            gui.restore_gui_state(state=restore_state)
        except UserConfigError:
            pass
    splash_screen.finish(gui)
    gui.raise_()
    return app.exec_()


def run_gui():
    """
    Run the pydidas graphical user interface process.
    """
    signal.signal(signal.SIGINT, signal.SIG_DFL)
    app = QtWidgets.QApplication([])
    _splash = PydidasSplashScreen()

    _ = start_pydidas_gui(_splash, restore_state="exit")
    app = QtWidgets.QApplication.instance()
    app.quit()


if __name__ == "__main__":
    run_gui()
