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
__all__ = ['ProcessingFullWorkflowFrame']

from PyQt5 import QtWidgets, QtCore
import qtawesome as qta

from pydidas.gui.base_frame import BaseFrame
from pydidas.core import ScanSettings, Parameter
from pydidas.workflow_tree import WorkflowTree
from pydidas.widgets import ReadOnlyTextWidget, CreateWidgetsMixIn
from pydidas.widgets.param_config import ParameterConfigMixIn

SCAN_SETTINGS = ScanSettings()
WORKFLOW_TREE = WorkflowTree()

_params = {
    'run_type': Parameter('Run type', str, default='Process in GUI', refkey='run_type',
                          choices=['Process in GUI', 'Command line', 'Remote command line']),
    'scan_index1': Parameter('Scan dim. 1 index', int, default=0,
                             refkey='scan_index1'),
    'scan_index2': Parameter('Scan dim. 2 index', int, default=0,
                             refkey='scan_index2'),
    'scan_index3': Parameter('Scan dim. 3 index', int, default=0,
                             refkey='scan_index3'),
    'scan_index4': Parameter('Scan dim. 4 index', int, default=0,
                             refkey='scan_index4'),
    }


class ProcessingFullWorkflowFrame(BaseFrame, ParameterConfigMixIn,
                                  CreateWidgetsMixIn):
    def __init__(self, **kwargs):
        parent = kwargs.get('parent', None)
        BaseFrame.__init__(self, parent)
        ParameterConfigMixIn.__init__(self)
        self.params = _params
        self._plugin = None
        self.scan_dim = 4
        self.initWidgets()
        # self.param_widgets['plugins'].currentTextChanged.connect(
        #     self.select_plugin)
        # self.button_plugin_input.clicked.connect(self.click_plugin_input)
        # self.button_plugin_exec.clicked.connect(self.click_execute_plugin)

    def initWidgets(self):
        _layout = self.layout()
        _layout.setHorizontalSpacing(10)
        _layout.setVerticalSpacing(5)

        self.create_label('Full processing workflow', fontsize=14,
                              gridPos=(0, 0, 1, 5))

        self.create_spacer(height=20, gridPos=(self.next_row(), 0, 1, 2))
        self.w_verify_cfg = self.create_button('Verify all settings', gridPos=(self.next_row(), 0, 1, 2), icon=qta.icon('mdi.text-search'))

        self.create_spacer(height=20, gridPos=(self.next_row(), 0, 1, 2))
        self.create_param_widget(self.params['run_type'])

        self.create_spacer(height=20, gridPos=(self.next_row(), 0, 1, 2))
        self.w_run = self.create_button('Run', gridPos=(self.next_row(), 0, 1, 2), icon=qta.icon('fa5s.play'))

        self.create_spacer(height=50, gridPos=(self.next_row(), 0, 1, 2))
        self.w_run = self.create_button('Processing feedback', gridPos=(self.next_row(), 0, 2, 4))
        self.w_run.setFixedHeight(200)
        self.w_run.setFixedWidth(600)


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
        ...


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
    STANDARD_FONT_SIZE = pydidas.config.STANDARD_FONT_SIZE



    _font = app.font()
    _font.setPointSize(STANDARD_FONT_SIZE)
    app.setFont(_font)
    gui = MainWindow()

    gui.register_frame('Test', 'Test', qta.icon('mdi.clipboard-flow-outline'), ProcessingFullWorkflowFrame)
    gui.create_toolbars()

    gui.show()
    sys.exit(app.exec_())

    app.deleteLater()
