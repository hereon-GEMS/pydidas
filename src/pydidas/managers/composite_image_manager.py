# This file is part of pydidas.
#
# Copyright 2023 - 2025, Helmholtz-Zentrum Hereon
# SPDX-License-Identifier: GPL-3.0-only
#
# pydidas is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License version 3 as
# published by the Free Software Foundation.
#
# Pydidas is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE. See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with Pydidas. If not, see <http://www.gnu.org/licenses/>.

"""
Module with the CompositeImageManager class used for creating mosaic images.
"""

__author__ = "Malte Storm"
__copyright__ = "Copyright 2023 - 2025, Helmholtz-Zentrum Hereon"
__license__ = "GPL-3.0-only"
__maintainer__ = "Malte Storm"
__status__ = "Production"
__all__ = ["CompositeImageManager"]


from copy import copy
from pathlib import Path
from typing import Literal, Self, Union

import numpy as np

from pydidas.core import (
    ObjectWithParameterCollection,
    Parameter,
    ParameterCollection,
    UserConfigError,
    get_generic_parameter,
)
from pydidas.core.constants.image_ops import IMAGE_OPS
from pydidas.data_io import export_data


class CompositeImageManager(ObjectWithParameterCollection):
    """
    A manager to arrrange images in a composite.

    The CompositeImage class holds a numpy array to combine individual images
    to a composite and to provide basic insertion and manipulation routines.
    """

    default_params = ParameterCollection(
        get_generic_parameter("image_shape"),
        get_generic_parameter("composite_nx"),
        get_generic_parameter("composite_ny"),
        get_generic_parameter("composite_dir"),
        get_generic_parameter("composite_image_op"),
        get_generic_parameter("composite_xdir_orientation"),
        get_generic_parameter("composite_ydir_orientation"),
        get_generic_parameter("datatype"),
        get_generic_parameter("threshold_low"),
        get_generic_parameter("threshold_high"),
    )

    def __init__(self, *args, **kwargs):
        ObjectWithParameterCollection.__init__(self)
        self.__image = None
        self.add_params(*args)
        self.set_default_params()
        self.update_param_values_from_kwargs(**kwargs)
        self.__read_default_qsettings()
        for _key, _item in kwargs.items():
            if isinstance(_item, Parameter):
                self.params[_key] = _item
            else:
                self.set_param_value(_key, _item)
        if self.__check_config():
            self.__create_image_array()

    def __read_default_qsettings(self):
        """
        Update local Parameters from the global QSetting values.
        """
        self._config["border_width"] = self.q_settings_get(
            "user/mosaic_border_width", int
        )
        self._config["border_value"] = self.q_settings_get(
            "user/mosaic_border_value", float
        )
        self._config["max_image_size"] = self.q_settings_get(
            "user/max_image_size", float
        )

    def __check_config(self) -> bool:
        """
        Check whether the config is consistent.

        Returns
        -------
        bool
            The method returns True if all Parameters have been set correctly.
        """
        return (
            self.get_param_value("image_shape")[0] > 0
            and self.get_param_value("image_shape")[1] > 0
            and self.get_param_value("composite_nx") > 0
            and self.get_param_value("composite_ny") > 0
        )

    def __verify_config(self):
        """
        Verify all required Parameters have been set.

        Raises
        ------
        ValueError
            If one or more of the required config fields have not been set.
        """
        if not self.__check_config():
            raise UserConfigError(
                "Not all required values for the creation of a "
                "CompositeImage have been set."
            )

    def __create_image_array(self):
        """
        Create the image array.

        This method creates the array based on the configuration and prepares
        it for inserting images.
        """
        self.__verify_config()
        _shape = self.__get_composite_shape()
        self.__check_max_size(_shape)
        self.__image = (
            np.zeros(_shape, dtype=self.get_param_value("datatype"))
            + self._config["border_value"]
        )

    def __get_composite_shape(self) -> tuple[int, int]:
        """
        Get the shape of the new array.

        Returns
        -------
        tuple[int, int]
            The new shape.
        """
        _shape = self.get_param_value("image_shape")
        _border_width = self._config["border_width"]
        _nx = (
            self.get_param_value("composite_nx") * (_shape[1] + _border_width)
            - _border_width
        )
        _ny = (
            self.get_param_value("composite_ny") * (_shape[0] + _border_width)
            - _border_width
        )
        return (_ny, _nx)

    def __check_max_size(self, shape: tuple[int, int]):
        """
        Check that the size of the new image is not larger than the global
        size limit.

        Parameters
        ----------
        shape : tuple[int, int]
            The size of the image in pixels.

        Raises
        ------
        UserConfigError
            If the size of the image is larger than the defined global limit.
        """
        _size = 1e-6 * shape[0] * shape[1]
        _maxsize = self.q_settings_get("global/max_image_size", float)
        if _size > _maxsize:
            raise UserConfigError(
                f"The requested image size ({_size} Mpx) is too large for the global "
                f"size limit of {_maxsize} Mpx."
            )

    def apply_thresholds(self, **kwargs: dict):
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
        self.__update_threshold("low", **kwargs)
        self.__update_threshold("high", **kwargs)
        _thresh_low = self.get_param_value("threshold_low")
        if _thresh_low is not None:
            self.__image[self.__image < _thresh_low] = _thresh_low
        _thresh_high = self.get_param_value("threshold_high")
        if _thresh_high is not None:
            self.__image[self.__image > _thresh_high] = _thresh_high

    def __update_threshold(self, key: Literal["low", "high"], **kwargs: dict):
        """
        Update the threshold from the kwargs.

        Parameters
        ----------
        key : Literal["low", "high"]
            The threshold key. Must be either "low" or "high"
        **kwargs : dict
            The kwargs passed on from the apply thresholds method.
        """
        if key not in kwargs:
            _thresh = self.get_param_value(f"threshold_{key}")
            if _thresh is not None and not np.isfinite(_thresh):
                self.set_param_value(f"threshold_{key}", None)
            return
        _thresh = kwargs.get(key)
        if _thresh is not None and not np.isfinite(_thresh):
            _thresh = None
        self.set_param_value(f"threshold_{key}", _thresh)

    def create_new_image(self):
        """
        Create a new image array with the stored Parameters.

        The new image array is accessible through the .image property.
        """
        self.__read_default_qsettings()
        self.__create_image_array()

    def insert_image(self, image: np.ndarray, index: int):
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
        _ypos, _xpos = self._get_image_pos_in_composite(index)
        image = self.__apply_thresholds_to_data(image)
        _image_op = self.get_param_value("composite_image_op")
        if _image_op is not None:
            _op = IMAGE_OPS[_image_op]
            image = _op(image)
        self.__image[_ypos, _xpos] = image

    def _get_image_pos_in_composite(self, index: int) -> tuple[slice, slice]:
        """
        Get the image position for the image in coordinates of the composite image.

        Parameters
        ----------
        index : int
            The index of the image.

        Returns
        -------
        tuple[slice, slice]
            The tuple with slice objects for the y and x position in the composite
            image.
        """
        _image_size = self.get_param_value("image_shape")
        if self.get_param_value("composite_dir") == "x":
            _iy = index // self.get_param_value("composite_nx")
            _ix = index % self.get_param_value("composite_nx")
        else:
            _iy = index % self.get_param_value("composite_ny")
            _ix = index // self.get_param_value("composite_ny")
        if self.get_param_value("composite_xdir_orientation") == "right-to-left":
            _ix = self.get_param_value("composite_nx") - _ix - 1
        if self.get_param_value("composite_ydir_orientation") == "bottom-to-top":
            _iy = self.get_param_value("composite_ny") - _iy - 1
        _start_y = _iy * (_image_size[0] + self._config["border_width"])
        _start_x = _ix * (_image_size[1] + self._config["border_width"])
        _yslice = slice(_start_y, _start_y + _image_size[0])
        _xslice = slice(_start_x, _start_x + _image_size[1])
        return _yslice, _xslice

    def __apply_thresholds_to_data(self, image: np.ndarray) -> np.ndarray:
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
        _low = self.get_param_value("threshold_low")
        _high = self.get_param_value("threshold_high")
        if _low is not None:
            image = np.where(image < _low, _low, image)
        if _high is not None:
            image = np.where(image > _high, _high, image)
        return image

    def save(self, output_fname: str):
        """
        Save the image in binary npy format.

        Parameters
        ----------
        output_fname : str
            The full filename and path to the output image file.
        """
        np.save(output_fname, self.__image)

    def export(self, output_fname: Union[Path, str], **kwargs: dict):
        """
        Export the image to a file.

        Parameters
        ----------
        output_fname : Union[Path, str]
            The full file system path and filename for the output image file.
        **kwargs : dict
            Optional keyword arguments to be passed to the exporters.
        """
        export_data(output_fname, self.__image, **kwargs)

    @property
    def image(self) -> np.ndarray:
        """
        Get the composite image.

        Returns
        -------
        np.ndarray
            The composite image.
        """
        return self.__image

    @property
    def shape(self) -> tuple[int, int]:
        """
        Get the shape of the composite image.

        Returns
        -------
        tuple[int, int]
            The shape of the composite image.
        """
        if self.__image is None:
            return (0, 0)
        return self.__image.shape

    def __copy__(self) -> Self:
        """
        Create a copy of the object.

        Returns
        -------
        fm : ObjectWithParameterCollection
            The copy with the same state.
        """
        obj = self.__class__()
        obj.params = self.params.copy()
        obj._config = copy(self._config)
        obj.__image = self.__image.copy()
        return obj
