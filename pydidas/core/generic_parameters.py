# This file is part of pydidas.

# pydidas is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.

# Foobar is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE. See the
# GNU General Public License for more details.

# You should have received a copy of the GNU General Public License
# along with Foobar.  If not, see <http://www.gnu.org/licenses/>.

"""
Module with a GENERIC_PARAMS dictionary which includes Parameters which
are being used several times."""

__author__      = "Malte Storm"
__copyright__   = "Copyright 2021, Malte Storm, Helmholtz-Zentrum Hereon"
__license__ = "GPL-3.0"
__version__ = "0.0.0"
__maintainer__ = "Malte Storm"
__status__ = "Development"
__all__ = ['GENERIC_PARAMS', 'get_generic_parameter']

from pathlib import Path
import numpy as np

from .parameter import Parameter
from .hdf_key import HdfKey
from .parameter_collection import ParameterCollection
from ..constants.generic_parameter_tooltips import TOOLTIPS

GENERIC_PARAMS = ParameterCollection(
    ###################################
    ## Generic processing paramters
    ###################################
    Parameter('live_processing', int, 0, name='Live processing',
              choices=[True, False], tooltip=TOOLTIPS['live_processing']),
    ###################################
    ## Parameters for CompositeCreation
    ###################################
    Parameter('first_file', Path, Path(), name='First file name',
      tooltip=TOOLTIPS['first_file']),
    Parameter('last_file', Path, Path(), name='Last file name',
        tooltip=TOOLTIPS['last_file']),
    Parameter('file_stepping', int, 1, name='File stepping',
              tooltip=TOOLTIPS['file_stepping']),
    Parameter('hdf5_key', HdfKey, HdfKey('/entry/data/data'),
              name='Hdf dataset key', tooltip=TOOLTIPS['hdf5_key']),
    Parameter('hdf5_dataset_shape', tuple, (0, 0, 0),
              name='Hdf5 dataset shape',
              tooltip=TOOLTIPS['hdf5_dataset_shape']),
    Parameter('hdf5_first_image_num', int, 0, name='First image number',
              tooltip=TOOLTIPS['hdf5_first_image_num']),
    Parameter('hdf5_last_image_num', int, -1, name='Last image number',
              tooltip=TOOLTIPS['hdf5_last_image_num']),
    Parameter('hdf5_stepping', int, 1, name='Hdf5 dataset stepping',
              tooltip=TOOLTIPS['hdf5_stepping']),
    Parameter('use_bg_file', int, 0, name='Subtract background image',
              choices=[True, False], tooltip=TOOLTIPS['use_bg_file']),
    Parameter('bg_file', Path, Path(), name='Background image file',
              tooltip=TOOLTIPS['bg_file']),
    Parameter('bg_hdf5_key', HdfKey, HdfKey('/entry/data/data'),
              name='Background Hdf dataset key',
              tooltip=TOOLTIPS['bg_hdf5_key']),
    Parameter('bg_hdf5_frame', int, 0, name='Background image number',
              tooltip=TOOLTIPS['bg_hdf5_frame']),
    Parameter('n_image', int, 0, name='Total number of images',
              tooltip=TOOLTIPS['n_image']),
    Parameter('n_files', int, 0, name='Total number of files',
              tooltip=TOOLTIPS['n_files']),
    Parameter('composite_nx', int, 1, name='Number of images in x',
              tooltip=TOOLTIPS['composite_nx']),
    Parameter('composite_ny', int, -1, name='Number of images in y',
              tooltip=TOOLTIPS['composite_ny']),
    Parameter('composite_dir', str, 'x',
              name='Preferred composite direction', choices=['x', 'y'],
              tooltip=TOOLTIPS['composite_dir']),
    Parameter('use_roi', int, 0, name='Use ROI', choices=[True, False],
              tooltip=TOOLTIPS['use_roi']),
    Parameter('roi_xlow', int, 0, name='ROI lower x limit',
              tooltip=TOOLTIPS['roi_xlow']),
    Parameter('roi_xhigh', int, -1, name='ROI upper x limit',
              tooltip=TOOLTIPS['roi_xhigh']),
    Parameter('roi_ylow', int, 0, name='ROI lower y limit',
              tooltip=TOOLTIPS['roi_ylow']),
    Parameter('roi_yhigh', int, -1, name='ROI upper y limit',
              tooltip=TOOLTIPS['roi_yhigh']),
    Parameter('use_thresholds', int, 0, name='Use Thresholds',
              choices=[True, False], tooltip=TOOLTIPS['use_thresholds']),
    Parameter('threshold_low', float, np.nan, name='Lower threshold',
              tooltip=TOOLTIPS['threshold_low']),
    Parameter('threshold_high', float, np.nan, name='Upper threshold',
              tooltip=TOOLTIPS['threshold_high']),
    Parameter('binning', int, 1, name='Binning factor',
              tooltip=TOOLTIPS['binning']),
    Parameter('images_per_file', int, 0, name='Images per file',
              tooltip=TOOLTIPS['images_per_file']),
    Parameter('image_shape', tuple, (0, 0), name='Image shape',
              tooltip=TOOLTIPS['image_shape']),
    Parameter('raw_image_shape', tuple, (0, 0), name='Raw image shape',
              tooltip=TOOLTIPS['raw_image_shape']),
    Parameter('datatype', None, np.float32, name='Datatype',
              tooltip=TOOLTIPS['datatype']),
    #################################
    ## Parameters for global geometry
    #################################
     Parameter('xray_wavelength', float, 1, unit='A',
               name='X-ray wavelength', tooltip=TOOLTIPS['xray_wavelength']),
     Parameter('xray_energy', float, 12.398, unit='keV',
               name='X-ray energy', tooltip=TOOLTIPS['xray_energy']),
    Parameter('detector_name', str, 'detector', name='Detector name',
              tooltip=TOOLTIPS['detector_name']),
    Parameter('detector_npixx', int, 0, name='Detector size X',
              unit='px',tooltip=TOOLTIPS['detector_npixx']),
    Parameter('detector_npixy', int, 0, name='Detector size Y', unit='px',
              tooltip=TOOLTIPS['detector_npixy']),
    Parameter('detector_sizex', float, -1, name='Detector pixel size X',
              unit='um',tooltip=TOOLTIPS['detector_sizex']),
    Parameter('detector_sizey', float, -1, name='Detector pixel size Y',
              unit='um', tooltip=TOOLTIPS['detector_sizey']),
    Parameter('detector_dist', float, 1, name='Sample-detector distance',
              unit='m', tooltip=TOOLTIPS['detector_dist']),
    Parameter('detector_poni1', float, 0, unit='m',
              name='Detector PONI1', tooltip=TOOLTIPS['detector_poni1']),
    Parameter('detector_poni2', float, 0, unit='m',
              name='Detector PONI2', tooltip=TOOLTIPS['detector_poni2']),
    Parameter('detector_rot1', float, 0, unit='rad',
              name='Detector Rot1', tooltip=TOOLTIPS['detector_rot1']),
    Parameter('detector_rot2', float, 0, unit='rad',
              name='Detector Rot2', tooltip=TOOLTIPS['detector_rot2']),
    Parameter('detector_rot3', float, 0, unit='rad',
              name='Detector Rot3', tooltip=TOOLTIPS['detector_rot3']),
    ############################
    ## Parameters for scan setup
    ############################
    Parameter('scan_dim', int, 2, name='Scan dimension', choices=[1, 2, 3, 4],
              tooltip=TOOLTIPS['scan_dim']),
    Parameter('scan_dir_1', str, '',
              name='Name of scan direction 1', tooltip=TOOLTIPS['scan_dir_1']),
    Parameter('n_points_1', int, 0, name='Number of scan points (dir. 1)',
              tooltip=TOOLTIPS['n_points_1']),
    Parameter('delta_1', float, 0, name='Step width in direction 1',
              tooltip=TOOLTIPS['delta_1']),
    Parameter('unit_1', str, '', name='Unit of direction 1',unit='',
              tooltip=TOOLTIPS['unit_1']),
    Parameter('offset_1', float, 0, name='Offset of direction 1',
              tooltip=TOOLTIPS['offset_1']),
    Parameter('scan_dir_2', str, '',name='Name of scan direction 2',
            tooltip=TOOLTIPS['scan_dir_2']),
    Parameter('n_points_2', int, 0,name='Number of scan points (dir. 2)',
              tooltip=TOOLTIPS['n_points_2']),
    Parameter('delta_2', float, 0, name='Step width in direction 2',
              tooltip=TOOLTIPS['delta_2']),
    Parameter('unit_2', str, '', name='Unit of direction 2',
              tooltip=TOOLTIPS['unit_2']),
    Parameter('offset_2', float, 0, name='Offset of direction 2',
              tooltip=TOOLTIPS['offset_2']),
    Parameter('scan_dir_3', str, '', name='Name of scan direction 3',
              tooltip=TOOLTIPS['scan_dir_3']),
    Parameter('n_points_3', int, 0, name='Number of scan points (dir. 3)',
              tooltip=TOOLTIPS['n_points_3']),
    Parameter('delta_3', float, 0, name='Step width in direction 3',
              tooltip=TOOLTIPS['delta_3']),
    Parameter('unit_3', str, '', name='Unit of direction 3',
              tooltip=TOOLTIPS['unit_3']),
    Parameter('offset_3', float, 0, name='Offset of direction 3',
              tooltip=TOOLTIPS['offset_3']),
    Parameter('scan_dir_4', str, '', name='Name of scan direction 4',
              tooltip=TOOLTIPS['scan_dir_4']),
    Parameter('n_points_4', int, 0, name='Number of scan points (dir. 4)',
              tooltip=TOOLTIPS['n_points_4']),
    Parameter('delta_4', float, 0, name='Step width in direction 4',
              tooltip=TOOLTIPS['delta_4']),
    Parameter('unit_4', str, '', name='Unit of direction 4',unit='',
            tooltip=TOOLTIPS['unit_4']),
    Parameter('offset_4', float, 0, name='Offset of direction 4',
              tooltip=TOOLTIPS['offset_4']),
    ############################
    ## selected scan indices
    ############################
    Parameter('scan_index1', int, 0, name='Scan dim. 1 index',
              tooltip=TOOLTIPS['scan_index1']),
    Parameter('scan_index2', int, 0, name='Scan dim. 2 index',
              tooltip=TOOLTIPS['scan_index2']),
    Parameter('scan_index3', int, 0, name='Scan dim. 3 index',
              tooltip=TOOLTIPS['scan_index3']),
    Parameter('scan_index4', int, 0, name='Scan dim. 4 index',
              tooltip=TOOLTIPS['scan_index4']),
    Parameter('image_num', int, 0, name='Image number',
              tooltip=TOOLTIPS['image_num']),

    ############################
    ## global app settings
    ############################
    Parameter('mp_n_workers', int, 4, name='Number of MP workers',
              tooltip=TOOLTIPS['mp_n_workers']),
    Parameter('det_mask', Path, Path(), name='Detector mask file',
              tooltip=TOOLTIPS['det_mask']),
    Parameter('det_mask_val', float, 0, name='Detector mask value',
              tooltip=TOOLTIPS['det_mask_val']),
    Parameter('mosaic_border_width', int, 0,
              name='Mosaic tiling border width',
              tooltip=TOOLTIPS['mosaic_border_width']),
    Parameter('mosaic_border_value', float, 0,
              name='Mosaic border value',
              tooltip=TOOLTIPS['mosaic_border_value']),
    Parameter('mosaic_max_size', float, 100,
              name='Mosaic maximum size (Mpx)',
              tooltip=TOOLTIPS['mosaic_max_size']),
    Parameter('run_type', str, 'Process in GUI', name='Run type',
              choices=['Process in GUI', 'Command line',
                       'Remote command line'],
              tooltip=TOOLTIPS['run_type']),
    ############################
    ## global choice settings
    ############################
    Parameter('use_global_mask', int, 1, choices=[True, False],
              name='Use global mask', tooltip=TOOLTIPS['use_global_mask']),
    ############################
    ## pyFAI settings parameters
    ############################
    Parameter('int_rad_npoint', int, 1000,
              name='Num points radial integration',
              tooltip=TOOLTIPS['int_rad_npoint']),
    Parameter('int_rad_unit', str, '2theta / deg',
              choices=['Q / nm^-1', 'Q / A^-1', '2theta / deg',
                       '2theta / rad'], name='Radial unit',
              tooltip=TOOLTIPS['int_rad_unit']),
    Parameter('int_rad_use_range', int, 0, choices=[True, False],
              name='Use radial range', tooltip=TOOLTIPS['int_rad_use_range']),
    Parameter('int_rad_range_lower', int, -1,
              name='Radial lower range',
              tooltip=TOOLTIPS['int_rad_range_lower']),
    Parameter('int_rad_range_upper', int, -1,
              name='Radial upper range',
              tooltip=TOOLTIPS['int_rad_range_upper']),
    Parameter('int_azi_npoint', int, 1000,
              name='Num points azimuthal integration',
              tooltip=TOOLTIPS['int_azi_npoint']),
    Parameter('int_azi_unit', str, 'chi / deg',
              choices=['chi / deg', 'chi / rad'], name='Azimuthal unit',
              tooltip=TOOLTIPS['int_azi_unit']),
    Parameter('int_azi_use_range', int, 0, choices=[True, False],
              name='Use azimuthal range',
              tooltip=TOOLTIPS['int_azi_use_range']),
    Parameter('int_azi_range_lower', int, -1,
              name='Azimuthal lower range',
              tooltip=TOOLTIPS['int_azi_range_lower']),
    Parameter('int_azi_range_upper', int, -1,
              name='Azimuthal upper range',
              tooltip=TOOLTIPS['int_azi_range_upper']),
    Parameter('int_method', str, 'CSR',
              name='PyFAI integration method',
              choices=['CSR', 'CSR OpenCL', 'LUT', 'LUT OpenCL'],
              tooltip=TOOLTIPS['int_method']),
)

def get_generic_parameter(refkey):
    """
    Get a copy of a generic Parameter.

    Parameters
    ----------
    refkey : str
        The reference key of the generic Parameter.

    Raises
    ------
    KeyError
        If not Parameter with refkey is included in the generic Parameters.

    Returns
    -------
    Parameter
        A copy of the Parameter object with the refkey.
    """
    if refkey not in GENERIC_PARAMS:
        raise KeyError(f'No Parameter with the reference key "{refkey}"'
                       'in the GENERIC_PARAMS collection.')
    _param = GENERIC_PARAMS.get_param(refkey)
    return _param.get_copy()
