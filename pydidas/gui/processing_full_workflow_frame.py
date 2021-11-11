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
from pydidas.apps import ExecuteWorkflowApp
from pydidas.workflow_tree import WorkflowTree
from pydidas.widgets import (ReadOnlyTextWidget, CreateWidgetsMixIn,
                             BaseFrameWithApp)
from pydidas.widgets.parameter_config import ParameterWidgetsMixIn
from pydidas.gui.builders.processing_full_workflow_frame_builder import (
    create_processing_full_workflow_frame_widgets_and_layout)

SCAN = ScanSettings()
WORKFLOW_TREE = WorkflowTree()

DEFAULT_PARAMS = ParameterCollection(
    get_generic_parameter('run_type'),
    get_generic_parameter('scan_index1'),
    get_generic_parameter('scan_index2'),
    get_generic_parameter('scan_index3'),
    get_generic_parameter('scan_index4'),
    )


class ProcessingFullWorkflowFrame(BaseFrameWithApp, ParameterWidgetsMixIn,
                                  CreateWidgetsMixIn):
    default_params = DEFAULT_PARAMS

    def __init__(self, **kwargs):
        parent = kwargs.get('parent', None)
        BaseFrameWithApp.__init__(self, parent)
        ParameterWidgetsMixIn.__init__(self)
        self._app = ExecuteWorkflowApp()
        self._create_param_collection()
        self.set_default_params()
        create_processing_full_workflow_frame_widgets_and_layout(self)
        self.__connect_signals()

    def _create_param_collection(self):
        """
        Create the local ParameterCollection which is an updated
        CompositeCreatorApp collection.
        """
        self.add_params(self._app.params)
        # for param in self._app.params.values():
        #     self.add_param(param)
        #     if param.refkey == 'hdf5_key':
        #         self.add_param(get_generic_parameter('hdf5_dataset_shape'))
        #     if param.refkey == 'file_stepping':
        #         self.add_param(get_generic_parameter('n_files'))
        #     if param.refkey == 'hdf5_stepping':
        #         self.add_param(get_generic_parameter('raw_image_shape'))
        #         self.add_param(get_generic_parameter('images_per_file'))
        #         self.add_param(
        #             Parameter('n_total', int, 0,
        #                       name='Total number of images',
        #                       tooltip=('The total number of images.')))

    def __connect_signals(self):
        self.param_widgets['autosave_results'].io_edited.connect(
            self.__update_autosave_widget_visibility)


    def frame_activated(self, index):
        ...

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

    gui.register_frame('Test', 'Test', qta.icon('mdi.clipboard-flow-outline'), ProcessingFullWorkflowFrame)
    gui.create_toolbars()

    gui.show()
    sys.exit(app.exec_())

    app.deleteLater()
