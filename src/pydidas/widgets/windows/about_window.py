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
Module with the AboutWindow class which shows basic information about the pydidas
software.
"""

__author__ = "Malte Storm"
__copyright__ = "Copyright 2024 - 2025, Helmholtz-Zentrum Hereon"
__license__ = "GPL-3.0-only"
__maintainer__ = "Malte Storm"
__status__ = "Production"
__all__ = ["AboutWindow"]


from qtpy import QtCore, QtWidgets

from pydidas.core.constants import (
    ALIGN_BOTTOM_RIGHT,
    ALIGN_TOP_RIGHT,
    FONT_METRIC_SMALL_BUTTON_WIDTH,
    FONT_METRIC_WIDE_CONFIG_WIDTH,
)
from pydidas.resources import logos
from pydidas.version import VERSION
from pydidas.widgets.framework import PydidasWindow


PYDIDAS_INFO = (
    f"Version {VERSION}<br><br>"
    "pydidas is developed by Helmholtz-Zentrum Hereon<br>"
    "and is made available under the "
    "<a href='http://www.gnu.org/licenses/gpl-3.0.txt'>GNU General Public License 3.0"
    "</a>.<br>"
    "A small section of code is adapted from code which is distributed with other, "
    "more permissive licenses and copyrighted by their respective "
    "owners (particularly the ESRF for pyFAI and silx)."
    "<br><br>pydidas Copyright 2020 - 2025, Helmholtz-Zentrum Hereon"
    "<br><br>pydidas homepage: "
    "<a href='https://pydidas.hereon.de/index.php.en'>pydidas.hereon.de</a>"
    "<br><br>pydidas GitHub: "
    "<a href='https://github.com/hereon-GEMS/pydidas'>pydidas@github</a>"
)


class AboutWindow(PydidasWindow):
    """
    Window which displays basic information about the pydidas software.
    """

    show_frame = False

    def __init__(self, **kwargs: dict):
        PydidasWindow.__init__(self, title="About pydidas", **kwargs)

    def build_frame(self):
        """
        Build the frame and create all widgets.
        """
        _font_height = QtWidgets.QApplication.instance().font_height
        self.create_label(
            "label_title",
            "About",
            bold=True,
            font_metric_height_factor=1,
            font_metric_width_factor=FONT_METRIC_WIDE_CONFIG_WIDTH,
            fontsize_offset=4,
        )
        self.create_label(
            "label_input",
            PYDIDAS_INFO,
            font_metric_height_factor=16,
            font_metric_width_factor=FONT_METRIC_WIDE_CONFIG_WIDTH,
            gridPos=(1, 0, 2, 1),
            textInteractionFlags=QtCore.Qt.LinksAccessibleByMouse,
            textFormat=QtCore.Qt.RichText,
            openExternalLinks=True,
            wordWrap=True,
        )
        self.add_any_widget(
            "svg_logo",
            logos.pydidas_logo_svg(),
            fixedHeight=_font_height * 9,
            fixedWidth=_font_height * 9,
            gridPos=(0, 1, 2, 2),
            layout_kwargs={"alignment": ALIGN_TOP_RIGHT},
        )
        self.create_button(
            "but_okay",
            "&OK",
            focusPolicy=QtCore.Qt.StrongFocus,
            font_metric_width_factor=FONT_METRIC_SMALL_BUTTON_WIDTH,
            gridPos=(-1, 2, 1, 1),
            layout_kwargs={"alignment": ALIGN_BOTTOM_RIGHT},
        )
        self.resize(QtCore.QSize(_font_height * 35, _font_height * 20))

    def connect_signals(self):
        """
        Build the frame and create all widgets.
        """
        self._widgets["but_okay"].clicked.connect(self.close)
        QtWidgets.QApplication.instance().sig_new_font_metrics.connect(
            self.process_new_font_metrics
        )

    @QtCore.Slot(float, float)
    def process_new_font_metrics(self, char_width: float, char_height: float):
        """
        Adjust the window based on the new font metrics.

        Parameters
        ----------
        char_width: float
            The font width in pixels.
        char_height : float
            The font height in pixels.
        """
        self._widgets["svg_logo"].setFixedSize(
            QtCore.QSize(char_height * 9, char_height * 9)
        )
        self.resize(QtCore.QSize(char_width * 70, char_height * 18))
        self.adjustSize()
