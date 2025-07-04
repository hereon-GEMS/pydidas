# This file is part of pydidas.
#
# Copyright 2025, Helmholtz-Zentrum Hereon
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
The pydidas_lineedit module defines the PydidasLineEdit, a subclassed QLineEdit with
automatic font adjustment and a custom sizeHint.
"""

__author__ = "Malte Storm"
__copyright__ = "Copyright 2025, Helmholtz-Zentrum Hereon"
__license__ = "GPL-3.0-only"
__maintainer__ = "Malte Storm"
__status__ = "Production"
__all__ = ["PydidasSvgWidget"]

from pathlib import Path

from qtpy import QtSvg

from pydidas.widgets.factory.pydidas_widget_mixin import PydidasWidgetMixin


class PydidasSvgWidget(PydidasWidgetMixin, QtSvg.QSvgWidget):
    """
    Create a QLineEdit with automatic font formatting.
    """

    def __init__(self, *args: tuple, **kwargs: dict):
        if not isinstance(args[0], (str, Path)):
            raise TypeError(
                "The first argument must be a string or Path object representing "
                "the SVG filename."
            )
        filename = str(args[0])
        parent = args[1] if len(args) == 2 else kwargs.get("parent", None)
        QtSvg.QSvgWidget.__init__(self, filename, parent)
        PydidasWidgetMixin.__init__(self, **kwargs)
