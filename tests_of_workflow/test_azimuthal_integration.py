# -*- coding: utf-8 -*-
"""
Created on Fri Apr  9 09:12:16 2021

@author: ogurreck
"""
import pydidas
import time
import h5py
import matplotlib.pyplot as plt
import numpy as np

EXP_SETTINGS = pydidas.core.ExperimentalSettings()
TREE = pydidas.workflow_tree.WorkflowTree()
PLUGIN_COLL = pydidas.plugins.PluginCollection()


EXP_SETTINGS.load_from_file('E:/p03data/calib_lab6_00001/pyfai_calib.poni')

_pluginclass = PLUGIN_COLL.get_plugin_by_name('Hdf5fileSeriesLoader')
_inputplugin = _pluginclass(
    first_file='E:\p03data\calib_lab6_00001\eiger9m\calib_lab6_00001_data_000001.h5',
    last_file='E:\p03data\calib_lab6_00001\eiger9m\calib_lab6_00001_data_000006.h5',
    images_per_file=21)
# _inputplugin.pre_execute()
# data = _inputplugin.execute(21)

_pluginclass = PLUGIN_COLL.get_plugin_by_name('pyFAIazimuthalIntegration')
_integrationplugin = _pluginclass()

TREE.create_and_add_node(_inputplugin)
TREE.create_and_add_node(_integrationplugin)


results = np.zeros((100, 1000))
raw_img = np.zeros((100, 3269, 3110))
for index in range(100):
    pydidas.utils.timed_print(f'Processing frame {index:03d}.')
    TREE.execute_process(index)
    xvalues, results[index] = TREE.nodes[1].results
    # raw_img[index], kwargs = TREE.execute_single_plugin(0, index)

_average = np.average(results, axis=0)
# plt.plot(xvalues, np.average(results, axis=0))

# with h5py.File('E:\p03data\calib_lab6_00001\eiger9m\calib_lab6_00001_data_000001.h5', 'r') as f:
#     _direct_data = f['entry/data/data'][...]

# mask = np.load('E:/p03data/calib_lab6_00001/p03_eiger_mask.npy')

# _masked = raw_img[0,:,:]
# _masked = np.where(mask, 0, _average)

# fig1 = plt.figure(figsize=(15, 8))
# fig1a = plt.subplot(131)
# fig1b = plt.subplot(132)
# fig1c = plt.subplot(133)

# fig1a.imshow(raw_img[0, 2900:3070, 80:160], vmax=60)
# fig1b.imshow(_masked[2900:3070, 80:160], vmax=60)
# fig1c.imshow(mask[2900:3070, 80:160])
