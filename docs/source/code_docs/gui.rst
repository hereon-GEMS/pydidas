The gui submodule
==================

The gui submodule is the equivalent to *apps* for the graphical user interface. 
*Frames* encapsulate specific functionalities and expose them to the user.

The :py:class:`pydidas.gui.main_window` class must be used to organize frames. It
provides methods to register frames and create menus.

.. toctree::
	:maxdepth: 3

	gui/main_window
	gui/composite_creator_frame
	gui/experimental_setup_frame
	gui/global_configuration_frame
	gui/image_math_frame
	gui/execute_workflow_frame
	gui/processing_single_plugin_frame
	gui/pyfai_calib_frame
	gui/scan_setup_frame
	gui/workflow_edit_frame
	gui/builders