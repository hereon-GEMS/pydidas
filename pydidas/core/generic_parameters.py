# This file is part of pydidas.

# pydidas is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.

# Pydidas is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE. See the
# GNU General Public License for more details.

# You should have received a copy of the GNU General Public License
# along with Pydidas. If not, see <http://www.gnu.org/licenses/>.

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


GENERIC_PARAMS = ParameterCollection(
    ###################################
    ## Generic processing paramters
    ###################################
    Parameter(
        'Live processing', int, default=0,refkey='live_processing',
        choices=[True, False],
        tooltip=('Set live processing to True if the files do not yet'
                 'exist at process startup. This will skip checks on'
                 'file existance and size.')),
    ###################################
    ## Parameters for CompositeCreation
    ###################################
    Parameter(
        'First file name', Path, default=Path(), refkey='first_file',
        tooltip=('The name of the first file for a file series or of the hdf5'
                 ' file in case of hdf5 file input.')),
    Parameter('Last file name', Path, default=Path(), refkey='last_file',
          tooltip=('Used only for file series: The name of the last file '
                   'to be added to the composite image.')),
    Parameter('File stepping', int, default=1, refkey='file_stepping',
          tooltip=('The step width (in files). A value n > 1 will only'
                   ' proess every n-th file for the composite.')),
    Parameter(
        'Hdf dataset key', HdfKey, default=HdfKey('/entry/data/data'),
        refkey='hdf5_key',
        tooltip=('Used only for hdf5 files: The dataset key.')),
    Parameter(
        'Hdf5 dataset shape', tuple, default=(0, 0, 0),
        refkey='hdf5_dataset_shape',
        tooltip=('The shape of the hdf5 dataset. This corresponds to '
                 '(nubmer of images, image size y, image size x).')),
    Parameter(
        'First image number', int, default=0, refkey='hdf5_first_image_num',
        tooltip=('The first image in the hdf5-dataset to be used. The default'
                 ' is 0.')),
    Parameter(
        'Last image number', int, default=-1, refkey='hdf5_last_image_num',
        tooltip=('The last image in the hdf5-dataset to be used. The value'
                 '-1 will default to the last image. The default is -1.')),
    Parameter(
        'Hdf5 dataset stepping', int, default=1, refkey='hdf5_stepping',
        tooltip=('The step width (in files). A value n > 1 will only'
                 ' proess every n-th file for the composite.')),
    Parameter(
        'Subtract background image', int, default=0,
        refkey='use_bg_file', choices=[True, False],
        tooltip=('Keyword to toggle usage of background subtraction.')),
    Parameter(
        'Background image file', Path, default=Path(), refkey='bg_file',
        tooltip=('The name of the file used for background correction.')),
    Parameter(
        'Background Hdf dataset key', HdfKey,
        default=HdfKey('/entry/data/data'), refkey='bg_hdf5_key',
        tooltip=('For hdf5 background image files: The dataset key.')),
    Parameter(
        'Background hdf5 image frame', int, default=0, refkey='bg_hdf5_frame',
        tooltip=('For hdf5 background image files: The image number in '
                 'the dataset')),
    Parameter(
        'Total number of images', int, default=0, refkey='n_image',
        tooltip=('The toal number of images in the composite images.')),
    Parameter(
        'Total number of files', int, default=0, refkey='n_files',
        tooltip=('The toal number of selected files.')),
    Parameter(
        'Number of images in x', int, default=1, refkey='composite_nx',
        tooltip=('The number of original images combined in the composite'
                 ' image in x direction. A value of -1 will determine the'
                 ' number of images in x direction automatically based on'
                 ' the number of images in y direction. The default is 1.')),
    Parameter(
        'Number of images in y', int, default=-1, refkey='composite_ny',
        tooltip=('The number of original images combined in the composite'
                 ' image in y direction. A value of -1 will determine the'
                 ' number of images in y direction automatically based on'
                 ' the number of images in x direction. The default is 1.')),
    Parameter(
        'Preferred composite direction', str, default='x',
        refkey='composite_dir', choices=['x', 'y'],
        tooltip=('The "fast" direction of the composite image. This '
                 'dimension will be filled first before going to the'
                 ' next row/column.')),
    Parameter(
        'Use ROI', int, default=0, refkey='use_roi', choices=[True, False],
        tooltip=('Keyword to toggle use of the ROI for cropping the '
                 'original images before combining them. The default is '
                 'False.')),
    Parameter(
        'ROI lower x limit', int, default=0, refkey='roi_xlow',
        tooltip=('The lower boundary (in pixel) for cropping images in x, if'
                 ' use_roi is enabled. Negative values will be modulated with'
                 ' the image width. The default is 0.')),
    Parameter(
        'ROI upper x limit', int, default=-1, refkey='roi_xhigh',
        tooltip=('The upper boundary (in pixel) for cropping images in x, if'
                 ' use_roi is enabled. Negative values will be modulated '
                 'with the image width, i.e. -1 is equivalent with the full '
                 'image size. The default is -1')),
    Parameter(
        'ROI lower y limit', int, default=0, refkey='roi_ylow',
        tooltip=('The lower boundary (in pixel) for cropping images in y, if'
                 ' use_roi is enabled. Negative values will be modulated with'
                 ' the image width. The default is 0.')),
    Parameter(
        'ROI upper y limit', int, default=-1, refkey='roi_yhigh',
        tooltip=('The upper boundary (in pixel) for cropping images in y, if'
                 ' use_roi is enabled. Negative values will be modulated '
                 'with the image height, i.e. -1 is equivalent with the '
                 'full image size. The default is -1')),
    Parameter(
        'Use Thresholds', int, default=0, refkey='use_thresholds',
        choices=[True, False],
        tooltip=('Keyword to toggle use of the thresholds for clipping the '
                 'data range in the original images before combining them. '
                 'The default is False.')),
    Parameter(
        'Lower threshold', float, default=np.nan, refkey='threshold_low',
        tooltip=('The lower threshold of the composite image. If any '
                 'finite value (i.e. not np.nan) is used, any pixels '
                 'with a value below the threshold will be replaced by '
                 'the threshold. A value of np.nan will ignore the '
                 'threshold. The default is np.nan.')),
    Parameter(
        'Upper threshold', float, default=np.nan, refkey='threshold_high',
        tooltip=('The upper threshold of the composite image. If any '
                 'finite value (i.e. not np.nan) is used, any pixels '
                 'with a value above the threshold will be replaced by '
                 'the threshold. A value of np.nan will ignore the '
                 'threshold. The default is np.nan.')),
    Parameter(
        'Binning factor', int, default=1, refkey='binning',
        tooltip=('The re-binning factor for the images in the composite. The '
                 'binning will be applied to the cropped images. The default '
                 'is 1.')),
    Parameter(
        'Images per file', int, default=0,
        refkey='images_per_file',
        tooltip=('The number of images in the file. For hdf5 files, this '
                 'corresponds to the number of frames in the hdf5 dataset.')),
    Parameter(
        'Image shape', tuple, default=(0, 0), refkey='image_shape',
        tooltip=('The shape of an image.')),
    Parameter(
        'Raw image shape', tuple, default=(0, 0), refkey='raw_image_shape',
        tooltip=('The image shape of the original image as loaded from the '
                 'file.')),
    Parameter(
        'Datatype', None, default=np.float32, refkey='datatype',
        tooltip='The datatype.'),
    #################################
    ## Parameters for global geometry
    #################################
     Parameter('X-ray wavelength', float, default=1, unit='A',
               refkey='xray_wavelength',
               tooltip=('The X-ray wavelength (in Angstrom). Any changes to '
                        'the wavelength will also update the X-ray energy '
                        'setting.')),
     Parameter('X-ray energy', float, default=12.398, unit='keV',
               refkey='xray_energy',
               tooltip= ('The X-ray energy (in keV). Changing this parameter '
                         'will also update the X-ray wavelength setting.')),
    Parameter('Detector name', str, default='detector', refkey='detector_name',
              tooltip='The detector name in pyFAI nomenclature.'),
    Parameter('Detector size X', int, default=0, refkey='detector_npixx',
              unit='px',
              tooltip=('The number of detector pixels in x direction '
                       '(horizontal).')),
    Parameter('Detector size Y', int, default=0, refkey='detector_npixy',
              unit='px',
              tooltip=('The number of detector pixels in y direction '
                       '(vertical).')),
    Parameter('Detector pixel size X', float, default=-1, unit='um',
              refkey='detector_sizex',
              tooltip='The detector pixel size in X-direction in micrometer.'),
    Parameter('Detector pixel size Y', float, default=-1, unit='um',
              refkey='detector_sizey',
              tooltip='The detector pixel size in Y-direction in micrometer.'),
    Parameter('Sample-detector distance', float, default=1,
              refkey='detector_dist',unit='m',
              tooltip='The sample-detector distance (in m).'),
    Parameter('Detector PONI1', float, default=0, unit='m',
              refkey='detector_poni1',
              tooltip=('The detector PONI1 (point of normal incidence; '
                       'in y direction). This is measured in meters from the'
                       'detector origin.')),
    Parameter('Detector PONI2', float, default=0, unit='m',
              refkey='detector_poni2',
              tooltip=('The detector PONI2 (point of normal incidence; '
                       'in x direction). This is measured in meters from the'
                       'detector origin.')),
    Parameter('Detector Rot1', float, default=0, unit='rad',
              refkey='detector_rot1',
              tooltip=('The detector rotation 1 (lefthanded around the '
                      '"up"-axis), given in rad.')),
    Parameter('Detector Rot2', float, default=0, unit='rad',
              refkey='detector_rot2',
              tooltip=('The detector rotation 2 (pitching the detector; '
                      'positive direction is tilting the detector towards the'
                      ' floor, i.e. left-handed), given in rad.')),
    Parameter('Detector Rot3', float, default=0, unit='rad',
              refkey='detector_rot3',
              tooltip=('The detector rotation 3 (around the beam axis; '
                      'right-handed when looking downstream with the beam.),'
                      ' given in rad.')),
    ############################
    ## Parameters for scan setup
    ############################
    Parameter('Scan dimension', int, default=2, refkey='scan_dim',
              unit='', choices=[1, 2, 3, 4],
              tooltip=('The scan_dimensionality. This is relevant for mosaic '
                       'and and mesh images.')),
    Parameter('Name of scan direction 1', str, default='',
              refkey='scan_dir_1', unit='',
              tooltip=('The axis name for scan direction 1. This information'
                       ' will only be used for labelling.')),
    Parameter('Number of scan points (dir. 1)', int, default=0,
              refkey='n_points_1', unit='',
              tooltip='The number of scan points in scan direction 1.'),
    Parameter('Step width in direction 1', float, default=0, refkey='delta_1',
              unit='', tooltip=('The step width between two scan points in'
                                ' scan direction 1.')),
    Parameter('Unit of direction 1', str, default='', refkey='unit_1',unit='',
              tooltip=('The unit of the movement / steps / offset in scan '
                       'direction 1.')),
    Parameter('Offset of direction 1', float, default=0, refkey='offset_1',
              unit='',
              tooltip=('The coordinate offset of the movement in scan '
                       'direction 1 (i.e. the coutner / motor position for '
                       'scan position 0).')),
    Parameter('Name of scan direction 2', str, default='',
              refkey='scan_dir_2', unit='',
              tooltip=('The axis name for scan direction 2. This information'
                       ' will only be used for labelling.')),
    Parameter('Number of scan points (dir. 2)', int, default=0,
              refkey='n_points_2', unit='',
              tooltip='The number of scan points in scan direction 2.'),
    Parameter('Step width in direction 2', float, default=0, refkey='delta_2',
              unit='', tooltip=('The step width between two scan points in'
                                ' scan direction 2.')),
    Parameter('Unit of direction 2', str, default='', refkey='unit_2',unit='',
              tooltip=('The unit of the movement / steps / offset in scan '
                       'direction 2.')),
    Parameter('Offset of direction 2', float, default=0, refkey='offset_2',
              unit='',
              tooltip=('The coordinate offset of the movement in scan '
                       'direction 2 (i.e. the coutner / motor position for '
                       'scan position 0).')),
    Parameter('Name of scan direction 3', str, default='',
              refkey='scan_dir_3', unit='',
              tooltip=('The axis name for scan direction 3. This information'
                       ' will only be used for labelling.')),
    Parameter('Number of scan points (dir. 3)', int, default=0,
              refkey='n_points_3', unit='',
              tooltip='The number of scan points in scan direction 3.'),
    Parameter('Step width in direction 3', float, default=0, refkey='delta_3',
              unit='', tooltip=('The step width between two scan points in'
                                ' scan direction 3.')),
    Parameter('Unit of direction 3', str, default='', refkey='unit_3',unit='',
              tooltip=('The unit of the movement / steps / offset in scan '
                       'direction 3.')),
    Parameter('Offset of direction 3', float, default=0, refkey='offset_3',
              unit='',
              tooltip=('The coordinate offset of the movement in scan '
                       'direction 3 (i.e. the coutner / motor position for '
                       'scan position 0).')),
    Parameter('Name of scan direction 4', str, default='',
              refkey='scan_dir_4', unit='',
              tooltip=('The axis name for scan direction 4. This information'
                       ' will only be used for labelling.')),
    Parameter('Number of scan points (dir. 4)', int, default=0,
              refkey='n_points_4', unit='',
              tooltip='The number of scan points in scan direction 4.'),
    Parameter('Step width in direction 4', float, default=0, refkey='delta_4',
              unit='', tooltip=('The step width between two scan points in'
                                ' scan direction 4.')),
    Parameter('Unit of direction 4', str, default='', refkey='unit_4',unit='',
              tooltip=('The unit of the movement / steps / offset in scan '
                       'direction 4.')),
    Parameter('Offset of direction 4', float, default=0, refkey='offset_4',
              unit='',
              tooltip=('The coordinate offset of the movement in scan '
                       'direction 4 (i.e. the coutner / motor position for '
                       'scan position 0).')),
    ############################
    ## selected scan indices
    ############################
    Parameter('Scan dim. 1 index', int, default=0, refkey='scan_index1',
              tooltip='The position index for the scan dimension 1.'),
    Parameter('Scan dim. 2 index', int, default=0, refkey='scan_index2',
              tooltip='The position index for the scan dimension 2.'),
    Parameter('Scan dim. 3 index', int, default=0, refkey='scan_index3',
              tooltip='The position index for the scan dimension 3.'),
    Parameter('Scan dim. 4 index', int, default=0, refkey='scan_index4',
              tooltip='The position index for the scan dimension 4.'),
    ############################
    ## global app settings
    ############################
    Parameter('Number of MP workers', int, default=4, refkey='mp_n_workers',
              unit='',
              tooltip=('The number of multiprocessing workers. Note that'
                       ' this number should not be set too high for two '
                       'reasons:\n1. File reading processes interfere with '
                       'each other if too many are active at once.\n2. pyFAI'
                       ' uses Parallelization as well and you can only gain'
                       'limited performace increases for multiple parallel'
                       ' processes.')),
    Parameter('Detector mask file', Path, default=Path(),
              refkey='det_mask', unit='',
              tooltip=('The path to the detector mask file.')),
    Parameter('Detector mask value', float, default=0,
              refkey='det_mask_val', unit='',
              tooltip=('The value to be used for the pixels masked on the '
                       'detector. Note that this value will only be used '
                       'for displaying the images. For pyFAI integration, '
                       'the pixels will be fully masked and not be '
                       'included.')),
    Parameter('Mosaic tiling border width', int, default=0,
              refkey='mosaic_border_width', unit='',
              tooltip=('The width of the border inserted between adjacent '
                       'frames in the mosaic creation.')),
    Parameter('Mosaic border value', float, default=0,
              refkey='mosaic_border_value', unit='',
              tooltip='The value to be put in the border pixels in mosaics.'),
    Parameter('Mosaic maximum size (Mpx)', float, default=100,
              refkey='mosaic_max_size', unit='',
              tooltip='The maximum size (in Mpx) of mosais images.'),
    ############################
    ## global choice settings
    ############################
    Parameter('Use global mask', int, default=1, choices=[True, False],
              refkey='use_global_mask',
              tooltip=('Select "True" to use the global settings for the '
                       'detector mask and mask value. A "False" settings '
                       'uses the local mask settings. Note: The mask value'
                       ' will not be used for integrating but only for '
                       'presentation.')),
    ############################
    ## pyFAI settings parameters
    ############################
    Parameter('Num points radial integration', int, default=1000,
              refkey='int_rad_npoint',
              tooltip=('The number of bins in radial direction for the '
                       'pyFAI integration.')),
    Parameter('Radial unit', str, default='2\u03b8 / deg',
              choices=['Q / nm^-1', 'Q / \u212b^-1', '2\u03b8 / deg',
                       '2\u03b8 / rad'], refkey='int_rad_unit',
              tooltip=('The unit and type of the azimuthal profile.')),
    Parameter('Use radial range', int, default=0, choices=[True, False],
              refkey='int_rad_use_range',
              tooltip=('Toggle to limit the radial integration range or use'
                       ' the full data range. If True, boundaries need to be '
                       'defined in the lower and upper radial range '
                       'Parameters.')),
    Parameter('Radial lower range', int, default=-1,
              refkey='int_rad_range_lower',
              tooltip=('The lower boundary of the radial integration range.'
                       ' This setting is only used if "Use radial range" is '
                       'True. This value needs to be given in the unit '
                       'selected as radial unit.')),
    Parameter('Radial upper range', int, default=-1,
              refkey='int_rad_range_upper',
              tooltip=('The upper boundary of the radial integration range.'
                       ' This setting is only used if "Use radial range" is '
                       'True. This value needs to be given in the unit '
                       'selected as radial unit.')),
    Parameter('Num points azimuthal integration', int, default=1000,
              refkey='int_azi_npoint',
              tooltip=('The number of bins in azimuthal direction for the '
                       'pyFAI integration.')),
    Parameter('Azimuthal unit', str, default='\u03c7 / deg',
              choices=['\u03c7 / deg', '\u03c7 / rad'], refkey='int_azi_unit',
              tooltip=('The unit and type of the azimuthal profile.')),
    Parameter('Use azimuthal range', int, default=0, choices=[True, False],
              refkey='int_azi_use_range',
              tooltip=('Toggle to limit the azimuthal integration range or use'
                       ' the full data range. If True, boundaries need to be '
                       'defined in the lower and upper azimuthal range '
                       'Parameters.')),
    Parameter('Azimuthal lower range', int, default=-1,
              refkey='int_azi_range_lower',
              tooltip=('The lower boundary of the azimuthal integration range.'
                       ' This setting is only used if "Use azimuthal range" is '
                       'True. This value needs to be given in the unit '
                       'selected as azimuthal unit.')),
    Parameter('Azimuthal upper range', int, default=-1,
              refkey='int_azi_range_upper',
              tooltip=('The upper boundary of the azimuthal integration range.'
                       ' This setting is only used if "Use azimuthal range" is '
                       'True. This value needs to be given in the unit '
                       'selected as azimuthal unit.')),
    Parameter('PyFAI integration method', str, default='CSR',
              refkey='int_method',
              choices=['CSR', 'CSR OpenCL', 'LUT', 'LUT OpenCL'],
              tooltip=('The integration method. For a full reference, please'
                       ' visit the pyfai documentation available at: '
                       'https://pyfai.readthedocs.io/')),
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
                       ' in the GENERIC_PARAMS collection.')
    return Parameter(*GENERIC_PARAMS[refkey].dump())
