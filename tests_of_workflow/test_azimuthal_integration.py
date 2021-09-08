# -*- coding: utf-8 -*-
"""
Created on Fri Apr  9 09:12:16 2021

@author: ogurreck
"""
import pydidas
import time
import h5py

TREE = pydidas.workflow_tree.WorkflowTree()
PLUGIN_COLL = pydidas.plugins.PluginCollection()

_pluginclass = PLUGIN_COLL.get_plugin_by_name('Hdf5fileSeriesLoader')
_inputplugin = _pluginclass(
    first_file='E:\p03data\calib_lab6_00001\eiger9m\calib_lab6_00001_data_000001.h5',
    last_file='E:\p03data\calib_lab6_00001\eiger9m\calib_lab6_00001_data_000006.h5',
    images_per_file=21)
_inputplugin.pre_execute()
_inputplugin.execute(21)

TREE.create_and_add_node(_inputplugin)
