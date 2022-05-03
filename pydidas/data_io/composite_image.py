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
Module with the CompositeImage class used for creating mosaic images.
"""

__author__ = "Malte Storm"
__copyright__ = "Copyright 2021-2022, Malte Storm, Helmholtz-Zentrum Hereon"
__license__ = "GPL-3.0"
__maintainer__ = "Malte Storm"
__status__ = "Development"
__all__ = ['CompositeImage']


from copy import copy

import numpy as np

from ..core import (AppConfigError, ParameterCollection, get_generic_parameter,
                   ObjectWithParameterCollection)
from .import_export import export_data


class CompositeImage(ObjectWithParameterCollection):
    """
    The CompositeImage class holds a numpy array to combine individual images
    to a composite and to provide basic insertion and manipulation routines.
    """
    default_params = ParameterCollection(
        get_generic_parameter('image_shape'),
        get_generic_parameter('composite_nx'),
        get_generic_parameter('composite_ny'),
        get_generic_parameter('composite_dir'),
        get_generic_parameter('datatype'),
        get_generic_parameter('threshold_low'),
        get_generic_parameter('threshold_high'),
        get_generic_parameter('mosaic_border_width'),
        get_generic_parameter('mosaic_border_value'),
        get_generic_parameter('mosaic_max_size'),
        )

    def __init__(self, *args, **kwargs):
        ObjectWithParameterCollection.__init__(self)
        self.__image = None
        self.set_default_params()
        self.__get_default_qsettings()
        for _key in kwargs:
            self.set_param_value(_key, kwargs[_key])
        if self.__check_config():
            self.__create_image_array()

    def __get_default_qsettings(self):
        """
        Update local Parameters with the global QSetting values.
        """
        self.set_param_value(
            'mosaic_border_width',
            self.q_settings_get_global_value('mosaic_border_width'))
        self.set_param_value(
            'mosaic_border_value',
            self.q_settings_get_global_value('mosaic_border_value'))
        self.set_param_value(
            'mosaic_max_size',
            self.q_settings_get_global_value('mosaic_max_size'))

    def __check_config(self):
        """
        Check whether the config is consistent.

        Returns
        -------
        _okay : bool
            The method returns True if all Parameters have been set correctly.
        """
        _okay = True
        if not self.get_param_value('image_shape')[0] > 0:
            _okay = False
        if not self.get_param_value('image_shape')[1] > 0:
            _okay = False
        if not self.get_param_value('composite_nx') > 0:
            _okay = False
        if not self.get_param_value('composite_ny') > 0:
            _okay = False
        return _okay

    def __verify_config(self):
        """
        Verify all required Parameters have been set.

        Raises
        ------
        ValueError
            If one or more of the required config fields have not been set.
        """
        if not self.__check_config():
            raise ValueError('Not all required values for the creation of a '
                             'CompositeImage have been set.')

    def __create_image_array(self):
        """
        Create the image array.

        This method creates the array based on the configuration and prepares
        it for inserting images.
        """
        self.__verify_config()
        _shape = self.__get_composite_shape()
        self.__check_max_size(_shape)
        self.__image = (np.zeros(_shape,
                                 dtype = self.get_param_value('datatype'))
                        + self.get_param_value('mosaic_border_value'))

    def __get_composite_shape(self):
        """
        Get the shape of the new array.

        Returns
        -------
        tuple
            The new shape.
        """
        _shape = self.get_param_value('image_shape')
        _border_width = self.get_param_value('mosaic_border_width')
        _nx =  (self.get_param_value('composite_nx')
                * (_shape[1] + _border_width) - _border_width)
        _ny =  (self.get_param_value('composite_ny')
                * (_shape[0] + _border_width) - _border_width)
        return (_ny, _nx)

    def __check_max_size(self, shape):
        """
        Check that the size of the new image is not larger than the global
        size limit.

        Parameters
        ----------
        shape : tuple
            The size of the image in pixels.

        Raises
        ------
        AppConfigError
            If the size of the image is larger than the defined global limit.
        """
        _size = 1e-6 * shape[0] * shape[1]
        _maxsize = self.get_param_value('mosaic_max_size')
        if _size > _maxsize:
            raise AppConfigError(f'The requested image size ({_size} Mpx)'
                                 ' is too large for the global size limit '
                                 f'of {_maxsize} Mpx.')

    def apply_thresholds(self, **kwargs):
        """
        Apply thresholds to the composite image.

        This method applies thresholds to the composite image. By default, it
        will apply the thresholds defined in the ParameterCollection but these
        can be overwritten with the low and high arguments. Note that these
        values will be used to update the ParameterCollection.
        This method will only apply the thresholds to the image but will not
        return the iamge itself.

        Parameters
        ----------
        low : Union[float, None], optional
            The lower threshold. If not specified, the stored lower threshold
            from the ParameterCollection will be used. A value of np.nan or
            None will be ignored.
        high : Union[float, None], optional
            The upper threshold. If not specified, the stored upper threshold
            from the ParameterCollection will be used. A value of np.nan or
            None will be ignored.
        """
        self.__update_threshold('low', **kwargs)
        self.__update_threshold('high', **kwargs)
        _thresh_low = self.get_param_value('threshold_low')
        if _thresh_low is not None:
            self.__image[self.__image < _thresh_low] = _thresh_low
        _thresh_high = self.get_param_value('threshold_high')
        if _thresh_high is not None:
            self.__image[self.__image > _thresh_high] = _thresh_high

    def __update_threshold(self, key, **kwargs):
        """
        Update the threshold from the kwargs, if the key in included and
        change non-finite numbers to None.

        Parameters
        ----------
        key : str
            The threshold key. Must be either "low" or "high"
        **kwargs : dict
            The kwargs passed on from the apply thresholds method.
        """
        _thresh = self.get_param_value(f'threshold_{key}')
        if key in kwargs:
            _thresh = kwargs.get(key)
        # check for non-finite values and convert them to None:
        if _thresh is not None and not np.isfinite(_thresh):
            _thresh = None
        self.set_param_value(f'threshold_{key}', _thresh)

    def create_new_image(self):
        """
        Create a new image array with the stored Parameters.

        The new image array is accessible through the .image property.
        """
        self.__get_default_qsettings()
        self.__create_image_array()

    def insert_image(self, image, index):
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
        """
        if self.__image is None:
            self.__create_image_array()
        _image_size = self.get_param_value('image_shape')
        _border = self.get_param_value('mosaic_border_width')
        if self.get_param_value('composite_dir') == 'x':
            _iy = index // self.get_param_value('composite_nx')
            _ix = index % self.get_param_value('composite_nx')
        else:
            _iy = index % self.get_param_value('composite_ny')
            _ix = index // self.get_param_value('composite_ny')
        _start_y = _iy * (_image_size[0] + _border)
        _start_x = _ix * (_image_size[1] + _border)
        yslice = slice(_start_y, _start_y + _image_size[0])
        xslice = slice(_start_x, _start_x + _image_size[1])
        image = self.__apply_thresholds_to_data(image)
        self.__image[yslice, xslice] = image

    def __apply_thresholds_to_data(self, image):
        """
        Apply thresholds to the data.

        Parameters
        ----------
        image : np.ndarray
            The input image

        Returns
        -------
        image : np.ndarray
            The image with thresholds applied.
        """
        _low = self.get_param_value('threshold_low')
        _high = self.get_param_value('threshold_high')
        if _low is not None:
            image = np.where(image < _low, _low, image)
        if _high is not None:
            image = np.where(image > _high, _high, image)
        return image

    def save(self, output_fname):
        """
        Save the image in binary npy format.

        Parameters
        ----------
        output_fname : str
            The full filename and path to the output image file.
        """
        np.save(output_fname, self.__image)

    def export(self, output_fname):
        """
        Export the image to a file.

        Parameters
        ----------
        output_fname : str
            The full file system path and filename for the output image file.
        """
        export_data(output_fname, self.__image)

    @property
    def image(self):
        """
        Get the composite image.

        Returns
        -------
        np.ndarray
            The composite image.
        """
        return self.__image

    @property
    def shape(self):
        """
        Get the shape of the composite image.

        Returns
        -------
        tuple
            The shape of the composite image.
        """
        if self.__image is None:
            return (0, 0)
        return self.__image.shape

    def __copy__(self):
        """
        Create a copy of the object.

        Returns
        -------
        fm : ObjectWithParameterCollection
            The copy with the same state.
        """
        obj = self.__class__()
        obj.params = self.params.get_copy()
        obj._config = copy(self._config)
        obj.__image = self.__image
        return obj
