TOOLTIPS = {
    'live_processing': ('Set live processing to True if the files do not yet '
                        'exist at process startup. This will skip checks on'
                        'file existence and size.'),
    'label': ('A label for identifying the Plugin in the results. '
              'Internally, all Plugins are identified by their node IDs, this'
              ' additional label is merely a handle for easier human '
              'identification.'),
    'filename': 'The file name of the input file.',
    'first_file': ('The name of the first file for a file series or of the '
                   'hdf5 file in case of hdf5 file input.'),
    'last_file': ('Used only for file series: The name of the last file '
                  'to be added to the composite image.'),
    'file_stepping': ('The step width (in files), A value n > 1 will only'
                      ' process every n-th file for the composite.'),
    'hdf5_key': ('Used only for hdf5 files: The dataset key.'),
    'hdf5_dataset_shape': ('The shape of the hdf5 dataset. This corresponds '
                           'to (number of images, image size y, '
                           'image size x).'),
    'hdf5_first_image_num': ('The first image in the hdf5-dataset to be '
                             'used.'),
    'hdf5_last_image_num': ('The last image in the hdf5-dataset to be used. '
                            'The value -1 will default to the last image.'),
    'hdf5_stepping': ('The step width (in frames). A value n > 1 will only'
                       ' process every n-th frame.'),
    'use_bg_file': ('Keyword to toggle usage of background subtraction.'),
    'bg_file': ('The name of the file used for background correction.'),
    'bg_hdf5_key': ('For hdf5 background image files: The dataset key.'),
    'bg_hdf5_frame': ('For hdf5 background image files: The image number in '
                      'the dataset'),
    'n_image': ('The toal number of images in the composite images.'),
    'n_files': ('The toal number of selected files.'),
    'composite_nx': ('The number of original images combined in the composite'
                     ' image in x direction. A value of -1 will determine the'
                     ' number of images in x direction automatically based on'
                     ' the number of images in y direction.'),
    'composite_ny': ('The number of original images combined in the composite'
                     ' image in y direction. A value of -1 will determine the'
                     ' number of images in y direction automatically based on'
                     ' the number of images in x direction.'),
    'composite_dir': ('The "fast" direction of the composite image. This '
                      'dimension will be filled first before going to the'
                      ' next row/column.'),
    'use_roi': ('Keyword to toggle use of the ROI for cropping the original '
                'images before combining them.'),
    'roi_xlow': ('The lower boundary (in pixel) for cropping images in x, if'
                 ' use_roi is enabled. Negative values will be modulated with'
                 ' the image width.'),
    'roi_xhigh': ('The upper boundary (in pixel) for cropping images in x, if'
                  ' use_roi is enabled. Negative values will be modulated '
                  'with the image width, i.e. -1 is equivalent with the full '
                  'image size.'),
    'roi_ylow': ('The lower boundary (in pixel) for cropping images in y, if'
                 ' use_roi is enabled. Negative values will be modulated with'
                 ' the image width.)'),
    'roi_yhigh': ('The upper boundary (in pixel) for cropping images in y, if'
                  ' use_roi is enabled. Negative values will be modulated '
                  'with the image height, i.e. -1 is equivalent with the '
                  'full image size.'),
    'use_thresholds': ('Keyword to toggle use of the thresholds for clipping '
                       'the data range in the original images before '
                       'combining them. '),
    'threshold_low': ('The lower threshold of the composite image. If any '
                      'finite value (i.e. not np.nan) is used, any pixels '
                      'with a value below the threshold will be replaced by '
                      'the threshold. A value of np.nan will ignore the '
                      'threshold.'),
    'threshold_high': ('The upper threshold of the composite image. If any '
                       'finite value (i.e. not np.nan) is used, any pixels '
                       'with a value above the threshold will be replaced by '
                       'the threshold. A value of np.nan will ignore the '
                       'threshold.'),
    'binning': ('The re-binning factor for the images in the composite. The '
                'binning will be applied to the cropped images. The default '
                'is 1.'),
    'images_per_file': ('The number of images in the file. For hdf5 files, '
                        'this corresponds to the number of frames in the hdf5'
                        ' dataset.'),
    'image_shape': ('The shape of an image.'),
    'raw_image_shape': ('The image shape of the original image as loaded from'
                        ' the file.'),
    'datatype': ('The datatype.'),
    'xray_wavelength': ('The X-ray wavelength (in Angstrom). Any changes to '
                        'the wavelength will also update the X-ray energy '
                        'setting.'),
    'xray_energy':  ('The X-ray energy (in keV). Changing this parameter '
                         'will also update the X-ray wavelength setting.'),
    'detector_name': ('The detector name in pyFAI nomenclature.'),
    'detector_npixx': ('The number of detector pixels in x direction '
                       '(horizontal).'),
    'detector_npixy': ('The number of detector pixels in y direction '
                       '(vertical).'),
    'detector_sizex': 'The detector pixel size in X-direction in micrometer.',
    'detector_sizey': 'The detector pixel size in Y-direction in micrometer.',
    'detector_dist': 'The sample-detector distance (in m).',
    'detector_poni1': ('The detector PONI1 (point of normal incidence; '
                       'in y direction). This is measured in meters from the'
                       ' detector origin.'),
    'detector_poni2': ('The detector PONI2 (point of normal incidence; '
                       'in x direction). This is measured in meters from the'
                       ' detector origin.'),
    'detector_rot1': ('The detector rotation 1 (lefthanded around the '
                      '"up"-axis), given in rad.'),
    'detector_rot2': ('The detector rotation 2 (pitching the detector; '
                      'positive direction is tilting the detector towards the'
                      ' floor, i.e. left-handed), given in rad.'),
    'detector_rot3': ('The detector rotation 3 (around the beam axis; '
                      'right-handed when looking downstream with the beam.)'
                      ', given in rad.'),
    'scan_dim': ('The scan dimensionality. This defines the number of '
                 'processed dimensions.'),
    'scan_name': ('The scan name or title. This is used exclusively for '
                  'reference in result exporters.'),
    'scan_dir_1': ('The axis name for scan direction 1. This information'
                   ' will only be used for labelling.'),
    'n_points_1': 'The number of scan points in scan direction 1.',
    'delta_1': 'The step width between two scan points in  scan direction 1.',
    'unit_1': ('The unit of the movement / steps / offset in scan '
               'direction 1.'),
    'offset_1': ('The coordinate offset of the movement in scan '
                 'direction 1 (i.e. the counter / motor position for '
                 'scan position 0).'),
    'scan_dir_2': ('The axis name for scan direction 2. This information'
                   ' will only be used for labelling.'),
    'n_points_2': 'The number of scan points in scan direction 2.',
    'delta_2': 'The step width between two scan points in scan direction 2.',
    'unit_2': ('The unit of the movement / steps / offset in scan '
               'direction 2.'),
    'offset_2': ('The coordinate offset of the movement in scan '
                 'direction 2 (i.e. the counter / motor position for '
                 'scan position 0).'),
    'scan_dir_3': ('The axis name for scan direction 3. This information'
                   ' will only be used for labelling.'),
    'n_points_3': 'The number of scan points in scan direction 3.',
    'delta_3': 'The step width between two scan points in scan direction 3.',
    'unit_3': ('The unit of the movement / steps / offset in scan '
               'direction 3.'),
    'offset_3': ('The coordinate offset of the movement in scan '
                 'direction 3 (i.e. the counter / motor position for '
                 'scan position 0).'),
    'scan_dir_4': ('The axis name for scan direction 4. This information'
                   ' will only be used for labelling.'),
    'n_points_4': 'The number of scan points in scan direction 4.',
    'delta_4': ('The step width between two scan points in'
                ' scan direction 4.'),
    'unit_4': ('The unit of the movement / steps / offset in scan '
               'direction 4.'),
    'offset_4': ('The coordinate offset of the movement in scan '
                 'direction 4 (i.e. the counter / motor position for '
                 'scan position 0).'),
    'scan_index1': 'The position index for the scan dimension 1.',
    'scan_index2': 'The position index for the scan dimension 2.',
    'scan_index3': 'The position index for the scan dimension 3.',
    'scan_index4': 'The position index for the scan dimension 4.',
    'image_num': 'The image number to be processed.',
    'mp_n_workers': ('The number of multiprocessing workers. Note that'
                     ' this number should not be set too high for two '
                     'reasons:\n1. File reading processes interfere with '
                     'each other if too many are active at once.\n2. pyFAI'
                     ' uses Parallelization as well and you can only gain '
                     'limited performance increases for multiple parallel'
                     ' processes.'),
    'shared_buffer_size': ('A shared buffer is used to efficiently transport'
                           ' data between the main App and multiprocessing '
                           'Processes. This buffer must be large enough to '
                           'store at least one instance of all result data.'),
    'shared_buffer_max_n': ('The maximum number of datasets in the buffer. '
                            'A dataset consists of all results for one frame. '
                            'For performance reasons, the buffer should not '
                            'be too large.'),
    'det_mask': 'The path to the detector mask file.',
    'det_mask_val': ('The value to be used for the pixels masked on the '
                     'detector. Note that this value will only be used '
                     'for displaying the images. For pyFAI integration, '
                     'the pixels will be fully masked and not be '
                     'included.'),
    'mosaic_border_width': ('The width of the border inserted between '
                            'adjacent frames in the mosaic creation.'),
    'mosaic_border_value': ('The value to be put in the border pixels in '
                            'mosaics.'),
    'mosaic_max_size': ('The maximum size (in Mpx) of mosaic images.'),

    'use_global_mask': ('Select "True" to use the global settings for the '
                        'detector mask and mask value. A "False" settings '
                        'uses the local mask settings. Note: The mask value'
                        ' will not be used for integrating but only for '
                        'presentation.'),
    'run_type': ('Specify how the processing shall be performed. It can be'
                 ' either called from the GUI, command line or remotely.'),
    'int_rad_npoint': ('The number of bins in radial direction for the '
                       'pyFAI integration.'),
    'int_rad_unit': ('The unit and type of the azimuthal profile.'),
    'int_rad_use_range': ('Toggle to limit the radial integration range or '
                          'use the full data range. If True, boundaries need '
                          'to be defined in the lower and upper radial range '
                          'Parameters.'),
    'int_rad_range_lower': ('The lower boundary of the radial integration '
                            'range.  This setting is only used if "Use radial'
                            ' range" is  True. This value needs to be given '
                            'in the unit selected as radial unit.'),
    'int_rad_range_upper': ('The upper boundary of the radial integration '
                            'range.  This setting is only used if "Use radial'
                            'range" is  True. This value needs to be given '
                            'in the unit selected as radial unit.'),
    'int_azi_npoint': ('The number of bins in azimuthal direction for the '
                       'pyFAI integration.'),
    'int_azi_unit': 'The unit and type of the azimuthal profile.',
    'int_azi_use_range': ('Toggle to limit the azimuthal integration range '
                          'or use  the full data range. If True, boundaries '
                          'need to be defined in the lower and upper '
                          'azimuthal range Parameters.'),
    'int_azi_range_lower': ('The lower boundary of the azimuthal integration '
                            'range. This setting is only used if "Use '
                            'azimuthal range" is True. This value needs to be'
                            ' given in the unit selected as azimuthal unit.'),
    'int_azi_range_upper': ('The upper boundary of the azimuthal integration'
                            ' range. This setting is only used if "Use '
                            'azimuthal range" is True. This value needs to be'
                            ' given in the unit selected as azimuthal unit.'),
    'int_method': ('The integration method. For a full reference, please'
                   ' visit the pyfai documentation available at: '
                   'https://pyfai.readthedocs.io/'),
    'autosave_results': ('Save the results automatically after finishing'
                         ' processing. The results for each plugin will be'
                         ' saved in a separete file (or files if multiple '
                         'formats have been selected).'),
    'autosave_dir': 'The directory for autosave files.',
    'autosave_format': ('The file format(s) for the data to be saved after '
                        'the workflow has been excuted. All data will be saved'
                        ' in a single folder for each run with one file for '
                        'each plugin.'),
    'selected_results': ('The selected node of the WorkflowTree to display'
                         ' the corresponding results.'),
}
