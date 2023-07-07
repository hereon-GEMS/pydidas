# This file is part of pydidas.
#
# Copyright 2023, Helmholtz-Zentrum Hereon
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
__copyright__ = "Copyright 2023, Helmholtz-Zentrum Hereon"
__license__ = "GPL-3.0-only"
__maintainer__ = "Malte Storm"
__status__ = "Production"
__all__ = ["AboutWindow"]


from qtpy import QtCore

from ...resources import logos
from ...version import VERSION
from ..framework import PydidasWindow


PYDIDAS_INFO = (
    f"Version {VERSION}<br><br>"
    "pydidas is developed by Helmholtz-Zentrum Hereon<br>"
    "and is made available under the "
    "<a href='http://www.gnu.org/licenses/gpl-3.0.txt'>GNU General Public License 3.0"
    "</a>.<br>"
    "A small section of code is made available through other, "
    "more permissive licenses and copyrighted by their respective "
    "owners (particularly the ESRF for pyFAI and silx)."
    "<br><br>Copyright for pydidas 2021- Helmholtz-Zentrum Hereon"
    "<br><br>pydidas Homepage: "
    "<a href='http://ms.hereon.de/pydidas'>pydidas</a>"
    "<br><br>pydidas github: "
    "<a href='https://github.com/hereon-GEMS'>GEMS@github</a>"
)


class AboutWindow(PydidasWindow):
    """
    Window which displays basic information about the pydidas software.
    """

    show_frame = False

    def __init__(self, parent=None, **kwargs):
        PydidasWindow.__init__(self, parent, title="About pydidas", **kwargs)

    def build_frame(self):
        """
        Build the frame and create all widgets.
        """
        self.create_label(
            "label_title",
            "About",
            fontsize=14,
            bold=True,
            gridPos=(0, 0, 1, 1),
        )
        self.create_spacer(None)
        self.create_label(
            "label_input",
            PYDIDAS_INFO,
            openExternalLinks=True,
            textInteractionFlags=QtCore.Qt.LinksAccessibleByMouse,
            textFormat=QtCore.Qt.RichText,
            gridPos=(-1, 0, 1, 1),
        )
        self.add_any_widget(
            "svg_logo",
            logos.pydidas_logo_svg(),
            gridPos=(0, 1, 3, 1),
            fixedHeight=150,
            fixedWidth=150,
            layout_kwargs={"alignment": (QtCore.Qt.AlignRight | QtCore.Qt.AlignTop)},
        )
        self.create_button(
            "but_okay", "&OK", gridPos=(-1, 1, 1, 1), focusPolicy=QtCore.Qt.StrongFocus
        )

    def connect_signals(self):
        """
        Build the frame and create all widgets.
        """
        self._widgets["but_okay"].clicked.connect(self.close)
