from PyQt5 import QtWidgets
from plugin_workflow_gui.config import gui_constants, qt_presets

PALETTES = qt_presets.PALETTES
STYLES = qt_presets.STYLES

class WorkflowPluginWidget(QtWidgets.QFrame):
    """Widget with title and delete button for every selected plugin
    in the processing chain.
    """
    widget_width = gui_constants.GENERIC_PLUGIN_WIDGET_WIDTH
    widget_height = gui_constants.GENERIC_PLUGIN_WIDGET_HEIGHT

    def __init__(self, qt_parent=None, qt_main=None, title='No title',
                 name=None, widget_id=None):
        super().__init__(qt_parent)
        self.qt_parent = qt_parent
        self.qt_main = qt_main
        self.active = False
        if not name:
            raise ValueError('No plugin name given.')
        if widget_id is None:
            raise ValueError('No plugin node id given.')

        self.widget_id = widget_id

        self.setFixedSize(self.widget_width, self.widget_height)
        self.setFrameStyle(QtWidgets.QFrame.Panel)
        self.setLineWidth(1)
        self.setAutoFillBackground(True)
        self.setStyleSheet(STYLES['workflow_plugin_inactive'])

        self.qtw_title = QtWidgets.QLabel(title, self)
        self.qtw_title.setStyleSheet(STYLES['workflow_plugin_title'])
        self.qtw_title.setGeometry(4, self.widget_height - 22,
                                   self.widget_width - 8, 20)

        self.qtw_del_button = QtWidgets.QPushButton(u'\u00D7', self)
        self.qtw_del_button.setGeometry(self.widget_width - 20, 2, 18, 18)
        self.qtw_del_button.setStyleSheet(STYLES['workflow_plugin_del_button'])
        self.qtw_del_button.clicked.connect(self.delete)

    def mousePressEvent(self, event):
        if not self.active:
            self.qt_main.workflow_edit_manager.set_active_node(self.widget_id)

    def delete(self):
        self.qt_main.workflow_edit_manager.delete_node(self.widget_id)
        #self.deleteLater()

    def widget_select(self):
        self.setLineWidth(2)
        self.setStyleSheet(STYLES['workflow_plugin_active'])
        self.setPalette(PALETTES['workflow_plugin_widget_active'])
        self.active = True

    def widget_deselect(self):
        self.setLineWidth(1)
        self.setStyleSheet(STYLES['workflow_plugin_inactive'])
        self.setPalette(PALETTES['workflow_plugin_widget'])
        self.active = False
