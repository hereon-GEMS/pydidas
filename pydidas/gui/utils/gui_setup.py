# This file is part of pydidas.
#
# pydidas is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
#
# Pydidas is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE. See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with Pydidas. If not, see <http://www.gnu.org/licenses/>.

"""
The pydidas.gui.utils.gui_setup module includes utility functions used for starting
the graphical user interface.
"""

__author__ = "Malte Storm"
__copyright__ = "Copyright 2021-2022, Malte Storm, Helmholtz-Zentrum Hereon"
__license__ = "GPL-3.0"
__maintainer__ = "Malte Storm"
__status__ = "Development"
__all__ = [
    "configure_qtapp_namespace",
    "update_qtapp_font_size",
    "apply_tooltip_event_filter",
]

from qtpy import QtWidgets

from ...core import constants
from .qtooltip_event_handler import QTooltipEventHandler


def configure_qtapp_namespace():
    """
    Set the QApplication organization and application names.
    """
    app = QtWidgets.QApplication.instance()
    app.setOrganizationName("Hereon")
    app.setOrganizationDomain("Hereon/WPI")
    app.setApplicationName("pydidas")


def update_qtapp_font_size():
    """
    Update the standard fonz size in the QApplication with the font size
    defined in pydidas.
    """
    _app = QtWidgets.QApplication.instance()
    if _app is not None:
        _font = _app.font()
        _font.setPointSize(constants.STANDARD_FONT_SIZE)
        _app.setFont(_font)


def apply_tooltip_event_filter():
    """
    Apply the pydidas.core.utils.QTooltipEventHandler to the QApplication
    to force the desired handling of tooltip.

    Without this filter
    """
    _app = QtWidgets.QApplication.instance()
    _app.installEventFilter(QTooltipEventHandler(_app))
