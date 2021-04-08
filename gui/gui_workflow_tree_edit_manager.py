import numpy as np

from plugin_workflow_gui.plugin_collection import PluginCollection
from plugin_workflow_gui.config import gui_constants, qt_presets

from plugin_workflow_gui.workflow_tree.generic_tree import GenericNode
from plugin_workflow_gui.widgets import WorkflowPluginWidget
from PyQt5 import QtCore
PLUGIN_COLLECTION = PluginCollection()
#WorkflowTree = pwg.WorkflowTree()
PALETTES = qt_presets.PALETTES
STYLES = qt_presets.STYLES


class _GuiWorkflowTreeNode(GenericNode):
    generic_width = gui_constants.GENERIC_PLUGIN_WIDGET_WIDTH
    generic_height = gui_constants.GENERIC_PLUGIN_WIDGET_HEIGHT
    child_spacing = gui_constants.GENERIC_PLUGIN_WIDGET_Y_OFFSET
    border_spacing = gui_constants.GENERIC_PLUGIN_WIDGET_X_OFFSET

    def __init__(self, parent=None, node_id=None):
        super().__init__(parent=parent)
        self.node_id = node_id
        self._children = []
        if parent:
            parent.add_child(self)

    @property
    def width(self):
        if self.is_leaf():
            return self.generic_width
        w = (len(self._children) - 1) * self.child_spacing
        for child in self._children:
            w += child.width
        return w

    @property
    def height(self):
        if len(self._children) == 0:
            return self.generic_height
        h = []
        for child in self._children:
            h.append(child.height)
        return max(h) + self.child_spacing + self.generic_height

    def get_recursive_connections(self):
        conns = []
        for child in self._children:
            conns.append([self.node_id, child.node_id])
            conns += child.get_recursive_connections()
        return conns

    def get_recursive_ids(self):
        res = [self.node_id]
        if not self.is_leaf():
            for child in self._children:
                res += child.get_recursive_ids()
        return res

    def get_relative_positions(self):
        pos = {self.node_id: [(self.width - self.generic_width) // 2, 0]}
        if self.is_leaf():
            return pos
        xoffset = 0
        yoffset = self.generic_height + self.child_spacing
        for child in self._children:
            _p = child.get_relative_positions()
            for key in _p:
                pos.update({key: [_p[key][0] + xoffset,
                                  _p[key][1] + yoffset]})
            xoffset += child.width + self.child_spacing
        self.make_grid_positions_positive(pos)
        return pos

    @staticmethod
    def make_grid_positions_positive(pos_dict):
        vals = np.asarray(list(pos_dict.values()))
        xoffset = np.amin(vals[:, 0])
        yoffset = np.amin(vals[:, 1])
        for key in pos_dict:
            pos_dict[key] = [pos_dict[key][0] - xoffset,
                             pos_dict[key][1] - yoffset]


class _GuiWorkflowEditTreeManager(QtCore.QObject):
    plugin_to_edit = QtCore.pyqtSignal(int)
    pos_x_min = 5
    pos_y_min = 5

    def __init__(self, qt_canvas=None, qt_main=None):
        super().__init__()
        self.root = None
        self.qt_canvas= qt_canvas
        self.qt_main = qt_main

        self.node_pos = {}
        self.widgets = {}
        self.nodes = {}
        self.plugins = {}
        self.node_ids = []
        self.active_node = None
        self.active_node_id = None

    def update_qt_items(self, qt_canvas=None, qt_main=None):
        if qt_canvas:
            self.qt_canvas = qt_canvas
        if qt_main:
            self.qt_main = qt_main

    def add_plugin_node(self, name, title=None):
        if not self.root:
            _newid = 0
        else:
            _newid = self.node_ids[-1] + 1

        title = title if title else name
        widget = WorkflowPluginWidget(self.qt_canvas, self.qt_main, title, _newid)
        widget.setVisible(True)
        node = _GuiWorkflowTreeNode(self.active_node, _newid)
        if not self.root:
            self.root = node
        self.nodes[_newid] = node
        self.widgets[_newid] = widget
        self.plugins[_newid] = PLUGIN_COLLECTION.get_plugin_by_name(name)()
        self.node_ids.append(_newid)
        self.set_active_node(_newid)
        self.update_node_positions()
        self.qt_main.update()

    def update_node_positions(self):
        if not self.root:
            raise KeyError('No root node specified')
        _pos = self.root.get_relative_positions()
        _width = max(_pos.values())[0] + gui_constants.GENERIC_PLUGIN_WIDGET_WIDTH
        _offset = 0
        if _width < self.qt_main.params['workflow_edit_canvas_x']:
            _offset = (self.qt_main.params['workflow_edit_canvas_x'] - _width) // 2
        pos_vals = np.asarray(list(_pos.values()))
        pos_vals[:, 0] += - np.amin(pos_vals[:, 0]) + self.pos_x_min + _offset
        pos_vals[:, 1] += - np.amin(pos_vals[:, 1]) + self.pos_y_min
        self.node_pos = {}
        for i, key in enumerate(_pos):
            self.node_pos.update({key: pos_vals[i]})
        for node_id in self.node_ids:
            self.widgets[node_id].move(self.node_pos[node_id][0],
                                       self.node_pos[node_id][1])
        self.qt_canvas.setFixedSize(self.root.width + 2 * self.pos_x_min + _offset,
                                    self.root.height + 2 * self.pos_y_min)
        self.update_node_connections()

    def update_node_connections(self):
        node_conns = self.root.get_recursive_connections()
        widget_conns = []
        for node0, node1 in node_conns:
            x0 = self.node_pos[node0][0] + self.nodes[node1].generic_width // 2
            y0 = self.node_pos[node0][1] + self.nodes[node1].generic_height
            x1 = self.node_pos[node1][0] + self.nodes[node1].generic_width // 2
            y1 = self.node_pos[node1][1]
            widget_conns.append([x0, y0, x1, y1])
        self.qt_canvas.update_widget_connections(widget_conns)


    def set_active_node(self, node_id):
        for nid in self.widgets:
            if node_id == nid:
                self.widgets[nid].widget_select()
            else:
                self.widgets[nid].widget_deselect()
        self.active_node = self.nodes[node_id]
        self.active_node_id = node_id
        self.plugin_to_edit.emit(node_id)


    def delete_node(self, node_id):
        _all_ids = self.nodes[node_id].get_recursive_ids()
        self.nodes[node_id].delete_node()
        for _id in _all_ids:
            self.widgets[_id].deleteLater()
            del self.nodes[_id]
            del self.widgets[_id]
            del self.node_pos[_id]
            del self.plugins[_id]
        self.node_ids = [_id for _id in self.node_ids if _id not in _all_ids]
        self.update_node_connections()
        if len(self.node_ids) == 0:
            self.root = None
            self.active_node = None
            self.active_node_id = None
            return
        self.set_active_node(self.node_ids[-1])
        self.update_node_positions()


class _GuiWorkflowEditTreeManagerFactory:
    def __init__(self):
        self._instance = None

    def __call__(self, **kwargs):
        if not self._instance:
            self._instance = _GuiWorkflowEditTreeManager(**kwargs)
        return self._instance


GuiWorkflowEditTreeManager = _GuiWorkflowEditTreeManagerFactory()
