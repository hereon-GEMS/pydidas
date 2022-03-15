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
Module with the ExecuteWorkflowFrame which allows to run the full
processing workflow and visualize the results.
"""

__author__ = "Malte Storm"
__copyright__ = "Copyright 2021-2022, Malte Storm, Helmholtz-Zentrum Hereon"
__license__ = "GPL-3.0"
__version__ = "0.1.1"
__maintainer__ = "Malte Storm"
__status__ = "Development"
__all__ = ['ExecuteWorkflowFrame']

import time
import os

import numpy as np
from qtpy import QtCore, QtWidgets

from ..apps import ExecuteWorkflowApp
from ..core import get_generic_param_collection
from ..core.utils import pydidas_logger
from ..experiment import ExperimentalSetup, ScanSetup
from ..multiprocessing import AppRunner
from ..widgets.dialogues import critical_warning
from ..workflow import WorkflowTree, WorkflowResults
from .builders.execute_workflow_frame_builder import (
    ExecuteWorkflowFrameBuilder)


EXP = ExperimentalSetup()
SCAN = ScanSetup()
RESULTS = WorkflowResults()
TREE = WorkflowTree()
logger = pydidas_logger()


class ExecuteWorkflowFrame(ExecuteWorkflowFrameBuilder):
    """
    The ExecuteWorkflowFrame is used to start processing of the WorkflowTree
    and visualize the results.
    """
    default_params = get_generic_param_collection(
        'selected_results', 'saving_format', 'enable_overwrite')

    def __init__(self, **kwargs):
        parent = kwargs.get('parent', None)
        ExecuteWorkflowFrameBuilder.__init__(self, parent)
        _global_plot_update_time = self.q_settings_get_global_value(
            'plot_update_time', argtype=float)
        self._config = {'data_use_timeline': False,
                        'plot_dim': 2,
                        'plot_active': False,
                        'active_node': None,
                        'data_slices': (),
                        'plot_last_update': 0,
                        'plot_update_time': _global_plot_update_time,
                        'frame_active': True,
                        'source_hash': RESULTS.source_hash}
        self._axlabels = lambda i: ''
        self._app = ExecuteWorkflowApp()
        self.set_default_params()
        self.add_params(self._app.params)
        self.build_frame()
        self.connect_signals()
        self.__update_choices_of_selected_results()
        self.__update_result_node_information()

    def connect_signals(self):
        """
        Connect all required Qt slots and signals.
        """
        self.param_widgets['autosave_results'].io_edited.connect(
            self.__update_autosave_widget_visibility)
        self._widgets['but_exec'].clicked.connect(self.__execute)
        self._widgets['but_abort'].clicked.connect(self.__abort_execution)
        self._widgets['but_export_current'].clicked.connect(
            self.__export_current)
        self._widgets['but_export_all'].clicked.connect(
            self.__export_all)
        self._widgets['result_selector'].new_selection.connect(
            self.__update_result_selection)

    def __abort_execution(self):
        """
        Abort the execution of the AppRunner.
        """
        if self._runner is not None:
            self._runner.send_stop_signal()
        self.set_status('Aborted processing of full workflow.')
        self.__finish_processing()

    @QtCore.Slot()
    def __execute(self):
        """
        Execute the Application in the chosen type (GUI or command line).
        """
        self._verify_result_shapes_uptodate()
        self._run_app()

    def _verify_result_shapes_uptodate(self):
        """
        Verify that the underlying information for the WorkflowResults
        (i.e. the ScanSetup and WorkflowTree) have not changed.
        """
        _hash = RESULTS.source_hash
        if _hash != self._config['source_hash']:
            RESULTS.update_shapes_from_scan_and_workflow()
            self._config['source_hash'] = RESULTS.source_hash
            self.__clear_selected_results_entries()
            self.__clear_plot()
            self.__update_choices_of_selected_results()
            QtWidgets.QMessageBox.information(
                self, 'Results need to be updated',
                ('Underlying information for the WorkflowResults has changed '
                 'and the WorkflowResults must be updated. This will clear '
                 'all present results.\n'
                 'Either the WorkflowTree or the ScanSetup has been modified '
                 'and the consistency of the results cannot be guaranteed '
                 'without calculating them from scratch.'))

    def _run_app(self):
        """
        Parallel implementation of the execution method.
        """
        logger.debug('Starting workflow')
        self._prepare_app_run()
        self._app.multiprocessing_pre_run()
        self._config['last_update'] = time.time()
        self.__set_proc_widget_visibility_for_running(True)
        logger.debug('Starting AppRunner')
        self._runner = AppRunner(self._app)
        self._runner.sig_final_app_state.connect(self._set_app)
        self._runner.sig_progress.connect(self._apprunner_update_progress)
        self._runner.sig_finished.connect(self._apprunner_finished)
        self._runner.sig_results.connect(
            self._app.multiprocessing_store_results)
        self._runner.sig_results.connect(self.__update_result_node_information)
        self._runner.sig_results.connect(self.__check_for_plot_update)
        logger.debug('Running AppRunner')
        self._runner.start()

    def _prepare_app_run(self):
        """
        Do preparations for running the ExecuteWorkflowApp.

        This methods sets the required attributes both for serial and
        parallel running of the app.
        """
        self.set_status('Started processing of full workflow.')
        self._widgets['progress'].setValue(0)
        self.__clear_selected_results_entries()
        self.__clear_plot()

    def __clear_selected_results_entries(self):
        """
        Clear the selection of the results and reset the view. This method
        will hide the data selection widgets.
        """
        self.set_param_value('selected_results', 'No selection')
        self.params['selected_results'].choices = ['No selection']
        self._widgets['result_selector'].reset()

    def __clear_plot(self):
        """
        Clear all curves / images from the plot and disable any new updates.
        """
        self._config['plot_active'] = False
        for _plot in [self._widgets['plot1d'], self._widgets['plot2d']]:
            for _item in _plot.getItems():
                _plot.removeItem(_item)

    @QtCore.Slot()
    def _apprunner_finished(self):
        """
        Clean up after AppRunner is done.
        """
        self.set_status('Cleaning up Apprunner')
        logger.debug('Telling AppRunner to exit.')
        self._runner.exit()
        self._runner = None
        logger.debug('AppRunner successfully shut down.')
        self.set_status('Finished processing of full workflow.')
        self.__finish_processing()
        self._update_plot()

    @QtCore.Slot()
    def __update_result_node_information(self):
        """
        Update the information about the nodes' results after the AppRunner
        has sent the first results.
        """
        self._widgets['result_selector'].get_and_store_result_node_labels()
        try:
            self._runner.results.disconnect(
                self.__update_result_node_information)
        except AttributeError:
            pass

    @QtCore.Slot(bool, object, int, object, str)
    def __update_result_selection(self, use_timeline, active_plot_dims,
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
        self._update_plot()

    @QtCore.Slot()
    def __check_for_plot_update(self):
        _dt = time.time() - self._config['plot_last_update']
        if (_dt > self._config['plot_update_time']
                and self._config['frame_active']):
            self._config['plot_last_update'] = time.time()
            self._update_plot()

    def _update_plot(self):
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
        self._axlabels = lambda i: (
            _data.axis_labels.copy()[i]
            + (' / ' + _data.axis_units.copy()[i]
               if len(_data.axis_units.copy()) > 0 else ''))
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
            self._plot1d(data[_index], replace=False, legend=_legend(_index))

    def _plot1d(self, data, replace=True, legend=None):
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
        """
        _plot = self._widgets['plot1d']
        if not isinstance(data.axis_ranges[0], np.ndarray):
            data.axis_ranges[0] = np.arange(data.size)
        _plot.addCurve(data.axis_ranges[0], data.array, replace=replace,
                       linewidth=1.5, legend=legend)#, info=legend)
        _plot.setGraphYLabel(RESULTS.data_labels[self._config['active_node']])
        _plot.setGraphXLabel(self._axlabels(1))

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
               if len(data.axis_units[i]) > 0 else ''))
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

    @QtCore.Slot(int)
    def frame_activated(self, index):
        """
        Received a signal that a new frame has been selected.

        This method checks whether the selected frame is the current class
        and if yes, it will call some updates.

        Parameters
        ----------
        index : int
            The index of the newly activated frame.
        """
        if index == self.frame_index:
            self._verify_result_shapes_uptodate()
            self.__update_choices_of_selected_results()
            self.__check_for_plot_update()
        self._config['frame_active'] = (index == self.frame_index)

    def __finish_processing(self):
        """
        Perform finishing touches after the processing has terminated.
        """
        self.__set_proc_widget_visibility_for_running(False)
        self.__update_choices_of_selected_results()

    def __set_proc_widget_visibility_for_running(self, running):
        """
        Set the visibility of all widgets which need to be updated for/after
        procesing

        Parameters
        ----------
        running : bool
            Flag whether the AppRunner is running and widgets shall be shown
            accordingly or not.
        """
        self._widgets['but_exec'].setEnabled(not running)
        self._widgets['but_abort'].setVisible(running)
        self._widgets['progress'].setVisible(running)
        self._widgets['but_export_all'].setEnabled(not running)
        self._widgets['but_export_current'].setEnabled(not running)

    def __update_choices_of_selected_results(self):
        """
        Update the choices of the "selected_results" Parameter based on the
        latest WorkflowResults.
        """
        _param = self.get_param('selected_results')
        RESULTS.update_param_choices_from_labels(_param)

    def __update_autosave_widget_visibility(self):
        """
        Update the visibility of the autosave widgets based on the selection
        of the autosae_results Parameter.
        """
        _vis = self.get_param_value('autosave_results')
        for _key in ['autosave_dir', 'autosave_format']:
            self.toggle_param_widget_visibility(_key, _vis)

    @QtCore.Slot()
    def __export_current(self):
        """
        Export the current node's data to a WorkflowResults saver.
        """
        _node = self._widgets['result_selector']._active_node

        if _node == -1:
            critical_warning('No node selected',
                             ('No node has been selected. Please select a '
                              'node and try again.'))
            return
        self.__export(_node)

    @QtCore.Slot()
    def __export_all(self):
        """
        Export all datasets to a WorkflowResults saver.
        """
        self.__export(None)

    def __export(self, node):
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
