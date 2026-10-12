..
    This file is licensed under the
    Creative Commons Attribution 4.0 International Public License (CC-BY-4.0)
    Copyright 2024 - 2026, Helmholtz-Zentrum Hereon
    SPDX-License-Identifier: CC-BY-4.0

.. _package_structure:

Package structure
-----------------

The pydidas sub-packages are organized hierarchically with only upward references
to allow a clean architecture. A list of the sub-packages including internal
references is given below.


Index of sub-packages
^^^^^^^^^^^^^^^^^^^^^

The list of all pydidas subpackages including their internal requirements is
given below:

+-------------------+------------------------------------------------+
| **sub-package**   | **requirements**                               |
+-------------------+------------------------------------------------+
| core              |                                                |
+-------------------+------------------------------------------------+
| multiprocessing   | core                                           |
+-------------------+------------------------------------------------+
| data_io           | core                                           |
+-------------------+------------------------------------------------+
| contexts          | core                                           |
+-------------------+------------------------------------------------+
| managers          | core, data_io                                  |
+-------------------+------------------------------------------------+
| plugins           | core, data_io, managers                        |
+-------------------+------------------------------------------------+
| workflow          | core, contexts, plugins                        |
+-------------------+------------------------------------------------+
| apps              | core, data_io, contexts, managers, workflow    |
+-------------------+------------------------------------------------+
| widgets           | core, contexts, workflow, apps                 |
+-------------------+------------------------------------------------+
| unittest_objects  | core, data_io, plugins, apps                   |
+-------------------+------------------------------------------------+
| gui               | core, multiprocessing, data_io, contexts,      |
|                   | workflow, apps, widgets                        |
+-------------------+------------------------------------------------+

Sub-package descriptions
^^^^^^^^^^^^^^^^^^^^^^^^

- **pydidas.core**

    The core classes and functions which are used throughout the pydidas
    package. These include data structure, generic objects, and factories.

  - *pydidas.core.constants*

        Hardcoded constants (numerical and for GUI behaviour) used by pydidas.

  - *pydidas.core.io_registry*

        Base classes for a metaclass-based registry to associate specific
        actions with specific file extensions.

  - *pydidas.core.utils*

        Utility functions for various purposes.

- **pydidas.multiprocessing**

        All the required functionality to run simple functions or apps in
        parallel processes.

- **pydidas.data_io**

        The pydidas image reader and writer implementation and registry classes
        for the various formats.

  - *pydidas.data_io.implementations*

        Specific implementations for various file formats.

  - *pydidas.data_io.low_level_readers*

        Low-level implementations of file readers used by *implementations*
        (e.g. reading slices out of hdf5 files).

- **pydidas.contexts**

    Singleton classes which manage global settings for the experimental setup
    and the scan setup. This information can be used by plugins or apps to query
    the global processing parameters.

  - *pydidas.contexts.experiment_context*

        Classes for the global experimental settings and import/export.

  - *pydidas.contexts.scan*

        Classes for the global scan settings and import/export.

- **pydidas.managers**

    Classes which manage specific tasks or aspects of processing and which can
    be used by plugins and apps.

- **pydidas.plugins**

    Base classes for plugins and the plugin collection singleton which handles
    the collection of plugin classes from (possibly) different locations and
    which can return single classes for instantiation in a workflow tree.

- **pydidas.workflow**

    Classes of nodes and trees to describe the workflow and execute plugins in
    the order defined by the user.

  - *pydidas.workflow.result_io*

        Classes to handle writing the results of the workflow execution to
        files.

  - *pydidas.workflow.processing_tree_io*

        Registry with importers/exporters and the importer/exporter
        implementations.

- **pydidas.apps**

    The pydidas use cases have been defined in apps which can be called from the
    command line or using the GUI. All apps are parallelizable using the
    functionality of the multiprocesing subpackage.

- **pydidas.widgets**

    pydidas-specific PyQt5 widgets which are used in the graphical user
    interface.

  - *pydidas.widgets.base_classes*

        Base classes and mix-ins for pydidas widgets, frames and windows.

  - *pydidas.widgets.base_reimplementations*

        Re-implementations of generic Qt widgets with pydidas-specific extensions.

  - *pydidas.widgets.controllers*

        Widget-specific controllers which handle the interaction between different widgets.

  - *pydidas.widgets.data_viewer*

        Widgets to view and browse data.

  - *pydidas.widgets.dialogs*

        User dialog widgets which show in their own windows.

  - *pydidas.widgets.extended_widgets*

        Extended generic widgets used throughout pydidas.

  - *pydidas.widgets.file_browser*

        Widgets used to browse the file system.

  - *pydidas.widgets.misc*

        Miscellaneous widgets for specific jobs.

  - *pydidas.widgets.param_io*

        Widgets to edit the values of Parameters.

  - *pydidas.widgets.plugin_config_widgets*

        Widgets to configure the Parameters of plugins.

  - *pydidas.widgets.pyqtgraph_plot*

        Widgets for plotting based on pyqtgraph.

  - *pydidas.widgets.silx_plot*

        Widgets used to extend the silx plotting functionality.

  - *pydidas.widgets.windows*

        Windows offering specific and more complicated functionality.

  - *pydidas.widgets.workflow_edit*

        Widgets used to show and edit the workflow tree.

- **pydidas.unittest_objects**

    Objects which are not used in the deployed pydidas version but which are
    required to run unittests with simplified objects.

- **pydidas.gui**

    All the functionality required for building and running the graphical user
    interface. Functionality is organized in "frames" which can all be accessed
    from the main window.

  - *pydidas.gui.frames*

        Frames are the top-level widgets used in pydidas to organize and show
        content in the GUI.

  - *pydidas.gui.frames.builders*

        Mix-in classes for the individual frames which include the layout and
        arrangement of widgets.

  - *pydidas.gui.managers*

        Manager classes for the GUI.

  - *pydidas.gui.mixins*

        Mix-in classes for the GUI which add specific functionality to the base
        frame classes.

  - *pydidas.gui.windows*

        Stand-alone main windows which can be opened from within the pydidas
        main window, for example for the documentation.
