..
    This file is licensed under the
    Creative Commons Attribution 4.0 International Public License (CC-BY-4.0)
    Copyright 2023 - 2025, Helmholtz-Zentrum Hereon
    SPDX-License-Identifier: CC-BY-4.0

.._view_results_frame:

View workflow results frame
===========================

.. contents::
    :depth: 2
    :local:
    :backlinks: none

The *View workflow results* frame is very similar to the *Run full workflow*
frame except that it does not allow to start the processing but to import
results.

This frame allow to explore current and past results.

.. image:: images/view_results_overview.png
    :width:  600px
    :align: center

The configuration on the left holds the following functions which will be 
described in more detail below:

  - Import results
  - Selecting the results to be displayed
  - Manually exporting results

Importing results
-----------------

Using the *Import results from directory* button in the top left of the frame 
opens a window to select a directory. The selected directory is scanned for 
pydidas-written node result files which will be imported.

.. note::

    Importing results will also import Scan and Diffraction Experiment 
    defintions into separate instances in the background. Therefore, the 
    imported data is completely independent from any current processing.

Result selection
----------------

Node results
^^^^^^^^^^^^

.. include:: ./workflow_result_selection.rst

Export of results
-----------------

.. include:: ./workflow_result_export.rst

Data display
------------

1D and 2D data can be displayed using the two widgets described below.

.. include:: ../silx/plot1d.rst

.. include:: ../silx/plot2d.rst
