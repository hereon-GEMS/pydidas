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
Module with the PydidasQApplication class which is the pydidas subclassed QApplication.
"""

__author__ = "Malte Storm"
__copyright__ = "Copyright 2023, Helmholtz-Zentrum Hereon"
__license__ = "GPL-3.0-only"
__maintainer__ = "Malte Storm"
__status__ = "Production"
__all__ = ["PydidasQApplication"]


import argparse
import sys

from qtpy import QtCore, QtWidgets, QtGui
import matplotlib as mpl
import matplotlib.font_manager as mpl_font_manager
import matplotlib.ft2font as mpl_ft2font
import numpy as np

from . import fontsize


_LOCALE = QtCore.QLocale(QtCore.QLocale.English)
_LOCALE.setNumberOptions(
    QtCore.QLocale.OmitGroupSeparator | QtCore.QLocale.RejectGroupSeparator
)
QtCore.QLocale.setDefault(_LOCALE)


def parse_cmd_args():
    """
    Parse commandline arguments.

    Returns
    -------
    dict :
        The parsed command line arguments.
    """
    parser = argparse.ArgumentParser()
    parser.add_argument(
        "-fontsize",
        type=int,
        help="The standard font size in points.",
    )
    parser.add_argument("--qt6", action="store_true")

    _args, _unknown = parser.parse_known_args()
    _kwargs = {_key: _val for _key, _val in vars(_args).items() if _val is not None}
    for _name in ["fontsize"]:
        if f"-{_name}" in sys.argv:
            _pos = sys.argv.index(f"-{_name}")
            sys.argv.pop(_pos)
            sys.argv.pop(_pos)
    return _kwargs


class PydidasQApplication(QtWidgets.QApplication):
    """
    A subclassed QApplication used in pydidas for controlling the UI and event loops.

    The PydidasQApplication also handles font changes and scaling of the GUI based on
    font metrics.
    """

    sig_close_gui = QtCore.Signal()
    sig_new_fontsize = QtCore.Signal(float)
    sig_font_size_changed = QtCore.Signal()
    sig_new_font_family = QtCore.Signal(str)
    sig_font_family_changed = QtCore.Signal()
    sig_new_font_height = QtCore.Signal(float)
    sig_font_height_changed = QtCore.Signal()
    sig_mpl_font_change = QtCore.Signal()
    sig_mpl_font_setting_error = QtCore.Signal(str)

    def __init__(self, args):
        QtWidgets.QApplication.__init__(self, args)
        self.setOrganizationName("Hereon")
        self.setOrganizationDomain("Hereon/WPI")
        self.setApplicationName("pydidas")
        self.__settings = QtCore.QSettings()
        self.__standard_font = self.font()
        self.__available_mpl_fonts = mpl_font_manager.get_font_names()
        self.__font_config = {
            "size": float(
                self.__settings.value("font/point_size", fontsize.STANDARD_FONT_SIZE)
            ),
            "family": self.__settings.value("font/family", self.font().family()),
            "height": 20,
        }
        _kwargs = parse_cmd_args()
        self.standard_font_size = _kwargs.get("fontsize", self.__font_config["size"])
        self.standard_font_family = self.__font_config["family"]
        self._update_font_height()
        # self.__initialization = False

    def _update_font_height(self):
        """
        Update the stored font height metrics.
        """
        _font_height = QtGui.QFontMetrics(self.font()).boundingRect("Height").height()
        if _font_height != self.__font_config["height"]:
            self.__font_config["height"] = _font_height
            self.sig_new_font_height.emit(_font_height)
            self.sig_font_height_changed.emit()

    def _update_matplotlib_font_family(self):
        """
        Update the matplotlib font from the app's font config.
        """
        _family = self.__font_config["family"]
        if mpl.rcParams["font.family"] != _family:
            if _family not in self.__available_mpl_fonts:
                self.sig_mpl_font_setting_error.emit(
                    f"The chosen font *{_family}* is not supported by matplotlib. "
                    "Defaulting to DejaVu Sans."
                )
                return
            _font = mpl_ft2font.FT2Font(mpl_font_manager.findfont(_family))
            _char_keys = set(_font.get_charmap().keys())
            if not set(np.arange(33, 125)).issubset(_char_keys):
                self.sig_mpl_font_setting_error.emit(
                    f"The chosen font *{_family}* is not supported by matplotlib. "
                    "The font for plots has not been updated."
                )
                return
        mpl.rc("font", family=self.__font_config["family"])
        self.sig_mpl_font_change.emit()

    @QtCore.Slot()
    def send_gui_close_signal(self):
        """Send the signal that the GUI is about to close to all Windows."""
        self.sig_close_gui.emit()

    @property
    def standard_font_size(self) -> float:
        """
        Return the standard fontSize set for the app.

        Returns
        -------
        float
            The font size.
        """
        return self.__font_config["size"]

    @standard_font_size.setter
    def standard_font_size(self, value: float):
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
        self._update_font_height()
        mpl.rc("font", size=self.__font_config["size"])
        self.sig_new_fontsize.emit(self.__font_config["size"])
        self.sig_font_size_changed.emit()
        self.sig_mpl_font_change.emit()

    @property
    def standard_font_height(self) -> int:
        """
        Get the standard font height in pixels.

        Returns
        -------
        int
            The height of the font.
        """
        return self.__font_config["height"]

    @property
    def standard_font_family(self) -> str:
        """
        Get the standard font family.

        Returns
        -------
        str
            The font family.
        """
        return self.__font_config["family"]

    @standard_font_family.setter
    def standard_font_family(self, font_family: str):
        """
        Set the standard font family.

        Parameters
        ----------
        family : str
            The font family name.
        """
        if font_family == self.font().family():
            return
        self.__font_config["family"] = font_family
        self.__settings.setValue("font/family", font_family)
        _font = self.font()
        _font.setFamily(font_family)
        self.setFont(_font)
        self._update_matplotlib_font_family()
        self._update_font_height()
        self.sig_new_font_family.emit(font_family)
        self.sig_font_size_changed.emit()

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
        self._update_font_height()
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
        return self.style().pixelMetric(QtWidgets.QStyle.PM_ScrollBarExtent)
