..
    This file is licensed under the
    Creative Commons Attribution 4.0 International Public License (CC-BY-4.0)
    Copyright 2023 - 2025, Helmholtz-Zentrum Hereon
    SPDX-License-Identifier: CC-BY-4.0

.. _graphical_user_interface:

Graphical user interface
========================

.. contents::
    :depth: 2
    :local:
    :backlinks: none

The graphical user interface is organized in *Frames* which are independent of
each other and which each hold persistent information during each session.

The individual :ref:`gui_frames` and :ref:`gui_windows` are presented below before
:ref:`gui_recipes` are described which give a detailed guide on individual use
cases.

Overview
--------

The general pydidas GUI layout is shown below:

.. image:: images/gui_generic_layout.png
    :width: 600px
    :align: center

- The menu
    The menu bar allows access to global functionality like state import and
    export, global and user settings as well as help and bug reporting. The
    details are described in the :ref:`Menu manual <gui_menu>`.
- The status & logging area
    This dockable area is used by all frames to send status updates and to
    display them globally.
- The Frame selection toolbar
    This toolbar is used to select which frame to display in the central widget
    of the GUI. Some entries can open a submenu with additional choices.
    Clicking on the icon will open the frame. Frames are persistent within a
    session and information is stored when switching between different frames.
- The central frame
    This widget displays the active frame and the main interaction with the user
    happens here.

After starting the GUI, the home frame gives links to the documentation and a
very brief reminder how to user the pydidas GUI.


The UI state
------------

The state of the interface, including all configurations of frames and apps, can
be stored and restored by the user. This is handled in the **File > GUI state**
menu and details are explained in detail :ref:`Menu manual <gui_menu>`.

This function allows to either store the state in a automatically controlled
file in the OS-specific user's application config directory or in a file
specified by the user itself. For restoring, similar options exist.
In addition, pydidas stores the GUI's state when closing the GUI properly (i.e.
a regular exit), allowing the user to pick up where they left.

.. note::
    The automatically-controlled files are user-specific and if users log in
    on the same machine using a different user account, the file will not be
    accessible.


Generic GUI information
-----------------------

.. toctree::
    :maxdepth: 1

    menu
    editing_parameters
    silx/plots

.. _gui_frames:

Frames
------

Detailed descriptions of the individual frames are given section about :ref:`frames_main`.

.. toctree::
    :maxdepth: 1
    :hidden:

    frames/frames_main

.. _gui_windows:

Windows
-------

Detailed information about the individual windows are given in hte section about :ref:`windows_main`.

.. toctree::
    :maxdepth: 1
    :hidden:

    windows/windows_main

.. _gui_recipes:

Recipes
-------

.. toctree::
    :maxdepth: 1

    recipes/pydidas_processing
