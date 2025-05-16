..
    This file is licensed under the
    Creative Commons Attribution 4.0 International Public License (CC-BY-4.0)
    Copyright 2023 - 2025, Helmholtz-Zentrum Hereon
    SPDX-License-Identifier: CC-BY-4.0


    - live_processing (bool, default: False)
        Keyword to toggle live processing which means file existance and size 
        checks will be disabled in the setup process and the file processing 
        will wait for files to be created (indefinitely). 
    - first_file (Union[str, pathlib.Path], default: Path() [empty path])
        The name of the first file for a file series or of the hdf5 file in 
        case of hdf5 file input.
    - last_file (Union[str, pathlib.Path], default: Path() [empty path])
        Used only for file series: The name of the last file to be added to the 
        composite image. 
    - file_stepping (int, default: 1)
        The step width (in files). A value n > 1 will only process every n-th 
        image for the composite.
    - hdf5_key (type: Hdf5key, default: entry/data/data)
        Used only for hdf5 files: The dataset key. 
    - hdf5_first_image_num (type: int, default: 0)
        The first image in the hdf5-dataset to be used. 
    - hdf5_last_image_num (type: int, default: -1)
        The last image in the hdf5-dataset to be used. The value -1 will
        default to the last image in the file. 
    - hdf5_stepping (type: int, default: 1)
        The step width (in images) of hdf5 datasets. A value n > 1 will only
        add every n-th image to the composite. 
    - use_bg_file (type: bool, default: False)
        Keyword to toggle usage of background subtraction. 
    - bg_file (type: Union[str, pathlib.Path], default: Path() [empty path])
        The name of the file used for background correction. 
    - bg_hdf5_key (type: Hdf5key, default: entry/data/data)
        Required for hdf5 background image files: The dataset key with the
        image for the background file. 
    - bg_hdf5_frame (type: int, default: 0)
        Required for hdf5 background image files: The image number of the
        background image in the dataset.
    - use_global_det_mask (type: bool, default: True
        Keyword to enable or disable using the global detector mask as
        defined by the global mask file and mask value.
    - use_roi (type: bool, default: False)
        Keyword to toggle use of the ROI for cropping the original images
        before combining them. 
    - roi_xlow (type: int, default: 0)
        The lower boundary (in pixel) for cropping images in x, if use_roi is
        enabled. Negative values will be modulated with the image width.
    - roi_xhigh (type: Union[int, None], default: None)
        The upper boundary (in pixel) for cropping images in x, if use_roi is
        enabled. Negative values will be modulated with the image width, i.e.
        -1 is equivalent to the full image size minus one. None corresponds
        to the full image width (with respect to the upper boundary).
    - roi_ylow (type: int, default: 0)
        The lower boundary (in pixel) for cropping images in y, if use_roi is
        enabled. Negative values will be modulated with the image width.
    - roi_yhigh (type: Union[int, None], default: None)
        The upper boundary (in pixel) for cropping images in y, if use_roi is
        enabled. Negative values will be modulated with the image width, i.e.
        -1 is equivalent to the full image size minus one. Use None to
        select the full range. 
    - use_thresholds (type: bool, default: False)
        Keyword to enable or disable the use of thresholds. If True,
        threshold use is enabled and both threshold values will be used. 
    - threshold_low (type: int, default: None)
        The lower threshold of the composite image. If any finite value
        (i.e. not np.nan or None) is used, the value of any pixels with a value
        below the threshold will be replaced by the threshold value. A value
        of np.nan or None will ignore the threshold. 
    - threshold_high (type: int, default: None)
        The upper threshold of the composite image. If any finite value
        (i.e. not np.nan or None) is used, the value of any pixels with a value
        above the threshold will be replaced by the threshold value. A value
        of np.nan or None will ignore the threshold. 
    - binning (type: int, default: 1)
        The re-binning factor for the images in the composite. The binning
        will be applied to the cropped images. 
    - composite_nx (type: int, default: 1)
        The number of original images combined in the composite image in
        x direction. A value of -1 will determine the number of images in
        x direction automatically based on the number of images in y
        direction. 
    - composite_ny (type: int, default: -1)
        The number of original images combined in the composite image in
        y direction. A value of -1 will determine the number of images in
        y direction automatically based on the number of images in x
        direction.
    - composite_image_op (type: str, default: None)
        The image operation applied to each raw image prior to merging it in 
        the composite image. This allows to adjust the image orientation with 
        respect to the scan.
    - composite_xdir_orientation (type: str, default: left-to-right)
        The direction of how images are inserted into the composite in x 
        direction. Left-to-right starts with low indices (python standard) 
        whereas right-to-left will insert image at the max index position first.
    - composite_ydir_orientation (type: str, default: left-to-right)
        The direction of how images are inserted into the composite in y 
        direction. Top-to-bottom starts with low indices (python standard)
        whereas bottom-to-top will insert image at the max index position 
        first. Note that the display may be flipped with the origin at the 
        bottom.