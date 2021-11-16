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
Module with the create_execute_workflow_frame_widgets_and_layout
function which is used to populate the ProcessingFullWorkflowFrame with
widgets.
"""

__author__      = "Malte Storm"
__copyright__   = "Copyright 2021, Malte Storm, Helmholtz-Zentrum Hereon"
__license__ = "GPL-3.0"
__version__ = "0.0.1"
__maintainer__ = "Malte Storm"
__status__ = "Development"
__all__ = ['create_execute_workflow_frame_widgets_and_layout']

from PyQt5 import QtCore, QtWidgets
from silx.gui.plot import PlotWindow

from pydidas.widgets import (ScrollArea, create_default_grid_layout)
from pydidas.widgets.parameter_config import ParameterCollectionEditWidget

CONFIG_WIDGET_WIDTH = 300


def create_execute_workflow_frame_widgets_and_layout(frame):
    """
    Create all widgets and initialize their state.

    Parameters
    ----------
    frame : pydidas.gui.ProcessingFullWorkflowFrame
        The ProcessingFullWorkflowFrame instance.
    """
    def __get_param_widget_config(param_key):
        """
        Get Formatting options for create_param_widget instances.
        """
        if param_key in ['autosave_dir', 'run_type']:
            return  dict(linebreak=True,
                         parent_widget=frame._widgets['io_frame'],
                         halign_text=QtCore.Qt.AlignLeft,
                         valign_text=QtCore.Qt.AlignBottom,
                         width_total=CONFIG_WIDGET_WIDTH,
                         width_io=CONFIG_WIDGET_WIDTH - 50,
                         width_text=CONFIG_WIDGET_WIDTH - 20,
                         width_unit=0,
                         row=frame._widgets['io_frame'].next_row())
        return dict(parent_widget=frame._widgets['io_frame'],
                    width_io=100, width_unit=0,
                    width_text=CONFIG_WIDGET_WIDTH - 100,
                    width_total=CONFIG_WIDGET_WIDTH,
                    row=frame._widgets['io_frame'].next_row())

    frame._widgets = {}
    _layout = frame.layout()
    _layout.setHorizontalSpacing(10)
    _layout.setVerticalSpacing(5)

    frame.create_label('title', 'Full processing workflow', fontsize=14,
                       gridPos=(0, 0, 1, 5))
    frame.create_spacer('title_spacer', height=20, gridPos=(1, 0, 1, 1))

    frame._widgets['io_frame'] = ParameterCollectionEditWidget(
        frame, initLayout=False, lineWidth=5,
        sizePolicy= (QtWidgets.QSizePolicy.Fixed,
                     QtWidgets.QSizePolicy.Expanding))
    frame._widgets['io_frame'].setLayout(create_default_grid_layout())
    _layout.addWidget(frame._widgets['io_frame'], 2, 0, 1, 1)

    frame.create_param_widget(frame.get_param('autosave_results'),
                              **__get_param_widget_config('autosave_results'))
    frame.create_param_widget(frame.get_param('autosave_dir'),
                              **__get_param_widget_config('autosave_dir'))
    frame.create_param_widget(frame.get_param('autosave_format'),
                              **__get_param_widget_config('autosave_format'))
    frame.create_param_widget(frame.get_param('run_type'),
                              **__get_param_widget_config('run_type'))
    for _key in ['autosave_dir', 'autosave_format']:
        frame.toggle_param_widget_visibility(_key, False)

    frame.create_spacer('runtype_spacer', height=20, gridPos=(-1, 0, 1, 1),
                        parent_widget=frame._widgets['io_frame'])

    frame.create_button('but_exec', 'Start processing', gridPos=(-1, 0, 1, 1),
                        fixedWidth=CONFIG_WIDGET_WIDTH,
                        parent_widget=frame._widgets['io_frame'])

    frame.create_progress_bar('progress', gridPos=(-1, 0, 1, 1), visible=False,
                              fixedWidth=CONFIG_WIDGET_WIDTH, minimum=0,
                              maximum=100,
                              parent_widget=frame._widgets['io_frame'])

    frame.create_button('but_abort', 'Abort processing',
                        gridPos=(-1, 0, 1, 1), enabled=True, visible=False,
                        fixedWidth=CONFIG_WIDGET_WIDTH,
                        parent_widget=frame._widgets['io_frame'])

    frame.create_button('but_show', 'Show composite', enabled=False,
                        gridPos=(-1, 0, 1, 1), fixedWidth=CONFIG_WIDGET_WIDTH,
                        parent_widget=frame._widgets['io_frame'])

    frame.create_button('but_save', 'Save composite image', enabled=False,
                        gridPos=(-1, 0, 1, 1), fixedWidth=CONFIG_WIDGET_WIDTH,
                        parent_widget=frame._widgets['io_frame'])

    frame.create_spacer('vis_spacer', height=20, gridPos=(-1, 0, 1, 1))

    _plot = PlotWindow(
        parent=frame, resetzoom=True, autoScale=False, logScale=False,
        grid=False, curveStyle=False, colormap=True, aspectRatio=True,
        yInverted=True, copy=True, save=True, print_=True, control=False,
        position=True, roi=False, mask=True)
    frame.add_any_widget(
        'plot_window', _plot, alignment=None,
        gridPos=(0, 1, 3, 1), visible=True, stretch=(1, 1),
        sizePolicy=(QtWidgets.QSizePolicy.Expanding,
                    QtWidgets.QSizePolicy.Expanding))

    # frame.create_spacer(None, height=20, gridPos=(-1, 0, 1, 2))
    # frame.create_param_widget(frame.params['run_type'])

    # frame.create_spacer(None, height=20, gridPos=(-1, 0, 1, 2))
    # frame.create_button('but_run', 'Run', gridPos=(-1, 0, 1, 2),
    #                     icon=qta.icon('fa5s.play'), fixedHeight=50,
    #                     fixedWidth=600)

    # frame.create_spacer(None, height=50, gridPos=(-1, 0, 1, 2))
    # frame.create_button('but_feedback', 'Processing feedback',
    #                     gridPos=(-1, 0, 1, 2))
