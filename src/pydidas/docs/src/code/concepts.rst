..
    This file is licensed under the
    Creative Commons Attribution 4.0 International Public License (CC-BY-4.0)
    Copyright 2023 - 2025, Helmholtz-Zentrum Hereon
    SPDX-License-Identifier: CC-BY-4.0

Key concepts
------------

.. contents::
    :depth: 2
    :local:
    :backlinks: none

Variable handling
^^^^^^^^^^^^^^^^^

Variables accessible by the user have been wrapped in their own class as 
:py:class:`Parameter <pydidas.core.Parameter>`. These 
:py:class:`Parameters <pydidas.core.Parameter>`, in turn, are handled by a 
subclassed dictionary.

Parameter
"""""""""

All (externally by the user accessible) variables are handled as 
:py:class:`Parameters <pydidas.core.Parameter>`. These objects have a reference 
key, a type and value. Additional metadata can be handled in form of a longer 
name, a unit and pre-defined choices for the value.

:py:class:`Parameters <pydidas.core.Parameter>` enforce type-checking when 
setting the value which makes input/output operations by the user more 
esilient.

Generic parameters have been pre-defined in the core.constants sub-package and 
these can be used without the need to re-define the full Parameter.

ParameterCollection
"""""""""""""""""""

:py:class:`Parameter collections <pydidas.core.ParameterCollection>` are 
subclassed dictionaries which allow only 
:py:class:`Parameters <pydidas.core.Parameter>` values. They are used by most 
pydidas objects and allow an easy and standardized access to all Parameters.
For the full documentation of the 
:py:class:`ParameterCollection <pydidas.core.ParameterCollection>`, please 
refer to the documentation of the 
:py:class:`ParameterCollection <pydidas.core.ParameterCollection>` object.

De-coupling of processing and user interface
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^

The full functionality of the pydidas suite [*]_ is available from the command 
line and can be used in scripted application without the need to invoke the 
graphical user interface. 
While the GUI allows for a convenient editing of Parameters and Workflows, it 
is not required for processing data.

Use cases
^^^^^^^^^

pydidas has been developed with diffraction data analysis in mind, but the 
structure is flexible enough to allow other use cases as well. Each single use 
case has been defined as a unique 
:py:class:`Application <pydidas.core.BaseApp>` which can be called via command 
line. Alternatively, pydidas includes a GUI frame for each generic application.

Parallelization
^^^^^^^^^^^^^^^ 

pydidas includes functionality for parallel processing of applications 
(or functions). The :py:mod:`multiprocessing <pydidas.multiprocessing>`
sub-package includes the required functionality. Results can be received using 
the PyQt5 signal/slot mechanism.


.. [*] Some functionality like image browsing and viewing inherently requires a 
       graphical interface and is not available from the command line.
       
