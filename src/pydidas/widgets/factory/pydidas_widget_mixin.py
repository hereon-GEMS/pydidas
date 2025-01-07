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
The pydidas_widget_mixin module includes the PydidasWidgetMixin class to add additional
functionality implemented in PydidasQApplication.
"""

__author__ = "Malte Storm"
__copyright__ = "Copyright 2023 - 2025, Helmholtz-Zentrum Hereon"
__license__ = "GPL-3.0-only"
__maintainer__ = "Malte Storm"
__status__ = "Production"
__all__ = ["PydidasWidgetMixin"]


from typing import Union

from qtpy import QtCore
from qtpy.QtWidgets import QApplication

from pydidas.core.constants import (
    GENERIC_STANDARD_WIDGET_WIDTH,
    MINIMUN_WIDGET_DIMENSIONS,
)
from pydidas.core.utils import apply_qt_properties, update_qobject_font


class PydidasWidgetMixin:
    """
    Mixin class to handle automatic font updated from the QApplication.

    This class allows to use custom font settings (different sizes, bold etc) and
    still update them automatically.
    """

    init_kwargs = [
        "bold",
        "fontsize_offset",
        "font_metric_height_factor",
        "font_metric_width_factor",
        "italic",
        "minimum_width",
        "size_hint_width",
        "underline",
    ]

    def __init__(self, **kwargs: dict):
        """
        Set up the class instance of the subclassed QWidget.

        Parameters
        ----------
        **kwargs : dict
            Any kwargs for setting the font or other Qt parameters.
        """
        self.__font_config = {
            "bold": kwargs.get("bold", False),
            "italic": kwargs.get("italic", False),
            "size_offset": kwargs.get("fontsize_offset", 0),
            "underline": kwargs.get("underline", False),
        }
        self._size_hint = [
            kwargs.get("size_hint_width", GENERIC_STANDARD_WIDGET_WIDTH),
            25,
        ]
        apply_qt_properties(self, **kwargs)
        self._qtapp = QApplication.instance()
        self.update_fontsize(self._qtapp.font_size)
        self.update_font_family(self._qtapp.font_family)
        self._minimum_width = kwargs.get("minimum_width", MINIMUN_WIDGET_DIMENSIONS)
        if True in self.__font_config.values():
            update_qobject_font(self, **self.__font_config)
        self._font_metric_width_factor = kwargs.get("font_metric_width_factor", None)
        self._font_metric_height_factor = kwargs.get("font_metric_height_factor", None)
        self._qtapp.sig_new_fontsize.connect(self.update_fontsize)
        self._qtapp.sig_new_font_family.connect(self.update_font_family)
        self._qtapp.sig_new_font_metrics.connect(self.process_new_font_metrics)
        self.process_new_font_metrics(*self._qtapp.font_metrics)

    def sizeHint(self) -> QtCore.QSize:
        """
        Set a reasonable wide sizeHint so the label takes the available space.

        Returns
        -------
        QtCore.QSize
            The widget sizeHint
        """
        return QtCore.QSize(*self._size_hint)

    @QtCore.Slot(float)
    def update_fontsize(self, new_fontsize: float):
        """
        Update the fontsize with the new global default.

        Parameters
        ----------
        new_fontsize : float
            The new font size.
        """
        _font = self.font()
        _font.setPointSizeF(new_fontsize + self.__font_config["size_offset"])
        self.setFont(_font)

    @QtCore.Slot(str)
    def update_font_family(self, new_family: str):
        """
        Update the font family.

        Parameters
        ----------
        new_family : str
            The name of the new font family.
        """
        _font = self.font()
        _font.setFamily(new_family)
        self.setFont(_font)

    @QtCore.Slot(float, float)
    def process_new_font_metrics(self, font_width: float, font_height: float):
        """
        Set the fixed width of the widget dynamically from the font metrics.

        Parameters
        ----------
        font_width: float
            The font width in pixels.
        font_height : float
            The font height in pixels.
        """
        if self._font_metric_width_factor is not None:
            _width = max(
                self._minimum_width,
                int(self._font_metric_width_factor * font_width),
            )
            self._size_hint[0] = _width
            self.setFixedWidth(_width)
        if self._font_metric_height_factor is not None:
            _margins = self.contentsMargins()
            _height = max(
                MINIMUN_WIDGET_DIMENSIONS,
                int(self._font_metric_height_factor * font_height)
                + _margins.top()
                + _margins.bottom()
                + 6,
            )
            self._size_hint[1] = _height
            self.setFixedHeight(_height)

    @property
    def font_metric_height_factor(self) -> Union[None, float]:
        """
        Get the font metric height factor.

        This method returns None, if the factor has not been set.

        Returns
        -------
        Union[None, float]
            The font metric height factor.
        """
        return self._font_metric_height_factor

    @font_metric_height_factor.setter
    def font_metric_height_factor(self, factor: Union[None, float]):
        """
        Set the font metric height factor.

        Parameters
        ----------
        factor : Union[None, float]
            The new font metric height factor. None will disable scaling.
        """
        self._font_metric_height_factor = factor
        if factor is not None:
            self.process_new_font_metrics(*self._qtapp.font_metrics)

    @property
    def font_metric_width_factor(self) -> Union[None, float]:
        """
        Get the font metric width factor.

        This method returns None, if the factor has not been set.

        Returns
        -------
        Union[None, float]
            The font metric width factor.
        """
        return self._font_metric_width_factor

    @font_metric_width_factor.setter
    def font_metric_width_factor(self, factor: Union[None, float]):
        """
        Set the font metric width factor.

        Parameters
        ----------
        factor : Union[None, float]
            The new font metric width factor. None will disable scaling.
        """
        self._font_metric_width_factor = factor
        if factor is not None:
            self.process_new_font_metrics(*self._qtapp.font_metrics)
