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
Module with the ExecuteWorkflowFrameBuilder class which is used to
populate the ExecuteWorkflowFrame with widgets.
"""

__author__ = "Malte Storm"
__copyright__ = "Copyright 2021-2022, Malte Storm, Helmholtz-Zentrum Hereon"
__license__ = "GPL-3.0"
__maintainer__ = "Malte Storm"
__status__ = "Development"
__all__ = ['ExecuteWorkflowFrameBuilder']

from qtpy import QtCore, QtWidgets
from silx.gui.plot import Plot1D, Plot2D

from ...core.constants import CONFIG_WIDGET_WIDTH
from ...widgets import ScrollArea, BaseFrameWithApp
from ...widgets.selection import ResultSelectionWidget
from ...widgets.parameter_config import ParameterEditFrame

class ExecuteWorkflowFrameBuilder(BaseFrameWithApp):
    """
    Mix-in class which includes the build_frame method to populate the
    base class's UI and initialize all widgets.
    """
    def __init__(self, parent=None):
        BaseFrameWithApp.__init__(self, parent)
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
        if param_key in ['autosave_dir', 'selected_results']:
            _dict = dict(linebreak=True,
                         parent_widget=self._widgets['config'],
                         halign_text=QtCore.Qt.AlignLeft,
                         valign_text=QtCore.Qt.AlignBottom,
                         width_total=CONFIG_WIDGET_WIDTH,
                         width_io=CONFIG_WIDGET_WIDTH - 50,
                         width_text=CONFIG_WIDGET_WIDTH - 20,
                         width_unit=0,
                         row=self._widgets['config'].next_row())
        else:
            _dict = dict(parent_widget=self._widgets['config'],
                         width_io=100, width_unit=0,
                         width_text=CONFIG_WIDGET_WIDTH - 100,
                         width_total=CONFIG_WIDGET_WIDTH,
                         row=self._widgets['config'].next_row())
        if param_key in ['autosave_dir', 'autosave_format']:
            _dict['visible'] = False
        return _dict

    def build_frame(self):
        """
        Build the frame and create all widgets.
        """
        self.create_label('title', 'Full workflow processing', fontsize=14,
                          bold=True, gridPos=(0, 0, 1, 5))

        self.create_spacer('title_spacer', height=20, gridPos=(1, 0, 1, 1))

        self._widgets['config'] = ParameterEditFrame(
            parent=None, init_layout=True, lineWidth=5,
            sizePolicy= (QtWidgets.QSizePolicy.Fixed,
                         QtWidgets.QSizePolicy.Expanding))

        self.create_spacer('spacer1', gridPos=(-1, 0, 1, 2),
                            parent_widget=self._widgets['config'])

        self.create_any_widget(
            'config_area', ScrollArea, widget=self._widgets['config'],
            fixedWidth=CONFIG_WIDGET_WIDTH + 40,
            sizePolicy= (QtWidgets.QSizePolicy.Fixed,
                         QtWidgets.QSizePolicy.Expanding),
            gridPos=(-1, 0, 1, 1), stretch=(1, 0),
            layout_kwargs={'alignment': None})

        for _param in ['autosave_results', 'autosave_dir', 'autosave_format']:
            self.create_param_widget(self.get_param(_param),
                                     **self.__param_widget_config(_param))

        self.create_line('line_autosave', gridPos=(-1, 0, 1, 1),
                         parent_widget=self._widgets['config'])

        self.create_button(
            'but_exec', 'Start processing', gridPos=(-1, 0, 1, 1),
            fixedWidth=CONFIG_WIDGET_WIDTH,
            parent_widget=self._widgets['config'])

        self.create_progress_bar(
            'progress', gridPos=(-1, 0, 1, 1), visible=False, minimum=0,
            maximum=100, fixedWidth=CONFIG_WIDGET_WIDTH,
            parent_widget=self._widgets['config'])

        self.create_button(
            'but_abort', 'Abort processing', gridPos=(-1, 0, 1, 1),
            enabled=True, visible=False, fixedWidth=CONFIG_WIDGET_WIDTH,
            parent_widget=self._widgets['config'])

        self.create_line('line_results', gridPos=(-1, 0, 1, 1),
                         parent_widget=self._widgets['config'])

        self.create_any_widget(
            'result_selector', ResultSelectionWidget,
            parent_widget=self._widgets['config'], gridpos=(-1, 0, 1, 1),
            select_results_param=self.get_param('selected_results'))

        self.create_line('line_export', gridPos=(-1, 0, 1, 1),
                         parent_widget=self._widgets['config'])

        self.create_param_widget(self.get_param('saving_format'),
                                 **self.__param_widget_config('saving_format'))
        self.create_param_widget(
            self.get_param('enable_overwrite'),
            **self.__param_widget_config('enable_overwrite'))
        self.create_button(
            'but_export_current', 'Export current node results',
            gridPos=(-1, 0, 1, 1), fixedWidth=CONFIG_WIDGET_WIDTH,
            parent_widget=self._widgets['config'], enabled=False,
            toolTip=("Export the current node's results to file. Note that "
                     "the filenames are pre-determined based on node ID "
                     "and node label."))

        self.create_button(
            'but_export_all', 'Export all results', enabled=False,
            gridPos=(-1, 0, 1, 1), fixedWidth=CONFIG_WIDGET_WIDTH,
            parent_widget=self._widgets['config'],
            tooltip=('Export all results. Note that the directory must be '
                     'empty.'))

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
