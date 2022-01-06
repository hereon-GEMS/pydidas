The widgets sub-package
-----------------------

The widgets sub-package includes pydidas-specific PyQt5 widgets which can be used in the
graphical user interface.
Basic widgets are located in the generic :py:mod:`pydidas.widgets` whereas more specialized
widgets are located in the respective sub-packages.

.. list-table:: 
   :widths: 25 75
   :header-rows: 1
   :class: tight-table

   * - package
     - description
   * - *pydidas.widgets*
     - pydidas-specific PyQt5 widgets which are used in the graphical user interface.
   * - *pydidas.widgets.dialogues*
     - User dialogue widgets which show in their own windows.
   * - *pydidas.widgets.factory*
     - Convenience functions to create new widgets and set Qt properties defined by the user.
   * - *pydidas.widgets.parameter_config*
     - Specific widgets to edit the values of Parameters and functionality to create and manage parameter config widgets.
   * - *pydidas.widgets.selection*
     - Widgets used to select a specific item (e.g. combo boxes or from a file system tree).
   * - *pydidas.widgets.workflow_edit*
     - Widgets used to show and edit the workflow tree.


.. toctree::
	:maxdepth: 1

	widgets/base
	widgets/dialogues
	widgets/factory
	widgets/parameter_config
	widgets/selection
	widgets/workflow_edit
