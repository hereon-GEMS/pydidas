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
Module with the WorkflowTestFrameBuilder class used to populate the
the WorkflowTestFrame with widgets.
"""

__author__ = "Malte Storm"
__copyright__ = "Copyright 2021-2022, Malte Storm, Helmholtz-Zentrum Hereon"
__license__ = "GPL-3.0"
__maintainer__ = "Malte Storm"
__status__ = "Development"
__all__ = ['WorkflowTestFrameBuilder']

from qtpy import QtWidgets, QtCore
from silx.gui.plot import Plot1D, Plot2D

from ...widgets import BaseFrame, ReadOnlyTextWidget, ScrollArea
from ...core.constants import(
    CONFIG_WIDGET_WIDTH, DEFAULT_TWO_LINE_PARAM_CONFIG)
from ...widgets.parameter_config import ParameterEditFrame


class WorkflowTestFrameBuilder(BaseFrame):
    """
    Class which includes the build_self method to populate the
    base class's UI and initialize all widgets.
    """
    def __init__(self, parent=None):
        BaseFrame.__init__(self, parent)
        _layout = self.layout()
        _layout.setHorizontalSpacing(10)
        _layout.setVerticalSpacing(5)

    def __param_widget_config(self, param_key):
        """
        Get Formatting options for create_param_widget calls.

        Parameters
        ----------
        param_key : str
            The Parameter reference key.

        Returns
        -------
        dict :
            The dictionary with the formatting options.
        """
        if param_key in ['image_selection']:
            _dict = dict(parent_widget=self._widgets['config'],
                         halign_text=QtCore.Qt.AlignLeft,
                         valign_text=QtCore.Qt.AlignBottom,
                         width_total=CONFIG_WIDGET_WIDTH,
                         width_io=170,
                         width_text=CONFIG_WIDGET_WIDTH - 180,
                         width_unit=0,
                         row=self._widgets['config'].next_row())
        elif param_key in ['selected_results']:
            _dict = DEFAULT_TWO_LINE_PARAM_CONFIG.copy()
            _dict.update({'parent_widget': self._widgets['config'],
                          'row': self._widgets['config'].next_row()})
        else:
            _dict = dict(parent_widget=self._widgets['config'],
                         width_io=100, width_unit=0,
                         width_text=CONFIG_WIDGET_WIDTH - 100,
                         width_total=CONFIG_WIDGET_WIDTH,
                         row=self._widgets['config'].next_row())
        if param_key in ['scan_index1', 'scan_index2', 'scan_index3',
                         'scan_index4']:
            _dict['visible'] = False
        return _dict

    def build_frame(self):
        """
        Build the frame and create all widgets.
        """
        self.create_label('title', 'Test workflow', fontsize=14, bold=True,
                           gridPos=(0, 0, 1, 1))

        self.create_spacer('title_spacer', height=20, gridPos=(1, 0, 1, 1))

        self._widgets['config'] = ParameterEditFrame(
            parent=None, init_layout=True, lineWidth=5,
            sizePolicy= (QtWidgets.QSizePolicy.Fixed,
                         QtWidgets.QSizePolicy.Expanding))

        self.create_spacer('spacer1', gridPos=(-1, 0, 1, 1),
                            parent_widget=self._widgets['config'])

        self.create_any_widget(
            'config_area', ScrollArea, widget=self._widgets['config'],
            fixedWidth=CONFIG_WIDGET_WIDTH + 40,
            sizePolicy= (QtWidgets.QSizePolicy.Fixed,
                         QtWidgets.QSizePolicy.Expanding),
            gridPos=(-1, 0, 1, 1), stretch=(1, 0),
            layout_kwargs={'alignment': None})

        for _param in ['image_selection', 'image_num', 'scan_index1',
                       'scan_index2', 'scan_index3', 'scan_index4']:
            self.create_param_widget(self.get_param(_param),
                                     **self.__param_widget_config(_param))

        self.create_line('line_selection', gridPos=(-1, 0, 1, 1),
                         parent_widget=self._widgets['config'])

        self.create_button(
            'but_exec', 'Process frame', gridPos=(-1, 0, 1, 1),
            fixedWidth=CONFIG_WIDGET_WIDTH,
            parent_widget=self._widgets['config'])

        self.create_line('line_results', gridPos=(-1, 0, 1, 1),
                         parent_widget=self._widgets['config'])

        self.create_label('label_results', 'Results:', fontsize=11,
                          underline=True, gridPos=(-1, 0, 1, 1),
                          parent_widget=self._widgets['config'])

        self.create_param_widget(
            self.get_param('selected_results'),
            **self.__param_widget_config('selected_results'))

        self.create_any_widget(
            'result_info',  ReadOnlyTextWidget, gridPos=(-1, 0, 1, 1),
            fixedWidth=CONFIG_WIDGET_WIDTH,fixedHeight=400,
            alignment=QtCore.Qt.AlignTop, visible=False,
            parent_widget=self._widgets['config'])

        self.create_spacer('config_terminal_spacer', height=20,
                           gridPos=(-1, 0, 1, 1),
                           parent_widget=self._widgets['config'])

        self.create_spacer('menu_bottom_spacer', height=20,
                           gridPos=(-1, 0, 1, 1))

        self._widgets['plot1d'] = Plot1D()
        self._widgets['plot1d'].getRoiAction().setVisible(False)
        self._widgets['plot1d'].getFitAction().setVisible(False)
        self._widgets['plot2d'] = Plot2D()
        self.add_any_widget(
            'plot_stack', QtWidgets.QStackedWidget(), alignment=None,
            gridPos=(0, 1, 3, 1), visible=True, stretch=(1, 1),
            sizePolicy=(QtWidgets.QSizePolicy.Expanding,
                        QtWidgets.QSizePolicy.Expanding))
        self._widgets['plot_stack'].addWidget(self._widgets['plot1d'])
        self._widgets['plot_stack'].addWidget(self._widgets['plot2d'])
