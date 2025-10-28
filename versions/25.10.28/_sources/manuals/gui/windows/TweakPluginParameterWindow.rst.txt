..
    This file is licensed under the
    Creative Commons Attribution 4.0 International Public License (CC-BY-4.0)
    Copyright 2023 - 2025, Helmholtz-Zentrum Hereon
    SPDX-License-Identifier: CC-BY-4.0

.. _tweak_plugin_parameters_window:

Tweak Plugin Parameters window
==============================


The *Tweak Plugin Parameters window* will have a slightly different layout for 
each plugin, depending on the plugin parameters.

.. image:: images/tweak_plugin_parameters.png
    :width: 524 
    :align: center

If the plugin also has detailed results, a second linked window will be shown
for the detailed results of the tweaked plugin.

Parameter configuration
^^^^^^^^^^^^^^^^^^^^^^^

This region will have the same look and feel as the corresponding Parameter
configuration for the :py:class:`WorkflowTree <pydidas.workflow.WorkflowTree>`
in the :ref:`workflow_edit_frame`.

Control buttons
^^^^^^^^^^^^^^^

Three buttons allow to test the current configuration and confirm or discard
changes:

  - **Run plugin with currrent parameters**

    This button allows to execute the selected plugin with the current paramter
    configuration. Results (and detailed results) will be updated directly.
  
  - **Confirm current parameters and close window**
  
    This will confirm the current configuration and update the corresponding 
    plugin in the workflow tree. 
    
  - **Cancel parameter editing and discard changes**
  
    Clicking this button will close the window and restore the original 
    configuration of the current plugin.
    
Plugin result visualization
^^^^^^^^^^^^^^^^^^^^^^^^^^^

Results of the plugin can be visualized here. The specific type of results is
depending on the plugin. 
