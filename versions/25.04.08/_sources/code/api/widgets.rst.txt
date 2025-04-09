..
    This file is licensed under the
    Creative Commons Attribution 4.0 International Public License (CC-BY-4.0)
    Copyright 2023 - 2025, Helmholtz-Zentrum Hereon
    SPDX-License-Identifier: CC-BY-4.0

The widgets sub-package
-----------------------

The widgets sub-package includes pydidas-specific PyQt5 widgets which can be 
used in the graphical user interface.
Basic widgets are located in the generic :py:mod:`pydidas.widgets` whereas more 
specialized widgets are located in the respective sub-packages.

.. list-table:: 
   :widths: 25 75
   :header-rows: 1
   :class: tight-table

   * - package
     - description
   * - *pydidas.widgets*
     - pydidas-specific PyQt5 widgets which are used in the graphical user 
       interface.
   * - *pydidas.widgets.controllers*
     - Widget-specific controllers which handle the interaction between 
       different widgets.
   * - *pydidas.widgets.dialogues*
     - User dialogue widgets which show in their own windows.
   * - *pydidas.widgets.factory*
     - Convenience functions to create new widgets and set Qt properties 
       defined by the user.
   * - *pydidas.widgets.framework*
     - Generic widgets which are used throughout the pydidas framework.
   * - *pydidas.widgets.misc*
     - Miscellaneous widgets for specific jobs.
   * - *pydidas.widgets.parameter_config*
     - Specific widgets to edit the values of Parameters and functionality to 
       create and manage parameter config widgets.
   * - *pydidas.widgets.selection*
     - Widgets used to select a specific item (e.g. combo boxes or from a file 
       system tree).
   * - *pydidas.widgets.silx_plot*
     - Widgets used to extend the silx plotting functionality in pydidas.
   * - *pydidas.widgets.windows*
     - pydidas Windows offer specific and more complicated functionality
       for specific tasks.      
   * - *pydidas.widgets.workflow_edit*
     - Widgets used to show and edit the workflow tree.


.. toctree::
    :maxdepth: 1

    widgets/base
    widgets/controllers
    widgets/dialogues
    widgets/factory
    widgets/framework
    widgets/misc
    widgets/parameter_config
    widgets/selection
    widgets/silx_plot
    widgets/workflow_edit
    widgets/windows
