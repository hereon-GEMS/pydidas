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
Module with the create_processing_single_plugin_frame_widgets_and_layout
function which is used to populate the ProcessingSinglePluginFrame with
widgets.
"""

__author__      = "Malte Storm"
__copyright__   = "Copyright 2021, Malte Storm, Helmholtz-Zentrum Hereon"
__license__ = "GPL-3.0"
__version__ = "0.0.1"
__maintainer__ = "Malte Storm"
__status__ = "Development"
__all__ = ['create_processing_single_plugin_frame_widgets_and_layout']


from PyQt5 import QtWidgets, QtCore
from silx.gui.plot.StackView import StackView

from pydidas.widgets import ReadOnlyTextWidget
from pydidas.core import ScanSettings

SCAN_SETTINGS = ScanSettings()


class LargeStackView(StackView):
    """
    Reimplementation of the silx StackView with a larger sizeHint.
    """
    def sizeHint(self):
        return QtCore.QSize(500, 1000)


def create_processing_single_plugin_frame_widgets_and_layout(frame):
    """
    Create all widgets and initialize their state.

    Parameters
    ----------
    frame : pydidas.gui.ProcessingSinglePluginFrame
        The ProcessingSinglePluginFrame instance.
    """
    frame._widgets = {}
    _layout = frame.layout()
    _layout.setHorizontalSpacing(10)
    _layout.setVerticalSpacing(5)

    frame.create_label(None, 'Test of processing workflow', fontsize=14,
                          gridPos=(0, 0, 1, 5))
    frame.create_spacer(None, height=10, gridPos=(frame.next_row(), 0, 1, 2))
    frame.create_label(None, 'Select image', fontsize=12,
                          gridPos=(frame.next_row(), 0, 1, 2))
    frame.create_spacer(None, height=10, gridPos=(frame.next_row(), 0, 1, 2))

    # create button group for switching between
    _frame = QtWidgets.QFrame()
    _radio1 = QtWidgets.QRadioButton('Using image number', _frame)
    _radio2 = QtWidgets.QRadioButton('Using scan position', _frame)
    _radio1.setChecked(True)
    _layout.addWidget(_radio1, frame.next_row(), 0, 1, 2)
    _layout.addWidget(_radio2, frame.next_row(), 0, 1, 2)
    _radio1.toggled.connect(frame.select_image_nr)
    _row = frame.next_row()
    _iow = 40
    _txtw = 120
    frame.create_param_widget(frame.params['image_nr'], row=_row, width=_iow,
                          textwidth = _txtw)
    frame.create_param_widget(frame.params['scan_index1'], row=_row,
                          width=_iow, textwidth = _txtw)
    frame.create_param_widget(frame.params['scan_index2'], width=_iow,
                          textwidth = _txtw)
    frame.create_param_widget(frame.params['scan_index3'], width=_iow,
                          textwidth = _txtw)
    frame.create_param_widget(frame.params['scan_index4'], width=_iow,
                          textwidth = _txtw)
    frame.create_spacer(None, height=20, gridPos=(frame.next_row(), 0, 1, 2))
    for i in range(1, 5):
        frame.param_widgets[f'scan_index{i}'].setVisible(False)
        frame.param_textwidgets[f'scan_index{i}'].setVisible(False)
    frame.create_label(None, 'Select plugin', fontsize=12, width=250,
                       gridPos=(frame.next_row(), 0, 1, 2))

    frame.create_param_widget(frame.params['plugins'], n_columns=2, width=250,
                          n_columns_text=2, linebreak=True,
                          halign_text=QtCore.Qt.AlignLeft)

    frame.create_any_widget('plugin_info', ReadOnlyTextWidget,
                            fixedWidth=250, fixedHeight=250,
                            gridPos=(-1, 0, 1, 2), alignment=QtCore.Qt.AlignTop)

    frame.create_button('but_plugin_input', 'Show plugin input data',
                        enabled=False, gridPos=(-1, 0, 1, 2))
    frame.create_button('but_plugin_exec', 'Execute plugin && show ouput data',
                        enabled=False, gridPos=(-1, 0, 1, 2))
    frame.create_spacer(None, height=20, gridPos=(-1, 0, 1, 2),
                        policy=QtWidgets.QSizePolicy.Expanding)
    frame.w_output_data = QtWidgets.QStackedWidget(frame)
    frame.w_output_data.setSizePolicy(QtWidgets.QSizePolicy.Expanding,
                                     QtWidgets.QSizePolicy.Expanding)

    frame.w_output_data.addWidget(LargeStackView())
    _layout.addWidget(frame.w_output_data, 1, 3, _layout.rowCount(), 1)
