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

"""Module with the ExecuteWorkflowFrame which allows to run the full
processing workflow and visualize the results."""

__author__      = "Malte Storm"
__copyright__   = "Copyright 2021, Malte Storm, Helmholtz-Zentrum Hereon"
__license__ = "GPL-3.0"
__version__ = "0.0.1"
__maintainer__ = "Malte Storm"
__status__ = "Development"
__all__ = ['ExecuteWorkflowFrame']

import time


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

    def __create_param_collection(self):
        """
        Create the local ParameterCollection which is an updated
        CompositeCreatorApp collection.
        """
        self.add_params(self._app.params)
        self.add_param(Parameter('select_display', str, 'None'))
        self.__update_choices_of_select_display()

    def __connect_signals(self):
        self.param_widgets['autosave_results'].io_edited.connect(
            self.__update_autosave_widget_visibility)
        self._widgets['but_exec'].clicked.connect(self.__execute)
        self._widgets['but_abort'].clicked.connect(self.__abort_execution)

    def __abort_execution(self):
        if self._runner is not None:
            self._runner.send_stop_signal()
        self._widgets['but_abort'].setVisible(False)
        self._widgets['progress'].setVisible(False)
        self._widgets['but_exec'].setEnabled(True)
        self.set_status('Aborted processing of full workflow.')

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
        self._widgets['but_exec'].setEnabled(False)
        self._widgets['but_abort'].setVisible(True)
        self._widgets['progress'].setVisible(True)
        self._widgets['progress'].setValue(0)
        self._runner = AppRunner(self._app)
        logger.debug('Created  AppRunner')
        self._runner.final_app_state.connect(self._set_app)
        self._runner.progress.connect(self._apprunner_update_progress)
        self._runner.finished.connect(self._apprunner_finished)
        self._runner.results.connect(
            self._app.multiprocessing_store_results)
        self._runner.start()
        logger.debug('Started AppRunner')

    def _prepare_app_run(self):
        """
        Do preparations for running the ExecuteWorkflowApp.

        This methods sets the required attributes both for serial and
        parallel running of the app.
        """
        self.set_status('Started processing of full workflow.')

    @QtCore.pyqtSlot()
    def _apprunner_finished(self):
        """
        Clean up after AppRunner is done.
        """
        self._runner.exit()
        self._widgets['but_exec'].setEnabled(True)
        self._widgets['but_show'].setEnabled(True)
        self._widgets['but_save'].setEnabled(True)
        self._widgets['but_abort'].setVisible(False)
        self._widgets['progress'].setVisible(False)
        self.set_status('Finished processing of full workflow.')
        self._runner = None

    def __run_cmd_process(self):
        # subprocess.Popen(executable, creationflags=subprocess.CREATE_NEW_PROCESS_GROUP | subprocess.DETACHED_PROCESS, close_fds=True)
        ...

    def __update_choices_of_select_display(self):
        """
        Update the choices of the "select_display" Parameter based on the
        latest WorkflowResults.
        """
        _curr_display = self.get_param_value('select_display')
        _new_choices = (['None'] +
                        [f'{_val} (node #{_key:02d})'
                         for _key, _val in RESULTS.labels.items()])
        if _curr_display not in _new_choices:
            _curr_display = self.set_param_value('select_display', 'None')
        self.params['select_display'].choices = _new_choices


    def frame_activated(self, index):
        if index == self.frame_index:
            RESULTS.update_shapes_from_scan_and_workflow()
            self.__update_choices_of_select_display()

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
