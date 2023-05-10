# This file is part of pydidas.
#
# Copyright 2021-, Helmholtz-Zentrum Hereon
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
Module with the UtilitiesFrameBuilder class which is used to populate
the UtilitiesFrame with widgets.
"""

__author__ = "Malte Storm"
__copyright__ = "Copyright 2021-, Helmholtz-Zentrum Hereon"
__license__ = "GPL-3.0-only"
__maintainer__ = "Malte Storm"
__status__ = "Development"
__all__ = ["UtilitiesFrameBuilder"]


from qtpy import QtWidgets

from ....core import constants
from ....widgets.framework import BaseFrame


UTILITIES = {
    "user_config": {
        "title": "Edit user config",
        "text": (
            "Edit the user preferences for the generic application config."
            "(e.g. colormaps, plugin path)."
        ),
        "button_text": "Edit user config",
    },
    "global_settings": {
        "title": "Edit global settings",
        "text": ("Edit the global application settings (e.g. multiprocessing)."),
        "button_text": "Edit global settings",
    },
    "eiger_mask": {
        "title": "Export Eiger mask from master file",
        "text": (
            "Get the mask file for the Eiger detector from a Hdf5 master file written "
            "by the Eiger detector and export it as image."
        ),
        "button_text": "Export Eiger mask",
    },
    "mask_editor": {
        "title": "Edit detector mask",
        "text": (
            "Edit the detector mask: Import an image and add mask regions based on "
            "threshold selections, polygons, etc. This utility is an integrated version"
            " of the silx MaskToolsWidget."
        ),
        "button_text": "Edit detector mask",
    },
    "series_operations": {
        "title": "Image series operations",
        "text": (
            "Perform mathematical operations (e.g. sum, mean, max) on a series of "
            "images and save the results to a new single image."
        ),
        "button_text": "Image series operations",
    },
    "composite_creation": {
        "title": "Create composite image",
        "text": "Compose mosaic images of a large number of individual image files.",
        "button_text": "Create composite image",
    },
}


class UtilitiesFrameBuilder(BaseFrame):
    """
    Create all widgets and initialize their state.

    Parameters
    ----------
    self : pydidas.gui.DefineScanFrame
        The DefineScanFrame instance.
    """

    GROUP_WIDTH = 320
    GRID_NUM = 3

    def __init__(self, parent=None, **kwargs):
        BaseFrame.__init__(self, parent, **kwargs)
        self.setMinimumWidth(self.GRID_NUM * (self.GROUP_WIDTH + 10))

    def build_frame(self):
        """
        Create all widgets for the frame and place them in the layout.
        """
        self.create_label(
            "label_title",
            "Utilities\n",
            fontsize=constants.STANDARD_FONT_SIZE + 4,
            bold=True,
            gridPos=(0, 0, 1, 1),
            fixedWidth=self.GROUP_WIDTH,
        )

        for _index, (_key, _entries) in enumerate(UTILITIES.items()):
            _xpos = _index % self.GRID_NUM
            _ypos = _index // self.GRID_NUM + 1
            self.create_empty_widget(
                f"utility_{_key}",
                gridPos=(_ypos, _xpos, 1, 1),
                fixedWidth=self.GROUP_WIDTH,
                fixedHeight=170,
            )
            self.create_label(
                f"title_{_key}",
                _entries["title"],
                gridPos=(0, 0, 1, 1),
                parent_widget=self._widgets[f"utility_{_key}"],
                fontSize=constants.STANDARD_FONT_SIZE + 2,
                fixedWidth=self.GROUP_WIDTH - 20,
                bold=True,
            )
            self.create_label(
                f"text_{_key}",
                _entries["text"],
                gridPos=(1, 0, 1, 1),
                parent_widget=self._widgets[f"utility_{_key}"],
                fixedWidth=self.GROUP_WIDTH - 20,
                fontSize=constants.STANDARD_FONT_SIZE,
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
                alignment=constants.ALIGN_BOTTOM_LEFT,
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
