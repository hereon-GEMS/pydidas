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

"""Module with the ProcessingTestFrame which allows to test the processing
workflow and individual plugins on a single file."""

__author__      = "Malte Storm"
__copyright__   = "Copyright 2021, Malte Storm, Helmholtz-Zentrum Hereon"
__license__ = "GPL-3.0"
__version__ = "0.0.0"
__maintainer__ = "Malte Storm"
__status__ = "Development"
__all__ = ['ProcessingSinglePluginFrame']

from PyQt5 import QtWidgets, QtCore

from silx.gui.plot.StackView import StackView

from .base_frame import BaseFrame
from ..core import ScanSettings, Parameter
from ..workflow_tree import WorkflowTree
from ..widgets import ReadOnlyTextWidget, CreateWidgetsMixIn
from ..widgets.param_config import ParameterConfigMixIn

SCAN_SETTINGS = ScanSettings()
WORKFLOW_TREE = WorkflowTree()

_params = {
    'plugins': Parameter('Plugins', str, default='', refkey='plugins',
                         choices=['', 'HdfLoader (node 0)',
                                  'BackgroundCorrection (node 1) test test test test test test test6',
                                  'AzimuthalIntegration (node 2)']),
    'image_nr': Parameter('Image number', int, default=0, refkey='image_nr'),
    'scan_index1': Parameter('Scan dim. 1 index', int, default=0,
                             refkey='scan_index1'),
    'scan_index2': Parameter('Scan dim. 2 index', int, default=0,
                             refkey='scan_index2'),
    'scan_index3': Parameter('Scan dim. 3 index', int, default=0,
                             refkey='scan_index3'),
    'scan_index4': Parameter('Scan dim. 4 index', int, default=0,
                             refkey='scan_index4'),
    }


class LargeStackView(StackView):
    """
    Reimplementation of the silx StackView with a larger sizeHint.
    """
    def sizeHint(self):
        return QtCore.QSize(500, 1000)

class ProcessingSinglePluginFrame(BaseFrame, ParameterConfigMixIn,
                                  CreateWidgetsMixIn):
    def __init__(self, **kwargs):
        parent = kwargs.get('parent', None)
        BaseFrame.__init__(self, parent)
        ParameterConfigMixIn.__init__(self)
        self.params = _params
        self._plugin = None
        self.scan_dim = 4
        self.initWidgets()
        self.param_widgets['plugins'].currentTextChanged.connect(
            self.select_plugin)
        self.button_plugin_input.clicked.connect(self.click_plugin_input)
        self.button_plugin_exec.clicked.connect(self.click_execute_plugin)

    def initWidgets(self):
        _layout = self.layout()
        _layout.setHorizontalSpacing(10)
        _layout.setVerticalSpacing(5)

        self.create_label('Test of processing workflow', fontsize=14,
                              gridPos=(0, 0, 1, 5))
        self.create_spacer(height=10, gridPos=(self.next_row(), 0, 1, 2))
        self.create_label('Select image', fontsize=12,
                              gridPos=(self.next_row(), 0, 1, 2))
        self.create_spacer(height=10, gridPos=(self.next_row(), 0, 1, 2))

        # create button group for switching between
        _frame = QtWidgets.QFrame()
        _radio1 = QtWidgets.QRadioButton('Using image number', _frame)
        _radio2 = QtWidgets.QRadioButton('Using scan position', _frame)
        _radio1.setChecked(True)
        _layout.addWidget(_radio1, self.next_row(), 0, 1, 2)
        _layout.addWidget(_radio2, self.next_row(), 0, 1, 2)
        _radio1.toggled.connect(self.select_image_nr)
        _row = self.next_row()
        _iow = 40
        _txtw = 120
        self.create_param_widget(self.params['image_nr'], row=_row, width=_iow,
                              textwidth = _txtw)
        self.create_param_widget(self.params['scan_index1'], row=_row,
                              width=_iow, textwidth = _txtw)
        self.create_param_widget(self.params['scan_index2'], width=_iow,
                              textwidth = _txtw)
        self.create_param_widget(self.params['scan_index3'], width=_iow,
                              textwidth = _txtw)
        self.create_param_widget(self.params['scan_index4'], width=_iow,
                              textwidth = _txtw)
        self.create_spacer(height=20, gridPos=(self.next_row(), 0, 1, 2))
        for i in range(1, 5):
            self.param_widgets[f'scan_index{i}'].setVisible(False)
            self.param_textwidgets[f'scan_index{i}'].setVisible(False)
        self.create_label('Select plugin', fontsize=12, width=250,
                              gridPos=(self.next_row(), 0, 1, 2))

        self.create_param_widget(self.params['plugins'], n_columns=2, width=250,
                              n_columns_text=2, linebreak=True,
                              halign_text=QtCore.Qt.AlignLeft)

        self.w_plugin_info = ReadOnlyTextWidget(None, fixedWidth=250,
                                                fixedHeight=250)
        _layout.addWidget(self.w_plugin_info, self.next_row(), 0, 1, 2,
                          QtCore.Qt.AlignTop)

        self.button_plugin_input = self.create_button(
            'Show plugin input data', enabled=False,
            gridPos=(self.next_row(), 0, 1, 2))
        self.button_plugin_exec = self.create_button(
            'Execute plugin && show ouput data', enabled=False,
            gridPos=(self.next_row(), 0, 1, 2))
        self.create_spacer(height=20, gridPos=(self.next_row(), 0, 1, 2),
                        policy=QtWidgets.QSizePolicy.Expanding)
        self.w_output_data = QtWidgets.QStackedWidget(self)
        self.w_output_data.setSizePolicy(QtWidgets.QSizePolicy.Expanding,
                                         QtWidgets.QSizePolicy.Expanding)

        self.w_output_data.addWidget(LargeStackView())
        _layout.addWidget(self.w_output_data, 1, 3, _layout.rowCount(), 1)
        self.setup_stackview()

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
        self.button_plugin_input.setEnabled(True)
        self.button_plugin_exec.setEnabled(True)
        self.w_plugin_info.setText(text)
        ...

    def frame_activated(self, index):
        if index == self.frame_index:
            self.scan_dim = SCAN_SETTINGS.get('scan_dim')
            # _plugins = self.params['plugins']
            # _plugins.choices =
            _p_w = self.param_widgets['plugins']
            l = max([_p_w.view().fontMetrics().width(_p_w.itemText(i))
                     for i in range(_p_w.count())])
            _p_w.view().setMinimumWidth(l + 25)
            # TO DO :
            # disable buttons
