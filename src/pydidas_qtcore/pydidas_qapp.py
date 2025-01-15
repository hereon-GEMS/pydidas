# This file is part of pydidas.
#
# Copyright 2023 - 2025, Helmholtz-Zentrum Hereon
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
Module with the PydidasQApplication class which is the pydidas subclassed QApplication.
"""

__author__ = "Malte Storm"
__copyright__ = "Copyright 2023 - 2025, Helmholtz-Zentrum Hereon"
__license__ = "GPL-3.0-only"
__maintainer__ = "Malte Storm"
__status__ = "Production"
__all__ = ["PydidasQApplication"]


import argparse
import signal
import sys
import weakref
from typing import Tuple

import matplotlib as mpl
import matplotlib.font_manager as mpl_font_manager
import matplotlib.ft2font as mpl_ft2font
import numpy as np
from qtpy import QtCore, QtGui
from qtpy.QtWidgets import QApplication, QStyle

from . import fontsize


_LOCALE = QtCore.QLocale(QtCore.QLocale.English)
_LOCALE.setNumberOptions(
    QtCore.QLocale.OmitGroupSeparator | QtCore.QLocale.RejectGroupSeparator
)
QtCore.QLocale.setDefault(_LOCALE)


_TEST_TEXT = (
    "A B C D E F G H I J K L M N O P Q R S T U V W X Y Z abcdefghijklmnopqrstuvwxyz"
)


def parse_cmd_args():
    """
    Parse commandline arguments.

    Returns
    -------
    dict :
        The parsed command line arguments.
    """
    parser = argparse.ArgumentParser(prog="pydidas", add_help=False)
    parser.add_argument(
        "-fontsize",
        type=int,
        help="The standard font size in points.",
    )
    parser.add_argument("-screen", type=int, help="The screen to use.")
    parser.add_argument("--qt6", action="store_true", help="Use Qt6 instead of Qt5.")
    _args, _unknown = parser.parse_known_args()
    _kwargs = {_key: _val for _key, _val in vars(_args).items() if _val is not None}
    for _name in ["fontsize", "screen"]:
        if f"-{_name}" in sys.argv:
            _pos = sys.argv.index(f"-{_name}")
            sys.argv.pop(_pos)
            sys.argv.pop(_pos)
    return _kwargs


def sigint_signal_handler(signal_num: int, frame: object):
    """
    Handle the SIGINT signal to gracefully shut down when pressing Ctrl+C.

    Parameters
    ----------
    signal_num : int
        The signal number.
    frame : object
        The calling frame object.
    """
    _app = PydidasQApplication.instance()
    _app.sig_exit_pydidas.emit()
    _app.terminate_registered_threads()
    _app.quit()
    sys.exit()


class PydidasQApplication(QApplication):
    """
    A subclassed QApplication used in pydidas for controlling the UI and event loops.

    The PydidasQApplication also handles font changes and scaling of the GUI based on
    font metrics.

    The following signals are available:

        - sig_exit_pydidas:
            Signal to exit the pydidas application. This signal can be used
            by all objects to start a graceful shutdown.
        - sig_new_fontsize: float
            Signal which emits the new font size. This signal allows all
            widgets to update their own font size.
        - sig_font_size_changed:
            Signal that the font size has changed. This signal can be used
            to trigger a redraw of all widgets.
        - sig_new_font_family: str
            Signal which emits the new font family. This signal allows all
            widgets to update their own font family.
        - sig_font_family_changed:
            Signal that the font family has changed. This signal can be used
            to trigger a redraw of all widgets.
        - sig_new_font_metrics: (float, float)
            Signal which emits the new font metrics. This signal allows all
            widgets to update their geometry based on the new font metrics.
        - sig_font_metrics_changed:
            Signal that the font metrics have changed. This signal can be used
            by widgets to update their geometry.
        - sig_mpl_font_change:
            Signal that the matplotlib font has changed. This signal can be used
            to trigger a redraw of all matplotlib plots.
        - sig_mpl_font_setting_error: str
            Signal that the matplotlib font setting has failed. This signal can
            be used to inform the user that the chosen font is not supported by
            matplotlib.
        - sig_status_message: str
            Signal to set a status message. This signal can be used by central
            widgets to store or print status information.
        - sig_updated_user_config: (str, str)
            Signal that the user configuration has been updated. This signal emits
            the key and value of the updated configuration.
        - sig_gui_exception_occurred:
            Signal that an exception has occurred in the GUI. This signal can be
            used to inform other widgets about the exception.
        - sig_user_signal: (str, str)
            A signal which can be used by the user to emit custom signals. The
            signal takes two strings as arguments which can be used at the
            receiver side to identify the signal and its content.
    """

    sig_exit_pydidas = QtCore.Signal()
    sig_new_fontsize = QtCore.Signal(float)
    sig_font_size_changed = QtCore.Signal()
    sig_new_font_family = QtCore.Signal(str)
    sig_font_family_changed = QtCore.Signal()
    sig_new_font_metrics = QtCore.Signal(float, float)
    sig_font_metrics_changed = QtCore.Signal()
    sig_mpl_font_change = QtCore.Signal()
    sig_mpl_font_setting_error = QtCore.Signal(str)
    sig_status_message = QtCore.Signal(str)
    sig_updated_user_config = QtCore.Signal(str, str)
    sig_gui_exception_occurred = QtCore.Signal()
    sig_user_signal = QtCore.Signal(str, str)
    _instance = None

    @staticmethod
    def instance():
        return PydidasQApplication._instance

    def __init__(self, args):
        QApplication.__init__(self, args)
        signal.signal(signal.SIGINT, sigint_signal_handler)
        self.setOrganizationName("Hereon")
        self.setOrganizationDomain("Hereon/WPI")
        self.setApplicationName("pydidas")
        self.__settings = QtCore.QSettings()
        self.__status = ""
        self.__standard_font = self.font()
        self.__worker_threads = []
        self.__available_mpl_fonts = mpl_font_manager.get_font_names()
        self.__font_config = {
            "size": float(
                self.__settings.value("font/point_size", fontsize.STANDARD_FONT_SIZE)
            ),
            "family": self.__settings.value("font/family", self.font().family()),
            "height": 20,
            "font_metric_height": 0.0,
            "font_metric_width": 0.0,
        }
        _kwargs = parse_cmd_args()
        self.font_size = _kwargs.get("fontsize", self.__font_config["size"])
        self.font_family = self.__font_config["family"]
        self.screen_to_use = _kwargs.get("screen", None)
        self._update_font_metrics()
        PydidasQApplication._instance = self

    def _update_font_metrics(self):
        """
        Update the font metrics for the width and height.
        """
        _metrics = QtGui.QFontMetrics(self.font())
        _char_height = _metrics.boundingRect(_TEST_TEXT).height()
        _char_width = _metrics.horizontalAdvance(_TEST_TEXT) / 78
        if (
            _char_height != self.__font_config["font_metric_height"]
            or _char_width != self.__font_config["font_metric_width"]
        ):
            self.__font_config["font_metric_height"] = _char_height
            self.__font_config["font_metric_width"] = _char_width
            self.sig_new_font_metrics.emit(_char_width, _char_height)
            self.sig_font_metrics_changed.emit()

    def _update_matplotlib_font_family(self):
        """
        Update the matplotlib font from the app's font config.
        """
        _family = self.__font_config["family"]
        _error = (
            f"The chosen font *{_family}* is not supported by matplotlib. "
            "The font for plots has not been updated."
        )
        if mpl.rcParams["font.family"] != _family:
            if _family not in self.__available_mpl_fonts:
                self.sig_mpl_font_setting_error.emit(_error)
                return
            _font = mpl_ft2font.FT2Font(mpl_font_manager.findfont(_family))
            _char_keys = set(_font.get_charmap().keys())
            if not set(np.arange(33, 125)).issubset(_char_keys):
                self.sig_mpl_font_setting_error.emit(_error)
                return
        mpl.rc("font", family=self.__font_config["family"])
        self.sig_mpl_font_change.emit()

    @QtCore.Slot()
    def send_gui_close_signal(self):
        """Send the signal that the GUI is about to close to all Windows."""
        self.sig_exit_pydidas.emit()

    @property
    def font_size(self) -> float:
        """
        Return the standard fontSize set for the app.

        Returns
        -------
        float
            The font size.
        """
        return self.__font_config["size"]

    @font_size.setter
    def font_size(self, value: float):
        """
        Set the standard fontsize for the PydidasApp.

        Parameters
        ----------
        value : float
            The new standard fontsize.
        """
        if value == self.font().pointSizeF():
            return
        self.__font_config["size"] = value
        self.__settings.setValue("font/point_size", float(value))
        _font = self.font()
        _font.setPointSizeF(value)
        self.setFont(_font)
        self._update_font_metrics()
        mpl.rc("font", size=self.__font_config["size"])
        self.sig_new_fontsize.emit(self.__font_config["size"])
        self.sig_font_size_changed.emit()
        self.sig_mpl_font_change.emit()

    @property
    def font_height(self) -> int:
        """
        Get the standard font height in pixels.

        Returns
        -------
        int
            The height of the font.
        """
        return int(self.__font_config["font_metric_height"])

    @property
    def font_family(self) -> str:
        """
        Get the standard font family.

        Returns
        -------
        str
            The font family.
        """
        return self.__font_config["family"]

    @font_family.setter
    def font_family(self, font_family: str):
        """
        Set the standard font family.

        Parameters
        ----------
        font_family : str
            The font family name.
        """
        if font_family == self.font().family():
            return
        self.__font_config["family"] = font_family
        self.__settings.setValue("font/family", font_family)
        _font = self.font()
        _font.setFamily(font_family)
        self.setFont(_font)
        self._update_font_metrics()
        self.sig_new_font_family.emit(font_family)
        self.sig_font_family_changed.emit()
        self.sig_font_size_changed.emit()
        self._update_matplotlib_font_family()

    def reset_font_to_standard(self):
        """
        Reset all font settings to the standard values.
        """
        _current_family = self.font().family()
        _current_size = self.font().pointSizeF()
        self.setFont(self.__standard_font)
        self.__font_config["size"] = self.font().pointSizeF()
        self.__font_config["family"] = self.font().family()
        if self.__font_config["family"] != _current_family:
            self.__settings.setValue("font/family", self.__font_config["family"])
            self.sig_new_font_family.emit(self.__font_config["family"])
        if self.__font_config["size"] != _current_size:
            self.__settings.setValue(
                "font/point_size", float(self.__font_config["size"])
            )
            self.sig_new_fontsize.emit(self.__font_config["size"])
        self._update_font_metrics()
        self._update_matplotlib_font_family()

    @property
    def scrollbar_width(self) -> int:
        """
        Get the width of scrollbars.

        Returns
        -------
        int
            The width in pixels.
        """
        return self.style().pixelMetric(QStyle.PM_ScrollBarExtent)

    @property
    def font_char_width(self) -> float:
        """
        Get the width of an average character.

        This method returns the average floating point width of a character.

        Returns
        -------
        float
            The average width for each character.
        """
        return self.__font_config["font_metric_width"]

    @property
    def font_metrics(self) -> Tuple[float, float]:
        """
        Get the font metrics for width and height.

        Returns
        -------
        Tuple[float]
            The width and height of the font in pixels.
        """
        return (
            self.__font_config["font_metric_width"],
            self.__font_config["font_metric_height"],
        )

    def updated_user_config(self, key: str, value: str):
        """
        Handle the updated user config and emit a signal with the change to all plots.

        Parameters
        ----------
        key : str
            The user configuration key.
        value : str
            The key's new value.
        """
        self.sig_updated_user_config.emit(key, value)

    def set_status_message(self, status: str):
        """
        Set a status message.

        Parameters
        ----------
        status : str
            The new status message.
        """
        self.__status = status
        self.sig_status_message.emit(status)

    @property
    def status(self) -> str:
        """
        Get the status string.

        Returns
        -------
        str
            The current status string.
        """
        return self.__status

    def register_thread(self, controller: QtCore.QThread):
        """
        Register a started thread as active.

        Registering the thread allows for shutting it down gracefully in case of
        a SIGINT signal (e.g. pressing Ctrl+C).

        Parameters
        ----------
        controller : QtCore.QThread
            The thread to be registered.
        """
        _ref = weakref.ref(controller)
        self.__worker_threads.append(_ref)

    @QtCore.Slot(object)
    def unregister_thread(self, controller: QtCore.QThread):
        """
        Unregister the given thread from the list of active threads.

        Parameters
        ----------
        controller : QtCore.QThread
            The controller thread which is about to finish.
        """
        _index = None
        for _ref in self.__worker_threads:
            if _ref() == controller:
                _index = self.__worker_threads.index(_ref)
                break
        if _index is not None:
            _ = self.__worker_threads.pop(_index)

    def terminate_registered_threads(self):
        """
        Terminate all running and registered threads.

        This method should only be called by signal handlers because by default,
        all worker threads should shut down normally.
        """
        for _ref in self.__worker_threads:
            _thread = _ref()
            _thread.requestInterruption()
