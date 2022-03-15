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
Module with the ImageMathFrameBuilder class which is used to populate
the ImageMathFrame with widgets.
"""

__author__ = "Malte Storm"
__copyright__ = "Copyright 2021-2022, Malte Storm, Helmholtz-Zentrum Hereon"
__license__ = "GPL-3.0"
__version__ = "0.1.1"
__maintainer__ = "Malte Storm"
__status__ = "Development"
__all__ = ['ImageMathFrameBuilder']

import qtawesome as qta
from qtpy import QtWidgets
from silx.gui.plot.ImageView import ImageView

from ...widgets import BaseFrame


class ImageMathFrameBuilder(BaseFrame):
    """
    Create all widgets and initialize their state.

    Parameters
    ----------
    self : pydidas.gui.ImageMathFrame
        The ImageMathFrame instance.
    """
    def __init__(self, parent=None):
        BaseFrame.__init__(self, parent)
        _layout = self.layout()
        _layout.setHorizontalSpacing(10)
        _layout.setVerticalSpacing(5)

    def build_frame(self):
        """
        Build the frame by creating all required widgets and placing them
        in the layout.
        """
        self.create_label('title', 'Image mathematics', fontsize=14,
                          gridPos=(0, 0, 1, 5))

        self.create_spacer(None, height=20, gridPos=(-1, 0, 1, 2))
        self.create_param_widget(self.params['buffer_no'], width_text=130,
                                 width=110)

        self.create_button('but_open', 'Open image', gridPos=(-1, 0, 1, 2),
                           icon=qta.icon('ei.folder-open'))

        self.create_button('but_operations', 'Image operations',
                           gridPos=(-1, 0, 1, 2), fixedWidth=270,
                           fixedHeight=400)

        self.create_spacer(None, height=20, gridPos=(-1, 0, 1, 2),
                           policy=QtWidgets.QSizePolicy.Expanding)

        self.add_any_widget('history', QtWidgets.QListWidget(None),
                            fixedWidth=270, fixedHeight=200,
                            gridPos=(-1, 0, 1, 2))

        self.add_any_widget('viewer',  ImageView(),
                            gridPos=(2, 2, self.layout().rowCount(), 1))
        _row = self.next_row()
        self.create_button('but_undo', 'Undo', gridPos=(_row, 0, 1, 1))
        self.create_button('but_redo', 'Redo', gridPos=(_row, 1, 1, 1))

        self._widgets['history'].addItem('Image #1 Operation 1')
        self._widgets['history'].addItem('Image #1 Operation 2')
        self._widgets['history'].addItem('Image #1 Operation 3')
