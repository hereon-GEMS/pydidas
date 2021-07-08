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
import time
from pathlib import Path

import numpy as np
from PyQt5 import QtCore

from pydidas.apps.app_utils import FilelistManager, ImageMetadataManager
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
    get_generic_parameter('images_per_file'),
    get_generic_parameter('use_bg_file'),
    get_generic_parameter('bg_file'),
    get_generic_parameter('bg_hdf5_key'),
    get_generic_parameter('bg_hdf5_num'),
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
    live_processing : bool, optional
        Keyword to toggle live processing which means file existance and size
        checks will be disabled in the setup process and the file processing
        will wait for files to be created (indefinitely). The default is
        False.
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
        self._filelist = FilelistManager(self.params.get('first_file'),
                                         self.params.get('last_file'),
                                         self.params.get('live_processing'),
                                         self.params.get('file_stepping'))
        self._image_metadata = ImageMetadataManager(
            self.params.get('first_file'),
            self.params.get('hdf5_key'),
            self.params.get('hdf5_first_image_num'),
            self.params.get('hdf5_last_image_num'),
            self.params.get('hdf5_stepping'),
            self.params.get('images_per_file'),
            self.params.get('binning'),
            self.params.get('use_roi'),
            self.params.get('roi_xlow'),
            self.params.get('roi_xhigh'),
            self.params.get('roi_ylow'),
            self.params.get('roi_yhigh'),
            )

        self._config = { 'bg_image': None,
                         'current_fname': None,
                         'current_kwargs': {}}

    def multiprocessing_pre_run(self):
        """
        Perform operations prior to running main parallel processing function.
        """
        self.prepare_run()
        self._config['mp_pre_run_called'] = True
        _ntotal = (self._image_metadata.images_per_file
                   * self._filelist.n_files)
        self._config['mp_tasks'] = range(_ntotal)

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

    def multiprocessing_pre_cycle(self, index):
        _fname, _kwargs = self._get_args_for_read_image(index)
        self._config['current_fname'] = _fname
        self._config['current_kwargs'] = _kwargs

    def multiprocessing_carryon(self):
        if self.get_param_value('live_processing'):
            try:
                self._wait_for_image(self._config['current_fname'],
                                     timeout=0.1)
                return True
            except FileNotFoundError:
                return False
        return True

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
        _image = read_image(self._config['current_fname'],
                            **self._config['current_kwargs'])
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
        if self.get_param_value('use_bg_file'):
            image -= self._config['bg_image']
        self._composite.insert_image(image, index)

    def prepare_run(self):
        """
        Prepare running the composite creation.

        This method will check all settings and create the composite image or
        tell the CompositeImage to create a new image with changed size.

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
        self._filelist.update()
        self._image_metadata.update_input_data()
        self._image_metadata.update_final_image()
        self._check_composite_dims()
        if self.get_param_value('use_bg_file'):
            self._check_and_set_bg_file()

        if self._composite is None:
            self._composite = CompositeImage(
                image_shape=self._image_metadata.final_shape,
                composite_nx=self.get_param_value('composite_nx'),
                composite_ny=self.get_param_value('composite_ny'),
                composite_dir=self.get_param_value('composite_dir'),
                datatype=self._image_metadata.datatype)
        else:
            self.__check_and_update_composite_image()

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
                high=self.get_param_value('threshold_high'))

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
                           ROI=self._image_metadata.roi)
        else:
            _params = dict(binning=self.get_param_value('binning'),
                           ROI=self._image_metadata.roi)
        _bg_image = read_image(_bg_file, **_params)
        if not _bg_image.shape == self._image_metadata.final_shape:
            raise AppConfigError(f'The selected background file "{_bg_file}"'
                                 ' does not have the same image dimensions '
                                 'as the selected files.')
        self._config['bg_image'] = _bg_image



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
        _ntotal = (self._image_metadata.images_per_file
                   * self._filelist.n_files)
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

    def __check_and_update_composite_image(self):
        _update_required = False
        _image_shape = self._image_metadata.final_shape
        if _image_shape != self._composite.get_param_value('image_shape'):
            self._composite.set_param_value('image_shape', _image_shape)
            _update_required = True
        _nx = self.get_param_value('composite_nx')
        if _nx != self._composite.get_param_value('composite_nx'):
            self._composite.set_param_value('composite_nx', _nx)
            _update_required = True
        _ny = self.get_param_value('composite_ny')
        if _ny != self._composite.get_param_value('composite_ny'):
            self._composite.set_param_value('composite_ny', _ny)
            _update_required = True
        if _update_required:
            self._composite.create_new_image()


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
        _images_per_file = self._image_metadata.images_per_file
        _i_file = index // _images_per_file
        _fname = self._filelist.get_filename(_i_file)
        _params = dict(binning=self.get_param_value('binning'),
                       ROI=self._image_metadata.roi)
        if os.path.splitext(_fname)[1] in HDF5_EXTENSIONS:
            _hdf_index = index % _images_per_file
            _i_hdf = (self.get_param_value('hdf5_first_image_num')
                      + _hdf_index * self.get_param_value('hdf5_stepping'))
            _params = _params | dict(dataset=self.get_param_value('hdf5_key'),
                                     imageNo=_i_hdf)
        return _fname, _params

    def _wait_for_image(self, fname, timeout=-1):
        """
        Wait for the file to exist in the file system.

        Parameters
        ----------
        fname : str
            The file path & name.
        timeout : float, optional
            If a timeout larger than zero is selected, the process will wait
            a maximum of timeout seconds before raising an Exception.
            The value "-1" corresponds to no timeout. The default is -1.
        """
        _target_size = self._filelist.filesize
        _starttime = time.time()
        while os.stat(fname).st_size != _target_size:
            time.sleep(0.1)
            if timeout > 0 and time.time() - _starttime > timeout:
                raise FileNotFoundError(
                    f'The file {fname} was not found during the timeout'
                    'period. Aborting...')


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
