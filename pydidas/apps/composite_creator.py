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
from numbers import Integral

import numpy as np

from pydidas.apps.base_app import BaseApp
from pydidas._exceptions import AppConfigError
from pydidas.core import Parameter, HdfKey, ParameterCollection, CompositeImage, get_generic_parameter
from pydidas.config import HDF5_EXTENSIONS
from pydidas.utils import (get_hdf5_populated_dataset_keys,
                           get_hdf5_metadata)
from pydidas.image_reader import read_image

PARAM_TOOLTIPS = {
    'last_file': ('Used only for file series: The name of the last file to be'
                  ' added to the composite image.'),
    'use_bg_file' : ('Keyword to toggle usage of background subtraction.'),
    'bg_file': ('The name of the file used for background correction.'),
    'bg_hdf_key': ('For hdf5 background image files: The dataset key.'),
    'bg_hdf_num' : ('For hdf5 background image files: The image number in the'
                    ' dataset'),
    'stepping': ('The step width (in images). A value n > 1 will only add '
                 'every n-th image to the composite.'),
    'n_image': ('The toal number of images in the composite images.'),
    'save_name': ('The name used for saving the composite image. None will '
                  'default to no image saving. The default is None.')
}

DEFAULT_PARAMS = ParameterCollection(
    get_generic_parameter('first_file'),
    Parameter('Last file name', Path, default=Path(), refkey='last_file',
              tooltip=PARAM_TOOLTIPS['last_file']),
    get_generic_parameter('hdf_key'),
    get_generic_parameter('hdf_first_num'),
    get_generic_parameter('hdf_last_num'),
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
    Parameter('Total number of images', int, default=-1, refkey='n_image',
              tooltip=PARAM_TOOLTIPS['n_image']),
    get_generic_parameter('composite_nx'),
    get_generic_parameter('composite_ny'),
    get_generic_parameter('composite_dir'),
    get_generic_parameter('use_roi'),
    get_generic_parameter('roi_xlow'),
    get_generic_parameter('roi_xhigh'),
    get_generic_parameter('roi_ylow'),
    get_generic_parameter('roi_yhigh'),
    get_generic_parameter('threshold_low'),
    get_generic_parameter('threshold_high'),
    get_generic_parameter('binning'),
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
    use_bg_file : bool, optional
        Keyword to toggle usage of background subtraction. The default is
        False.
    bg_file : pathlib.Path
        The name of the file used for background correction.
    bg_hdf_key : HdfKey, optional
        Required for hdf5 background image files: The dataset key with the
        image for the background file.
    bg_hdf_num : int, optional
        Required for hdf5 background image files: The image number of the
        background image in the  dataset. The default is 0.
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
    default_params = DEFAULT_PARAMS

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

        _cmdline_args = self.__parse_arguments()
        self.set_default_params(self.default_params)
        # update default_params with command line entries:
        for _key in self.params:
            if _key in _cmdline_args:
                self.params.set_value(_key, _cmdline_args[_key])

        self.__composite = None
        self.__file_list = None
        self.__hdffile = None
        self.__raw_img_shape = None
        self.__n_image = None
        self.__file_path = None
        self.__bg_image = None
        self.__roi = None
        self.__final_image_size = None
        self.__datatype = None

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

    def __create_filelist(self):
        """
        Create the list of all files to be processed.

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
        self.__process_roi()

    def __check_hdf_key(self, fname, key):
        """
        Veriy that the selected file has a dataset with key.

        Parameters
        ----------
        fname : str
            The filename and path.
        key : str
            The dataset key.

        Raises
        ------
        AppConfigError
            If the dataset key is not found in the hdf5 file.
        Returns
        -------
        None.
        """
        dsets = get_hdf5_populated_dataset_keys(fname)
        if key not in dsets:
            raise AppConfigError(f'hdf_key "{key}" is not a valid key '
                                 f'for the file "{fname}."')

    def __check_file_exists(self, fname):
        """
        Check that a file exists and raise an Exception if not.

        Parameters
        ----------
        fname : str
            The filename and path.

        Raises
        ------
        AppConfigError
            If the selected filename does not exist.

        Returns
        -------
        None.
        """
        if not os.path.isfile(fname):
            raise AppConfigError(f'The selected filename "{fname}" does not '
                                 ' point to a valid file.')

    def __store_image_data_from_hdf_file(self):
        _first_file = self.get_param_value('first_file')
        _key = self.get_param_value('hdf_key')
        self.__check_hdf_key(_first_file, _key)

        _meta = get_hdf5_metadata(_first_file, ['shape', 'dtype'], _key)
        _n_image = _meta['shape'][0]
        self.__raw_img_shape = _meta['shape'][1:3]
        self.__datatype = _meta['dtype']
        _n0 = self.__apply_param_modulo('hdf_first_image_num', _n_image)
        _n1 = self.__apply_param_modulo('hdf_last_image_num', _n_image)
        # correct total number of images for stepping *after* the
        # numbers have been modulated to be in the image range.
        self.__n_image = _n_image // self.get_param_value('stepping')
        if not _n0 < _n1:
            raise AppConfigError(
                f'The image numbers for the hdf5 file, [{_n0}, {_n1}] do'
                'not describe a correct range.')

    def __store_image_data_from_file_range(self):
        _first_file = self.get_param_value('first_file')
        _last_file = self.get_param_value('last_file')
        _path1, _name1 = os.path.split(self.get_param_value('first_file'))
        _path2, _name2 = os.path.split(self.get_param_value('last_file'))
        if _path1 != _path2:
            raise AppConfigError(
                'The selected files are not in the same directory:\n'
                f'{_first_file}\nand\n{_last_file}')
        self.__create_filelist()
        # check that all selected files are of the same size:
        _fsizes = np.r_[[os.stat(f'{_path1}/{f}').st_size
                         for f in self.__file_list]]
        if _fsizes.std() > 0.:
            raise AppConfigError('The selected files are not all of the '
                                 'same size.')
        _test_image = read_image(_first_file)
        self.__datatype = _test_image.dtype
        self.__raw_img_shape = _test_image.shape
        self.__n_image = _fsizes.size // self.get_param_value('stepping')

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
        self.__check_file_exists(_first_file)
        if os.path.splitext(_first_file)[1] in HDF5_EXTENSIONS:
            self.__hdffile = True
            self.__store_image_data_from_hdf_file()
        else:
            self.__hdffile = False
            self.__store_image_data_from_file_range()


    def __apply_param_modulo(self, param_refkey, modulo):
        """
        Apply a modulo to a Parameter.

        This method applies a modulo to a Parameter, referenced by its
        refkey, for example for converting image sizes of -1 to the actual
        detector dimensions.

        Parameters
        ----------
        param_refkey : str
            The reference key for the selected Parameter.
        modulo : int
            The mathematical modulo to be applied.

        Raises
        ------
        ValueError
            If the datatype of the selected Parameter is not integer.

        Returns
        -------
        _val : int
            The modulated Parameter value
        """
        _param = self.params[param_refkey]
        if _param.type is not Integral:
            raise ValueError(f'The datatype of Parameter "{_param.refkey}"'
                             ' is not integer.')
        _val = np.mod(_param.value, modulo)
        _param.value = _val
        return _val

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
        self.__check_file_exists(_bg_file)
        self.__process_roi()
        # check hdf5 key and dataset dimensions
        if os.path.splitext(_bg_file)[1] in HDF5_EXTENSIONS:
            self.__check_hdf_key(_bg_file, self.get_param_value('bg_hdf_key'))
            _params = dict(dataset=self.get_param_value('bg_hdf_key'),
                           binning=self.get_param_value('binning'),
                           imageNo=self.get_param_value('bg_hdf_num'),
                           ROI=self.__roi)
        else:
            _params = dict(binning=self.get_param_value('binning'),
                           ROI=self.__roi)
        _bg_image = read_image(_bg_file, **_params)
        if not _bg_image.shape == self.__final_image_size:
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
            _x0 = self.__apply_param_modulo('roi_xlow',
                                            self.__raw_img_shape[1])
            _x1 = self.__apply_param_modulo('roi_xhigh',
                                            self.__raw_img_shape[1])
            _y0 = self.__apply_param_modulo('roi_ylow',
                                            self.__raw_img_shape[0])
            _y1 = self.__apply_param_modulo('roi_yhigh',
                                            self.__raw_img_shape[0])
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


    def __process_roi(self):
        """
        Process and ROI inputs and store the ROI.

        Returns
        -------
        None
        """
        _binning = self.get_param_value('binning')
        if self.get_param_value('use_roi'):
            _y0 = self.get_param_value('roi_ylow')
            _y1 = self.get_param_value('roi_yhigh')
            _x0 = self.get_param_value('roi_xlow')
            _x1 = self.get_param_value('roi_xhigh')
            self.__final_image_size = ((_y1 - _y0) // _binning,
                                         (_x1 - _x0) // _binning)
            self.__roi = (slice(_y0, _y1 + 1), slice(_x0, _x1 + 1))
        else:
            self.__final_image_size = (self.__raw_img_shape[0] // _binning,
                                       self.__raw_img_shape[1] // _binning)
            self.__roi = None

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
        if self.get_param_value('composite_dir') == 'x':
            _iy = index // self.get_param_value('composite_nx')
            _ix = index % self.get_param_value('composite_nx')
        else:
            _iy = index % self.get_param_value('composite_ny')
            _ix = index // self.get_param_value('composite_ny')
        yslice = slice(_iy * self.__final_image_size[0],
                       (_iy + 1) * self.__final_image_size[0])
        xslice = slice(_ix * self.__final_image_size[1],
                       (_ix + 1) * self.__final_image_size[1])
        if self.__bg_image is not None:
            image -= self.__bg_image
        self.__composite[yslice, xslice] = image

    def apply_thresholds(self, low=None, high=None):
        """
        Apply thresholds to the composite image.

        This method is a wrapper for the apply_thresholds method of the
        CompositeImage object.

        Parameters
        ----------
        low : Union[float, None], optional
            The lower threshold. If None, the stored lower thresholds from
            the ParameterCollection will be used. The default is None.
        high : Union[float, None], optional
            The upper threshold. If None, the stored upper thresholds from
            the ParameterCollection will be used. The default is None.

        Returns
        -------
        None.
        """
        self.__composite.apply_thresholds(low, high)


    def __get_args_for_read_image(self, index):
        if self.__hdffile:
            _params = dict(dataset=self.get_param_value('hdf_key'),
                           binning=self.get_param_value('binning'),
                           ROI=self.__roi, imageNo=index)
            _fname = self.get_param_value('first_file')
        else:
            _fname = os.path.join(self.__file_path, self.__file_list[index])
            _params = dict(binning=self.get_param_value('binning'),
                           ROI=self.__roi)
        return _fname, _params

    def prepare_run(self):
        """
        Prepare running the composite creation.

        This method will check all settings and create the composite image.

        Returns
        -------
        None.
        """
        self.check_entries()
        self.__composite = CompositeImage(
            image_shape=self.__final_image_size,
            composite_nx=self.get_param_value('composite_nx'),
            composite_ny=self.get_param_value('composite_ny'),
            composite_dir=self.get_param_value('composite_dir'),
            datatype=self.__datatype)

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
        self.check_entries()
        save_name = kwargs.get('save_name', None)
        if self.__composite is None:
            self.prepare_run()

        self.__composite.print_param_values()
        if self.__hdffile:
            _range = range(self.get_param_value('hdf_first_num'),
                           self.get_param_value('hdf_last_num') + 1,
                           self.get_param_value('stepping'))
        else:
            _range = range(len(self.__file_list))

        for compindex, imgindex in enumerate(_range):
            _fname, _kwargs = self.__get_args_for_read_image(imgindex)
            self.__composite.insert_image(read_image(_fname, **_kwargs),
                                          compindex)

        self.apply_thresholds()
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
        return self.__composite.image
