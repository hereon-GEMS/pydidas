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
__all__ = ['ProcessingFullWorkflowFrame']

from PyQt5 import QtWidgets, QtCore
import qtawesome as qta

from pydidas.core import (ScanSettings, Parameter, get_generic_parameter,
                          ParameterCollection)
from pydidas.workflow_tree import WorkflowTree
from pydidas.widgets import ReadOnlyTextWidget, CreateWidgetsMixIn, BaseFrame
from pydidas.widgets.parameter_config import ParameterConfigWidgetsMixIn
from pydidas.gui.builders.processing_full_workflow_frame_builder import (
    create_processing_full_workflow_frame_widgets_and_layout)

SCAN_SETTINGS = ScanSettings()
WORKFLOW_TREE = WorkflowTree()

DEFAULT_PARAMS = ParameterCollection(
    get_generic_parameter('run_type'),
    get_generic_parameter('scan_index1'),
    get_generic_parameter('scan_index2'),
    get_generic_parameter('scan_index3'),
    get_generic_parameter('scan_index4'),
    )


class ProcessingFullWorkflowFrame(BaseFrame, ParameterConfigWidgetsMixIn,
                                  CreateWidgetsMixIn):
    default_params = DEFAULT_PARAMS

    def __init__(self, **kwargs):
        parent = kwargs.get('parent', None)
        BaseFrame.__init__(self, parent)
        ParameterConfigWidgetsMixIn.__init__(self)
        self.set_default_params()
        self._plugin = None
        self.scan_dim = 4
        create_processing_full_workflow_frame_widgets_and_layout(self)

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
    STANDARD_FONT_SIZE = pydidas.constants.STANDARD_FONT_SIZE



    _font = app.font()
    _font.setPointSize(STANDARD_FONT_SIZE)
    app.setFont(_font)
    gui = MainWindow()

    gui.register_frame('Test', 'Test', qta.icon('mdi.clipboard-flow-outline'), ProcessingFullWorkflowFrame)
    gui.create_toolbars()

    gui.show()
    sys.exit(app.exec_())

    app.deleteLater()
