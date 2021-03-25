from PyQt5 import QtWidgets, QtCore
from plugin_workflow_gui.config import gui_constants, qt_presets

STYLES = qt_presets.STYLES

class WorkflowPluginWidget(QtWidgets.QLabel):
    """Widget with title and delete button for every selected plugin
    in the processing chain.
    """
    widget_width = gui_constants.GENERIC_PLUGIN_WIDGET_WIDTH
    widget_height = gui_constants.GENERIC_PLUGIN_WIDGET_HEIGHT

    def __init__(self, qt_parent=None, qt_main=None, title='No title',
                 widget_id=None):
        super().__init__(qt_parent)
        self.qt_parent = qt_parent
        self.qt_main = qt_main
        self.active = False
        if widget_id is None:
            raise ValueError('No plugin node id given.')

        self.widget_id = widget_id
        self.setText(title)

        self.setFixedSize(self.widget_width, self.widget_height)
        self.setAutoFillBackground(True)
        self.setAlignment(QtCore.Qt.AlignLeft | QtCore.Qt.AlignBottom)

        self.qtw_del_button = QtWidgets.QPushButton(self)
        self.qtw_del_button.setIcon(self.style().standardIcon(40))
        self.qtw_del_button.setGeometry(self.widget_width - 20, 2, 18, 18)
        for item in [self, self.qtw_del_button]:
            item.setStyleSheet(STYLES['workflow_plugin_inactive'])
        self.qtw_del_button.clicked.connect(self.delete)

    def mousePressEvent(self, event):
        event.accept()
        if not self.active:
            self.qt_main.workflow_edit_manager.set_active_node(self.widget_id)

    def delete(self):
        self.qt_main.workflow_edit_manager.delete_node(self.widget_id)

    def widget_select(self):
        self.setStyleSheet(STYLES['workflow_plugin_active'])
        self.active = True

    def widget_deselect(self):
        self.setStyleSheet(STYLES['workflow_plugin_inactive'])
        self.active = False
