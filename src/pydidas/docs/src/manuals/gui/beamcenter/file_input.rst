..
    This file is licensed under the
    Creative Commons Attribution 4.0 International Public License (CC-BY-4.0)
    Copyright 2023 - 2025, Helmholtz-Zentrum Hereon
    SPDX-License-Identifier: CC-BY-4.0


The input file can be selected in any one of four ways:

.. image:: ../beamcenter/_images/input.png
    :align: left

1. Use the "Select image file" button at the top.
2. Enter the full file path in the input field.
3. Use the small "open" button right of the input field.
4. Drag and drop a file from the system's file explorer.

.. image:: ../beamcenter/_images/input_hdf5.png
    :align: right

If the filename is valid, the selected file will be displayed immediately.

For hdf5 files, however, you need to select data the dataset and frame number 
first and confirm the selection with the "Confirm input selection" button before
any frame is loaded and displayed.

After loading an image, the current integration region is shown as an overlay.
By default,the overlay is orange and will cover the full image (because the full
detector is used by default).