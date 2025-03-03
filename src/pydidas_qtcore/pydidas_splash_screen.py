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
Module with the PydidasSplashScreen class to create a splash screen during startup.
"""

__author__ = "Malte Storm"
__copyright__ = "Copyright 2023 - 2025, Helmholtz-Zentrum Hereon"
__license__ = "GPL-3.0-only"
__maintainer__ = "Malte Storm"
__status__ = "Production"
__all__ = ["PydidasSplashScreen"]


from pathlib import Path
from typing import Optional

from qtpy import QtCore, QtGui, QtWidgets


_SPLASH_IMAGE_PATH = Path(__file__).parent.parent.joinpath(
    "pydidas", "resources", "images", "splash_image.png"
)


class PydidasSplashScreen(QtWidgets.QSplashScreen):
    """
    A splash screen which allows to show centered messages and with the pydidas icon.

    Parameters
    ----------
    pixmap : QtGui.QPixmap, optional
        The pixmap to be displayed on the splash screen.
    f : QtCore.Qt.WindowFlags, optional
        The window flags for the splash screen.
    custom_splash_image : Path, optional
        The path to a custom splash image to be displayed. This setting
        cannot be used in combination with the pixmap parameter. The
        pixmap parameter takes precedence.
    """

    def __init__(
        self,
        pixmap=None,
        f=QtCore.Qt.WindowStaysOnTopHint,
        custom_splash_image: Optional[Path] = None,
    ):
        if pixmap is None:
            _splash_path = (
                custom_splash_image if custom_splash_image else _SPLASH_IMAGE_PATH
            )
            pixmap = QtGui.QPixmap(str(_splash_path))
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
