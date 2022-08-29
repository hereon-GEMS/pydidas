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
The qtooltip_event_filter changes plain text tooltips to rich text tooltips
because Qt will format these correctly with linebreaks.
"""

__author__ = "Malte Storm"
__copyright__ = "Copyright 2021-2022, Malte Storm, Helmholtz-Zentrum Hereon"
__license__ = "GPL-3.0"
__maintainer__ = "Malte Storm"
__status__ = "Development"
__all__ = ["QTooltipEventFilter"]


import html
from qtpy.QtCore import Qt, QEvent, QObject
from qtpy.QtWidgets import QWidget


class QTooltipEventFilter(QObject):
    """
    Filter events for tooltips and convert plain text to rich text to force
    Qt to format it correctly.

    This is a `well-known long-standing issue <issue_>`__ for
    which no official resolution exists.

    .. _issue:
        https://bugreports.qt.io/browse/QTBUG-41051
    """

    def eventFilter(self, widget, event):
        """
        Tooltip-specific event filter handling the passed Qt object and event.

        Parameters
        ----------
        widget : QtWidget.QWidget
            The calling widget.
        event : QtCore.QEvent
            The event to be processed.

        Returns
        -------
        bool :
            Flag whether this event was handled.
        """
        if event.type() == QEvent.ToolTipChange:
            if not isinstance(widget, QWidget):
                raise ValueError(f'QObject "{widget}" is not a widget.')

            if isinstance(widget.toolTip, str):
                return False
            _tooltip = widget.toolTip()

            if len(_tooltip) > 0 and not Qt.mightBeRichText(_tooltip):
                _tooltip = f"<qt>{html.escape(_tooltip)}</qt>"
                widget.setToolTip(_tooltip)
                return True

        return super().eventFilter(widget, event)
