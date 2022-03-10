# This file is part of pydidas.
#
# pydidas is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
#
# Pydidas is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE. See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with Pydidas. If not, see <http://www.gnu.org/licenses/>.

"""
Module with the CompositeCreatorApp class which allows to combine
images to mosaics.
"""

__author__ = "Malte Storm"
__copyright__ = "Copyright 2021-2022, Malte Storm, Helmholtz-Zentrum Hereon"
__license__ = "GPL-3.0"
__version__ = "0.1.1"
__maintainer__ = "Malte Storm"
__status__ = "Development"
__all__ = ['CompositeCreatorApp']

import os
import time

import numpy as np
from qtpy import QtCore

from ..core import (Dataset, AppConfigError, get_generic_param_collection,
                    BaseApp)
from ..core.constants import HDF5_EXTENSIONS
from ..core.utils import (check_file_exists, check_hdf5_key_exists_in_file,
                          copy_docstring)
from ..image_io import CompositeImage, read_image, rebin2d
from ..managers import FilelistManager, ImageMetadataManager
from .parsers import composite_creator_app_parser


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

    Notes
    -----
    The full list of Parameters used by the CompositeCreatorApp:

    live_processing : bool, optional
        Keyword to toggle live processing which means file existance and size
        checks will be disabled in the setup process and the file processing
        will wait for files to be created (indefinitely). The default is
        False.
    first_file : Union[str, pathlib.Path]
        The name of the first file for a file series or of the hdf5 file in
        case of hdf5 file input.
    last_file : Union[str, pathlib.Path], optional
        Used only for file series: The name of the last file to be added to
        the composite image. The default is an empty Path.
    file_stepping : int, optional
        The step width (in files). A value n > 1 will only process every n-th
        image for the composite. The default is 1.
    hdf5_key : Hdf5key, optional
        Used only for hdf5 files: The dataset key. The default is
        entry/data/data.
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
    bg_file : Union[str, pathlib.Path], optional
        The name of the file used for background correction. The default is
        an empty Path.
    bg_hdf5_key : Hdf5key, optional
        Required for hdf5 background image files: The dataset key with the
        image for the background file. The default is entry/data/data
    bg_hdf5_frame : int, optional
        Required for hdf5 background image files: The image number of the
        background image in the dataset. The default is 0.
    use_global_det_mask : bool, optional
        Keyword to enable or disable using the global detector mask as
        defined by the global mask file and mask value. The default is True.
    use_roi : bool, optional
        Keyword to toggle use of the ROI for cropping the original images
        before combining them. The default is False.
    roi_xlow : int, optional
        The lower boundary (in pixel) for cropping images in x, if use_roi is
        enabled. Negative values will be modulated with the image width.
        The default is 0.
    roi_xhigh : Union[int, None], optional
        The upper boundary (in pixel) for cropping images in x, if use_roi is
        enabled. Negative values will be modulated with the image width, i.e.
        -1 is equivalent with the full image size minus one. None corresponds
		to the full image width (with respect to the upper boundary).The
        default is None.
    roi_ylow : int, optional
        The lower boundary (in pixel) for cropping images in y, if use_roi is
        enabled. Negative values will be modulated with the image width.
        The default is 0.
    roi_yhigh : Union[int, None], optional
        The upper boundary (in pixel) for cropping images in y, if use_roi is
        enabled. Negative values will be modulated with the image width, i.e.
        -1 is equivalent with the full image size minus one. None corresponds
		to the full image width (with respect to the upper boundary). The
        default is None.
    use_thresholds : bool, optional
        Keyword to enable or disable the use of thresholds. If True,
        threshold use is enabled and both threshold values will be used. The
        default is False.
    threshold_low : int, optional
        The lower threshold of the composite image. If any finite value
        (i.e. not np.nan or None) is used, the value of any pixels with a value
        below the threshold will be replaced by the threshold value. A value
        of np.nan or None will ignore the threshold. The default is None.
    threshold_high : int, optional
        The upper threshold of the composite image. If any finite value
        (i.e. not np.nan or None) is used, the value of any pixels with a value
        above the threshold will be replaced by the threshold value. A value
        of np.nan or None will ignore the threshold. The default is None.
    binning : int, optional
        The re-binning factor for the images in the composite. The binning
        will be applied to the cropped images. The default is 1.
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

    Parameters
    ----------
    *args : tuple
        Any number of Parameters. These will be added to the app's
        ParameterCollection.
    **kwargs : dict
        Parameters supplied with their reference key as dict key and the
        Parameter itself as value.
    """
    default_params = get_generic_param_collection(
        'live_processing', 'first_file', 'last_file', 'file_stepping',
        'hdf5_key', 'hdf5_first_image_num', 'hdf5_last_image_num',
        'hdf5_stepping', 'use_bg_file', 'bg_file', 'bg_hdf5_key',
        'bg_hdf5_frame', 'use_global_det_mask', 'use_roi', 'roi_xlow',
        'roi_xhigh', 'roi_ylow', 'roi_yhigh', 'use_thresholds',
        'threshold_low', 'threshold_high', 'binning', 'composite_nx',
        'composite_ny', 'composite_dir', )
    parse_func = composite_creator_app_parser
    attributes_not_to_copy_to_slave_app = ['_composite', '_det_mask',
                                           '_bg_image']
    mp_func_results = QtCore.Signal(object)
    updated_composite = QtCore.Signal()

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self._composite = None
        self._det_mask = None
        self._bg_image = None
        self._filelist = FilelistManager(*self.get_params(
            'first_file', 'last_file', 'live_processing', 'file_stepping'))
        self._image_metadata = ImageMetadataManager(*self.get_params(
            'first_file', 'hdf5_key', 'hdf5_first_image_num',
            'hdf5_last_image_num', 'hdf5_stepping', 'binning', 'use_roi',
            'roi_xlow', 'roi_xhigh', 'roi_ylow', 'roi_yhigh'))
        self._image_metadata.set_param_value('use_filename', False)
        self._config = {'current_fname': None,
                        'current_kwargs': {},
                        'det_mask_val': None}

    def multiprocessing_pre_run(self):
        """
        Perform operations prior to running main parallel processing function.
        """
        self.prepare_run()
        self._config['mp_pre_run_called'] = True
        _ntotal = (self._image_metadata.images_per_file
                   * self._filelist.n_files)
        self._config['mp_tasks'] = range(_ntotal)
        self._config['det_mask_val'] = float(self.q_settings_get_global_value(
            'det_mask_val'))
        self._det_mask = self.__get_detector_mask()

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
        self._image_metadata.update()
        self.__verify_total_number_of_images_in_composite()
        if self.get_param_value('use_bg_file'):
            self._check_and_set_bg_file()
        if self.slave_mode:
            self._composite = None
            return
        self.__check_and_update_composite_image()
        self.__check_and_store_thresholds()

    def __get_detector_mask(self):
        """
        Get the detector mask from the file specified in the global QSettings.

        Returns
        -------
        _mask : Union[None, np.ndarray]
            If the mask could be loaded from a numpy file, return the mask.
            Else, None is returned.
        """
        if not self.get_param_value('use_global_det_mask'):
            return None
        _maskfile = self.q_settings_get_global_value('det_mask')
        try:
            _mask = np.load(_maskfile)
        except (FileNotFoundError, ValueError):
            return None
        if self._image_metadata.roi is not None:
            _mask = _mask[self._image_metadata.roi]
        _bin = self.get_param_value('binning')
        if _bin > 1:
            _mask = rebin2d(_mask, _bin)
            _mask = np.where(_mask > 0, 1, 0)
            _mask = _mask.astype(np.bool_)
        return _mask

    def __verify_total_number_of_images_in_composite(self):
        """
        Check the dimensions of the composite image and verifies that it holds
        the right amount of images.

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
        _params = dict(binning=self.get_param_value('binning'),
                       roi=self._image_metadata.roi)
        if os.path.splitext(_bg_file)[1] in HDF5_EXTENSIONS:
            check_hdf5_key_exists_in_file(_bg_file,
                                          self.get_param_value('bg_hdf5_key'))
            _params['hdf5_dataset'] = self.get_param_value('bg_hdf5_key')
            _params['frame'] = self.get_param_value('bg_hdf5_frame')
        _bg_image = read_image(_bg_file, **_params)
        if _bg_image.shape != self._image_metadata.final_shape:
            raise AppConfigError(f'The selected background file "{_bg_file}"'
                                 ' does not have the same image dimensions '
                                 'as the selected files.')
        self._bg_image = self.__apply_mask(_bg_image)

    def __check_and_update_composite_image(self):
        """
        Check the size of the Composite and create a new Composite if the
        shape does not match the new input.
        """
        if self._composite is None:
            self._composite = CompositeImage(
                image_shape=self._image_metadata.final_shape,
                composite_nx=self.get_param_value('composite_nx'),
                composite_ny=self.get_param_value('composite_ny'),
                composite_dir=self.get_param_value('composite_dir'),
                datatype=self._image_metadata.datatype)
            return
        _update_required = False
        _bwidth = self.q_settings_get_global_value('mosaic_border_width', int)
        _bval = self.q_settings_get_global_value('mosaic_border_value', float)
        for _key, _value in [
                ['image_shape', self._image_metadata.final_shape],
                ['composite_nx', self.get_param_value('composite_nx')],
                ['composite_ny', self.get_param_value('composite_ny')],
                ['mosaic_border_width', _bwidth],
                ['mosaic_border_value', _bval]]:
            if _value != self._composite.get_param_value(_key):
                self._composite.set_param_value(_key, _value)
                _update_required = True
        if _update_required:
            self._composite.create_new_image()

    def __check_and_store_thresholds(self):
        """
        Check for thresholds and store them in the local config.
        """
        if self.get_param_value('use_thresholds'):
            self._composite.set_param_value(
                'threshold_low', self.get_param_value('threshold_low'))
            self._composite.set_param_value(
                'threshold_high', self.get_param_value('threshold_high'))

    def multiprocessing_get_tasks(self):
        """
        Return all tasks required in multiprocessing.
        """
        if 'mp_tasks' not in self._config.keys():
            raise KeyError('Key "mp_tasks" not found. Please execute'
                           'multiprocessing_pre_run() first.')
        return self._config['mp_tasks']

    def multiprocessing_pre_cycle(self, index):
        """
        Run preparatory functions in the cycle prior to the main function.

        Parameters
        ----------
        index : int
            The index of the image / frame.
        """
        self._store_args_for_read_image(index)

    def _store_args_for_read_image(self, index):
        """
        Create the required kwargs to pass to the read_image function and store
        them internally.

        Parameters
        ----------
        index : int
            The image index
        """
        _images_per_file = self._image_metadata.images_per_file
        _i_file = index // _images_per_file
        _fname = self._filelist.get_filename(_i_file)
        _params = dict(binning=self.get_param_value('binning'),
                       roi=self._image_metadata.roi)
        if os.path.splitext(_fname)[1] in HDF5_EXTENSIONS:
            _hdf_index = index % _images_per_file
            _i_hdf = (self.get_param_value('hdf5_first_image_num')
                      + _hdf_index * self.get_param_value('hdf5_stepping'))
            _params = (_params
                       | dict(hdf5_dataset=self.get_param_value('hdf5_key'),
                              frame=_i_hdf))
        self._config['current_fname'] = _fname
        self._config['current_kwargs'] = _params

    def multiprocessing_carryon(self):
        """
        Get the flag value whether to carry on processing.

        By default, this Flag is always True. In the case of live processing,
        a check is done whether the current file exists.

        Returns
        -------
        bool
            Flag whether the processing can carry on or needs to wait.

        """
        if self.get_param_value('live_processing'):
            return self._image_exists_check(self._config['current_fname'],
                                            timeout=0.02)
        return True

    def _image_exists_check(self, fname, timeout=-1):
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

        Returns
        -------
        bool
            Flag if the image exists and has the same size as the refernce
            file.
        """
        _target_size = self._filelist.filesize
        _starttime = time.time()
        if not os.path.exists(fname):
            return False
        while os.stat(fname).st_size != _target_size:
            time.sleep(0.1)
            if time.time() - _starttime > timeout > 0:
                return False
        return True

    def multiprocessing_func(self, index):
        """
        Perform key operation with parallel processing.

        Returns
        -------
        _image : pydidas.core.Dataset
            The (pre-processed) image.
        """
        _image = read_image(self._config['current_fname'],
                            **self._config['current_kwargs'])
        _image = self.__apply_mask(_image)
        return _image

    def __apply_mask(self, image):
        """
        Apply the detector mask to the image.

        Parameters
        ----------
        image : np.ndarray
            The image data.

        Returns
        -------
        image : pydidas.core.Dataset
            The masked image data.
        """
        if self._det_mask is None:
            return image
        if self._config['det_mask_val'] is None:
            raise AppConfigError('No numerical value has been defined'
                                  ' for the mask!')
        return Dataset(np.where(self._det_mask,
                                self._config['det_mask_val'], image),
                       axis_ranges=image.axis_ranges,
                       axis_labels=image.axis_labels,
                       axis_units=image.axis_units,
                       metadata=image.metadata)

    def multiprocessing_post_run(self):
        """
        Perform operatinos after running main parallel processing function.
        """

    @copy_docstring(CompositeImage)
    def apply_thresholds(self, **kwargs):
        """
        Please refer to pydidas.core.CompositeImage docstring.
        """
        if (self.get_param_value('use_thresholds')
                or 'low' in kwargs or 'high' in kwargs):
            if 'low' in kwargs:
                self.set_param_value('threshold_low', kwargs.get('low'))
            if 'high' in kwargs:
                self.set_param_value('threshold_high', kwargs.get('high'))
            self._composite.apply_thresholds(
                low=self.get_param_value('threshold_low'),
                high=self.get_param_value('threshold_high'))

    @QtCore.Slot(int, object)
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
        if self.slave_mode:
            return
        if self.get_param_value('use_bg_file'):
            image -= self._bg_image
        self._composite.insert_image(image, index)
        self.updated_composite.emit()

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
        image : Union[None, np.ndarray]
            The composite image in np.ndarray format. If no composite has
            been created, this property returns None.
        """
        if self._composite is None:
            return None
        return self._composite.image
