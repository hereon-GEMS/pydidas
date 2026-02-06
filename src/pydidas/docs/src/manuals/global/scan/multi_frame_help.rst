..
    This file is licensed under the
    Creative Commons Attribution 4.0 International Public License (CC-BY-4.0)
    Copyright 2025 - 2026, Helmholtz-Zentrum Hereon
    SPDX-License-Identifier: CC-BY-4.0

.. _multi_frame_help:

Explanations of Scan multi-frame handling
-----------------------------------------


The multi-frame handling allows to specify how individual (detector) frames are 
assigned to *scan points*, i.e. to the scanned grid of time and/or motor positions.

The parameter *Frame index stepping per scan point* defines how the global frame
counter is incremented for each scan point. For example, if the value is set to 1,
the frame counter will be incremented by 1 for each scan point. This corresponds to a 
1:1 relation between scan points and data frames. At a value of 3, the frame counter 
would be incremented by 3 for each scan point, i.e. scan point #0 would use frame #0, 
scan point #1 would use frame #3, etc. 

The *Frames to process per scan point* determines how many frames are processed
at each scan point. If this value larger than 1, the *Frame index stepping per 
scan point* will determine the first frame index that is used for the scan point.

The *Multi-frame handling* parameter defines how the individual frames should be
processed for each scan point. The given operation will be applied per pixel. Note 
that this parameter is only relevant if the *Frames to process per scan point*
is larger than 1. The options are:

    - **Average**: The average of the frames is calculated and assigned to the 
      scan point.
    -  **Sum**: The sum of the frames is calculated and assigned to the scan point.
    - **Maximum**: The maximum of the frames is calculated and assigned to the scan
      point.
    - **Stack**: The individual frames are loaded and an image stack is created and
      assigned to the scan point. This will result in a multi-dimensional dataset.

**Note:** The multi-frame handling applies to the individual frame, not files.
Files with multiple frames per file, e.g. HDF5 files, are compatible because the 
frames in each file are treated individually.

**Note: If multiple frames are processed at each scan point, the number of scan
points must be reduced accordingly.** For example, if 30 frames have been acquired
and 3 frames are processed at each scan point, the number of scan points cannot be
larger than 10. If n_frames is the total number of frames, delta is the increment of
the frame index per scan point, and m_frames is the number of frames processed at
each scan point, the maximum number of scan points is given by:
``max_scan_points = 1 + (n_frames - m_frames) / delta``, rounded down to the nearest
integer. Please consult the table below for examples of how
the number of scan points must be adjusted depending on the parameters:


+----------------+------------------------+---------------------+----------------------+
| Total number   | Frame index stepping   | Frames to process   | Maximum number       |
| of frames      | per scan point         | per scan point      | of scan points       |
+================+========================+=====================+======================+
| 30             | 1                      | 1                   | 30                   |
+----------------+------------------------+---------------------+----------------------+
| 30             | 3                      | 1                   | 10                   |
+----------------+------------------------+---------------------+----------------------+
|                | If only every third frame is used, the maximum number of            |
|                | scan points must be divided by 3.                                   |
+----------------+------------------------+---------------------+----------------------+
| 30             | 1                      | 3                   | 28                   |
+----------------+------------------------+---------------------+----------------------+
|                | If 3 frames are processed at each scan point, the maximum number of |
|                | scan points must be reduced by 2. The scan point #27 (*) will use   |
|                | the frames #27, #28, and #29 and scan point #29 would require up to |
|                | frame #30.                                                          |
|                |                                                                     |
|                | (*) Note that counting starts at 0, i.e. #27 is the 28th scan point.|
+----------------+------------------------+---------------------+----------------------+
| 30             | 4                      | 6                   | 7                    |
+----------------+------------------------+---------------------+----------------------+
|                | Because 6 frames are processed at each scan point, the maximum      |
|                | number of scan points must be reduced by 6. Since the frame index   |
|                | is incremented by 4 for each scan point, the maximum number of scan |
|                | points must be divided by 4. Finally, add one for the initial       |
|                | point. Therefore, a total of 1 + (30 - 6) / 4 = 1 + 6 = 7           |
|                | scan points can be used. The last scan point #6 (*) will            |
|                | use the frames #24, #25, #26, #27, #28, and #29. The scan point #7  |
|                | would require images up to frame #33 which are not available (**).  |
|                |                                                                     |
|                | (*) Note that counting starts at 0, i.e. #6 is the 7th scan point.  |
|                |                                                                     |
|                | (**) The 30 frames include the frames #0 to #29.                    |
+----------------+------------------------+---------------------+----------------------+


Examples
^^^^^^^^

The following examples are meant to provide some hands-on guidance on the
practical use of the multi-frame handling parameters.

+-------+----------------+------------------------+---------------------+-------------+
|       | Scan/file      | Frame index stepping   | Frames to process   | Multi-frame |
|       | naming pattern | per scan point         | per scan point      | handling    |
+=======+================+========================+=====================+=============+
| Acquisition of multiple frames per scan point: In this example, multiple frames     |
| are acquired per scan point, and the sum of the frames is required:                 |
+-------+----------------+------------------------+---------------------+-------------+
|       | image_####.tif | 3                      | 3                   | Sum         |
+-------+----------------+------------------------+---------------------+-------------+
|       | These settings will result in the following data usage:                     |
|       |                                                                             |
|       | Scan point #0: sum(image_0000.tif, image_0001.tif, image_0002.tif)          |
|       |                                                                             |
|       | Scan point #1: sum(image_0003.tif, image_0004.tif, image_0005.tif)          |
|       |                                                                             |
|       | etc.                                                                        |
+-------+----------------+------------------------+---------------------+-------------+
| Analysis with rolling average over multiple scan points: In this example, one frame |
| is acquired per scan point, but the frames of multiple scan points are used to      |
| calculate a rolling average.                                                        |
+-------+----------------+------------------------+---------------------+-------------+
|       | image_####.tif | 1                      | 3                   | Average     |
+-------+----------------+------------------------+---------------------+-------------+
|       | These settings will result in the following data usage:                     |
|       |                                                                             |
|       | Scan point #0: mean(image_0000.tif, image_0001.tif, image_0002.tif)         |
|       |                                                                             |
|       | Scan point #1: mean(image_0001.tif, image_0002.tif, image_0003.tif)         |
|       |                                                                             |
|       | etc.                                                                        |
+-------+----------------+------------------------+---------------------+-------------+
| Analysis with rolling average over multiple scan points for groups of scan points:  |
| In this example, the acquisition is performed in groups of 4 images per scan point, |
| and a rolling average over 2 scan points is processed as output.                    |
+-------+----------------+------------------------+---------------------+-------------+
|       | data_##.npy    | 4                      | 8                   | Average     |
+-------+----------------+------------------------+---------------------+-------------+
|       | These settings will result in the following data usage:                     |
|       |                                                                             |
|       | Scan point #0: mean(data_00.npy, data_01.npy, data_02.npy, data_03.npy)     |
|       |                                                                             |
|       | Scan point #1: mean(data_04.npy, data_05.npy, data_06.npy, data_07.npy)     |
|       |                                                                             |
|       | etc.                                                                        |
+-------+----------------+------------------------+---------------------+-------------+
| Analysis with four acquisition per scan point which need to be processed            |
| individually further along the pipeline. The `Stack` option will result in a        |
| 3-dimensional dataset of shape (4, det_y, det_x).                                   |
+-------+----------------+------------------------+---------------------+-------------+
|       | data_##.npy    | 4                      | 4                   | Stack       |
+-------+----------------+------------------------+---------------------+-------------+
|       | These settings will result in the following data usage:                     |
|       |                                                                             |
|       | Scan point #0: array([data_00.npy, data_01.npy, data_02.npy, data_03.npy])  |
|       |                                                                             |
|       | Scan point #1: array([data_04.npy, data_05.npy, data_06.npy, data_07.npy])  |
|       |                                                                             |
|       | etc.                                                                        |
+-------+----------------+------------------------+---------------------+-------------+
| Using a single HDF5 file: In this example, the  ::<num> syntax is used to specify   |
| the index of frames to be processed at each scan point.                             |
+-------+----------------+------------------------+---------------------+-------------+
|       | data_AB.h5     | 4                      | 4                   | Average     |
+-------+----------------+------------------------+---------------------+-------------+
|       | These settings will result in the following data usage:                     |
|       |                                                                             |
|       | Scan point #0: mean(data_AB.h5::0, data_AB.h5::1, data_AB.h5::2,            |
|       | data_AB.h5::3)                                                              |
|       |                                                                             |
|       | Scan point #1: mean(data_AB.h5::4, data_AB.h5::5, data_AB.h5::6,            |
|       | data_AB.h5::7)                                                              |
|       |                                                                             |
|       | etc.                                                                        |
+-------+----------------+------------------------+---------------------+-------------+


Programmatic access
^^^^^^^^^^^^^^^^^^^

For accessing the ScanContext parameters programmatically, the following keys
must be used:

An example of modifying the scan/file naming pattern programmatically is shown below:

.. code-block::

    Scan = pydidas.contexts.ScanContext()
    Scan.set_param("frame_indices_per_scan_point", "5")
    Scan.set_param("scan_frames_per_point", 2)
    Scan.set_param("scan_multi_frame_handling", "Sum")
