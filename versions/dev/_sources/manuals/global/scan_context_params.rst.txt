..
    This file is licensed under the
    Creative Commons Attribution 4.0 International Public License (CC-BY-4.0)
    Copyright 2023 - 2025, Helmholtz-Zentrum Hereon
    SPDX-License-Identifier: CC-BY-4.0

List of all ScanContext Parameters
----------------------------------

- scan_dim (type: int, default: 2, unit: "")
    The scan dimensionality. This defines the number of processed dimensions.
- scan_title (type: str, default: "", unit: "")
    The scan name or title. This is used exclusively for reference in axis 
    labels and result exporters.
- scan_base_directory (type: Path, default: ".", unit: "")
    The base directory in which the raw scan data is stored. 
- scan_name_pattern (type: str, default: "", unit: "")
    The name pattern for scan files, subdirectories etc. User hashes ("#") to
    mark wildcard characters to be filled in with the current index.
- scan_start_index (type: int, default: 0, unit: "")
    The starting index for files etc. of the first point in the scan.
- scan_index_stepping (type: int, default: 1, unit: "")
    The stepping of the index, i.e. the difference in the index between two 
    adjacent scan points.
- scan_multiplicity (type: int, default: 1, unit: "")
    The image multiplicity: The number of frames acquired at each unique scan
    point. Use this value only if the multiple images should be combined. 
    Otherwise, use an additional scan dimension for the multiplicity.
- scan_multi_image_handling (type: str, default: "Average", unit: "")
    The handling instructions for multiple frames at each scan point. Can be
    either "Average" or "Sum".

The following Parameters exist for each scan dimension, i.e. scan_dim\ *{i}*\ 
_label stands for scan_dim0_label, scan_dim1_label, scan_dim2_label, 
scan_dim3_label. For clarity, only the generic form is described here.

- scan_dim\ *{i}*\ _label (type: str, default: "")
    The axis name for scan direction *{i}*. This information will only be used
    for labelling.
- scan_dim\ *{i}*\ _n_points (type: int, default: 0)
    The number of scan points in scan direction *{i}*.
- scan_dim\ *{i}*\ _delta (type: float, default: 1)
    The step width between two scan points in scan direction *{i}*.
- scan_dim\ *{i}*\ _offset (type: float, default: 0)
    The coordinate offset of the movement in scan direction *{i}* (i.e. the
    counter / motor position for scan step #0).
- scan_dim\ *{i}*\ _unit (type: str, default: "")
    The unit of the movement / steps / offset in scan direction *{i}*.

