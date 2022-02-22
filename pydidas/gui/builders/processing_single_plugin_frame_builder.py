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
Module with the builder mixin class for the ProcessingSinglePluginFrame.
"""

__author__ = "Malte Storm"
__copyright__ = "Copyright 2021, Malte Storm, Helmholtz-Zentrum Hereon"
__license__ = "GPL-3.0"
__version__ = "0.1.0"
__maintainer__ = "Malte Storm"
__status__ = "Development"
__all__ = ['ProcessingSinglePluginFrameBuilder']

from qtpy import QtWidgets, QtCore
from silx.gui.plot.StackView import StackView

from ...experiment import ScanSetup
from ...widgets import BaseFrame, ReadOnlyTextWidget
from ...widgets.selection import RadioButtonGroup
from ...core.constants import CONFIG_WIDGET_WIDTH


SCAN_SETTINGS = ScanSetup()


class LargeStackView(StackView):
    """
    Reimplementation of the silx StackView with a larger sizeHint.
    """
    def sizeHint(self):
        return QtCore.QSize(500, 1000)


class ProcessingSinglePluginFrameBuilder(BaseFrame):
    """
    Mix-in class which includes the build_self method to populate the
    base class's UI and initialize all widgets.
    """
    def __init__(self, parent=None):
        BaseFrame.__init__(self, parent)
        _layout = self.layout()
        _layout.setHorizontalSpacing(10)
        _layout.setVerticalSpacing(0)
        _layout.setContentsMargins(0, 0, 0, 0)

    def build_frame(self):
        """
        Build the frame and create all required widgets.
        """
        _io_width = 40
        _txt_width = 120
        self.create_label(None, 'Test of processing workflow', fontsize=14,
                          gridPos=(0, 0, 1, 2))
        self.create_spacer(None, height=10, gridPos=(-1, 0, 1, 1))
        self.create_label(None, 'Select image', fontsize=12,
                          gridPos=(-1, 0, 1, 2), width=CONFIG_WIDGET_WIDTH)
        self.create_spacer(None, height=10, gridPos=(-1, 0, 1, 1))


        # create button group for switching between
        self.create_any_widget(
            'select_number', RadioButtonGroup, vertical=True,
            entries=['Image number', 'Scan position'],
            title='Select frame number using:', active=1,
            fixedWidth=CONFIG_WIDGET_WIDTH)
        self.create_param_widget(
            self.params['image_num'], width_io=_io_width,
            width_text =_txt_width, width_total=CONFIG_WIDGET_WIDTH)
        self.create_param_widget(
            self.params['scan_index1'], visible=False, width_io=_io_width,
            width_text=_txt_width, width_total=CONFIG_WIDGET_WIDTH)
        self.create_param_widget(
            self.params['scan_index2'], visible=False, width_io=_io_width,
            width_text=_txt_width, width_total=CONFIG_WIDGET_WIDTH)
        self.create_param_widget(
            self.params['scan_index3'], visible=False, width_io=_io_width,
            width_text=_txt_width, width_total=CONFIG_WIDGET_WIDTH)
        self.create_param_widget(
            self.params['scan_index4'], visible=False, width_io=_io_width,
            width_text=_txt_width, width_total=CONFIG_WIDGET_WIDTH)
        self.create_spacer(None, height=20, gridPos=(-1, 0, 1, 1))

        self.create_label('label_plugin', 'Select plugin', fontsize=12,
                          width=CONFIG_WIDGET_WIDTH, gridPos=(-1, 0, 1, 1))

        self.create_param_widget(
            self.params['plugins'], width_io=CONFIG_WIDGET_WIDTH-30,
            width_text=CONFIG_WIDGET_WIDTH-30, width_total=CONFIG_WIDGET_WIDTH,
            width_unit=0, linebreak=True, halign_text=QtCore.Qt.AlignLeft)

        self.create_any_widget(
            'plugin_info', ReadOnlyTextWidget, fixedWidth=CONFIG_WIDGET_WIDTH,
            fixedHeight=250, gridPos=(-1, 0, 1, 1),
            alignment=QtCore.Qt.AlignTop)

        self.create_button(
            'but_plugin_input', 'Show plugin input data', enabled=False,
            gridPos=(-1, 0, 1, 1), fixedWidth=CONFIG_WIDGET_WIDTH)
        self.create_button(
            'but_plugin_exec', 'Execute plugin && show ouput data',
            gridPos=(-1, 0, 1, 1), fixedWidth=CONFIG_WIDGET_WIDTH,
            enabled=False)
        self.create_spacer(None, height=20, gridPos=(-1, 0, 1, 1),
                           vertical_policy=QtWidgets.QSizePolicy.Expanding)
        _widget = QtWidgets.QStackedWidget()
        _widget.addWidget(LargeStackView())
        _widget.setSizePolicy(
            QtWidgets.QSizePolicy.Expanding, QtWidgets.QSizePolicy.Expanding)
        self.add_any_widget('data_output', _widget, stretch=(1, 1),
                            gridPos=(1, 1, self.layout().rowCount() - 1, 1))
