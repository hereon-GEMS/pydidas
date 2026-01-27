..
    This file is licensed under the
    Creative Commons Attribution 4.0 International Public License (CC-BY-4.0)
    Copyright 2023 - 2025, Helmholtz-Zentrum Hereon
    SPDX-License-Identifier: CC-BY-4.0

The apps sub-package
--------------------

The apps are the pydidas use cases in the form of encapsulated processing programs. They can be run 
from the GUI or command line. For the graphical user interface, the framework will organize argument 
passing from the input fields.

For the command line, arguments can be either passed aa keywords during initialization, as command
line arguments or by updating the Parameter values of the app class in scripts.

.. toctree::
    :maxdepth: 2
    
    apps/composite_creator_app
    apps/execute_workflow_app
    apps/directory_spy_app
    apps/execute_workflow_runner