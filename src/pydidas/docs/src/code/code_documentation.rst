..
    This file is licensed under the
    Creative Commons Attribution 4.0 International Public License (CC-BY-4.0)
    Copyright 2023 - 2025, Helmholtz-Zentrum Hereon
    SPDX-License-Identifier: CC-BY-4.0

.. _code_documentation:

Code documentation
==================

This section documents the code and is intended as reference for developers.

.. contents::
    :depth: 2
    :local:
    :backlinks: none

Introduction
------------

A fundamental consideration is the separation of GUI and functionality. All computational 
functionality is designed to be accessible from the command line / scripts. (Although the 
GUI does provide some additional convenience methods.)
Some funcionality like file browsing and result visualization requires a GUI and is not
available from the command line.

Requirements
------------

Much of pydidas' functionality is based on Qt (PyQt5) and its QObjects with the inherent 
signal/slot system. For more information about Qt, please visit the Qt documentation.
Qt is also used for storing persistent information about global settings in the registry.

The computational part requires the pyFAI, numpy and scipy packages.

Additionally, the GUI uses widgets from pyFAI and silx and requires both packages.

Architecture
------------

pydidas is designed to be versatile and expandable. The processing is completely separated
from the GUI and can be used from command line scripts as well.

Generic functionality is grouped in basic sub-modules (for a full description please refer
to the `Package Structure <package_structure.html>`_\ ). Specific use cases are defined as 
stand-alone applications and are agnostic to the way they are called (serial or parallel). 
Parallelization of apps is provided by the multiprocessing sub-package and works with all
generic apps.

Widgets and the GUI are not referenced by other components and are independant of the rest of the
pydidas package.

Further code documentation
--------------------------

.. toctree::
    :maxdepth: 1
    
    concepts
    package_structure


API documentation
-----------------

.. toctree::
    :maxdepth: 1
    
    api/core
    api/multiprocessing
    api/data_io
    api/contexts
    api/managers
    api/plugins
    api/workflow
    api/apps
    api/widgets
    api/gui
    