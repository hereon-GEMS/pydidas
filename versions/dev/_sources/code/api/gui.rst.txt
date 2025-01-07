..
    This file is licensed under the
    Creative Commons Attribution 4.0 International Public License (CC-BY-4.0)
    Copyright 2023 - 2025, Helmholtz-Zentrum Hereon
    SPDX-License-Identifier: CC-BY-4.0

The gui submodule
==================

.. contents::
    :depth: 2
    :local:
    :backlinks: none

The gui submodule for the graphical user interface is the equivalent to *apps* 
submodule for processing as it exposes functionality to the user.

The main graphical interface is handled by the :py:class:`MainWindow 
<pydidas.gui.MainWindow>` class. It handles the individual frames and persistent
state storage.

Functionality is organized in individual :py:class:`Frames 
<pydidas.widgets.BaseFrame>` which allow storage of state and which are shown
in the central widget and independent :py:class:`PydidasWindows 
<pydidas.gui.windows.PydidasWindow>` which are not persistent and are used for
individual and independent tasks.

Global GUI classes
------------------

.. toctree::
    :maxdepth: 3

    gui/main_window
    
Frames
------    

.. toctree::
    :maxdepth: 3

    gui/frames/data_browsing_frame
    gui/frames/pyfai_calib_frame
    gui/frames/composite_creator_frame
    gui/frames/define_diffraction_exp_frame
    gui/frames/define_scan_frame
    gui/frames/workflow_edit_frame
    gui/frames/workflow_test_frame
    gui/frames/workflow_run_frame
    gui/frames/view_results_frame
    gui/frames/builders

Windows
-------
    
.. toctree::
    :maxdepth: 3
    
    widgets/windows/global_settings_window