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
The main_gui module includes a function to run the GUI.
"""

__author__ = "Malte Storm"
__copyright__ = "Copyright 2021, Malte Storm, Helmholtz-Zentrum Hereon"
__license__ = "GPL-3.0"
__version__ = "0.0.1"
__maintainer__ = "Malte Storm"
__status__ = "Development"
__all__ = []

import sys

from PyQt5 import QtWidgets
import numpy as np


from pydidas.gui import (
    DataBrowsingFrame,  WorkflowEditFrame, PyfaiCalibFrame, HomeFrame,
    ExperimentalSetupFrame, ScanSetupFrame, ExecuteWorkflowFrame,
    CompositeCreatorFrame, get_pyfai_calib_icon, MainWindow)
from pydidas.widgets import BaseFrame


class ProcessingSetupFrame(BaseFrame):
    show_frame = False
    def __init__(self, **kwargs):
        parent = kwargs.get('parent', None)
        super().__init__(parent)


class ToolsFrame(BaseFrame):
    show_frame = False
    def __init__(self, **kwargs):
        parent = kwargs.get('parent', None)
        super().__init__(parent)


def run_gui(qtapp):
    """
    Run the GUI application with the generic pydidas layout.

    Parameters
    ----------
    qtapp : QtWidgets.QApplication
        The QApplication instance.
    """
    gui = MainWindow()
    gui.register_frame(HomeFrame, 'Home','Home', 'qta::mdi.home')
    gui.register_frame(DataBrowsingFrame, 'Data browsing', 'Data browsing',
                       'qta::mdi.image-search-outline')
    gui.register_frame(ToolsFrame, 'Tools', 'Tools' , 'qta::mdi.tools')
    gui.register_frame(PyfaiCalibFrame, 'pyFAI calibration',
                       'Tools/pyFAI calibration', get_pyfai_calib_icon())
    gui.register_frame(CompositeCreatorFrame, 'Composite image creator',
                       'Tools/Composite image creator', 'qta::mdi.view-comfy')
    gui.register_frame(ProcessingSetupFrame, 'Processing setup',
                       'Processing setup', 'qta::mdi.cogs')
    gui.register_frame(ExperimentalSetupFrame, 'Experimental settings',
                       'Processing setup/Experimental settings',
                       'qta::mdi.card-bulleted-settings-outline')
    gui.register_frame(ScanSetupFrame, 'Scan settings',
                       'Processing setup/Scan settings', 'qta::ei.move')
    gui.register_frame(WorkflowEditFrame, 'Workflow editing',
                       'Processing setup/Workflow editing',
                       'qta::mdi.clipboard-flow-outline')
    gui.register_frame(ExecuteWorkflowFrame, 'Run full processing',
                       'Run full procesing', 'qta::mdi.sync')
    # gui.register_frame(ResultVisualizationFrame, 'Result visualization',
    #                    'Result visualization', 'qta::mdi.monitor-eye')
    gui.show()
    gui.raise_()
    sys.exit(app.exec_())
    gui.deleteLater()


if __name__ == '__main__':
    #### temporary insert to speed up opening and testing
    import pickle

    from pydidas.core import Dataset
    from pydidas.experiment import ExperimentalSetup, ScanSetup
    from pydidas.workflow import WorkflowResults, WorkflowTree

    EXP = ExperimentalSetup()
    EXP.import_from_file('H:/myPython/pydidas/tests_of_workflow/__calib.poni')

    SCAN = ScanSetup()
    SCAN.import_from_file(
        'H:/myPython/pydidas/tests_of_workflow/__scan_settings.yaml')

    TREE = WorkflowTree()
    TREE.import_from_file(
        'H:/myPython/pydidas/tests_of_workflow/__workflow_new.yaml')

    RESULTS = WorkflowResults()
    RESULTS.__dict__ = pickle.load(
        open('d:/tmp/saved_results/results.pickle', 'rb'))
    for _i in [1, 2]:
        _data = Dataset(np.load(f'd:/tmp/saved_results/node_{_i:02d}.npy'))
        _meta = pickle.load(
            open(f'd:/tmp/saved_results/node_{_i:02d}.pickle', 'rb'))
        _data.axis_labels = _meta['axis_labels']
        _data.axis_units = _meta['axis_units']
        _data.axis_ranges = _meta['axis_ranges']
        RESULTS._WorkflowResults__composites[_i] = _data
    #### end insert

    app = QtWidgets.QApplication(sys.argv)
    run_gui(app)
    app.deleteLater()
