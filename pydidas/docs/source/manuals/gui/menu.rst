.. _gui_menu:

The menu
========

The main user interaction with the GUI is controlled by the toolbar to the left
and the frames itself. The menu houses some functions which are not used as 
frequently.

The UI state
------------

The state of the interface, including all configurations of frames and apps, can
be stored and restored by the user. This is handled in the **File > GUI state**
menu and details will be explained in detail in the corresponding menu section.

This function allows to either store the state in a automatically controlled 
file in the OS-specific user's application config directory or in a file 
specified by the user itself. For restoring, similar options exist.

.. note::
    The automatically-controlled files are user-specific and if users log in
    on the same machine using a different user account, the file will not be
    accessible. 


The File menu
-------------

GUI state
^^^^^^^^^

The *GUI state* submenu includes entries to save and restore the UI state as 
discussed above.

GUI state > Store
"""""""""""""""""

The *Store* entry will store the current state in an automatically handled file.
The file location depends on the operating system and is handled through Qts
QStandardPaths. 
A dialog asks for confirmation before actually writing the file to disk.

GUI state > Export
""""""""""""""""""

The *Export* entry will query the user to select a file to store the state. The 
file content is similar to the *Store* action but the file can be placed 
anywhere in the filesystem and therefore allows to share state between different
users or machines.

GUI state > Restore
"""""""""""""""""""

The *Restore* entry will open a dialog to confirm that the user wants to restore 
the UI state from pydidas's automatically handled state file. If confirmed,
all pydidas objects are updated and the GUI view is changed to the active view
when storing the state.

GUI state > Import
""""""""""""""""""

The *Import* entry will open a file selection dialog to select a file with the 
UI state. 

.. note::
    No additional confirmation is required, selecting a file is sufficient. To
    abort, simple use the *Cancel* button (or the ``Esc`` key) in the file 
    selection dialog, this will stop the import.
    
Exit
^^^^

This action will close the pydidas GUI **without confirmation**.

The Extras menu
---------------

Settings
^^^^^^^^

The settings menu entry will open an independent window which allows to 
configure the pydidas global settings, similar to the :ref:`global_settings_frame`.
Please refer to the documentation there for more information.

Export Eiger Pixelmask
^^^^^^^^^^^^^^^^^^^^^^

This menu item will open a small window which allows the user to specify an
Eiger-written *master* file which includes detector metadata, including the
detector pixelmask and an output filename to write the exported mask.

Average images
^^^^^^^^^^^^^^

The *Average images* menu entry allows users to select any number of frames from
one or multiple files and average them all and store the result in a single new
file. This functionality is designed for example for averaging calibration data.

The Help menu
-------------

The help menu has options to show the html documentation. Either as a pop-up
window using the *Open documentation in a separate window* entry or in a
browser by using the *Open documentation in default web browser*. Note that the
default web browser is determined by the user settings in the operating system.


