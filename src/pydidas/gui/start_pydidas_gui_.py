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
The start_pydidas_gui module includes a function to run start pydidas GUI instances.
"""

__author__ = "Malte Storm"
__copyright__ = "Copyright 2024 - 2025, Helmholtz-Zentrum Hereon"
__license__ = "GPL-3.0-only"
__maintainer__ = "Malte Storm"
__status__ = "Production"
__all__ = ["start_pydidas_gui"]


import multiprocessing as mp
import signal
import warnings
from pathlib import Path
from typing import Optional, Type

from qtpy.QtWidgets import QApplication

from pydidas.core import UserConfigError
from pydidas.gui import MainWindow
from pydidas.gui.frames import DEFAULT_FRAMES
from pydidas.resources import icons
from pydidas.widgets.framework import BaseFrame
from pydidas_qtcore import PydidasQApplication, PydidasSplashScreen


def start_pydidas_gui(
    *frames: tuple[BaseFrame],
    use_default_frames: bool = True,
    restore_state: str = "exit",
    custom_mainwindow: Optional[Type[MainWindow]] = None,
    custom_splash_image: Optional[Path] = None,
):
    """
    Open the pydidas GUI with the given frames and run the QEventLoop.

    Parameters
    ----------
    frames : tuple[BaseFrame]
        The frames to be registered in the GUI.
    use_default_frames : bool, optional
        Flag to use all the default frames to the GUI.
    restore_state : str, optional
        Flag to restore the state of the pydidas GUI. Flags can be either "None" to
        start fresh, "exit" to restore the exit state or "saved" to restore the last
        saved state.
    custom_mainwindow : MainWindow, optional
        Custom MainWindow class to be used. If not provided, the default MainWindow
        class will be used.
    custom_splash_image : Path, optional
        The path to a custom splash image to be used. If not provided, the
        default splash image will be used.
    """
    main_window_cls = MainWindow if custom_mainwindow is None else custom_mainwindow
    restore_state = "None" if restore_state is None else restore_state
    _prepare_interpreter()
    if use_default_frames:
        frames = DEFAULT_FRAMES + frames
    _check_frames(frames)
    _splash = PydidasSplashScreen(custom_splash_image=custom_splash_image)
    try:
        _splash.show_aligned_message("Starting QApplication")
        _app = _get_pydidas_qapplication()
        _app.sig_gui_exception_occurred.connect(_splash.close)
        _splash.show_aligned_message("Creating objects")
        _gui = main_window_cls()
        for frame in frames:
            _gui.register_frame(frame)
        _splash.show_aligned_message("Creating widgets")
        _gui.show()
        if restore_state.upper() not in ["NONE", "EXIT", "SAVED"]:
            raise UserConfigError(
                "The restore_state must be 'None', 'saved' or 'exit'."
            )
        _splash.show_aligned_message("Restoring interface state")
        try:
            _gui.restore_gui_state(state=restore_state)
        except UserConfigError:
            pass
        _splash.finish(_gui)
        _gui.check_for_updates(auto_check=True)
        _gui.setWindowIcon(icons.pydidas_icon_with_bg())
        _gui.raise_()
        _ = _app.exec_()
    except Exception:
        _splash.close()
    _app.deleteLater()


def _prepare_interpreter():
    """
    Prepare the interpreter for the pydidas GUI.
    """
    signal.signal(signal.SIGINT, signal.SIG_DFL)
    if mp.get_start_method() != "spawn":
        try:
            mp.set_start_method("spawn", force=True)
        except RuntimeError:
            warnings.warn(
                "Could not set the multiprocessing Process startup method to 'spawn'. "
                "Multiprocessing with OpenGL will not work in Unix-based systems. "
                "To solve this issue, restart the kernel and import pydidas before "
                "starting any multiprocessing."
            )


def _check_frames(frames: tuple[BaseFrame]):
    """
    Check if the given frames are valid.

    Parameters
    ----------
    frames : tuple[BaseFrame]
        The frames to be checked.
    """
    _invalid_frames = [frame for frame in frames if not issubclass(frame, BaseFrame)]
    if _invalid_frames:
        raise UserConfigError(
            "The following frames are not subclasses of BaseFrame:\n"
            + "\n".join([frame.__name__ for frame in _invalid_frames])
        )
    _frame_names = [frame.__name__ for frame in frames]
    if len(_frame_names) > len(set(_frame_names)):
        raise UserConfigError(
            "Duplicate frames detected in the specified list of frames.\n"
            "Please check the list of frames and remove any duplicates."
        )


def _get_pydidas_qapplication() -> PydidasQApplication:
    """
    Get the PydidasQApplication instance.

    Returns
    -------
    PydidasQApplication
        The PydidasQApplication instance.
    """
    _app = QApplication.instance()
    if not isinstance(_app, PydidasQApplication):
        _app = PydidasQApplication([])
    return _app
