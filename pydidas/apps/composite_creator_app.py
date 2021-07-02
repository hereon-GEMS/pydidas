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

"""Module with the CompositeCreatorApp class which allows to combine
images to mosaics."""

__author__      = "Malte Storm"
__copyright__   = "Copyright 2021, Malte Storm, Helmholtz-Zentrum Hereon"
__license__ = "GPL-3.0"
__version__ = "0.0.0"
__maintainer__ = "Malte Storm"
__status__ = "Development"
__all__ = ['CompositeCreatorApp']

import os
import argparse
import re
from pathlib import Path

import numpy as np
from PyQt5 import QtCore

from pydidas.apps.base_app import BaseApp
from pydidas._exceptions import AppConfigError
from pydidas.core import (Parameter, HdfKey, ParameterCollection,
                          CompositeImage, get_generic_parameter)
from pydidas.config import HDF5_EXTENSIONS, FILENAME_DELIMITERS
from pydidas.utils import (get_hdf5_metadata, check_file_exists,
                           check_hdf5_key_exists_in_file,
                           verify_files_in_same_directory,
                           verify_files_of_range_are_same_size)
from pydidas.image_reader import read_image
from pydidas.utils import copy_docstring

DEFAULT_PARAMS = ParameterCollection(
    get_generic_parameter('live_processing'),
    get_generic_parameter('first_file'),
    get_generic_parameter('last_file'),
    get_generic_parameter('file_stepping'),
    get_generic_parameter('hdf5_key'),
    get_generic_parameter('hdf5_first_image_num'),
    get_generic_parameter('hdf5_last_image_num'),
    get_generic_parameter('hdf5_stepping'),
    get_generic_parameter('use_bg_file'),
    get_generic_parameter('bg_file'),
    get_generic_parameter('bg_hdf5_key'),
    get_generic_parameter('bg_hdf5_num'),
    Parameter('Total number of images', int, default=0, refkey='n_total',
              tooltip=('The total number of images.')),
    get_generic_parameter('composite_nx'),
    get_generic_parameter('composite_ny'),
    get_generic_parameter('composite_dir'),
    get_generic_parameter('use_roi'),
    get_generic_parameter('roi_xlow'),
    get_generic_parameter('roi_xhigh'),
    get_generic_parameter('roi_ylow'),
    get_generic_parameter('roi_yhigh'),
    get_generic_parameter('use_thresholds'),
    get_generic_parameter('threshold_low'),
    get_generic_parameter('threshold_high'),
    get_generic_parameter('binning'),
    Parameter('Composite image filename (npy format)', Path, default=Path(),
              refkey='output_fname',
              tooltip=('The name used for saving the composite image (in '
                       'numpy file format). An empty Path will default to no '
                       'automatic image saving. The default is Path().')),
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
    file_stepping : int, optional
        The step width (in files). A value n > 1 will only process every n-th
        image for the composite. The default is 1.
    hdf5_key : HdfKey, optional
        Used only for hdf5 files: The dataset key.
    hdf5_first_image_num : int, optional
        The first image in the hdf5-dataset to be used. The default is 0.
    hdf5_last_image_num : int, optional
        The last image in the hdf5-dataset to be used. The value -1 will
        default to the last image. The default is -1.
    hdf5_stepping : int, optional
        The step width (in images) of hdf5 datasets. A value n > 1 will only
        add every n-th image to the composite. The default is 1.
    use_bg_file : bool, optional
        Keyword to toggle usage of background subtraction. The default is
        False.
    bg_file : pathlib.Path, optional
        The name of the file used for background correction.
    bg_hdf5_key : HdfKey, optional
        Required for hdf5 background image files: The dataset key with the
        image for the background file.
    bg_hdf5_num : int, optional
        Required for hdf5 background image files: The image number of the
        background image in the  dataset. The default is 0.
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
    output_fname : Union[pathlib.Path, str], optional
        The name used for saving the composite image (in numpy file format).
        An empty Path will default to no image saving. The default is Path().
    """
    default_params = DEFAULT_PARAMS
    mp_func_results = QtCore.pyqtSignal(object)

    def __init__(self, *args, **kwargs):
        """
        Create a CompositeCreatorApp instance.
        """
        super().__init__(*args, **kwargs)
        _cmdline_args = _parse_composite_creator_cmdline_arguments()
        self.set_default_params()

        # update default_params with command line entries:
        for _key in self.params:
            if _key in _cmdline_args and _cmdline_args[_key] is not None:
                self.params.set_value(_key, _cmdline_args[_key])

        self._composite = None
        self._config = {'file_list': [],
                         'file_path': None,
                         'hdffile': None,
                         'raw_img_shape_x': None,
                         'raw_img_shape_y': None,
                         'n_image_per_file': 1,
                         'n_files': None,
                         'n_total': None,
                         'bg_image': None,
                         'roi': None,
                         'final_image_size_x': None,
                         'final_image_size_y': None,
                         'datatype': None}

    def multiprocessing_pre_run(self):
        """
        Perform operations prior to running main parallel processing function.
        """
        self.prepare_run()
        self._config['mp_pre_run_called'] = True
        self._config['mp_tasks'] = range(self._config['n_total'])

    def multiprocessing_post_run(self):
        """
        Perform operatinos after running main parallel processing function.
        """
        output_fname = self.get_param_value('output_fname')
        self.apply_thresholds()
        if os.path.exists(os.path.dirname(output_fname)):
            self._composite.save(output_fname)

    def multiprocessing_get_tasks(self):
        """
        Return all tasks required in multiprocessing.
        """
        if 'mp_tasks' not in self._config.keys():
            raise KeyError('Key "mp_tasks" not found. Please execute'
                           'multiprocessing_pre_run() first.')
        return self._config['mp_tasks']

    def multiprocessing_func(self, index):
        """
        Perform key operation with parallel processing.

        Returns
        -------
        _composite_index : int
            The image index for the composite image.
        _image : np.ndarray
            The (pre-processed) image.
        """
        _fname, _kwargs = self._get_args_for_read_image(index)
        _image = read_image(_fname, **_kwargs)
        return index, _image

    @QtCore.pyqtSlot(int, object)
    def multiprocessing_store_results(self, index, image):
        """
        Store the results of the multiprocessing operation.

        Parameters
        ----------
        index : int
            The index in the composite image.
        image : np.ndarray
            The image data.
        """
        self._composite.insert_image(image, index)

    def prepare_run(self):
        """
        Prepare running the composite creation.

        This method will check all settings and create the composite image or
        tell the CompositeImage to create a new image with changed size.
        """
        self.check_entries()
        _shape = (self._config['final_image_size_y'],
                  self._config['final_image_size_x'])
        if self._composite is None:
            self._composite = CompositeImage(
                image_shape=_shape,
                composite_nx=self.get_param_value('composite_nx'),
                composite_ny=self.get_param_value('composite_ny'),
                composite_dir=self.get_param_value('composite_dir'),
                datatype=self._config['datatype'])
            return
        if self._composite.shape != _shape:
            self._composite.create_new_image()

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
        """
        self._check_files()
        self._check_roi()
        self._check_composite_dims()
        self._process_roi()
        if self.get_param_value('use_bg_file'):
            self._check_and_set_bg_file()

    @copy_docstring(CompositeImage)
    def apply_thresholds(self, **kwargs):
        if (self.get_param_value('use_thresholds')
                or 'low' in kwargs or 'high' in kwargs):
            if 'low' in kwargs:
                self.set_param_value('threshold_low', kwargs.get('low'))
            if 'high' in kwargs:
                self.set_param_value('threshold_high', kwargs.get('high'))
            self._composite.apply_thresholds(
                low=self.get_param_value('threshold_low'),
                high=self.get_param_value('threshold_high')
                )

    def export_image(self, output_fname):
        """
        Export the CompositeImage to a file.

        This method is a wrapper for the CompositeImage.export method.
        Supported file types for export are: binary, numpy, hdf5, png, tiff,
        jpg.

        Parameters
        ----------
        output_fname : str
            The full file system path and filename for the output image file.
        """
        self._composite.export(output_fname)

    @property
    def composite(self):
        """
        Get the composite image.

        Returns
        -------
        np.ndarray
            The composite image in np.ndarray format.
        """
        return self._composite.image

    def _check_files(self):
        """
        Check the file names, paths and (for hdf5 images), the size of the
        dataset with respect to the selected image numbers.

        Raises
        ------
        AppConfigError
            If any of the checks fail.
        """
        _first_file = self.get_param_value('first_file')
        check_file_exists(_first_file)
        self._create_filelist()
        if os.path.splitext(_first_file)[1] in HDF5_EXTENSIONS:
            self._store_image_data_from_hdf5_file()
        else:
            self._store_image_data_from_single_image()
        self._config['n_total'] = (self._config['n_image_per_file']
                                   * self._config['n_files'])

    def _store_image_data_from_hdf5_file(self):
        """
        Store config metadata from hdf5 file.

        Raises
        ------
        AppConfigError
            If the selected image range is not included in the hdf5 dataset.
        """
        _first_file = self.get_param_value('first_file')
        _key = self.get_param_value('hdf5_key')
        check_hdf5_key_exists_in_file(_first_file, _key)

        _meta = get_hdf5_metadata(_first_file, ['shape', 'dtype'], _key)
        _n0 = self._apply_param_modulo('hdf5_first_image_num',
                                       _meta['shape'][0])
        _n1 = self._apply_param_modulo('hdf5_last_image_num',
                                       _meta['shape'][0])
        if not _n0 < _n1:
            raise AppConfigError(
                f'The image numbers for the hdf5 file, [{_n0}, {_n1}] do'
                ' not describe a correct range.')
        self._store_image_data(_meta['shape'][1:3], _meta['dtype'])
        # correct total number of images for stepping *after* the
        # numbers have been modulated to be in the image range.
        _n_per_file = ((_n1 - _n0 - 1)
                       // self.get_param_value('hdf5_stepping') + 1)
        self._config['n_image_per_file'] = _n_per_file
        self._config['hdffile'] = True

    def _store_image_data_from_single_image(self):
        """
        Store config metadata from file range.
        """
        _test_image = read_image(self.get_param_value('first_file'))
        self._store_image_data(_test_image.shape, _test_image.dtype)
        self._config['hdffile'] = False

    def _store_image_data(self, img_shape, img_dtype):
        """
        Store the data about the image shape and datatype.

        Parameters
        ----------
        img_shape : tuple
            The shape of the image.
        img_dtype : datatype
            The python datatype of the image.
        """
        self._config['n_image_per_file'] = 1
        self._config['datatype'] = img_dtype
        self._config['raw_img_shape_x'] = img_shape[1]
        self._config['raw_img_shape_y'] = img_shape[0]

    def _create_filelist(self):
        """
        Create the list of all files to be processed.
        """
        verify_files_in_same_directory(self.get_param_value('first_file'),
                                       self.get_param_value('last_file'))
        if self.get_param_value('live_processing'):
            self._create_filelist_live_processing()
        else:
            self._create_filelist_static()

    def _create_filelist_static(self):
        """
        Create the list of files for static processing,

        The list of files to be processed is created based on the filenames
        of the first and last files. The directory content will be sorted
        and the first and last files names will be used to select the part
        of filesnames to be stored.
        """
        _path1, _fname1 = os.path.split(self.get_param_value('first_file'))
        _path2, _fname2 = os.path.split(self.get_param_value('last_file'))
        if _path2 == '':
            self._config['file_list'] = [_fname1]
            self._config['file_path'] = _path1
            self._config['n_files'] = 1
            return
        _list = sorted(os.listdir(_path1))
        _i1 = _list.index(_fname1)
        _i2 = _list.index(_fname2)
        _list = _list[_i1:_i2+1:self.get_param_value('file_stepping')]
        if not self.get_param_value('live_processing'):
            verify_files_of_range_are_same_size(_path1, _list)
        self._config['file_list'] = _list
        self._config['file_path'] = _path1
        self._config['n_files'] = len(_list)

    def _create_filelist_live_processing(self):
        """
        Create the filelist for live processing.

        This method will filter the compare the names of the first and last
        file and try to interprete the selected range.
        """
        _path1, _fname1 = os.path.split(self.get_param_value('first_file'))
        _path2, _fname2 = os.path.split(self.get_param_value('last_file'))
        _items1 = re.split(FILENAME_DELIMITERS, os.path.splitext(_fname1)[0])
        _items2 = re.split(FILENAME_DELIMITERS, os.path.splitext(_fname2)[0])
        diff_index = []
        for index in range(len(_items1)):
            if _items1[index] != _items2[index]:
                diff_index.append(index)
        if len(diff_index) != 1:
            raise AppConfigError(
                'Could not interprete the filenames. The filenames do not '
                'differ in exactly one item, as determined by the delimiters.'
                f'Delimiters considered are: {FILENAME_DELIMITERS.split("|")}')
        diff_index = diff_index[0]
        _index1 = int(_items1[diff_index])
        _index2 = int(_items2[diff_index])
        _n = len(_items1[diff_index])
        _strindex = np.sum(np.r_[[len(_items1[index]) + 1
                                  for index in range(diff_index)]])

        _fnames = (_fname1[:_strindex] + '{index:0' + f'{_n}' + 'd}'
                   + _fname1[_strindex + _n:])
        self._config['file_list'] = [_fnames.format(index=i) for i in
                                     range(_index1, _index2 + 1)]
        self._config['file_path'] = _path1
        self._config['n_files'] = _index2 - _index1 + 1


    def _check_and_set_bg_file(self):
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
        """
        _bg_file = self.get_param_value('bg_file')
        check_file_exists(_bg_file)
        # check hdf5 key and dataset dimensions
        if os.path.splitext(_bg_file)[1] in HDF5_EXTENSIONS:
            check_hdf5_key_exists_in_file(_bg_file,
                                          self.get_param_value('bg_hdf5_key'))
            _params = dict(dataset=self.get_param_value('bg_hdf5_key'),
                           binning=self.get_param_value('binning'),
                           imageNo=self.get_param_value('bg_hdf5_num'),
                           ROI=self._config['roi'])
        else:
            _params = dict(binning=self.get_param_value('binning'),
                           ROI=self._config['roi'])
        _bg_image = read_image(_bg_file, **_params)
        if not _bg_image.shape == (self._config['final_image_size_y'],
                                   self._config['final_image_size_x']):
            raise AppConfigError(f'The selected background file "{_bg_file}"'
                                 ' does not have the same image dimensions '
                                 'as the selected files.')
        self._config['bg_image'] = _bg_image

    def _check_roi(self):
        """
        Check the ROI for consistency.

        Raises
        ------
        AppConfigError
            If the ROI boundaries are not consistent.
        """
        if self.get_param_value('use_roi'):
            _warning = ''
            _x0 = self._apply_param_modulo('roi_xlow',
                                           self._config['raw_img_shape_x'])
            _x1 = self._apply_param_modulo('roi_xhigh',
                                           self._config['raw_img_shape_x'])
            _y0 = self._apply_param_modulo('roi_ylow',
                                           self._config['raw_img_shape_y'])
            _y1 = self._apply_param_modulo('roi_yhigh',
                                           self._config['raw_img_shape_y'])
            if _x1 < _x0:
                _warning += f'ROI x-range incorrect: [{_x0}, {_x1}]'
            if _y1 < _y0:
                _warning += f'ROI y-range incorrect: [{_y0}, {_y1}]'
            if _warning:
                raise AppConfigError(_warning)

    def _check_composite_dims(self):
        """
        Check the dimensions of the composite image.

        Raises
        ------
        AppConfigError
            If the composite dimensions are too small or too large to match
            the total number of images.
        """
        _nx = self.get_param_value('composite_nx')
        _ny = self.get_param_value('composite_ny')
        _ntotal = self._config['n_image_per_file'] * self._config['n_files']
        if _nx == -1:
            _nx = int(np.ceil(_ntotal / _ny))
            self.params.set_value('composite_nx', _nx)
        if _ny == -1:
            _ny = int(np.ceil(_ntotal / _nx))
            self.params.set_value('composite_ny', _ny)
        if _nx * _ny < _ntotal:
            raise AppConfigError(
                'The selected composite dimensions are too small to hold all'
                f' images. (nx={_nx}, ny={_ny}, n={_ntotal})')
        if ((_nx - 1) * _ny >= _ntotal or _nx * (_ny - 1) >= _ntotal):
            raise AppConfigError(
                'The selected composite dimensions are too large for all'
                f' images. (nx={_nx}, ny={_ny}, n={_ntotal})')

    def _process_roi(self):
        """
        Process the ROI inputs and store the ROI.
        """
        _binning = self.get_param_value('binning')
        if self.get_param_value('use_roi'):
            _y0 = self.get_param_value('roi_ylow')
            _y1 = self.get_param_value('roi_yhigh')
            _x0 = self.get_param_value('roi_xlow')
            _x1 = self.get_param_value('roi_xhigh')
            self._config['final_image_size_x'] = (_x1 - _x0) // _binning
            self._config['final_image_size_y'] = (_y1 - _y0) // _binning
            self._config['roi'] = (slice(_y0, _y1), slice(_x0, _x1))
        else:
            self._config['final_image_size_x'] = \
                self._config['raw_img_shape_x'] // _binning
            self._config['final_image_size_y'] = \
                self._config['raw_img_shape_y'] // _binning
            self._config['roi'] = None

    def _get_args_for_read_image(self, index):
        """
        Create the required kwargs to pass to the read_image function.

        Parameters
        ----------
        index : int
            The image index

        Returns
        -------
        _fname : str
            The filename of the file to be opened.
        _params : dict
            The required parameters as dictionary.
        """
        _i_file = index // self._config['n_image_per_file']
        _fname = os.path.join(self._config['file_path'],
                              self._config['file_list'][_i_file])
        if self._config['hdffile']:
            _hdf_index = index % self._config['n_image_per_file']
            _i_hdf = (self.get_param_value('hdf5_first_image_num')
                      + _hdf_index * self.get_param_value('hdf5_stepping'))
            _params = dict(dataset=self.get_param_value('hdf5_key'),
                           binning=self.get_param_value('binning'),
                           ROI=self._config['roi'], imageNo=_i_hdf)
        else:
            _params = dict(binning=self.get_param_value('binning'),
                           ROI=self._config['roi'])
        return _fname, _params


def _parse_composite_creator_cmdline_arguments():
    """
    Use argparse to get command line arguments.

    Returns
    -------
    dict
        A dictionary with the parsed arugments which holds all the entries
        and entered values or  - if missing - the default values.
    """
    parser = argparse.ArgumentParser()
    parser.add_argument('-first_file', '-f',
                        help=DEFAULT_PARAMS['first_file'].tooltip)
    parser.add_argument('-last_file', '-l',
                        help=DEFAULT_PARAMS['last_file'].tooltip)
    parser.add_argument('-file_stepping', type=int,
                        help=DEFAULT_PARAMS['file_stepping'].tooltip)
    parser.add_argument('-hdf5_key',
                        help=DEFAULT_PARAMS['hdf5_key'].tooltip)
    parser.add_argument('-hdf5_first_image_num', type=int,
                        help=DEFAULT_PARAMS['hdf5_first_image_num'].tooltip)
    parser.add_argument('-hdf5_last_image_num', type=int,
                        help=DEFAULT_PARAMS['hdf5_last_image_num'].tooltip)
    parser.add_argument('-hdf5_stepping', type=int,
                        help=DEFAULT_PARAMS['hdf5_stepping'].tooltip)
    parser.add_argument('--use_bg_file', action='store_true',
                        help=DEFAULT_PARAMS['use_bg_file'].tooltip)
    parser.add_argument('-bg_file',
                        help=DEFAULT_PARAMS['bg_file'].tooltip)
    parser.add_argument('-bg_hdf5_key',
                        help=DEFAULT_PARAMS['bg_hdf5_key'].tooltip)
    parser.add_argument('-bg_hdf5_num', type=int,
                        help=DEFAULT_PARAMS['bg_hdf5_num'].tooltip)
    parser.add_argument('-composite_nx', type=int,
                        help=DEFAULT_PARAMS['composite_nx'].tooltip)
    parser.add_argument('-composite_ny', type=int,
                        help=DEFAULT_PARAMS['composite_ny'].tooltip)
    parser.add_argument('--use_roi', action='store_true',
                        help=DEFAULT_PARAMS['use_roi'].tooltip)
    parser.add_argument('-roi_xlow', type=int,
                        help=DEFAULT_PARAMS['roi_xlow'].tooltip)
    parser.add_argument('-roi_xhigh', type=int,
                        help=DEFAULT_PARAMS['roi_xhigh'].tooltip)
    parser.add_argument('-roi_ylow', type=int,
                        help=DEFAULT_PARAMS['roi_ylow'].tooltip)
    parser.add_argument('-roi_yhigh', type=int,
                        help=DEFAULT_PARAMS['roi_yhigh'].tooltip)
    parser.add_argument('--use_thresholds', action='store_true',
                        help=DEFAULT_PARAMS['use_thresholds'].tooltip)
    parser.add_argument('-threshold_low', type=int,
                        help=DEFAULT_PARAMS['threshold_low'].tooltip)
    parser.add_argument('-threshold_high', type=int,
                        help=DEFAULT_PARAMS['threshold_high'].tooltip)
    parser.add_argument('-binning', type=int,
                        help=DEFAULT_PARAMS['binning'].tooltip)
    parser.add_argument('-output_fname',
                        help=DEFAULT_PARAMS['output_fname'].tooltip)
    _args = dict(vars(parser.parse_args()))
    # store None for keyword arguments which were not selected:
    for _key in ['use_roi', 'use_thresholds', 'use_bg_file']:
        _args[_key] = _args[_key] if _args[_key] else None
    return _args
