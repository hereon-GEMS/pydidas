# MIT License
#
# Copyright (c) 2021 Malte Storm, Helmholtz-Zentrum Hereon.
#
# Permission is hereby granted, free of charge, to any person obtaining a copy
# of this software and associated documentation files (the "Software"), to deal
# in the Software without restriction, including without limitation the rights
# to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
# copies of the Software, and to permit persons to whom the Software is
# furnished to do so, subject to the following conditions:
#
# The above copyright notice and this permission notice shall be included in all
# copies or substantial portions of the Software.

# THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
# IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
# FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
# AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
# LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
# OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE
# SOFTWARE.

"""Module with the ProcessingTestFrame which allows to test the processing
workflow and individual plugins on a single file."""

__author__      = "Malte Storm"
__copyright__   = "Copyright 2021, Malte Storm, Helmholtz-Zentrum Hereon"
__license__ = "MIT"
__version__ = "0.0.0"
__maintainer__ = "Malte Storm"
__status__ = "Development"
__all__ = ['ProcessingTestFrame']

from PyQt5 import QtWidgets, QtCore

from pydidas.gui.toplevel_frame import ToplevelFrame
from pydidas.core import ScanSettings, Parameter
from pydidas.workflow_tree import WorkflowTree
from pydidas.widgets.utilities import excepthook
from pydidas.widgets.param_config import ParamConfigMixIn

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


class ProcessingTestFrame(ToplevelFrame, ParamConfigMixIn):
    def __init__(self, **kwargs):
        parent = kwargs.get('parent', None)
        super().__init__(parent)
        self.params = _params
        self._plugin = None
        self.scan_dim = 4
        self.initWidgets()

    def initWidgets(self):
        _layout = self.layout()
        _layout.setHorizontalSpacing(10)
        _layout.setVerticalSpacing(5)

        self.add_label('Test of processing workflow', fontsize=14,
                       gridPos=(0, 0, 1, 4))
        self.add_spacer(height=30)
        self.add_label('Select image', fontsize=12,
                       gridPos=(self.next_row(), 0, 1, 4))
        self.add_spacer(height=10)

        # create button group for switching between
        _frame = QtWidgets.QFrame()
        _radio1 = QtWidgets.QRadioButton('Using image number', _frame)
        # _radio1.setMinimumWidth(180)
        _radio2 = QtWidgets.QRadioButton('Using scan position', _frame)
        # _radio2.setMinimumWidth(180)
        _radio1.setChecked(True)
        _layout.addWidget(_radio1, self.next_row(), 0, 1, 2)
        _layout.addWidget(_radio2, self.next_row(), 0, 1, 2)
        _radio1.toggled.connect(self.select_image_nr)
        _row = self.next_row()
        _iow = 40
        _txtw = 120
        self.add_param(self.params['image_nr'], row=_row, width=_iow,
                       textwidth = _txtw)
        self.add_param(self.params['scan_index1'], row=_row, width=_iow,
                       textwidth = _txtw)
        self.add_param(self.params['scan_index2'], width=_iow,
                       textwidth = _txtw)
        self.add_param(self.params['scan_index3'], width=_iow,
                       textwidth = _txtw)
        self.add_param(self.params['scan_index4'], width=_iow,
                       textwidth = _txtw)
        # for _r in range(_row, _row + 5):
        #     _layout.setRowMinimumHeight(_r, 25)
        for i in range(1, 5):
            self.param_widgets[f'scan_index{i}'].setVisible(False)
            self.param_txtwidgets[f'scan_index{i}'].setVisible(False)
        self.add_spacer(height=20)
        self.add_label('Select plugin', fontsize=12, width=200,
                       gridPos=(self.next_row(), 0, 1, 2))
        self.add_param(self.params['plugins'], n_columns=2, width=200,
                       n_columns_text=2, linebreak=True, align_text=QtCore.Qt.AlignLeft)
        self.param_widgets['plugins'].currentTextChanged.connect(
            self.select_plugin)

        self.button_plugin_input = self.add_button(
            'Show plugin input data', enabled=False,
            gridPos=(self.next_row(), 0, 1, 2))
        self.button_plugin_input.clicked.connect(self.click_plugin_input)
        self.button_plugin_exec = self.add_button(
            'Execute plugin', enabled=False,
            gridPos=(self.next_row(), 0, 1, 2))
        self.button_plugin_exec.clicked.connect(self.click_execute_plugin)


    def select_image_nr(self, active):
        self.param_widgets['image_nr'].setVisible(active)
        self.param_txtwidgets['image_nr'].setVisible(active)
        for i in range(1, 5):
            self.param_widgets[f'scan_index{i}'].setVisible(
                (not active) & (i <= self.scan_dim))
            self.param_txtwidgets[f'scan_index{i}'].setVisible(
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



if __name__ == '__main__':

    from pydidas.gui.main_window import MainWindow
    import pydidas.widgets
    from pydidas.config import STANDARD_FONT_SIZE
    import sys
    import qtawesome as qta
    sys.excepthook = pydidas.widgets.excepthook
    #app.setStyle('Fusion')

    # needs to be initialized after the app has been created.
    app = QtWidgets.QApplication(sys.argv)
#    CENTRAL_WIDGET_STACK = pydidas.widgets.CentralWidgetStack()



    _font = app.font()
    _font.setPointSize(STANDARD_FONT_SIZE)
    app.setFont(_font)
    gui = MainWindow()

    gui.register_frame('Test', 'Test', qta.icon('mdi.home'), ProcessingTestFrame)

    gui.show()
    sys.exit(app.exec_())

    app.deleteLater()