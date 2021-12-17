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
Module with the ProcessingSinglePluginFrame which allows to test the processing
workflow and individual plugins on a single file.
"""

__author__ = "Malte Storm"
__copyright__ = "Copyright 2021, Malte Storm, Helmholtz-Zentrum Hereon"
__license__ = "GPL-3.0"
__version__ = "0.0.1"
__maintainer__ = "Malte Storm"
__status__ = "Development"
__all__ = ['ProcessingSinglePluginFrame']

from PyQt5 import QtCore

from pydidas.core import (Parameter, ParameterCollection,
                          get_generic_param_collection)
from pydidas.experiment import ScanSetup
from pydidas.workflow import WorkflowTree
from pydidas.widgets import  BaseFrame
from pydidas.gui.builders import ProcessingSinglePlugin_FrameBuilder


SCAN_SETTINGS = ScanSetup()
WORKFLOW_TREE = WorkflowTree()
_plugin_param = Parameter(
    'plugins', str, '', name='Plugins',
    choices=['', 'HdfLoader (node 0)', 'BackgroundCorrection (node 1)',
             'AzimuthalIntegration (node 2)'])

class ProcessingSinglePluginFrame(BaseFrame,
                                  ProcessingSinglePlugin_FrameBuilder):
    """
    The ProcessingSinglePluginFrame allows to run / test single plugins on a
    single datapoint.
    """
    default_params = ParameterCollection(
        _plugin_param,  get_generic_param_collection(
            'image_num', 'scan_index1', 'scan_index2', 'scan_index3',
            'scan_index4'))

    def __init__(self, **kwargs):
        parent = kwargs.get('parent', None)
        BaseFrame.__init__(self, parent)
        ProcessingSinglePlugin_FrameBuilder.__init__(self)
        self.set_default_params()
        self._plugin = None
        self.scan_dim = 4
        self.build_frame()
        self.setup_stackview()
        self.connect_signals()

    def connect_signals(self):
        """
        Connect all required signals and slots.
        """
        self._widgets['select_number'].new_button_index.connect(
            self.__use_scan_pos_for_selection)
        self.param_widgets['plugins'].currentTextChanged.connect(
            self.selected_plugin)
        self._widgets['but_plugin_input'].clicked.connect(
            self.click_plugin_input)
        self._widgets['but_plugin_exec'].clicked.connect(
            self.click_execute_plugin)


    def setup_stackview(self):
        """
        Dummy method to fill the stackview with browsable data.
        """
        import numpy
        a, b, c = numpy.meshgrid(numpy.linspace(-10, 10, 200),
                                 numpy.linspace(-10, 5, 150),
                                 numpy.linspace(-5, 10, 120),
                                 indexing="ij")
        mystack = numpy.asarray(numpy.sin(a * b * c) / (a * b * c),
                                dtype='float32')
        # linear calibrations (a, b), x -> a + bx
        dim0_calib = (-10., 20. / 200.)
        dim1_calib = (-10., 15. / 150.)
        dim2_calib = (-5., 15. / 120.)
        sv = self._widgets['data_output'].widget(0)
        sv.setColormap("jet", autoscale=True)
        sv.setStack(mystack,
                    calibrations=[dim0_calib, dim1_calib, dim2_calib])
        sv.setLabels(["dim0: -10 to 10 (200 samples)",
                      "dim1: -10 to 5 (150 samples)",
                      "dim2: -5 to 10 (120 samples)"])

    @QtCore.pyqtSlot(int)
    def __use_scan_pos_for_selection(self, use_scan_pos):
        """
        Get the signal to use scan position or image number for selection
        and process it.

        Parameters
        ----------
        use_scan_pos : int
            The signal if the choice of scan position is to be used.
        """
        self.param_composite_widgets['image_num'].setVisible(not use_scan_pos)
        for i in range(1, 5):
            self.param_composite_widgets[f'scan_index{i}'].setVisible(
                use_scan_pos & (i <= self.scan_dim))

    def update_plugin_list(self):
        ...

    def click_plugin_input(self):
        ...

    def click_execute_plugin(self):
        ...

    @QtCore.pyqtSlot(str)
    def selected_plugin(self, text):
        """
        Perform all required steps after a new plugin has been selected-

        Parameters
        ----------
        text : str
            The name of the selected plugin.
        """
        self._widgets['but_plugin_input'].setEnabled(True)
        self._widgets['but_plugin_exec'].setEnabled(True)
        self._widgets['plugin_info'].setText(text)
        ...

    @QtCore.pyqtSlot(int)
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
            self.scan_dim = SCAN_SETTINGS.get_param_value('scan_dim')
            _p_w = self.param_widgets['plugins']
            l = max([_p_w.view().fontMetrics().width(_p_w.itemText(i))
                     for i in range(_p_w.count())])
            _p_w.view().setMinimumWidth(l + 25)
            # TODO :
            # disable buttons
