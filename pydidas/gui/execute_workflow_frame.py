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
Module with the ExecuteWorkflowFrame which allows to run the full
processing workflow and visualize the results.
"""

__author__      = "Malte Storm"
__copyright__   = "Copyright 2021, Malte Storm, Helmholtz-Zentrum Hereon"
__license__ = "GPL-3.0"
__version__ = "0.0.1"
__maintainer__ = "Malte Storm"
__status__ = "Development"
__all__ = ['ExecuteWorkflowFrame']

import time

import numpy as np
from PyQt5 import QtWidgets, QtCore
import qtawesome as qta

from pydidas.core import (ScanSettings, Parameter, get_generic_parameter,
                          ParameterCollection, ExperimentalSettings)
from pydidas.apps import ExecuteWorkflowApp
from pydidas.multiprocessing import AppRunner
from pydidas.workflow_tree import WorkflowTree, WorkflowResults
from pydidas.widgets import (ReadOnlyTextWidget, CreateWidgetsMixIn,
                             BaseFrameWithApp)
from pydidas.widgets.parameter_config import ParameterWidgetsMixIn
from pydidas.gui.builders.execute_workflow_frame_builder import (
    create_execute_workflow_frame_widgets_and_layout)
from pydidas.utils import timed_print


EXP = ExperimentalSettings()
SCAN = ScanSettings()
RESULTS = WorkflowResults()
TREE = WorkflowTree()

DEFAULT_PARAMS = ParameterCollection(
    get_generic_parameter('run_type'),
    get_generic_parameter('scan_index1'),
    get_generic_parameter('scan_index2'),
    get_generic_parameter('scan_index3'),
    get_generic_parameter('scan_index4'),
    )

SCAN.import_from_file('H:/myPython/pydidas/tests_of_workflow/__scan_settings.yaml')
EXP.import_from_file('H:/myPython/pydidas/tests_of_workflow/__calib.poni')
TREE.import_from_file('H:/myPython/pydidas/tests_of_workflow/__workflow_new.yaml')


import pickle
from pydidas.core import Dataset
RESULTS.__dict__ = pickle.load(open('d:/tmp/saved_results/results.pickle', 'rb'))
for _i in [1, 2]:
    _data = Dataset(np.load(f'd:/tmp/saved_results/node_{_i:02d}.npy'))
    _meta = pickle.load(open(f'd:/tmp/saved_results/node_{_i:02d}.pickle', 'rb'))
    _data.axis_labels = _meta['axis_labels']
    _data.axis_units = _meta['axis_units']
    _data.axis_ranges = _meta['axis_ranges']
    RESULTS._WorkflowResults__composites[_i] = _data


class ExecuteWorkflowFrame(BaseFrameWithApp, ParameterWidgetsMixIn,
                           CreateWidgetsMixIn):
    default_params = DEFAULT_PARAMS

    def __init__(self, **kwargs):
        parent = kwargs.get('parent', None)
        BaseFrameWithApp.__init__(self, parent)
        ParameterWidgetsMixIn.__init__(self)
        self._config = {}
        self._app = ExecuteWorkflowApp()
        self.__create_param_collection()
        self.set_default_params()
        create_execute_workflow_frame_widgets_and_layout(self)
        self.__connect_signals()
        self.__update_result_selection()

    def __create_param_collection(self):
        """
        Create the local ParameterCollection which is an updated
        CompositeCreatorApp collection.
        """
        self.add_params(self._app.params)
        self.add_param(get_generic_parameter('selected_results'))

        self.__update_choices_of_selected_results()

    def __connect_signals(self):
        self.param_widgets['autosave_results'].io_edited.connect(
            self.__update_autosave_widget_visibility)
        self._widgets['but_exec'].clicked.connect(self.__execute)
        self._widgets['but_abort'].clicked.connect(self.__abort_execution)
        # self._widgets['combo_results'].currentIndexChanged.connect(
        #     self.__result_selection_changed)
        self.param_widgets['selected_results'].currentIndexChanged.connect(
            self.__result_selection_changed)


    def __abort_execution(self):
        if self._runner is not None:
            self._runner.send_stop_signal()
        self.set_status('Aborted processing of full workflow.')
        self.__finish_processing()

    def __execute(self):
        """
        Execute the Application in the chosen type (GUI or command line).
        """
        if self.get_param_value('run_type') == 'Process in GUI':
            self._run_app()
        elif self.get_param_value('run_type') == 'Command line':
            self.__run_cmd_process()

    def _run_app(self):
        """
        Parallel implementation of the execution method.
        """
        import pydidas
        import logging
        logger = pydidas.utils.pydidas_logger()
        logger.setLevel(logging.DEBUG)

        logger.debug('Starting')
        self._prepare_app_run()
        logger.debug('Prepared app_run')
        self._app.multiprocessing_pre_run()
        logger.debug('Finished MP pre-run')
        self._config['last_update'] = time.time()
        self.__set_proc_widget_visibility_for_running(True)

        # self._widgets['but_exec'].setEnabled(False)
        # self._widgets['but_abort'].setVisible(True)
        # self._widgets['progress'].setVisible(True)
        self._widgets['progress'].setValue(0)
        self._runner = AppRunner(self._app)
        logger.debug('Created  AppRunner')
        self._runner.final_app_state.connect(self._set_app)
        self._runner.progress.connect(self._apprunner_update_progress)
        self._runner.finished.connect(self._apprunner_finished)
        self._runner.results.connect(
            self._app.multiprocessing_store_results)
        self._runner.results.connect(self.__update_result_selection)
        self._runner.start()
        logger.debug('Started AppRunner')

    def _prepare_app_run(self):
        """
        Do preparations for running the ExecuteWorkflowApp.

        This methods sets the required attributes both for serial and
        parallel running of the app.
        """
        self.set_status('Started processing of full workflow.')
        self.__clear_selected_results_entries()

    def __clear_selected_results_entries(self):
        self.set_param_value('selected_results', 'No selection')
        self.params['selected_results'].choices = ['No selection']
        self.toggle_param_widget_visibility('selected_results', False)
        self.param_widgets['selected_results'].update_choices(['No selection'])
        print('Combo text: ', self.param_widgets['selected_results'].currentText())

    @QtCore.pyqtSlot()
    def _apprunner_finished(self):
        """
        Clean up after AppRunner is done.
        """
        self.set_status('Cleaning up Apprunner')
        self._runner.exit()
        self._runner = None
        self.set_status('Finished processing of full workflow.')
        self.__finish_processing()

    @QtCore.pyqtSlot()
    def __update_result_selection(self):
        try:
            self._runner.results.disconnect(self.__update_result_selection)
        except AttributeError:
            pass
        self.param_widgets['selected_results'].currentIndexChanged.disconnect(
            self.__result_selection_changed)

        self.__update_choices_of_selected_results()
        self.toggle_param_widget_visibility('selected_results', True)
        self.param_widgets['selected_results'].update_choices(
            self.get_param('selected_results').choices)
        self.param_widgets['selected_results'].currentIndexChanged.connect(
            self.__result_selection_changed)



    def __finish_processing(self):
        self.__set_proc_widget_visibility_for_running(False)
        # self.__populate_results_combo()
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
        self._widgets['label_results'].setVisible(not running)
        self._widgets['combo_results'].setVisible(not running)
        self._widgets['but_abort'].setVisible(running)
        self._widgets['progress'].setVisible(running)
        self._widgets['but_show'].setEnabled(not running)
        self._widgets['but_save'].setEnabled(not running)

    def __populate_results_combo(self):
        """
        Populate the results QComboBox with entries for all WorkflowResults.
        """
        self._widgets['combo_results'].currentIndexChanged.disconnect()
        _combo = self._widgets['combo_results']
        _combo.clear()
        _combo.addItem('None')
        for _id, _label in RESULTS.labels.items():
            _combo.addItem(f'{_label} (node #{_id:03d})')
        _combo.setCurrentIndex(0)
        self._widgets['combo_results'].currentIndexChanged.connect(
            self.__result_selection_changed)



    @QtCore.pyqtSlot(int)
    def __result_selection_changed(self, index):
        """
        Received signal that the selection in the results combo box has
        changed.

        Parameters
        ----------
        index : int
            The new QComboBox selection index.
        """
        print('New index: ', index)
        print(f'Combo entry: "{self.param_widgets["selected_results"].currentText()}"')
        print(f'Param value: "{self.get_param_value("selected_results")}"')
        self.__update_text_description_of_node_results()

    def __update_text_description_of_node_results(self):
        # _txt = self._widgets['combo_results'].currentText()
        _txt = self.param_widgets["selected_results"].currentText()
        if _txt in ['None', 'No selection', '']:
            self._widgets['result_info'].setVisible(False)
            return
        self._widgets['result_info'].setVisible(True)
        print(_txt, _txt == '', _txt is None)
        _id = int(_txt[-4:-1])
        _meta = RESULTS.get_result_metadata(_id)
        _ax_labels = _meta['axis_labels']
        _ax_units= _meta['axis_units']
        _ax_ranges = _meta['axis_ranges']
        _txt = ''
        for _axis in _ax_labels:
            if isinstance(_ax_ranges[_axis], (np.ndarray, list, tuple)):
                _range = (f'{_ax_ranges[_axis][0]:.6f} .. '
                          f'{_ax_ranges[_axis][-1]:.6f} {_ax_units[_axis]}')
            else:
                _range = f'unknown range (unit: {_ax_units[_axis]}'
            _txt += (f'Axis #{_axis:02d}:\n'
                     f'  Label: {_ax_labels[_axis]}\n'
                     f'  Range: {_range}\n')
        self._widgets['result_info'].setText(_txt)

    def __run_cmd_process(self):
        # subprocess.Popen(executable, creationflags=subprocess.CREATE_NEW_PROCESS_GROUP | subprocess.DETACHED_PROCESS, close_fds=True)
        ...

    def __update_choices_of_selected_results(self):
        """
        Update the choices of the "selected_results" Parameter based on the
        latest WorkflowResults.
        """
        _curr_display = self.get_param_value('selected_results')
        _new_choices = (['No selection'] +
                        [f'{_val} (node #{_key:03d})'
                         for _key, _val in RESULTS.labels.items()])
        if _curr_display not in _new_choices:
            _curr_display = self.set_param_value('selected_results',
                                                 'No selection')
        self.params['selected_results'].choices = _new_choices




    def frame_activated(self, index):
        if index == self.frame_index:
            RESULTS.update_shapes_from_scan_and_workflow()
            self.__update_choices_of_selected_results()

    def __update_autosave_widget_visibility(self):
        _vis = self.get_param_value('autosave_results')
        for _key in ['autosave_dir', 'autosave_format']:
            self.toggle_param_widget_visibility(_key, _vis)



if __name__ == '__main__':
    import pydidas
    from pydidas.gui.main_window import MainWindow
    import sys
    import qtawesome as qta
    app = QtWidgets.QApplication(sys.argv)
    #app.setStyle('Fusion')

    # needs to be initialized after the app has been created.
    # sys.excepthook = pydidas.widgets.excepthook
    CENTRAL_WIDGET_STACK = pydidas.widgets.CentralWidgetStack()
    STANDARD_FONT_SIZE = pydidas.constants.STANDARD_FONT_SIZE



    _font = app.font()
    _font.setPointSize(STANDARD_FONT_SIZE)
    app.setFont(_font)
    gui = MainWindow()

    gui.register_frame('Test', 'Test', qta.icon('mdi.clipboard-flow-outline'), ExecuteWorkflowFrame)
    gui.create_toolbars()

    gui.show()
    sys.exit(app.exec_())

    app.deleteLater()
