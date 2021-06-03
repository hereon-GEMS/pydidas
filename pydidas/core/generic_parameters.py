# MIT License
#
# Copyright (c) 2021 Malte Storm, Helmholtz-Zentrum Hereon.
#
# Permission is hereby granted, free of charge, to any person obtaining a copy
# of this software and associated documentation files (the "Software"), to deal
# in the Software without restriction, including without limitation the rights
# to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
# copies of the Software, and to permit persons to whom the Software is
# furnished to do so, subject to the following conditions:
#
# The above copyright notice and this permission notice shall be included in all
# copies or substantial portions of the Software.

# THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
# IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
# FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
# AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
# LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
# OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE
# SOFTWARE.

"""
Module with a GENERIC_PARAMS dictionary which includes Parameters which
are being used several times."""

__author__      = "Malte Storm"
__copyright__   = "Copyright 2021, Malte Storm, Helmholtz-Zentrum Hereon"
__license__ = "MIT"
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
    Parameter(
        'First file name', Path, default=Path(), refkey='first_file',
        tooltip=('The name of the first file for a file series or of the hdf5'
                 ' file in case of hdf5 file input.')),
    Parameter(
        'Hdf dataset key', HdfKey, default=HdfKey(''), refkey='hdf_key',
        tooltip=('Used only for hdf5 files: The dataset key.')),
    Parameter(
        'First image number', int, default=0, refkey='hdf_first_num',
        tooltip=('The first image in the hdf5-dataset to be used. The default'
                 ' is 0.')),
    Parameter(
        'Last image number', int, default=-1, refkey='hdf_last_num',
        tooltip=('The last image in the hdf5-dataset to be used. The value'
                 '-1 will default to the last image. The default is -1.')),
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
        'Lower threshold', float, default=np.nan, refkey='threshold_low',
        tooltip=('The lower threshold of the composite image. If any '
                 ' finite value (i.e. not np.nan) is used, any pixels '
                 'with a value below the threshold will be replaced by '
                 'the threshold. A value of np.nan will ignore the '
                 'threshold. The default is np.nan.')),
    Parameter(
        'Upper threshold', float, default=np.nan, refkey='threshold_high',
        tooltip=('The upper threshold of the composite image. If any '
                 ' finite value (i.e. not np.nan) is used, any pixels '
                 'with a value above the threshold will be replaced by '
                 'the threshold. A value of np.nan will ignore the '
                 'threshold. The default is np.nan.')),
    Parameter(
        'Binning factor', int, default=1, refkey='binning',
        tooltip=('The re-binning factor for the images in the composite. The '
                 'binning will be applied to the cropped images. The default '
                 'is 1.')),
    Parameter(
        'Image shape', tuple, default=(0, 0), refkey='image_shape',
        tooltip='The image shape of the inserted image'),
    Parameter(
        'Datatype', None, default=np.float32, refkey='datatype',
        tooltip='The datatype.'),
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
    return Parameter(*GENERIC_PARAMS[refkey].dump())