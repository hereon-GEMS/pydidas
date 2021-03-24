# -*- coding: utf-8 -*-
"""
Created on Mon Mar 22 15:24:10 2021

@author: ogurreck
"""

from plugin_workflow_gui import PluginCollection


def format_plugin_hints(plugin_name):
    plugin = PluginCollection().get_plugin_by_name(plugin_name)
    # Hint text
