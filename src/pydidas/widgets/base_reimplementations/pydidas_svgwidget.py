# This file is part of pydidas.
#
# Copyright 2025 - 2026, Helmholtz-Zentrum Hereon
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
The pydidas_svgwidget module defines the PydidasSvgWidget, a subclassed QSvgWidget
with automatic font adjustment and a custom sizeHint.
"""

__author__ = "Malte Storm"
__copyright__ = "Copyright 2025 - 2026, Helmholtz-Zentrum Hereon"
__license__ = "GPL-3.0-only"
__maintainer__ = "Malte Storm"
__status__ = "Production"
__all__ = ["PydidasSvgWidget"]


from pathlib import Path
from typing import Any

import qtpy


if qtpy.QT5:
    from qtpy.QtSvg import QSvgWidget
elif qtpy.QT6:
    from qtpy.QtSvgWidgets import QSvgWidget

from pydidas.widgets.base_classes import PydidasWidgetMixIn


class PydidasSvgWidget(PydidasWidgetMixIn, QSvgWidget):
    """
    A QSvgWidget with automatic font adjustment and a custom sizeHint.
    """

    def __init__(self, *args: Any, **kwargs: Any) -> None:
        """
        Initialize the PydidasSvgWidget.

        Parameters
        ----------
        *args : Any
            Positional arguments. The first argument must be a string or
            Path object representing the SVG filename. An optional second
            argument may be the parent QWidget.
        **kwargs : Any
            Keyword arguments passed to PydidasWidgetMixIn, e.g. bold,
            fontsize_offset, italic, underline.
        """
        if not args or not isinstance(args[0], (str, Path)):
            raise TypeError(
                "The first argument must be a string or Path object representing "
                "the SVG filename."
            )
        filename = str(args[0])
        parent = args[1] if len(args) == 2 else kwargs.get("parent", None)
        QSvgWidget.__init__(self, filename, parent)
        PydidasWidgetMixIn.__init__(self, **kwargs)
