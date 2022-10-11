Scan setup frame
================

.. contents::
    :depth: 2
    :local:
    :backlinks: none

The *Scan setup* frame is a graphical interface to configure the 
:py:class:`SetupScan <pydidas.experiment.setup_scan.setup_scan._SetupScan>` 
which holds information about the scan setup. 

The frame only holds the configuration widgets for its Parameters as well as 
some buttons for convenience functionality.

.. image:: images/scan_setup_overview.png
    :width:  600px
    :align: center

Control buttons
---------------

Import scan settings
^^^^^^^^^^^^^^^^^^^^

.. image:: images/scan_setup_import.png
    :align: left

The Scan settings can be importted from file. Clicking the corresponding 
button will open a selection dialogue to pick the file with the stored settings.
File extensions will be pre-selected based on the available importers. 

Reset Parameters
^^^^^^^^^^^^^^^^

.. image:: images/scan_setup_reset.png
    :align: left

The "Reset all scan settings" button allows the user to change all Parameters
back to their default values. 

Export scan settings
^^^^^^^^^^^^^^^^^^^^

.. image:: images/scan_setup_export.png
    :align: left

At the bottom of the Frame, the export button allows users to export the current
:py:class:`SetupScan <pydidas.experiment.setup_scan.setup_scan._SetupScan>` 
Parameters to a file. This button will open a filename dialogue.

Global Parameters
-----------------

.. image:: images/scan_setup_globals.png
    :align: left

Here, *global* refers to general scan Parameters in contrast to Parameters for 
a specific scan dimension. The scan dimensionality defines the number of used
dimensions (and also shows or hides the corresponding widgets for the selected
dimensions). The scan title is used as reference in titles and captions.

The base directory and scan name pattern are used for :py:class:`InputPlugins
<pydidas.plugins.InputPlugin>` to define the raw data source. The starting index
defines the number of the first data file.

For a detailed description of each Parameter, please refer to the 
:ref:`list of SetupScan Parameters <setup_scan_params>` found at the bottom of 
this page.

Configuring a scan dimension
----------------------------

.. note::
    Following the python nomenclature, the first index is 0 (zero) and so forth.

.. image:: images/scan_setup_dimension.png
    :align: left

The configuration for each scan dimension is the same, and dimension #1 is shown
only exemplarily. 

At the top, next to the name, are two small buttons with up and down arrows 
which allow to move the given scan dimension up or down in the list to change
the order. Only reasonable arrows are shown, for example the first scan 
dimension cannot be further moved upwards. 

Each scan dimension has one mandatory field which is the number of scan points. 
This number determines the layout of the data in pydidas. The other information
is metadata which is used to determine labels and axis ranges (for plots and 
export metadata) but which has no further relevance. The name of the scan 
dimension corresponds to the label. The unit is also used to label the 
dimension range.

The range of each scan dimension is determined by the number of points 
:math:`N`, the step width :math:`\Delta x` between two points and the offset 
:math:`x_0`. The full range is thus

.. math::

    x_0,\ x_0 + \Delta x,\ x_0 + 2 * \Delta x,\ ...,\ x_0 + (N - 1) * \Delta x.


Using the Scan settings
-------------------------------

The :py:class:`SetupScan <pydidas.experiment.setup_scan.setup_scan._SetupScan>` 
is not used directly but the information is required in applications, e.g. to
run processing workflows.
   
.. _setup_scan_params:

.. include:: ../../global/setup_scan_params.rst
