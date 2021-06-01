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

"""Module with the CompositeCreatorApp class which allows to combine
images to mosaics."""

__author__      = "Malte Storm"
__copyright__   = "Copyright 2021, Malte Storm, Helmholtz-Zentrum Hereon"
__license__ = "MIT"
__version__ = "0.0.0"
__maintainer__ = "Malte Storm"
__status__ = "Development"
__all__ = ['CompositeCreatorApp']

import os
import argparse
from pathlib import Path

import numpy as np

from pydidas.apps.base_app import BaseApp
from pydidas._exceptions import AppConfigError
from pydidas.core import Parameter, HdfKey, ParameterCollection
from pydidas.config import HDF5_EXTENSIONS
from pydidas.utils import (get_hdf5_populated_dataset_keys,
                           get_hdf5_dataset_shape)
from pydidas.image_reader import read_image

PARAM_TOOLTIPS = {
    'first_file': ('The name of the first file for a file series or of the '
                   'hdf5 file in case of hdf5 file input.'),
    'last_file': ('Used only for file series: The name of the last file to be'
                  ' added to the composite image.'),
    'hdf_key': ('Used only for hdf5 files: The dataset key.'),
    'hdf_first_num': ('The first image in the hdf5-dataset to be used. The '
                      'default is 0.'),
    'hdf_last_num': ('The last image in the hdf5-dataset to be used. The '
                     'value -1 will default to the last image. The default '
                     'is -1.'),
    'use_bg_file' : ('Keyword to toggle usage of background subtraction.'),
    'bg_file': ('The name of the file used for background correction.'),
    'bg_hdf_key': ('For hdf5 background image files: The dataset key.'),
    'bg_hdf_num' : ('For hdf5 background image files: The image number in the'
                    ' dataset'),
    'stepping': ('The step width (in images). A value n > 1 will only add '
                 'every n-th image to the composite.'),
    'n_image': ('The toal number of images in the composite images.'),
    'composite_nx': ('The number of original images combined in the composite'
                     ' image in x direction. A value of -1 will determine the'
                     ' number of images in x direction automatically based on'
                     ' the number of images in y direction. The default is '
                     '1.'),
    'composite_ny': ('The number of original images combined in the composite'
                     ' image in y direction. A value of -1 will determine the'
                     ' number of images in y direction automatically based on'
                     ' the number of images in x direction. The default is '
                     '-1.'),
    'composite_dir': ('The "fast" direction of the composite image. This '
                      'dimension will be filled first before going to the'
                      ' next row/column.'),
       'use_roi': ('Keyword to toggle use of the ROI for cropping the '
                   'original images before combining them. The default is '
                   'False.'),
    'roi_xlow': ('The lower boundary (in pixel) for cropping images in x, if'
                 ' use_roi is enabled. Negative values will be modulated with'
                 ' the image width. The default is 0.'),
    'roi_xhigh': ('The upper boundary (in pixel) for cropping images in x, if'
                  ' use_roi is enabled. Negative values will be modulated '
                  'with the image width, i.e. -1 is equivalent with the full '
                  'image size. The default is -1'),
    'roi_ylow': ('The lower boundary (in pixel) for cropping images in y, if'
                 ' use_roi is enabled. Negative values will be modulated with'
                 ' the image width. The default is 0.'),
    'roi_yhigh': ('The upper boundary (in pixel) for cropping images in y, if'
                  ' use_roi is enabled. Negative values will be modulated '
                  'with the image height, i.e. -1 is equivalent with the '
                  'full image size. The default is -1'),
    'threshold_low': ('The lower threshold of the composite image. If a value'
                      ' other than -1 is used, any pixels with a value below '
                      'the threshold will be replaced by the threshold. A '
                      'value of -1 will ignore the threshold. The default is '
                      '0.'),
    'threshold_high': ('The upper threshold of the composite image. If a value'
                      ' other than -1 is used, any pixels with a value above '
                      'the threshold will be replaced by the threshold. A '
                      'value of -1 will ignore the threshold. The default is '
                      '-1.'),
    'binning': ('The re-binning factor for the images in the composite. The '
                'binning will be applied to the cropped images. The default '
                'is 1.'),
    'save_name': ('The name used for saving the composite image. None will '
                  'default to no image saving. The default is None.')
}

DEFAULT_PARAMS = ParameterCollection(
    Parameter('First file name', Path, default=Path(), refkey='first_file',
              tooltip=PARAM_TOOLTIPS['first_file']),
    Parameter('Last file name', Path, default=Path(), refkey='last_file',
              tooltip=PARAM_TOOLTIPS['last_file']),
    Parameter('Hdf dataset key', HdfKey, default=HdfKey(''), refkey='hdf_key',
              tooltip=PARAM_TOOLTIPS['hdf_key']),
    Parameter('First image number', int, default=0, refkey='hdf_first_num',
              tooltip=PARAM_TOOLTIPS['hdf_first_num']),
    Parameter('Last image number', int, default=-1, refkey='hdf_last_num',
              tooltip=PARAM_TOOLTIPS['hdf_last_num']),
    Parameter('Subtract background image', int, default=0,
              refkey='use_bg_file', choices=[True, False],
              tooltip=PARAM_TOOLTIPS['use_bg_file']),
    Parameter('Background image file', Path, default=Path(), refkey='bg_file',
              tooltip=PARAM_TOOLTIPS['bg_file']),
    Parameter('Background Hdf dataset key', HdfKey, default=HdfKey(''),
              refkey='bg_hdf_key', tooltip=PARAM_TOOLTIPS['bg_hdf_key']),
    Parameter('Background image number', int, default=0, refkey='bg_hdf_num',
              tooltip=PARAM_TOOLTIPS['bg_hdf_num']),
    Parameter('Stepping', int, default=1, refkey='stepping',
              tooltip=PARAM_TOOLTIPS['stepping']),
    Parameter('Number of images in x', int, default=1, refkey='composite_nx',
              tooltip=PARAM_TOOLTIPS['composite_nx']),
    Parameter('Number of images in y', int, default=-1, refkey='composite_ny',
              tooltip=PARAM_TOOLTIPS['composite_ny']),
    Parameter('Preferred composite direction', str, default='x',
              refkey='composite_dir', choices=['x', 'y'],
              tooltip=PARAM_TOOLTIPS['composite_dir']),
    Parameter('Use ROI', int, default=0, refkey='use_roi',
              choices=[True, False], tooltip=PARAM_TOOLTIPS['use_roi']),
    Parameter('ROI lower x limit', int, default=0, refkey='roi_xlow',
              tooltip=PARAM_TOOLTIPS['roi_xlow']),
    Parameter('ROI upper x limit', int, default=-1, refkey='roi_xhigh',
              tooltip=PARAM_TOOLTIPS['roi_xhigh']),
    Parameter('ROI lower y limit', int, default=0, refkey='roi_ylow',
              tooltip=PARAM_TOOLTIPS['roi_ylow']),
    Parameter('ROI upper y limit', int, default=-1, refkey='roi_yhigh',
              tooltip=PARAM_TOOLTIPS['roi_yhigh']),
    Parameter('Lower threshold', int, default=0, refkey='threshold_low',
              tooltip=PARAM_TOOLTIPS['threshold_low']),
    Parameter('Upper threshold', int, default=-1, refkey='threshold_high',
              tooltip=PARAM_TOOLTIPS['threshold_high']),
    Parameter('Binning factor', int, default=1, refkey='binning',
              tooltip=PARAM_TOOLTIPS['binning']),
    Parameter('Composite image filename', Path, default=Path(),
              refkey='save_name', tooltip=PARAM_TOOLTIPS['save_name'])
)


class CompositeCreatorApp(BaseApp):
    """
    The CompositeCreatorApp can compose mosaic images of a large number of
    individual image files.

    Parameters can be passed either through the argparse module during
    command line calls or through keyword arguments in scripts.

    The names of the parameters are similar for both cases, only the calling
    syntax changes slightly, based on the underlying structure used.
    For the command line, parameters must be passed as -<parameter name>
    <value>.
    For keyword arguments, parameters must be passed during instantiation
    using the standard <parameter name>=<value>.

    Parameters
    ----------
    first_file : pathlib.Path
        The name of the first file for a file series or of the hdf5 file in
        case of hdf5 file input.
    last_file : pathlib.Path, optional
        Used only for file series: The name of the last file to be added to
        the composite image.
    hdf_key : HdfKey
        Used only for hdf5 files: The dataset key.
    hdf_first_num : int, optional
        The first image in the hdf5-dataset to be used. The default is 0.
    hdf_last_num : int, optional
        The last image in the hdf5-dataset to be used. The value -1 will
        default to the last image. The default is -1.
    stepping : int, optional
        The step width (in images). A value n > 1 will only add every n-th
        image to the composite.
    composite_nx : int, optional
        The number of original images combined in the composite image in
        x direction. A value of -1 will determine the number of images in
        x direction automatically based on the number of images in y
        direction. The default is 1.
    composite_ny : int, optional
        The number of original images combined in the composite image in
        y direction. A value of -1 will determine the number of images in
        y direction automatically based on the number of images in x
        direction. The default is -1.
    use_roi : bool, optional
        Keyword to toggle use of the ROI for cropping the original images
        before combining them. The default is False.
    roi_xlow : int, optional
        The lower boundary (in pixel) for cropping images in x, if use_roi is
        enabled. Negative values will be modulated with the image width.
        The default is 0.
    roi_xhigh : int, optional
        The upper boundary (in pixel) for cropping images in x, if use_roi is
        enabled. Negative values will be modulated with the image width, i.e.
        -1 is equivalent with the full image size. The default is -1
    roi_ylow : int, optional
        The lower boundary (in pixel) for cropping images in y, if use_roi is
        enabled. Negative values will be modulated with the image width.
        The default is 0.
    roi_yhigh : int, optional
        THe upper boundary (in pixel) for cropping images in y, if use_roi is
        enabled. Negative values will be modulated with the image width, i.e.
        -1 is equivalent with the full image size. The default is -1
    threshold_low : int, optional
        The lower threshold of the composite image. If a value  other than -1
        is used, any pixels with a value below the threshold will be replaced
        by the threshold. A value of -1 will ignore the threshold. The
        default is 0.
    threshold_high : int, optional
        The upper threshold of the composite image. If a value other than -1
        is used, any pixels with a value above the threshold will be replaced
        by the threshold. A value of -1 will ignore the threshold. The default
        is -1.
    binning : int, optional
        The re-binning factor for the images in the composite. The binning
        will be applied to the cropped images. The default is 1.
    save_name : Union[pathlib.Path, None], optional
        The name used for saving the composite image. None will default to
        no image saving. The default is None.
    """
    def __init__(self, *args, **kwargs):
        """
        Create a CompositeCreatorApp instance.

        Parameters
        ----------
        *args : list
            Any arguments.
        **kwargs : dict
            A dictionary of keyword arguments.

        Returns
        -------
        None.
        """
        super().__init__(*args, **kwargs)

        # update DEFAULT_PARAMS with command line entries:
        _cmdline_args = self.__parse_arguments()
        for _key in DEFAULT_PARAMS:
            if _key in _cmdline_args:
                DEFAULT_PARAMS.set_value(_key, _cmdline_args[_key])

        self.set_default_params(DEFAULT_PARAMS)
        self.__composite = None
        self.__file_list = None
        self.__hdffile = None
        self.__img_shape = None
        self.__n_image = None
        self.__file_path = None
        self.__bg_image = None

    @staticmethod
    def __parse_arguments():
        """
        Use argparse to get command line arguments.

        Returns
        -------
        dict
            A dictionary with the parsed arugments which holds all the entries
            and entered values or  - if missing - the default values.
        """
        parser = argparse.ArgumentParser()
        parser.add_argument('-first_file', '-f', default=Path(),
                            help=DEFAULT_PARAMS['first_file'].tooltip)
        parser.add_argument('-last_file', '-l', default=Path(),
                            help=DEFAULT_PARAMS['last_file'].tooltip)
        parser.add_argument('-hdf_key', default=HdfKey(''),
                            help=DEFAULT_PARAMS['hdf_key'].tooltip)
        parser.add_argument('-hdf_first_num', default=0, type=int,
                            help=DEFAULT_PARAMS['hdf_first_num'].tooltip)
        parser.add_argument('-hdf_last_num', default=-1, type=int,
                            help=DEFAULT_PARAMS['hdf_last_num'].tooltip)
        parser.add_argument('--use_bg_file', action='store_true',
                            help=DEFAULT_PARAMS['use_bg_file'].tooltip)
        parser.add_argument('-bg_file', default=Path(),
                            help=DEFAULT_PARAMS['bg_file'].tooltip)
        parser.add_argument('-bg_hdf_key', default=HdfKey(''),
                            help=DEFAULT_PARAMS['bg_hdf_key'].tooltip)
        parser.add_argument('-bg_hdf_num', default=0, type=int,
                            help=DEFAULT_PARAMS['bg_hdf_num'].tooltip)
        parser.add_argument('-stepping', '-s', default=1, type=int,
                            help=DEFAULT_PARAMS['stepping'].tooltip)
        parser.add_argument('-composite_nx', default=1, type=int,
                            help=DEFAULT_PARAMS['composite_nx'].tooltip)
        parser.add_argument('-composite_ny', default=-1, type=int,
                            help=DEFAULT_PARAMS['composite_ny'].tooltip)
        parser.add_argument('--use_roi', action='store_true',
                            help=DEFAULT_PARAMS['use_roi'].tooltip)
        parser.add_argument('-roi_xlow', default=0, type=int,
                            help=DEFAULT_PARAMS['roi_xlow'].tooltip)
        parser.add_argument('-roi_xhigh', default=-1, type=int,
                            help=DEFAULT_PARAMS['roi_xhigh'].tooltip)
        parser.add_argument('-roi_ylow', default=0, type=int,
                            help=DEFAULT_PARAMS['roi_ylow'].tooltip)
        parser.add_argument('-roi_yhigh', default=0, type=int,
                            help=DEFAULT_PARAMS['roi_yhigh'].tooltip)
        parser.add_argument('-threshold_low', default=0, type=int,
                            help=DEFAULT_PARAMS['threshold_low'].tooltip)
        parser.add_argument('-threshold_high', default=-1, type=int,
                            help=DEFAULT_PARAMS['threshold_high'].tooltip)
        parser.add_argument('-binning', default=1, type=int,
                            help=DEFAULT_PARAMS['binning'].tooltip)
        parser.add_argument('--save_name', default=Path(),
                            help=DEFAULT_PARAMS['save_name'].tooltip)
        return dict(vars(parser.parse_args()))

    def __get_filelist(self):
        """
        Get the list of all files to be processed.

        The list of files to be processed is created based on the filenames
        of the first and last files. The directory content will be sorted
        and the first and last files names will be used to select the part
        of filesnames to be stored.

        Returns
        -------
        None.
        """
        _path1, _fname1 = os.path.split(self.get_param_value('first_file'))
        _path2, _fname2 = os.path.split(self.get_param_value('last_file'))
        _file_list = os.listdir(_path1)
        _file_list.sort()
        _i1 = _file_list.index(_fname1)
        _i2 = _file_list.index(_fname2)
        _file_list = _file_list[_i1:_i2 + 1:self.get_param_value('stepping')]
        self.__file_list = _file_list
        self.__file_path = _path1

    def check_entries(self):
        """
        Check the stores parameters for consistency.

        This method will perform the following checks:

            - Check that filename for the first and last file exist
            - If first file is hdf5 file: Check that the dataset key
              exists.
            - If first file is hdf5 file: Check that the selected image
              numbers are included in the dataset dimensions.
            - If first file is not an hdf5 file: Verify that first and last
              file are in the same directory and that all selected images
              have the same file size. The file size instead of the actual
              file content is checked to speed up the process.
            - Check the ROI settings and assert that the selected dimensions
              are valid and within the image size.
            - Check the composite dimensions and assert that the composite
              image size covers all selected files / images.
            - If a background subtraction is used, check the background file
              and assert the image size is the same.

        Returns
        -------
        None.
        """
        self.__check_files()
        self.__check_roi()
        self.__check_composite_dims()
        self.__check_and_set_bg_file()

    def __check_files(self):
        """
        Check the file names, paths and (for hdf5 images), the size of the
        dataset with respect to the selected image numbers.

        Raises
        ------
        AppConfigError
            If any of the checks fail.

        Returns
        -------
        None
        """
        _first_file = self.get_param_value('first_file')
        if not os.path.isfile(_first_file):
            raise AppConfigError(f'first_file "{_first_file}" is not a valid '
                                 'file!')
        # check hdf5 key and dataset dimensions
        if os.path.splitext(_first_file)[1] in HDF5_EXTENSIONS:
            self.__hdffile = True
            _key = self.get_param_value('hdf_key')
            dsets = get_hdf5_populated_dataset_keys(_first_file)
            if _key not in dsets:
                raise AppConfigError(f'hdf_key "{_key}" is not a valid key '
                                     f'for the file "{_first_file}."')
            _shape = get_hdf5_dataset_shape(_first_file, _key)
            _n_image = _shape[0]
            self.__img_shape = _shape[1:3]
            _n0 = self.__get_param_in_range('hdf_first_image_num', 0,
                                            _n_image, _n_image)
            _n1 = self.__get_param_in_range('hdf_last_image_num', 0,
                                            _n_image, _n_image)
            # correct total number of images for stepping *after* the
            # numbers have been modulated to be in the image range.
            self.__n_image = _n_image // self.get_param_value('stepping')
            if not _n0 < _n1:
                raise AppConfigError(
                    f'The image numbers for the hdf5 file, [{_n0}, {_n1}] do'
                    'not describe a correct range.')
        # case of non-hdf5 files: Check 2nd file and file range
        else:
            self.__hdffile = False
            _last_file = self.get_param_value('last_file')
            _path1, _name1 = os.path.split(self.get_param_value('first_file'))
            _path2, _name2 = os.path.split(self.get_param_value('last_file'))
            if _path1 != _path2:
                raise AppConfigError(
                    'The selected files are not in the same directory:\n'
                    f'{_first_file}\nand\n{_last_file}')
            self.__get_filelist()
            # check that all selected files are of the same size:
            _fsizes = np.r_[[os.stat(f'{_path1}/{f}').st_size
                             for f in self.__file_list]]
            if _fsizes.std() > 0.:
                raise AppConfigError('The selected files are not all of the '
                                     'same size.')
            self.__img_shape = read_image(_first_file)[0].shape
            self.__n_image = _fsizes.size // self.get_param_value('stepping')

    def __check_and_set_bg_file(self):
        """
        Check the selected background image file for consistency.

        The background image file is checked and if all checks pass, the
        background image is stored.

        Raises
        ------
        AppConfigError
            - If the selected background file does not exist
            - If the selected dataset key does not exist (in case of hdf5
              files)
            - If the  selected dataset number does not exist (in case of
              hdf5 files)
            - If the image dimensions for the background file differ from the
              image files.

        Returns
        -------
        None.
        """
        if not self.get_param_value('use_bg_file'):
            return
        _bg_file = self.get_param_value('bg_file')
        if not os.path.isfile(_bg_file):
            raise AppConfigError(f'bg_file "{_bg_file}" is not a valid '
                                 'file!')
        _roi, _img_pix_y, _img_pix_x = self.__get_roi_and_img_size()
        # check hdf5 key and dataset dimensions
        if os.path.splitext(_bg_file)[1] in HDF5_EXTENSIONS:
            _key = self.get_param_value('bg_hdf_key')
            dsets = get_hdf5_populated_dataset_keys(_bg_file)
            if _key not in dsets:
                raise AppConfigError(f'bg_hdf_key "{_key}" is not a valid key '
                                     f'for the file "{_bg_file}."')
            _bg_image = read_image(self.get_param_value('bg_file'),
                                   dataset=self.get_param_value('bg_hdf_key'),
                                   binning=self.get_param_value('binning'),
                                   imageNo=self.get_param_value('bg_hdf_num'),
                                   ROI=_roi)[0]
        else:
            _bg_image = read_image(_bg_file, ROI=_roi,
                                   binning=self.get_param_value('binning'))[0]
        if not _bg_image.shape == (_img_pix_y, _img_pix_x):
            raise AppConfigError(f'The selected background file "{_bg_file}"'
                                 ' does not the same image dimensions as the'
                                 'selected files.')
        self.__bg_image = _bg_image

    def __check_roi(self):
        """
        Check the ROI for consistency.

        Raises
        ------
        AppConfigError
            If the ROI boundaries are not consistent.

        Returns
        -------
        None.
        """
        if self.get_param_value('use_roi'):
            _warning = ''
            _x0 = self.__get_param_in_range(
                'roi_xlow', 0, self.__img_shape[1], self.__img_shape[1]
                )
            _x1 = self.__get_param_in_range(
                'roi_xhigh', 0, self.__img_shape[1], self.__img_shape[1]
                )
            _y0 = self.__get_param_in_range(
                'roi_ylow', 0, self.__img_shape[0], self.__img_shape[0]
                )
            _y1 = self.__get_param_in_range(
                'roi_yhigh', 0, self.__img_shape[0], self.__img_shape[0]
                )
            if _x1 < _x0:
                _warning += f'ROI x-range incorrect: [{_x0}, {_x1}]'
            if _y1 < _y0:
                _warning += f'ROI y-range incorrect: [{_y0}, {_y1}]'
            if _warning:
                raise AppConfigError(_warning)

    def __check_composite_dims(self):
        """
        Check the dimensions of the composite image.

        Raises
        ------
        AppConfigError
            If the composite dimensions are too small or too large to match
            the total number of images.

        Returns
        -------
        None.
        """
        _nx = self.get_param_value('composite_nx')
        _ny = self.get_param_value('composite_ny')
        if _nx == -1:
            _nx = int(np.ceil(self.__n_image / _ny))
            self.params.set_value('composite_nx', _nx)
        if _ny == -1:
            _ny = int(np.ceil(self.__n_image / _nx))
            self.params.set_value('composite_ny', _ny)
        if _nx * _ny < self.__n_image:
            raise AppConfigError(
                'The selected composite dimensions are too small to hold all'
                f'images. (nx={_nx}, ny={_ny}, n={self.__n_image})')
        if ((_nx - 1) * _ny > self.__n_image
                or _nx * (_ny - 1) > self.__n_image):
            raise AppConfigError(
                'The selected composite dimensions are too large for all'
                f'images. (nx={_nx}, ny={_ny}, n={self.__n_image})')

    def __get_roi_and_img_size(self):
        """
        Get the ROI and image size.

        This method calculates the ROI and image size based on the ROI flag
        and boundaries.

        Returns
        -------
        roi : Union[tuple, None]
            If the use_roi flag is set, a tuple of 2 slice objects for y and x
            is returned. If not, the return value is None.
        img_pix_y : int
            The number of pixels in the image in y direction.
        img_pix_x : int
            The number of pixels in the image in x direction.
        """
        _binning = self.get_param_value('binning')
        if self.get_param_value('use_roi'):
            _y0 = self.get_param_value('roi_ylow')
            _y1 = self.get_param_value('roi_yhigh')
            _x0 = self.get_param_value('roi_xlow')
            _x1 = self.get_param_value('roi_xhigh')
            img_pix_x = (_x1 - _x0) // _binning
            img_pix_y = (_y1 - _y0) // _binning
            roi = (slice(_y0, _y1 + 1), slice(_x0, _x1 + 1))
        else:
            img_pix_x = self.__img_shape[1] // _binning
            img_pix_y = self.__img_shape[0] // _binning
            roi = None
        return roi, img_pix_y, img_pix_x

    def __put_image_in_composite(self, image, index):
        """
        Put the image in the composite image.

        This method will find the correct place for the image in the composite
        and copy the image data there.

        Parameters
        ----------
        image : np.ndarray
            The image data.
        index : int
            The image index. This is needed to find the correct place for
            the image in the composite.

        Returns
        -------
        None.
        """
        _roi, _img_pix_y, _img_pix_x = self.__get_roi_and_img_size()
        if self.get_param_value('composite_dir') == 'x':
            _iy = index // self.get_param_value('composite_nx')
            _ix = index % self.get_param_value('composite_nx')
        else:
            _iy = index % self.get_param_value('composite_ny')
            _ix = index // self.get_param_value('composite_ny')
        del _roi
        yslice = slice(_iy * _img_pix_y, (_iy + 1) * _img_pix_y)
        xslice = slice(_ix * _img_pix_x, (_ix + 1) * _img_pix_x)
        if self.__bg_image is not None:
            image -= self.__bg_image
        self.__composite[yslice, xslice] = image

    def __apply_thresholds(self):
        """
        Apply thresholds to the composite image.

        Returns
        -------
        None.
        """
        _thresh_low= self.get_param_value('threshold_low')
        if _thresh_low != -1:
            self.__composite[self.__composite < _thresh_low] = _thresh_low
        _thresh_high = self.get_param_value('threshold_high')
        if _thresh_high != -1:
            self.__composite[self.__composite > _thresh_high] = _thresh_high

    def run(self, *args, **kwargs):
        """
        Run the composite creation.

        This method will first call the check_entries method to verify that
        the parameter entries are consistent. The composite image will be
        created and stored. If the save_name has been specified, the composite
        image will be saved. Otherwise, it will only be available by reference


        Parameters
        ----------
        save_name : Union[int, Path, None]
        Returns
        -------
        None.

        """
        save_name = kwargs.get('save_name', None)
        self.check_entries()
        _roi, _img_pix_y, _img_pix_x = self.__get_roi_and_img_size()
        self.__composite = np.zeros(
            (self.get_param_value('composite_ny') * _img_pix_y,
             self.get_param_value('composite_nx') * _img_pix_x)
        )
        if self.__hdffile:
            for i in range(self.get_param_value('hdf_first_num'),
                           self.get_param_value('hdf_last_num') + 1,
                           self.get_param_value('stepping')):
                _image = read_image(self.get_param_value('first_file'),
                                    dataset=self.get_param_value('hdf_key'),
                                    binning=self.get_param_value('binning'),
                                    ROI=_roi, imageNo=i)[0]
                self.__put_image_in_composite(
                    _image, i - self.get_param_value('hdf_first_num')
                )
        else:
            for i, fname in enumerate(self.__file_list):
                _path = os.path.join(self.__file_path, fname)
                _image = read_image(_path, ROI=_roi,
                                    binning=self.get_param_value('binning'))[0]
                self.__put_image_in_composite(_image, i)

        self.__apply_thresholds()
        save_name = (save_name if save_name is not None
                     else self.get_param_value('save_name'))
        if (save_name is not None
                and os.path.exists(os.path.dirname(save_name))):
            np.save(save_name, self.__composite)

    @property
    def composite(self):
        """
        Get the composite image.

        Returns
        -------
        np.ndarray
            The composite image in np.ndarray format.

        """
        return self.__composite
