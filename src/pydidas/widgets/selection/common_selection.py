# This file is part of pydidas
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
# along with pydidas If not, see <http://www.gnu.org/licenses/>.

"""
Module with common functionality for selection widgets.
"""

__author__ = "Malte Storm"
__copyright__ = "Copyright 2024 - 2025, Helmholtz-Zentrum Hereon"
__license__ = "GPL-3.0-only"
__maintainer__ = "Malte Storm"
__status__ = "Production"
__all__ = ["register_plot_widget_method"]


from qtpy import QtWidgets


def register_plot_widget_method(self, widget: QtWidgets.QWidget):
    """
    Register a view widget to be used for full visualization of data.

    This method registers an external view widget for data visualization.
    Note that the widget must accept frames through a ``addImage`` method.

    Parameters
    ----------
    self : object
        The class to call this method.
    widget : QWidget
        A widget with an ``addImage`` or ``display_image`` method to pass frames to.

    Raises
    ------
    TypeError
        If the widget is not a QWidget.
    AttributeError
        if the widget does not have a ``addImage`` or ``display_image`` method.
    """
    if not isinstance(widget, QtWidgets.QWidget):
        raise TypeError("Error: Object must be a QWidget.")
    if not (hasattr(widget, "display_image") or hasattr(widget, "addImage")):
        raise AttributeError(
            "Error: The selected widget is not supported, as it does not have an "
            "`addImage` or `display_image` method."
        )
    self._widgets["plot"] = widget
    if hasattr(widget, "display_image"):
        self.show_image_method = widget.display_image
    elif hasattr(widget, "addImage"):
        self.show_image_method = widget.addImage
