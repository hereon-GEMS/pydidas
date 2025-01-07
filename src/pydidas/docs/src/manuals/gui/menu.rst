..
    This file is licensed under the
    Creative Commons Attribution 4.0 International Public License (CC-BY-4.0)
    Copyright 2023 - 2025, Helmholtz-Zentrum Hereon
    SPDX-License-Identifier: CC-BY-4.0

.. _gui_menu:

The menu
========

The main user interaction with the GUI is controlled by the toolbar to the left
and the frames itself. The menu includes some functions which are not used as 
frequently. 

**This documentation page covers the menu bar, not the toolbar.**

pydidas menu structure
----------------------

- File 
    - GUI state
        The *GUI state* submenu includes entries to save and restore the UI 
        state as discussed above.
        
        - Store GUI state
            The *Store* entry will store the current state in an automatically 
            handled file. The file location depends on the operating system and 
            is handled through Qts QStandardPaths. A dialog asks for 
            confirmation before actually writing the file to disk.
        - Export GUI state
            The *Export* entry will query the user to select a file to store 
            the state. The file content is similar to the *Store* action but 
            the file can be placed anywhere in the filesystem and therefore 
            allows to share state between different users or machines.
        - Restore GUI state
            The *Restore* entry will open a dialog to confirm that the user 
            wants to restore the UI state from pydidas's automatically handled 
            state file. If confirmed, all pydidas objects are updated and the 
            GUI view is changed to the active view. (Corresponding saver: 
            *Store GUI state*)
        - Restore GUI state at exit
            The *Restore at Exit* entry will open a dialog to confirm that the 
            user wants to restore the UI state from pydidas's automatically 
            handled exit state file. If confirmed, all pydidas objects are 
            updated and the GUI view is changed to the active view when last 
            closing the GUI.

            .. warning::
                The stored state at exit is written when the GUI closes 
                correctly, i.e. this state will not be updated upon a crash or 
                upon terminating the process using OS tools. Therefore, the exit 
                state is not necessarily the state when the user last used the 
                pydidas GUI.
    
        - Import
            The *Import* entry will open a file selection dialog to select a 
            file with the UI state to be restored.

            .. note::
                No additional confirmation is required, selecting a file is 
                sufficient. To abort, simple use the **Cancel** button (or the 
                :py:data`Esc` key) in the file selection dialog, this will stop 
                the import.
        
    - Exit
        This action will close the pydidas GUI **without confirmation**.
- Tools
    - Export Eiger Pixelmask
        This menu item will open a small window which allows the user to 
        specify an Eiger-written *master* file which includes detector metadata, 
        including the detector pixelmask and an output filename to write the 
        exported mask.
    - Images series processing
        The *Image series processing* menu entry opens a new window to proces 
        a series of images. This allows a user, for example, to average 
        calibration data. For more information, please refer to the :ref:`Image 
        series operations window manual <series_ops_window>`.
    - Edit detector mask
        This menu entry will open a window to define and edit a detector mask. 
        For more information, please refer to the corresponding :ref:`Mask 
        editor window manual <mask_editor_window>`.
    - Clear local log filesystem
        Using this menu entry will try to clear all written pydidas log files 
        from the local file system. 
- Options
    - User config
        The User config entry opens a window to modify user preferences like 
        colormaps, default detector masks, or the plugin paths. For more 
        information, please see the :ref:`User config manual 
        <user_config_window>`.
    - Settings
        The settings menu entry will open a window with global settings like
        multiprocessing and memory configuration. For more information, please 
        refer to the documentation in the :ref:`Global settings window manual 
        <global_settings_window>`.
- Help
    - Open documentation in browser
        Using this menu entry will open the documentation home in a new tab in 
        the operating system's default web browser. 
    - Open feedback form
        The *open feedback form* will open the pydidas feedback form in a new 
        web browser tab. The feedback form allows to submit bug reports,
        improvement suggestions or questions.
    - Pydidas paths
        This entry will open a small window with information about the local
        paths in which log files and configuration files are placed by the 
        pydidas application.
    - Check for update
        Using this option will require an active internet connection. Pydidas
        will check the latest release version on Github and compare the 
        remote version number with the locally installed version. The result
        will be supplied to the user in a pop-up window.
    - About
        The about window has copyright information and links to the pydidas 
        homepage and github home.
        
        
