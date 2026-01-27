# This file is part of pydidas.
#
# Copyright 2023 - 2026, Helmholtz-Zentrum Hereon
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
__copyright__ = "Copyright 2023 - 2026, Helmholtz-Zentrum Hereon"
__license__ = "GPL-3.0-only"
__maintainer__ = "Malte Storm"
__status__ = "Production"
__all__ = ["PydidasSplashScreen"]


from pathlib import Path
from typing import Any

from qtpy import QtCore, QtGui, QtWidgets


_SPLASH_IMAGE_PATH = (
    Path(__file__).parents[1] / "pydidas" / "resources" / "images" / "splash_image.png"
)
_ICON_PATH = (
    Path(__file__).parents[1] / "pydidas" / "resources" / "icons" / "pydidas_snakes.svg"
)


class PydidasSplashScreen(QtWidgets.QSplashScreen):
    """
    A splash screen which shows centered messages with the pydidas icon.

    Parameters
    ----------
    pixmap : QtGui.QPixmap, optional
        The pixmap to be displayed on the splash screen.
    custom_splash_image : Path or None, optional
        The path to a custom splash image to be displayed. The default
        is None.
    """

    _instance = None

    @classmethod
    def is_active(cls) -> bool:
        """
        Check whether the PydidasSplashScreen is currently active.

        Returns
        -------
        bool
            True if an instance is active, False otherwise.
        """
        return cls._instance is not None

    @classmethod
    def instance(cls, **kwargs: Any) -> "PydidasSplashScreen":
        """
        Get the singleton instance of the PydidasSplashScreen.

        Parameters
        ----------
        **kwargs : Any
            Keyword arguments to pass to the constructor.

        Returns
        -------
        PydidasSplashScreen
            The singleton instance.
        """
        if cls._instance is None:
            cls._instance = cls(**kwargs)
        if kwargs.get("custom_splash_image") is not None:
            _pixmap = QtGui.QPixmap(str(kwargs["custom_splash_image"]))
            cls._instance.setPixmap(_pixmap)
        return cls._instance

    def __init__(
        self,
        pixmap: QtGui.QPixmap | None = None,
        custom_splash_image: Path | None = None,
    ) -> None:
        """
        Initialize the PydidasSplashScreen.

        Parameters
        ----------
        pixmap : QtGui.QPixmap or None, optional
            The pixmap to display. If None, a default splash image is used.
            The default is None.
        custom_splash_image : Path or None, optional
            Path to a custom splash image. Only used if pixmap is None.
            The default is None.
        """
        if PydidasSplashScreen._instance is not None:
            return PydidasSplashScreen._instance
        if pixmap is None:
            _splash_path = (
                custom_splash_image if custom_splash_image else _SPLASH_IMAGE_PATH
            )
            pixmap = QtGui.QPixmap(str(_splash_path))
        QtWidgets.QSplashScreen.__init__(self, pixmap)
        PydidasSplashScreen._instance = self
        self.setWindowFlag(QtCore.Qt.Tool, False)
        self.setWindowIcon(QtGui.QIcon(str(_ICON_PATH)))
        self.show_aligned_message("Importing packages")
        self.show()
        QtWidgets.QApplication.instance().processEvents()

    def show_aligned_message(self, message: str) -> None:
        """
        Show a message aligned bottom / center.

        Parameters
        ----------
        message : str
            The message to be displayed.
        """
        self.showMessage(message, int(QtCore.Qt.AlignHCenter | QtCore.Qt.AlignBottom))
