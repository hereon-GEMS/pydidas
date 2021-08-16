# This file is part of pydidas.

# pydidas is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.

# Foobar is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE. See the
# GNU General Public License for more details.

# You should have received a copy of the GNU General Public License
# along with Foobar.  If not, see <http://www.gnu.org/licenses/>.

"""Module with the CompositeCreatorFrameBuilder which is used to populate the
CompositeCreatorFrame with widgets."""

__author__      = "Malte Storm"
__copyright__   = "Copyright 2021, Malte Storm, Helmholtz-Zentrum Hereon"
__license__ = "GPL-3.0"
__version__ = "0.0.0"
__maintainer__ = "Malte Storm"
__status__ = "Development"
__all__ = ['CompositeCreatorFrameBuilder']

from PyQt5 import QtWidgets, QtCore

from silx.gui.plot import PlotWindow

from pydidas.widgets import (ScrollArea, create_default_grid_layout)
from pydidas.widgets.parameter_config import ParameterConfigWidget


class CompositeCreatorFrameBuilder:
    """
    Frame with Parameter setup for the CompositeCreatorApp and result
    visualization.
    """
    CONFIG_WIDGET_WIDTH = 300

    def __init__(self, composite_creator_frame):
        self.__ccf = composite_creator_frame
        self.init_widgets()

    def init_widgets(self):
        """
        Create all widgets and initialize their state.
        """
        self.__ccf._widgets = {}
        self.__ccf.layout().setContentsMargins(0, 0, 0, 0)

        self.__ccf._widgets['config'] = ParameterConfigWidget(
            self.__ccf, initLayout=False, lineWidth=5,
            sizePolicy= (QtWidgets.QSizePolicy.Fixed,
                         QtWidgets.QSizePolicy.Expanding))
        self.__ccf._widgets['config'].setLayout(create_default_grid_layout())

        self.__ccf.create_label(
            'title', 'Composite image creator', fontsize=14,
            gridPos=(0, 0, 1, 2), parent_widget=self.__ccf._widgets['config'],
            fixedWidth=self.CONFIG_WIDGET_WIDTH)

        self.__ccf.create_spacer('spacer1', gridPos=(-1, 0, 1, 2),
                                 parent_widget=self.__ccf._widgets['config'])

        self.__ccf.create_any_widget(
            'config_area', ScrollArea, widget=self.__ccf._widgets['config'],
            fixedWidth=self.CONFIG_WIDGET_WIDTH + 55,
            sizePolicy= (QtWidgets.QSizePolicy.Fixed,
                          QtWidgets.QSizePolicy.Expanding),
            gridPos=(-1, 0, 1, 1), stretch=(1, 0),
            layout_kwargs={'alignment': None})

        self.__ccf.create_button(
            'but_clear', 'Clear all entries', gridPos=(-1, 0, 1, 2),
            parent_widget=self.__ccf._widgets['config'],
            fixedWidth=self.CONFIG_WIDGET_WIDTH)

        _plot = PlotWindow(
            parent=self.__ccf, resetzoom=True, autoScale=False, logScale=False,
            grid=False, curveStyle=False, colormap=True, aspectRatio=True,
            yInverted=True, copy=True, save=True, print_=True, control=False,
            position=False, roi=False, mask=True)
        self.__ccf.add_any_widget(
            'plot_window', _plot, alignment=None,
            gridPos=(0, 3, 1, 1), visible=False, stretch=(1, 1),
            sizePolicy=(QtWidgets.QSizePolicy.Expanding,
                        QtWidgets.QSizePolicy.Expanding))

        for _key in self.__ccf.params:
            _options = self.__get_param_widget_config(_key)
            self.__ccf.create_param_widget(self.__ccf.params[_key], **_options)
            # self.__check_to_add_local_params(_key)

            # add spacers between groups:
            if _key in ['n_files', 'images_per_file', 'bg_hdf5_num',
                        'composite_dir', 'roi_yhigh', 'threshold_high',
                        'binning', 'output_fname', 'n_total']:
                self.__ccf.create_line(f'line_{_key}',
                    parent_widget=self.__ccf._widgets['config'],
                    fixedWidth=self.__ccf.CONFIG_WIDGET_WIDTH)

        self.__ccf.param_widgets['output_fname'].modify_file_selection(
            ['NPY files (*.npy *.npz)'])

        self.__ccf.create_button(
            'but_exec', 'Generate composite',
            parent_widget=self.__ccf._widgets['config'],
            gridPos=(-1, 0, 1, 2), enabled=False,
            fixedWidth=self.CONFIG_WIDGET_WIDTH)

        self.__ccf.create_progress_bar(
            'progress', parent_widget=self.__ccf._widgets['config'],
            gridPos=(-1, 0, 1, 2), visible=False,
            fixedWidth=self.CONFIG_WIDGET_WIDTH, minimum=0, maximum=100)

        self.__ccf.create_button(
            'but_abort', 'Abort composite creation',
            parent_widget=self.__ccf._widgets['config'],
            gridPos=(-1, 0, 1, 2), enabled=True, visible=False,
            fixedWidth=self.CONFIG_WIDGET_WIDTH)

        self.__ccf.create_button(
            'but_show', 'Show composite',
            parent_widget=self.__ccf._widgets['config'],
            gridPos=(-1, 0, 1, 2), enabled=False,
            fixedWidth=self.CONFIG_WIDGET_WIDTH)

        self.__ccf.create_button(
            'but_save', 'Save composite image',
            parent_widget=self.__ccf._widgets['config'],
            gridPos=(-1, 0, 1, 2), enabled=False,
            fixedWidth=self.CONFIG_WIDGET_WIDTH)

        self.__ccf.create_spacer(
            'spacer_bottom', parent_widget=self.__ccf._widgets['config'],
            gridPos=(-1, 0, 1, 2), policy = QtWidgets.QSizePolicy.Expanding,
            height=300)

        for _key in ['n_total', 'hdf5_dataset_shape', 'n_files',
                     'raw_image_shape', 'images_per_file']:
            self.__ccf.param_widgets[_key].setEnabled(False)
        for _key in ['hdf5_key', 'hdf5_first_image_num', 'hdf5_last_image_num',
                     'last_file','hdf5_stepping', 'hdf5_dataset_shape',
                     'hdf5_stepping']:
            self.__ccf.toggle_widget_visibility(_key, False)

        self.__ccf.toggle_widget_visibility('hdf5_dataset_shape', False)
        self.__ccf.toggle_widget_visibility('raw_image_shape', False)


    def __get_param_widget_config(self, param_key):
        """
        Get Formatting options for create_param_widget instances.
        """
        _config_next_row = self.__ccf._widgets['config'].next_row
        # special formatting for some parameters:
        if param_key in ['first_file', 'last_file', 'hdf5_key', 'bg_file',
                         'bg_hdf5_key', 'output_fname']:
            _config = dict(linebreak=True, n_columns=2, n_columns_text=2,
                           halign_text=QtCore.Qt.AlignLeft,
                           valign_text=QtCore.Qt.AlignBottom,
                           width=self.CONFIG_WIDGET_WIDTH,
                           width_text=self.CONFIG_WIDGET_WIDTH - 50,
                           parent_widget=self.__ccf._widgets['config'],
                           row=_config_next_row())
        else:
            _config = dict(width=100, row=_config_next_row(),
                           parent_widget=self.__ccf._widgets['config'],
                           width_text=self.CONFIG_WIDGET_WIDTH - 110)
        return _config
