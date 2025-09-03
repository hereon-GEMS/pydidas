..
    This file is licensed under the
    Creative Commons Attribution 4.0 International Public License (CC-BY-4.0)
    Copyright 2023 - 2025, Helmholtz-Zentrum Hereon
    SPDX-License-Identifier: CC-BY-4.0

List of all ScanContext Parameters
----------------------------------

- scan_title (type: str, default: , unit: )
    The scan name or title. This is used exclusively for reference in result
    exporters.
- scan_base_directory (type: Path, default: , unit: )
    The absolute path of the base directory in which to find this scan. Note that
    individual plugins may automatically discover and use subdirectories. Please
    refer to the specific InputPlugin in use for more information.
- scan_name_pattern (type: Path, default: , unit: )
    The pattern used for naming scan (files). Use hashes '#' for wildcards which
    will be filled in with numbers for the various files. Note that individual
    plugins may use this Parameter for either directory or file names. Please refer
    to the specific InputPlugin in use for more information.
- pattern_number_offset (type: int, default: 0, unit: )
    The first number in the pattern to be used in processing. This number will be
    applied as offset in the scan naming pattern to identify the respective filename
    for scan points. For example, if the first file is named `scan_0001.h5`, the
    offset should be set to 1.
- pattern_number_delta (type: int, default: 1, unit: )
    The difference in the index between two consecutive pattern points. A value of 1
    would mean that each index is processed in the pattern whereas a value of n
    would mean that only every n-th index (e.g. filename) is processed.For example,
    a value of 3 would process the files with the names `scan_0000.h5`,
    `scan_0003.h5`, `scan_0006.h5` etc.
- frame_indices_per_scan_point (type: int, default: 1, unit: )
    The number of frame indices (in frames) between two scan points. A value of 1
    would increment the image index by 1 for each scan point whereas a value of n
    corresponds to only using every n-th index. For example, a value of 3 frame
    indices per scan point process the frame 0 for scan point 0, frame 3 for scan
    point 1 etc.Please note that the index stepping refers to the frames, not the
    filenames. In the case of container files (e.g. hdf5), the index stepping will
    skip process every n-th frame, not every n-th file.
- scan_multi_frame_handling (type: str, default: Average, unit: )
    Define the handling of images if multiple images were acquired per scan point.
    If all individual images should be kept, please set the scan multiplicity to 1
    and add an additional dimension with the multiplicity to the scan.
- scan_frames_per_point (type: int, default: 1, unit: )
    The number of frames to process at *each* scan point. The default of `1`
    corresponds to one image per scan point. Please note that the value for the
    points. If this setting is used for `averaging` images, please reduce the number
    of scan points correspondingly.

The following Parameters exist for each scan dimension, i.e. scan_dim{i}_label 
stands for scan_dim0_label, scan_dim1_label, scan_dim2_label, 
scan_dim3_label. For clarity, only the generic form is described here.

- scan_dim{i}_label (type: str, default: "")
    The axis name for scan direction *{i}*. This information will only be used
    for labelling.
- scan_dim{i}_n_points (type: int, default: 0)
    The number of scan points in scan direction *{i}*.
- scan_dim{i}_delta (type: float, default: 1)
    The step width between two scan points in scan direction *{i}*.
- scan_dim{i}_offset (type: float, default: 0)
    The coordinate offset of the movement in scan direction *{i}* (i.e. the
    counter / motor position for scan step #0).
- scan_dim{i}_unit (type: str, default: "")
    The unit of the movement / steps / offset in scan direction *{i}*.
