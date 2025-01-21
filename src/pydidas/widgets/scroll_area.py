# This file is part of pydidas.
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
# along with Pydidas. If not, see <http://www.gnu.org/licenses/>.

"""
Module with the ScrollAreaclass, a QScrollArea implementation with convenience
calling arguments for simplified formatting.
"""

__author__ = "Malte Storm"
__copyright__ = "Copyright 2024 - 2025, Helmholtz-Zentrum Hereon"
__license__ = "GPL-3.0-only"
__maintainer__ = "Malte Storm"
__status__ = "Production"
__all__ = ["ScrollArea"]


from qtpy.QtCore import QSize, Slot
from qtpy.QtWidgets import QApplication, QFrame, QScrollArea

from pydidas.core.constants import POLICY_EXP_EXP
from pydidas.core.utils import apply_qt_properties


class ScrollArea(QScrollArea):
    """
    Convenience class to simplify the setup of a QScrollArea.

    Parameters
    ----------
    parent : QWidget, optional
        The parent widget. The default is None.
    **kwargs : dict
        Any additional keyword arguments. All Qt attributes with a setAttribute
        method are valid keywords.
    """

    init_kwargs = ["resize_to_widget_width"]

    def __init__(self, parent=None, **kwargs):
        QScrollArea.__init__(self, parent)
        kwargs["widgetResizable"] = True
        kwargs["autoFillBackground"] = True
        kwargs["sizePolicy"] = POLICY_EXP_EXP
        kwargs["frameShape"] = QFrame.NoFrame
        apply_qt_properties(self, **kwargs)
        self.__scrollbar_width = QApplication.instance().scrollbar_width
        if kwargs.get("resize_to_widget_width", False):
            QApplication.instance().sig_font_metrics_changed.connect(
                self.force_width_from_size_hint
            )

    def sizeHint(self):
        """
        Get the size hint.

        If a widget has been set, the ScrollArea will use the widget's sizeHint
        to determine the required size. If no widget is set, it will default
        to the QScrollArea sizeHint.

        Returns
        -------
        QtCore.QSize
            The size hint for the ScrollArea.
        """
        if self.widget() is not None:
            _hint = self.widget().sizeHint()
            return QSize(_hint.width() + self.__scrollbar_width + 12, _hint.height())
        return super().sizeHint()

    @Slot()
    def force_width_from_size_hint(self):
        """
        Enforce a fixed width based on the own sizeHint.
        """
        self.setFixedWidth(self.sizeHint().width())
