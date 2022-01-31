Code documentation
==================

This sections lays out the API of the code and is intended as reference for developers.

Introduction
------------

A fundamental consideration is the separation of GUI and functionality. All computational 
functionality is designed to be accessible from the command line / scripts. (Although the 
GUI does provide some convenience editing methods.)
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
to the `Package Structure <code_docs/package_structure.html>`_\ ). Specific use cases are defined as 
stand-alone applications and are agnostic to the way they are called (serial or parallel). Parallelization 
of apps is provided by the multiprocessing sub-package.

Widgets and the GUI are not referenced by other components and are independant of the rest of the
pydidas package.

Further code documentation
--------------------------

.. toctree::
    :maxdepth: 1
    
    code_docs/concepts
    code_docs/package_structure


  
  
Package documentation
---------------------

.. toctree::
    :maxdepth: 1
    
    code_docs/core
    code_docs/multiprocessing
    code_docs/image_io
    code_docs/experiment
    code_docs/managers
    code_docs/plugins
    code_docs/workflow
    code_docs/apps
    code_docs/widgets
    code_docs/gui
    