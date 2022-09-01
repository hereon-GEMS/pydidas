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
Module with the UtilitiesFrameBuilder class which is used to populate
the UtilitiesFrame with widgets.
"""

__author__ = "Malte Storm"
__copyright__ = "Copyright 2021-2022, Malte Storm, Helmholtz-Zentrum Hereon"
__license__ = "GPL-3.0"
__maintainer__ = "Malte Storm"
__status__ = "Development"
__all__ = ["UtilitiesFrameBuilder"]

from qtpy import QtWidgets

from ....core.constants import QT_BOTTOM_ALIGNMENT
from ....widgets import BaseFrame


UTILITIES = {
    "eiger_mask": {
        "title": "Save Eiger mask from master file",
        "text": (
            "Get the mask file for the Eiger detector from a Hdf5 master file written "
            "by the Eiger detector."
        ),
        "button_text": "Get and save Eiger mask",
    },
    "series_operations": {
        "title": "File series operations",
        "text": (
            "Perform mathematical operations (e.g. sum, mean, median) on a series of "
            "images and save the results to a new single image."
        ),
        "button_text": "File series operations",
    },
    "series_operations2": {
        "title": "File series operations",
        "text": (
            "Perform mathematical operations (e.g. sum, mean, median) on a series of "
            "images and save the results to a new single image."
        ),
        "button_text": "File series operations",
    },
}


class UtilitiesFrameBuilder(BaseFrame):
    """
    Create all widgets and initialize their state.

    Parameters
    ----------
    self : pydidas.gui.SetupScanFrame
        The SetupScanFrame instance.
    """

    GROUP_WIDTH = 320

    def __init__(self, parent=None, **kwargs):
        BaseFrame.__init__(self, parent, **kwargs)

    def build_frame(self):
        """
        Create all widgets for the frame and place them in the layout.
        """
        self.create_label(
            "label_title",
            "Utilities\n",
            fontsize=14,
            bold=True,
            gridPos=(0, 0, 1, 1),
            fixedWidth=self.GROUP_WIDTH,
        )

        for _index, (_key, _entries) in enumerate(UTILITIES.items()):
            _xpos = _index % 2
            _ypos = _index // 2 + 1
            self.create_empty_widget(
                f"utility_{_key}",
                gridPos=(_ypos, _xpos, 1, 1),
                fixedWidth=self.GROUP_WIDTH,
                fixedHeight=150,
            )
            self.create_label(
                f"title_{_key}",
                _entries["title"],
                gridPos=(0, 0, 1, 1),
                parent_widget=self._widgets[f"utility_{_key}"],
                fontSize=12,
                fixedWidth=self.GROUP_WIDTH - 20,
                bold=True,
            )
            self.create_label(
                f"text_{_key}",
                _entries["text"],
                gridPos=(1, 0, 1, 1),
                parent_widget=self._widgets[f"utility_{_key}"],
                fixedWidth=self.GROUP_WIDTH - 20,
                fontSize=11,
            )
            self.create_spacer(
                f"spacer_{_key}",
                gridPos=(2, 0, 1, 1),
                policy=QtWidgets.QSizePolicy.Minimum,
                vertical_policy=QtWidgets.QSizePolicy.Expanding,
                parent_widget=self._widgets[f"utility_{_key}"],
                fixedWidth=self.GROUP_WIDTH - 20,
            )
            self.create_button(
                f"button_{_key}",
                _entries["button_text"],
                gridPos=(3, 0, 1, 1),
                fixedWidth=self.GROUP_WIDTH - 20,
                parent_widget=self._widgets[f"utility_{_key}"],
                alignment=QT_BOTTOM_ALIGNMENT,
            )
            self.create_spacer(
                f"spacer_{_key}_2",
                gridPos=(4, 0, 1, 1),
                policy=QtWidgets.QSizePolicy.Minimum,
                parent_widget=self._widgets[f"utility_{_key}"],
                fixedHeight=50,
            )

        self.create_spacer(
            "final_spacer",
            gridPos=(_ypos + 1, 2, 1, 1),
            policy=QtWidgets.QSizePolicy.Expanding,
        )
