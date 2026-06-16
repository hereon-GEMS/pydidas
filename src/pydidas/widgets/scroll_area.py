# This file is part of pydidas.
#
# Copyright 2024 - 2026, Helmholtz-Zentrum Hereon
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
Module with the ScrollArea class, a QScrollArea implementation with
convenience calling arguments for simplified formatting.
"""

__author__ = "Malte Storm"
__copyright__ = "Copyright 2024 - 2026, Helmholtz-Zentrum Hereon"
__license__ = "GPL-3.0-only"
__maintainer__ = "Malte Storm"
__status__ = "Production"
__all__ = ["ScrollArea"]


from typing import Any

from qtpy.QtCore import QSize, Slot
from qtpy.QtWidgets import QFrame, QScrollArea, QWidget

from pydidas.core.constants import POLICY_EXP_EXP
from pydidas.core.utils import apply_qt_properties
from pydidas_qtcore import PydidasQApplication


class ScrollArea(QScrollArea):
    """
    Convenience class to simplify the setup of a QScrollArea.

    Parameters
    ----------
    parent : QWidget, optional
        The parent widget. The default is None.
    **kwargs : Any
        Any additional keyword arguments. All Qt attributes with a
        setAttribute method are valid keywords.
    """

    init_kwargs = ["resize_to_widget_width", "embedded_widget"]

    def __init__(self, parent: QWidget | None = None, **kwargs: Any) -> None:
        QScrollArea.__init__(self, parent)  # type: ignore[arg-type]
        kwargs["widgetResizable"] = True
        kwargs["autoFillBackground"] = True
        kwargs["sizePolicy"] = POLICY_EXP_EXP
        kwargs["frameShape"] = QFrame.NoFrame
        apply_qt_properties(self, **kwargs)  # type: ignore[arg-type]
        _app = PydidasQApplication.instance()
        self.__scrollbar_width = _app.scrollbar_width  # type: ignore[attr-defined]
        if kwargs.get("resize_to_widget_width", False):
            _app.sig_font_metrics_changed.connect(  # type: ignore[attr-defined]
                self.force_width_from_size_hint
            )

    def sizeHint(self) -> QSize:
        """
        Get the size hint.

        If a widget has been set, the ScrollArea will use the widget's sizeHint
        to determine the required size. If no widget is set, it will default
        to the QScrollArea sizeHint.

        Returns
        -------
        QSize
            The size hint for the ScrollArea.
        """
        if self.widget() is not None:
            _hint = self.widget().sizeHint()
            return QSize(_hint.width() + self.__scrollbar_width + 12, _hint.height())
        return super().sizeHint()

    @Slot()
    def force_width_from_size_hint(self) -> None:
        """
        Enforce a fixed width based on the own sizeHint.
        """
        self.setFixedWidth(self.sizeHint().width())
