The gui submodule
==================

The gui submodule is the equivalent to *apps* for the graphical user interface. 
*Frames* encapsulate specific functionalities and expose them to the user.

The :py:class:`pydidas.gui.main_window` class must be used to organize frames. 
It provides methods to register frames and create menus.

.. toctree::
    :maxdepth: 3

    gui/main_window
    gui/data_browsing_frame
    gui/pyfai_calib_frame
    gui/composite_creator_frame
    gui/setup_experiment_frame
    gui/setup_scan_frame
    gui/workflow_edit_frame
    gui/workflow_test_frame
    gui/workflow_run_frame
    gui/view_results_frame
    gui/global_configuration_frame
    gui/builders