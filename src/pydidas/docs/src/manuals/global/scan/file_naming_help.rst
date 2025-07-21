..
    This file is licensed under the
    Creative Commons Attribution 4.0 International Public License (CC-BY-4.0)
    Copyright 2025, Helmholtz-Zentrum Hereon
    SPDX-License-Identifier: CC-BY-4.0

.. _file_naming_help:

Explanations of Scan file naming
--------------------------------


The scan/file naming pattern determines how the input plugins in the pydidas Workflow
interpret the path to the detector images.

For most input plugins, the scan/file naming pattern corresponds directly to the
file names of the files.

Some plugins use the scan/file naming pattern not only for the file names but also
to access files in a nested directory structure. Please check the documentation
of the individual input plugins for details on how the scan/file naming pattern is
used by the particular plugin.

If multiple files are used in a scan, the scan/file naming pattern must be set up
to specify which part of the file name corresponds to the counting variable.
The dynamic part of the file name must be replaced by a placeholder of hash characters
`**#**` of the same length as the digits of the number to be replaced. Files which
include a counter of variable length (e.g. `image_9.tif`, `image_10.tif`, etc.)
should use a placeholder of the minimum length of the counter.

The *First pattern number* is the first number that should be used in the
scan/file naming pattern. The index stepping of filenames defines by how much the
counter should be incremented for each file.

Programmatic access
^^^^^^^^^^^^^^^^^^^
For accessing the ScanContext parameters programmatically, the following keys 
must be used:

.. list-table::
    :widths: 40 40
    :class: tight-table
    :header-rows: 1

    * - item
      - reference key
    * - Scan/file naming pattern
      - scan_name_pattern
    * - First filename number
      - pattern_number_offset
    * - Index stepping of filenames
      - pattern_number_delta



An example of modifying the scan/file naming pattern programmatically is shown below:

.. code-block::

    Scan = pydidas.contexts.ScanContext()
    Scan.set_param(scan_name_pattern, image_####.tif)
    Scan.set_param(pattern_number_offset, 1)

Examples
^^^^^^^^

.. list-table::
    :widths: 26 12 12 50
    :class: tight-table
    :header-rows: 1

    * - naming pattern
      - first number
      - index stepping
      - resulting filenames
    * - image_####.tif
      - 1
      - 1
      - image_0001.tif, image_0002.tif, image_0003.tif, ...
    * - image_##.tif
      - 0
      - 10
      - image_00.tif, image_10.tif, ..., image_90.tif, image_100.tif, ...
    * - scan_42_######_data.h5
      - 3
      - 3
      - scan_42_00003_data.h5, scan_42_00006_data.h5, ...
    * - scan_42a_#.fio
      - 0
      - 5
      - scan_42a_0.fio, scan_42a_5.fio, scan_42a_10.fio, scan_42a_15.fio, ...
