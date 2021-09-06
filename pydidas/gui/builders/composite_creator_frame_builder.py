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
Module with the create_composite_creator_frame_widgets_and_layout function
which is used to populate the CompositeCreatorFrame with widgets.
"""

__author__      = "Malte Storm"
__copyright__   = "Copyright 2021, Malte Storm, Helmholtz-Zentrum Hereon"
__license__ = "GPL-3.0"
__version__ = "0.0.0"
__maintainer__ = "Malte Storm"
__status__ = "Development"
__all__ = ['create_composite_creator_frame_widgets_and_layout']

from PyQt5 import QtWidgets, QtCore

from silx.gui.plot import PlotWindow

from pydidas.widgets import (ScrollArea, create_default_grid_layout)
from pydidas.widgets.parameter_config import ParameterConfigWidget


CONFIG_WIDGET_WIDTH = 300

def create_composite_creator_frame_widgets_and_layout(frame):
    """
    Create all widgets and initialize their state.

    Parameters
    ----------
    frame : pydidas.gui.CompositeCreatorFrame
        The CompositeCreatorFrame instance.
    """
    def __get_param_widget_config(param_key):
        """
        Get Formatting options for create_param_widget instances.
        """
        _config_next_row = frame._widgets['config'].next_row
        # special formatting for some parameters:
        if param_key in ['first_file', 'last_file', 'hdf5_key', 'bg_file',
                         'bg_hdf5_key', 'output_fname']:
            _config = dict(linebreak=True, n_columns=2, n_columns_text=2,
                           halign_text=QtCore.Qt.AlignLeft,
                           valign_text=QtCore.Qt.AlignBottom,
                           width=CONFIG_WIDGET_WIDTH,
                           width_text=CONFIG_WIDGET_WIDTH - 50,
                           parent_widget=frame._widgets['config'],
                           row=_config_next_row())
        else:
            _config = dict(width=100, row=_config_next_row(),
                           parent_widget=frame._widgets['config'],
                           width_text=CONFIG_WIDGET_WIDTH - 110)
        return _config

    frame._widgets = {}
    frame.layout().setContentsMargins(0, 0, 0, 0)

    frame._widgets['config'] = ParameterConfigWidget(
        frame, initLayout=False, lineWidth=5,
        sizePolicy= (QtWidgets.QSizePolicy.Fixed,
                     QtWidgets.QSizePolicy.Expanding))
    frame._widgets['config'].setLayout(create_default_grid_layout())

    frame.create_label(
        'title', 'Composite image creator', fontsize=14,
        gridPos=(0, 0, 1, 2), parent_widget=frame._widgets['config'],
        fixedWidth=CONFIG_WIDGET_WIDTH)

    frame.create_spacer('spacer1', gridPos=(-1, 0, 1, 2),
                             parent_widget=frame._widgets['config'])

    frame.create_any_widget(
        'config_area', ScrollArea, widget=frame._widgets['config'],
        fixedWidth=CONFIG_WIDGET_WIDTH + 55,
        sizePolicy= (QtWidgets.QSizePolicy.Fixed,
                      QtWidgets.QSizePolicy.Expanding),
        gridPos=(-1, 0, 1, 1), stretch=(1, 0),
        layout_kwargs={'alignment': None})

    frame.create_button(
        'but_clear', 'Clear all entries', gridPos=(-1, 0, 1, 2),
        parent_widget=frame._widgets['config'],
        fixedWidth=CONFIG_WIDGET_WIDTH)

    _plot = PlotWindow(
        parent=frame, resetzoom=True, autoScale=False, logScale=False,
        grid=False, curveStyle=False, colormap=True, aspectRatio=True,
        yInverted=True, copy=True, save=True, print_=True, control=False,
        position=False, roi=False, mask=True)
    frame.add_any_widget(
        'plot_window', _plot, alignment=None,
        gridPos=(0, 3, 1, 1), visible=False, stretch=(1, 1),
        sizePolicy=(QtWidgets.QSizePolicy.Expanding,
                    QtWidgets.QSizePolicy.Expanding))

    for _key in frame.params:
        _options = __get_param_widget_config(_key)
        frame.create_param_widget(frame.params[_key], **_options)

        # add spacers between groups:
        if _key in ['n_files', 'images_per_file', 'bg_hdf5_num',
                    'composite_dir', 'roi_yhigh', 'threshold_high',
                    'binning', 'output_fname', 'n_total']:
            frame.create_line(f'line_{_key}',
                parent_widget=frame._widgets['config'],
                fixedWidth=frame.CONFIG_WIDGET_WIDTH)

    frame.param_widgets['output_fname'].modify_file_selection(
        ['NPY files (*.npy *.npz)'])

    frame.create_button(
        'but_exec', 'Generate composite',
        parent_widget=frame._widgets['config'],
        gridPos=(-1, 0, 1, 2), enabled=False,
        fixedWidth=CONFIG_WIDGET_WIDTH)

    frame.create_progress_bar(
        'progress', parent_widget=frame._widgets['config'],
        gridPos=(-1, 0, 1, 2), visible=False,
        fixedWidth=CONFIG_WIDGET_WIDTH, minimum=0, maximum=100)

    frame.create_button(
        'but_abort', 'Abort composite creation',
        parent_widget=frame._widgets['config'],
        gridPos=(-1, 0, 1, 2), enabled=True, visible=False,
        fixedWidth=CONFIG_WIDGET_WIDTH)

    frame.create_button(
        'but_show', 'Show composite',
        parent_widget=frame._widgets['config'],
        gridPos=(-1, 0, 1, 2), enabled=False,
        fixedWidth=CONFIG_WIDGET_WIDTH)

    frame.create_button(
        'but_save', 'Save composite image',
        parent_widget=frame._widgets['config'],
        gridPos=(-1, 0, 1, 2), enabled=False,
        fixedWidth=CONFIG_WIDGET_WIDTH)

    frame.create_spacer(
        'spacer_bottom', parent_widget=frame._widgets['config'],
        gridPos=(-1, 0, 1, 2), policy = QtWidgets.QSizePolicy.Expanding,
        height=300)

    for _key in ['n_total', 'hdf5_dataset_shape', 'n_files',
                 'raw_image_shape', 'images_per_file']:
        frame.param_widgets[_key].setEnabled(False)
    for _key in ['hdf5_key', 'hdf5_first_image_num', 'hdf5_last_image_num',
                 'last_file','hdf5_stepping', 'hdf5_dataset_shape',
                 'hdf5_stepping']:
        frame.toggle_widget_visibility(_key, False)

    frame.toggle_widget_visibility('hdf5_dataset_shape', False)
    frame.toggle_widget_visibility('raw_image_shape', False)
