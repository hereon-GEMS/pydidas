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

"""Module with the ProcessingTestFrame which allows to test the processing
workflow and individual plugins on a single file."""

__author__      = "Malte Storm"
__copyright__   = "Copyright 2021, Malte Storm, Helmholtz-Zentrum Hereon"
__license__ = "GPL-3.0"
__version__ = "0.0.1"
__maintainer__ = "Malte Storm"
__status__ = "Development"
__all__ = ['ProcessingSinglePluginFrame']

from PyQt5 import QtWidgets, QtCore


from ..core import ScanSettings, Parameter, ParameterCollection
from ..workflow_tree import WorkflowTree
from ..widgets import ReadOnlyTextWidget, CreateWidgetsMixIn, BaseFrame
from ..widgets.parameter_config import ParameterConfigWidgetsMixIn
from .builders.processing_single_plugin_frame_builder import (
    create_processing_single_plugin_frame_widgets_and_layout)

SCAN_SETTINGS = ScanSettings()
WORKFLOW_TREE = WorkflowTree()

DEFAULT_PARAMS =  ParameterCollection(
    Parameter('Plugins', str, default='', refkey='plugins',
              choices=['', 'HdfLoader (node 0)',
                       'BackgroundCorrection (node 1) test test test test test test test6',
                       'AzimuthalIntegration (node 2)']),
    Parameter('Image number', int, default=0, refkey='image_nr'),
    Parameter('Scan dim. 1 index', int, default=0, refkey='scan_index1'),
    Parameter('Scan dim. 2 index', int, default=0, refkey='scan_index2'),
    Parameter('Scan dim. 3 index', int, default=0, refkey='scan_index3'),
    Parameter('Scan dim. 4 index', int, default=0, refkey='scan_index4'))

class ProcessingSinglePluginFrame(BaseFrame, ParameterConfigWidgetsMixIn,
                                  CreateWidgetsMixIn):

    default_params = DEFAULT_PARAMS

    def __init__(self, **kwargs):
        parent = kwargs.get('parent', None)
        BaseFrame.__init__(self, parent)
        ParameterConfigWidgetsMixIn.__init__(self)
        self.set_default_params()

        self._plugin = None
        self.scan_dim = 4
        create_processing_single_plugin_frame_widgets_and_layout(self)
        self.setup_stackview()
        self.param_widgets['plugins'].currentTextChanged.connect(
            self.select_plugin)
        self._widgets['but_plugin_input'].clicked.connect(self.click_plugin_input)
        self._widgets['but_plugin_exec'].clicked.connect(self.click_execute_plugin)

    def setup_stackview(self):
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

        # sv = StackView()
        sv = self.w_output_data.widget(0)
        sv.setColormap("jet", autoscale=True)
        sv.setStack(mystack,
                    calibrations=[dim0_calib, dim1_calib, dim2_calib])
        sv.setLabels(["dim0: -10 to 10 (200 samples)",
                      "dim1: -10 to 5 (150 samples)",
                      "dim2: -5 to 10 (120 samples)"])

    def select_image_nr(self, active):
        self.param_widgets['image_nr'].setVisible(active)
        self.param_textwidgets['image_nr'].setVisible(active)
        for i in range(1, 5):
            self.param_widgets[f'scan_index{i}'].setVisible(
                (not active) & (i <= self.scan_dim))
            self.param_textwidgets[f'scan_index{i}'].setVisible(
                (not active) & (i <= self.scan_dim))

        ...
    def update_plugin_list(self):
        ...

    def click_plugin_input(self):
        ...

    def click_execute_plugin(self):
        ...

    def select_plugin(self, text):
        self._widgets['but_plugin_input'].setEnabled(True)
        self._widgets['but_plugin_exec'].setEnabled(True)
        self.w_plugin_info.setText(text)
        ...

    def frame_activated(self, index):
        if index == self.frame_index:
            self.scan_dim = SCAN_SETTINGS.get_param_value('scan_dim')
            _p_w = self.param_widgets['plugins']
            l = max([_p_w.view().fontMetrics().width(_p_w.itemText(i))
                     for i in range(_p_w.count())])
            _p_w.view().setMinimumWidth(l + 25)
            # TODO :
            # disable buttons
