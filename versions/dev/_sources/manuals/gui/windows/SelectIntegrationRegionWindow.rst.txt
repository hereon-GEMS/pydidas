..
    This file is licensed under the
    Creative Commons Attribution 4.0 International Public License (CC-BY-4.0)
    Copyright 2023 - 2025, Helmholtz-Zentrum Hereon
    SPDX-License-Identifier: CC-BY-4.0

.. _select_integration_region_window:

Select integration region window
================================

The *Select integration region window* allows to visualize the integration ROI
in the image as well as changing the boundaries by clicking directly in the
image.

.. image:: images/select_int_roi_overview.png
    :align: center
    :width: 600

The left side offers controls for loading images, adjusting the integration 
regions and starting the graphic selection. The image with the integration 
region overlay is shown on the right. Note that if not image has been selected
yet, an image with zero intensity in the correct detector dimensions is shown.

Controls
--------

File input
^^^^^^^^^^

.. include:: ../beamcenter/file_input.rst

Plot overlay
^^^^^^^^^^^^

The Parameter for the plot overlay color allows to select a number of different
colors to increase the overlay visibility for a wide range of colormaps.

Manual selection of integration regions
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^

Any of the parameters for the integration range and limits can be updated in the
Parameter edit widgets. Any changes made will be displayed in the plot for 
inspection.

.. include:: ../integration_roi/select_roi.rst
