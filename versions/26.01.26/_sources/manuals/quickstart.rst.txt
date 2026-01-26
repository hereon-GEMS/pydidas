..
    This file is licensed under the
    Creative Commons Attribution 4.0 International Public License (CC-BY-4.0)
    Copyright 2024 - 2025, Helmholtz-Zentrum Hereon
    SPDX-License-Identifier: CC-BY-4.0

.. _quickstart:

Pydidas quick-start guide
=========================

Pydidas is usable both through its graphical user interface as well as through the 
command line / notebooks.

To quickly start using pydidas, there are multiple options:

  - Entry points (if pydidas was installed using pip)
  - Scripts in the ``pydidas_scripts`` folder.
  - Using the ``pydidas`` module in the python shell. 

Entry points
------------

If installed as wheel, pydidas offers the following entry points:

  - ``pydidas-gui`` to start the graphical user interface.
  - ``pydidas-documentation`` to open the pydidas documentation in the default system
    web browser. **Note:** The pydidas module must have been run at least once
    (either through opening the GUI or imported in a python shell) for the
    documentation to have been created.
  - ``pydidas-clear-settings`` Remove the stored registry keys for pydidas.
  - ``pydidas-updater`` Start a script which automatically updates pydidas to the latest
    version available on GitHub.
  - ``pydidas-remove-local-files`` This script removes all local log files and stored
    configuration files.
  - ``run-pydidas-workflow`` Script to run a defined workflow in the console. This script
    also requires configuration files for the scan and diffraction experiment. Please
    refer to the full documentation for more details.
  - ``remove-pydidas`` Remove all local config files and registry settings from the
    system. Please note that this script will not remove the python code itself, but
    only cleans up the system.

Scripts
-------
Pydidas includes multiple scripts which are located in the ``pydidas_scripts`` folder,
which is located in the same folder as ``pydidas``.
These can be called directly by python from the command line and they are:

  - ``pydidas_gui.py`` to start the GUI.
  - ``pydidas_documentation.py`` to open the html documentation in a browser.
  - ``run_pydidas_workflow.py`` to run a processing workflow on the command line.
  - ``pydidas_updater_script.py`` to update pydidas to the latest release published on
    GitHub.
  - ``clear_local_settings.py`` to remove all registry settings written by pydidas.

Example
^^^^^^^

If pydidas, was installed in `/user/myname/code/python/my_packages/pydidas`,
the ``pydidas_scripts`` will be located in

.. code-block:: bash

    $ cd /user/myname/code/python/my_packages/pydidas_scripts
    $ python pydidas_gui.py



Command line
------------
Much of pydidas' functionality is also available from the command line or notebooks.
Pydidas can be imported and used as any other python module. Please refer to the
documentation, in particular to the :ref:`command_line_manual`.
