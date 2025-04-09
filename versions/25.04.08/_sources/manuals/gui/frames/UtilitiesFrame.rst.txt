..
    This file is licensed under the
    Creative Commons Attribution 4.0 International Public License (CC-BY-4.0)
    Copyright 2023 - 2025, Helmholtz-Zentrum Hereon
    SPDX-License-Identifier: CC-BY-4.0

..  _utilities_frame:

Utilities frame
===============

.. contents::
    :depth: 2
    :local:
    :backlinks: none

The *Utilties* frame allows users to access various stand-alone windows with
various functionalities.

.. image:: images/utilities_overview.png
    :width: 600px
    :align: center

The following windows can be opened:


.. list-table::
    :widths: 30 70
    :header-rows: 1
    :class: tight-table

    * - Window title
      - description
    * - :ref:`User config window <user_config_window>`
      - Edit the user preferences for the generic application config.
        (e.g. colormaps, plugin path)
    * - :ref:`Global settings window <global_settings_window>`
      - Edit the global application settings (e.g. multiprocessing preferences).
    * - :ref:`Export Eiger Mask window <export_eiger_pixelmask_window>`
      - Get the mask file for the Eiger detector from a Hdf5 master file 
        written by the Eiger detector and export it as an image.
    * - :ref:`Edit detector mask window <mask_editor_window>`
      - Edit the detector mask: Import an image and add mask regions based on 
        threshold selections, polygons, etc. This utility is an integrated 
        version of the silx MaskToolsWidget.
    * - :ref:`Image series operations window <series_ops_window>`
      - Perform mathematical operations (e.g. sum, mean, max) on a series of 
        images and save the results to a new single image.
    * - :ref:`Composite creator frame <composite_creator_frame>`
      - Create composite images from a number of individual images.

