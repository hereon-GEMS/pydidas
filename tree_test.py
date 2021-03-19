# -*- coding: utf-8 -*-
"""
Created on Thu Mar 11 10:24:52 2021

@author: ogurreck
"""

import sys
import inspect
import os
import numpy as np
#from qtpy import QtWidgets, QtGui, QtCore
from PyQt5 import QtWidgets, QtGui, QtCore, Qt

p = 'h:/myPython'
if not p in sys.path:
    sys.path.insert(0, p)

import plugin_workflow_gui as pwg


PLUGIN_COLLECTION = pwg.PluginCollection()
WorkflowTree = pwg.WorkflowTree()

WorkflowTree.set_root('test root', PLUGIN_COLLECTION.plugins['input']['HdfLoader']())
WorkflowTree.add_node('test c1', PLUGIN_COLLECTION.plugins['proc']['BackgroundCorrection']())
# WorkflowTree.add_node('test c2', PLUGIN_COLLECTION.plugins['proc']['BackgroundCorrection'](), node_id=1)
WorkflowTree.add_node('test c2', PLUGIN_COLLECTION.plugins['proc']['BackgroundCorrection'](), parent=WorkflowTree.nodes[0])

# a.add_child(pwg.WorkflowNode(name='test c1', plugin=PLUGIN_COLLECTION.plugins['proc']['BackgroundCorrection']()))
# a.add_child(pwg.WorkflowNode(name='test c2', plugin=PLUGIN_COLLECTION.plugins['proc']['BackgroundCorrection']()))
# a._children[0].add_child(pwg.WorkflowNode(name='test c2-1', plugin=PLUGIN_COLLECTION.plugins['proc']['AzimuthalIntegration']()))

print(WorkflowTree.nodes)

#WorkflowTree.delete_node(1)
#print(WorkflowTree.nodes)
#print(WorkflowTree.nodes[0])


WorkflowTree.nodes[0].execute_plugin_chain(6)

print(WorkflowTree.find_nodes_by_plugin_key('plugin_type', 1))