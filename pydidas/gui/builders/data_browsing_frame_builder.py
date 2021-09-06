# This file is part of pydidas.

# pydidas is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.

# Pydidas is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE. See the
# GNU General Public License for more details.

# You should have received a copy of the GNU General Public License
# along with Pydidas. If not, see <http://www.gnu.org/licenses/>.

"""
Module with the create_data_browsing_frame_widgets_and_layout
function which is used to populate the DataBrowsingFrame with
widgets.
"""

__author__      = "Malte Storm"
__copyright__   = "Copyright 2021, Malte Storm, Helmholtz-Zentrum Hereon"
__license__ = "GPL-3.0"
__version__ = "0.0.0"
__maintainer__ = "Malte Storm"
__status__ = "Development"
__all__ = ['create_data_browsing_frame_widgets_and_layout']

from PyQt5 import QtWidgets, QtCore
import qtawesome as qta
from silx.gui.plot.ImageView import ImageView

from pydidas.widgets import (DirectoryExplorer, Hdf5DatasetSelector)


class ImageViewSmallHist(ImageView):
    """
    Subclass silx ImageView with a smaller historgram.
    """
    HISTOGRAMS_HEIGHT = 120

    def __init__(self):
        super().__init__()


def create_data_browsing_frame_widgets_and_layout(frame):
    """
    Create all widgets and initialize their state.

    Parameters
    ----------
    frame : pydidas.gui.DataBrowsingFrame
        The DataBrowsingFrame instance.
    """
    frame._widgets = {}
    frame.create_label(None, 'Data exploration view', fontsize=14)

    _bsize = 25
    frame._widgets['selection'] = QtWidgets.QFrame()
    frame._widgets['selection'].setSizePolicy(QtWidgets.QSizePolicy.Fixed,
                                              QtWidgets.QSizePolicy.Expanding)
    frame._widgets['selection'].setLayout(QtWidgets.QGridLayout())
    frame._widgets['selection'].layout().setRowStretch(0, 10)
    frame.create_any_widget('tree', DirectoryExplorer,
                            parent_widget=frame._widgets['selection'],
                            gridPos=(0, 0, 3, 1))
    frame.create_any_widget('hdf_dset', Hdf5DatasetSelector,
                            parent_widget=frame._widgets['selection'],
                            gridPos=(3, 0, 1, 1))
    frame.create_button(
        'but_minimize', '', icon=qta.icon('fa.chevron-left'),
        iconSize=QtCore.QSize(_bsize, _bsize), fixedHeight=_bsize,
        fixedWidth=_bsize, gridPos=(0, 1, 1, 1),
        parent_widget=frame._widgets['selection'])
    frame.create_button(
        'but_maximize', '', icon=qta.icon('fa.chevron-right'),
        iconSize=QtCore.QSize(_bsize, _bsize), fixedHeight=_bsize,
        fixedWidth=_bsize,gridPos=(2, 1, 1, 1),
        parent_widget=frame._widgets['selection'])

    frame._widgets['viewer'] = ImageViewSmallHist()
    frame._widgets['viewer'].setData = frame._widgets['viewer'].setImage
    frame._widgets['viewer'].setAttribute(QtCore.Qt.WA_DeleteOnClose)

    frame._widgets['hdf_dset'].register_view_widget(frame._widgets['viewer'])
    frame._widgets['splitter'] = QtWidgets.QSplitter()
    frame._widgets['splitter'].setSizePolicy(QtWidgets.QSizePolicy.Expanding,
                                             QtWidgets.QSizePolicy.Expanding)
    frame._widgets['splitter'].addWidget(frame._widgets['selection'])
    frame._widgets['splitter'].addWidget(frame._widgets['viewer'])
    frame.layout().addWidget(frame._widgets['splitter'])
