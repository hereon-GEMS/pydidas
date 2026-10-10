..
    This file is licensed under the
    Creative Commons Attribution 4.0 International Public License (CC-BY-4.0)
    Copyright 2023 - 2026, Helmholtz-Zentrum Hereon
    SPDX-License-Identifier: CC-BY-4.0

The widgets sub-package
-----------------------

The widgets sub-package includes pydidas-specific PyQt5 widgets which can be
used in the graphical user interface. Basic widgets are located in the generic
:py:mod:`pydidas.widgets` whereas more specialized widgets are located in the
respective sub-packages.

.. list-table::
   :widths: 25 75
   :header-rows: 1
   :class: tight-table

   * - Package
     - Description
   * - *pydidas.widgets*
     - pydidas-specific PyQt5 widgets which are used in the graphical user
       interface.
   * - *pydidas.widgets.base_classes*
     - Base classes and mix-ins for pydidas widgets, frames and windows.
   * - *pydidas.widgets.base_reimplementations*
     - Re-implementations of generic Qt widgets with pydidas-specific extensions.
   * - *pydidas.widgets.controllers*
     - Widget-specific controllers which handle the interaction between different widgets.
   * - *pydidas.widgets.data_viewer*
     - Widgets to view and browse data.
   * - *pydidas.widgets.dialogs*
     - User dialog widgets which show in their own windows.
   * - *pydidas.widgets.extended_widgets*
     - Extended generic widgets which are used throughout the pydidas framework.
   * - *pydidas.widgets.file_browser*
     - Widgets used to browse the file system.
   * - *pydidas.widgets.misc*
     - Miscellaneous widgets for specific jobs.
   * - *pydidas.widgets.param_io*
     - Widgets to edit the values of Parameters.
   * - *pydidas.widgets.plugin_config_widgets*
     - Widgets to configure the Parameters of plugins.
   * - *pydidas.widgets.pyqtgraph_plot*
     - Widgets for plotting based on pyqtgraph.
   * - *pydidas.widgets.silx_plot*
     - Widgets used to extend the silx plotting functionality in pydidas.
   * - *pydidas.widgets.windows*
     - pydidas Windows offer specific and more complicated functionality for specific tasks.
   * - *pydidas.widgets.workflow_edit*
     - Widgets used to show and edit the workflow tree.


.. toctree::
    :maxdepth: 1

    widgets/base
    widgets/base_classes
    widgets/base_reimplementations
    widgets/controllers
    widgets/data_viewer
    widgets/dialogs
    widgets/extended_widgets
    widgets/file_browser
    widgets/misc
    widgets/param_io
    widgets/plugin_config_widgets
    widgets/pyqtgraph_plot
    widgets/silx_plot
    widgets/windows
    widgets/workflow_edit
