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
Module with the ViewResultsFrame which allows to visualize results from
running the pydidas WorkflowTree.
"""

__author__ = "Malte Storm"
__copyright__ = "Copyright 2021-2022, Malte Storm, Helmholtz-Zentrum Hereon"
__license__ = "GPL-3.0"
__maintainer__ = "Malte Storm"
__status__ = "Development"
__all__ = ['ViewResultsMixin']

import time
import os

import numpy as np
from qtpy import QtCore, QtWidgets

from ...core import get_generic_param_collection
from ...core.utils import pydidas_logger
from ...widgets.dialogues import critical_warning
from ...workflow import WorkflowTree, WorkflowResults


RESULTS = WorkflowResults()


class ViewResultsMixin:
    """
    The ViewResultsMixin has all the necessary functionality to show and
    export results.

    It requires the following widgets which need to be created by the
    parent frame:

    - ResultSelectionWidget (referenced as self._widgets['result_selector'])
    - QStackedWidget with plots (referenced as self._widgets['plot_stack'])
    - silx Plot1D canvas (referenced as self._widgets['plot1d'])
    - silx Plot2D canvas (referenced as self._widgets['plot2d'])
    - ParameterWidget for the 'enable_overwrite' Parameter
    - ParameterWidget for the 'saving_format' Parameter
    - Button to export current node results
      (referenced as self._widgets['but_export_current'])
    - Button to export all node results
      (referenced as self._widgets['but_export_all'])

     It also requires the following Parameters which need to be created by
     the main class:
      - selected_results
      - saving_format
      - enable_overwrite
    """
    def __init__(self, **kwargs):
        self._config.update({'data_use_timeline': False,
                             'plot_dim': 2,
                             'plot_active': False,
                             'active_node': None,
                             'data_slices': (),
                             'frame_active': True,
                             'source_hash': RESULTS.source_hash})
        self._axlabels = lambda i: ''
        self.connect_view_results_mixin_signals()
        self._update_choices_of_selected_results()

    def connect_view_results_mixin_signals(self):
        """
        Connect all required Qt slots and signals.
        """
        self._widgets['but_export_current'].clicked.connect(
            self._export_current)
        self._widgets['but_export_all'].clicked.connect(
            self._export_all)
        self._widgets['result_selector'].new_selection.connect(
            self.update_result_selection)

    def _verify_result_shapes_uptodate(self):
        """
        Verify that the underlying information for the WorkflowResults
        (i.e. the ScanSetup and WorkflowTree) have not changed.
        """
        _hash = RESULTS.source_hash
        if _hash != self._config['source_hash']:
            RESULTS.update_shapes_from_scan_and_workflow()
            self._config['source_hash'] = RESULTS.source_hash
            self._clear_selected_results_entries()
            self._clear_plot()
            self._update_choices_of_selected_results()

    def _clear_selected_results_entries(self):
        """
        Clear the selection of the results and reset the view. This method
        will hide the data selection widgets.
        """
        self.set_param_value('selected_results', 'No selection')
        self.params['selected_results'].choices = ['No selection']
        self._widgets['result_selector'].reset()

    def _clear_plot(self):
        """
        Clear all curves / images from the plot and disable any new updates.
        """
        self._config['plot_active'] = False
        for _plot in [self._widgets['plot1d'], self._widgets['plot2d']]:
            for _item in _plot.getItems():
                _plot.removeItem(_item)

    @QtCore.Slot(bool, object, int, object, str)
    def update_result_selection(self, use_timeline, active_plot_dims,
                                  node_id, slices, plot_type):
        """
        Update the selection of results to show in the plot.

        Parameters
        ----------
        use_timeline : bool
            Flag whether to use a timeline and collapse all scan dimensions
            or not.
        active_plot_dims : list
            The dimensions of the plot results.
        node_id : int
            The result node ID.
        slices : tuple
            The tuple with the slices which select the data for plotting.
        plot_type : str
            The type of plot to be shown.
        """
        self._config['plot_active'] = True
        self._config['data_use_timeline'] = use_timeline
        self._config['active_dims'] = active_plot_dims
        self._config['active_node'] = node_id
        self._config['data_slices'] = slices
        self._config['plot_type'] = plot_type
        _datalength = np.asarray([_n.size for _n in slices])
        self._config['local_dims'] = {_val: _index for _index, _val in
                                      enumerate(np.where(_datalength > 1)[0])}
        self.update_plot()

    def update_plot(self):
        """
        Update the plot.

        This method will get the latest result (subset) from the
        WorkflowResults and update the plot.
        """
        if not self._config['plot_active']:
            return
        _dim = (1 if self._config['plot_type']
                in ['1D plot', 'roup of 1D plots'] else 2)
        _node = self._config['active_node']
        _data = RESULTS.get_result_subset(
            _node, self._config['data_slices'],
            flattened_scan_dim=self._config['data_use_timeline'],
            force_string_metadata=True)
        _data.axis_units = ['' if _unit is None else _unit
                            for _unit in _data.axis_units]
        self._axlabels = lambda i: (
            _data.axis_labels.copy()[i]
            + (' / ' + _data.axis_units.copy()[i]
               if len(str(_data.axis_units.copy())) > 0 else ''))
        if self._config['plot_type'] == 'group of 1D plots':
            self._widgets['plot_stack'].setCurrentIndex(0)
            self._plot_group_of_curves(_data)
        elif self._config['plot_type'] == '1D plot':
            self._widgets['plot_stack'].setCurrentIndex(0)
            self._plot1d(_data, replace=True)
        elif self._config['plot_type'] in ['2D full axes', '2D data subset']:
            self._widgets['plot_stack'].setCurrentIndex(1)
            self._plot_2d(_data)
        _plot = self._widgets[f'plot{_dim}d']
        _plot.setGraphTitle(RESULTS.labels[_node] + f' (node #{_node:03d})')

    def _plot_group_of_curves(self, data):
        """
        Plot a group of 1D curves.

        Parameters
        ----------
        data : pydidas.core.Dataset
            The dataset with the data to be plotted.
        """
        _active_dim = self._config['active_dims'][0]
        _local_dim = self._config['local_dims'][_active_dim]
        if _local_dim == 0:
            data = data.transpose()
        _legend = lambda i: (data.axis_labels[0] + '='
                             + f'{data.axis_ranges[0][i]:.4f}'
                             + data.axis_units[0])
        self._plot1d(data[0], replace=True, legend=_legend(0))
        for _index in range(1, data.shape[0]):
            self._plot1d(data[_index], replace=False, legend=_legend(_index),
                         label_dim=1)

    def _plot1d(self, data, replace=True, legend=None, label_dim=0):
        """
        Plot a 1D-dataset in the 1D plot widget.

        Parameters
        ----------
        data : pydidas.core.Dataset
            The data object.
        replace : bool, optional
            Keyword to toggle replacing the currently plotted lines or keep
            them and only add the new line. The default is True.
        legend : Union[None, str], optional
            If desired, a legend entry for this curve. If None, no legend
            entry will be added. The default is None.
        label_dim : int, optional
            The dimension of the X-axis label. For 1D-Datasets, this is 0.
            The default is 0.
        """
        _plot = self._widgets['plot1d']
        if not isinstance(data.axis_ranges[0], np.ndarray):
            data.axis_ranges[0] = np.arange(data.size)
        _plot.addCurve(data.axis_ranges[0], data.array, replace=replace,
                       linewidth=1.5, legend=legend)
        _plot.setGraphYLabel(RESULTS.data_labels[self._config['active_node']])
        _plot.setGraphXLabel(self._axlabels(label_dim))

    def _plot_2d(self, data):
        """
        Plot a 2D dataset as an image.

        Parameters
        ----------
        data : pydidas.core.Dataset
            The data.
        """
        _plot = self._widgets['plot2d']
        for _dim in [0, 1]:
            if not isinstance(data.axis_ranges[_dim], np.ndarray):
                data.axis_ranges[_dim] = np.arange(data.shape[_dim])
        _dim0, _dim1  = self._config['active_dims']
        if _dim0 > _dim1:
            data = data.transpose()
        _ax_label = lambda i: (
            data.axis_labels[i]
            + (' / ' + data.axis_units[i]
               if len(str(data.axis_units[i])) > 0 else ''))
        _originx, _scalex = self.__get_2d_plot_ax_settings(
            data.axis_ranges[1])
        _originy, _scaley = self.__get_2d_plot_ax_settings(
            data.axis_ranges[0])
        _plot.addImage(data, replace=True, copy=False,
                       origin=(_originx, _originy),
                       scale=(_scalex, _scaley))
        _plot.setGraphYLabel(_ax_label(0))
        _plot.setGraphXLabel(_ax_label(1))

    @staticmethod
    def __get_2d_plot_ax_settings(axis):
        """
        Get the

        Parameters
        ----------
        axis : np.ndarray
            The numpy array with the axis positions.

        Returns
        -------
        _origin : float
            The value for the axis origin.
        _scale : float
            The value for the axis scale to squeeze it into the correct
            dimensions for silx ImageView.
        """
        _delta = axis[1] - axis[0]
        _scale = (axis[-1] - axis[0] + _delta) / axis.size
        _origin = axis[0] - _delta / 2
        return _origin, _scale

    def _update_choices_of_selected_results(self):
        """
        Update the choices of the "selected_results" Parameter based on the
        latest WorkflowResults.
        """
        _param = self.get_param('selected_results')
        RESULTS.update_param_choices_from_labels(_param)
        self._widgets['result_selector'].get_and_store_result_node_labels()

    def _update_export_button_activation(self):
        """
        Update the enabled state of the export buttons based on available
        results.
        """
        _active = (RESULTS.shapes != {})
        self._widgets['but_export_current'].setEnabled(_active)
        self._widgets['but_export_all'].setEnabled(_active)

    @QtCore.Slot()
    def _export_current(self):
        """
        Export the current node's data to a WorkflowResults saver.
        """
        _node = self._widgets['result_selector']._active_node
        if _node == -1:
            critical_warning('No node selected',
                             ('No node has been selected. Please select a '
                              'node and try again.'))
            return
        self._export(_node)

    @QtCore.Slot()
    def _export_all(self):
        """
        Export all datasets to a WorkflowResults saver.
        """
        self._export(None)

    def _export(self, node):
        """
        Export data of

        Parameters
        ----------
        node : Union[None, int]
            The single node to be exported. If None, all nodes will be
            exported. The default is None.
        """
        _formats = self.get_param_value('saving_format')
        if _formats is None:
            critical_warning('No format selected',
                             ('No saving format node has been selected. '
                              'Please select a format and try again.'))
            return
        _overwrite = self.get_param_value('enable_overwrite')
        while True:
            _dirname = QtWidgets.QFileDialog.getExistingDirectory(
                self, 'Name of directory', None)
            if _dirname == '' or len(os.listdir(_dirname)) == 0 or _overwrite:
                break
            critical_warning('Directory not empty',
                             'The selected directory is not empty. Please '
                             'select an empty directory or cancel.')
        if _dirname == '':
            return
        RESULTS.save_results_to_disk(_dirname, _formats, overwrite=_overwrite,
                                     node_id=node)
