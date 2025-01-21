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
Module with the ImageMetadataManager class which is used to organize
image metadata.
"""

__author__ = "Malte Storm"
__copyright__ = "Copyright 2023 - 2025, Helmholtz-Zentrum Hereon"
__license__ = "GPL-3.0-only"
__maintainer__ = "Malte Storm"
__status__ = "Production"
__all__ = ["ImageMetadataManager"]


from pathlib import Path
from typing import Union

from pydidas.core import (
    ObjectWithParameterCollection,
    UserConfigError,
    get_generic_param_collection,
)
from pydidas.core.constants import HDF5_EXTENSIONS
from pydidas.core.utils import (
    check_hdf5_key_exists_in_file,
    get_extension,
    get_hdf5_metadata,
)
from pydidas.data_io import import_data


class ImageMetadataManager(ObjectWithParameterCollection):
    """
    Class to handle image metadata.

    The ImageMetadataManager is responsible for keeping track of the
    metadata (shape, datatype, imager per file) of image files. All the
    metadata is available for the user through class properties.

    Note
    ----
    The ImageMetadataManager uses the following generic Parameters:

    filename : Path
        The name of the first file for a file series or of the hdf5 file in
        case of hdf5 file input.
    hdf5_key : Hdf5key, optional
        Used only for hdf5 files: The dataset key.
    hdf5_slicing_axis : int, optional
        The slicing axis for hdf5 files, i.e. the axis used for iterating over
        the images. The default is 0.
    hdf5_first_image_num : int, optional
        The first image in the hdf5-dataset to be used. The default is 0.
    hdf5_last_image_num : int, optional
        The last image in the hdf5-dataset to be used. The value -1 will
        default to the last image. The default is -1.
    hdf5_stepping : int, optional
        The step width (in images) of hdf5 datasets. A value n > 1 will only
        add every n-th image to the composite. The default is 1.
    binning : int, optional
        The re-binning factor for the images in the composite. The binning
        will be applied to the cropped images. The default is 1.

    Parameters
    ----------
    *args : tuple
        Any of the Parameters in use can be given as instances.
    **kwargs : dict
        Parameters can also be supplied as kwargs, referencey by their refkey.
    """

    default_params = get_generic_param_collection(
        "hdf5_key",
        "hdf5_slicing_axis",
        "hdf5_first_image_num",
        "hdf5_last_image_num",
        "hdf5_stepping",
        "binning",
        "use_roi",
        "roi_ylow",
        "roi_yhigh",
        "roi_xlow",
        "roi_xhigh",
    )

    def __init__(self, *args: tuple, **kwargs: dict):
        ObjectWithParameterCollection.__init__(self)
        self.add_params(*args)
        self.set_default_params()
        self.update_param_values_from_kwargs(**kwargs)
        self._config = {
            "raw_img_shape_x": None,
            "raw_img_shape_y": None,
            "datatype": None,
            "numbers": None,
            "final_shape": None,
            "roi": None,
            "images_per_file": -1,
            "hdf5_dset_shape": None,
            "filename": "",
        }

    @property
    def raw_size_x(self) -> int:
        """
        Get the x-size of the raw image.

        Returns
        -------
        int
            The number of pixels in x-direction.
        """
        return self._config["raw_img_shape_x"]

    @property
    def raw_size_y(self) -> int:
        """
        Get the y-size of the raw image.

        Returns
        -------
        int
            The number of pixels in y-direction.
        """
        return self._config["raw_img_shape_y"]

    @property
    def datatype(self) -> type:
        """
        Get the datatype of the raw image.

        Returns
        -------
        type
            The datatype class.
        """
        return self._config["datatype"]

    @property
    def numbers(self) -> Union[range, int]:
        """
        Get the frame numbers pointing to the selected images.

        Returns
        -------
        Union[range, int]
            The selected frame numbers.
        """
        return self._config["numbers"]

    @property
    def final_shape(self) -> tuple[float, float]:
        """
        Get the final shape of the processed image (cropped & binned).

        Returns
        -------
        tuple[float, float]
            The final shape of the image.
        """
        return self._config["final_shape"]

    @property
    def roi(self) -> Union[None, tuple[slice, slice]]:
        """
        Get the ROI object required to achieve the final image shape.

        Returns
        -------
        Union[None, tuple[slice, slice]]
            Either None, if no ROI has been defined or a tuple with the slice
            objects for y and x dimensions.
        """
        return self._config["roi"]

    @property
    def images_per_file(self) -> int:
        """
        Get the number of images per file.

        Returns
        -------
        int
            The number of images per file.
        """
        return self._config["images_per_file"]

    @property
    def hdf5_dset_shape(self) -> tuple[int, ...]:
        """
        Get the shape of the hdf5 dataset.

        Returns
        -------
        tuple[int, ...]
            The shape (number of datapoints) of the dataset.
        """
        return self._config["hdf5_dset_shape"]

    @property
    def filename(self) -> Path:
        """
        Get the currently stored reference filename.

        Returns
        -------
        Path
            The filename.
        """
        return self._config["filename"]

    @filename.setter
    def filename(self, filename: Union[Path, str]):
        """
        Set the filename for processing.

        Parameters
        ----------
        filename : Union[str, Path]
            The full path of the selected file.

        Raises
        ------
        UserConfigError
            If the filename cannot be found in the file system.
        """
        filename = Path(filename) if isinstance(filename, str) else filename
        if not filename.is_file():
            raise UserConfigError(
                f"Cannot find the file *{str(filename)}* specified for the "
                "ImageMetadataManager."
            )
        self._config["filename"] = filename

    def update(self, filename: Union[str, Path, None] = None):
        """
        Perform a full update.

        If a new filename is specified, it will be set as first action. Otherwise,
        the metadata will be extracted from the current file.

        Parameters
        ----------
        filename : Union[str, Path, None], optional
            The filename to be updated. If None, the current filename will be used.
            The default is None.
        """
        if filename is not None:
            self.filename = filename
        self.update_input_data()
        self.update_final_image()

    def update_input_data(self):
        """
        Update the image metadata from new input.
        """
        _filename = self._config["filename"]
        if get_extension(_filename) in HDF5_EXTENSIONS:
            self._store_image_data_from_hdf5_file()
        else:
            self._store_image_data_from_single_image()

    def update_final_image(self):
        """
        Calculate the dimensions of the final image.
        """
        self._calculate_final_image_shape()

    def _store_image_data_from_hdf5_file(self):
        """
        Store config metadata from hdf5 file.
        """
        _filename = self._config["filename"]
        _key = self.get_param_value("hdf5_key")
        _slice_ax = self.get_param_value("hdf5_slicing_axis")
        check_hdf5_key_exists_in_file(_filename, _key)
        _meta = get_hdf5_metadata(_filename, ["shape", "dtype"], _key)
        self.__verify_selection_range(_meta["shape"][_slice_ax])

        _n0 = self.get_param_value("hdf5_first_image_num")
        _n1 = self._get_param_value_with_modulo(
            "hdf5_last_image_num", _meta["shape"][_slice_ax]
        )
        _step = self.get_param_value("hdf5_stepping")
        _n_per_file = (_n1 - _n0 - 1) // _step + 1
        self._config["numbers"] = range(_n0, _n1, _step)
        self._config["hdf5_dset_shape"] = _meta["shape"]
        _img_shape = list(_meta["shape"][:])
        _img_shape.pop(_slice_ax)
        self.store_image_data(_img_shape, _meta["dtype"], _n_per_file)

    def __verify_selection_range(self, dset_length: int):
        """
        Verify the selection is valid for the size of the hdf5 dataset.

        Parameters
        ----------
        dset_length : int
            The length of the dataset (i.e. the number of images in it).

        Raises
        ------
        UserConfigError
            If the range is not valid.
        """
        _n0 = self._get_param_value_with_modulo("hdf5_first_image_num", dset_length)
        _n1 = self._get_param_value_with_modulo("hdf5_last_image_num", dset_length)
        if not _n0 < _n1:
            raise UserConfigError(
                f"The image numbers for the hdf5 file, [{_n0}, {_n1}] do "
                "not describe a correct range."
            )

    def _store_image_data_from_single_image(self):
        """
        Store config metadata from file range.
        """
        _test_image = import_data(self._config["filename"])
        self._config["numbers"] = [0]
        self._config["hdf5_dset_shape"] = (0, 0, 0)
        self.store_image_data(_test_image.shape, _test_image.dtype, 1)

    def store_image_data(
        self, img_shape: tuple[int, int], img_dtype: type, n_image: int
    ):
        """
        Store the data about the image shape and datatype.

        Parameters
        ----------
        img_shape : tuple[int, int]
            The shape of the image.
        img_dtype : type
            The python datatype of the image.
        n_image : int
            The number of images per file.
        """
        self._config["images_per_file"] = n_image
        self._config["datatype"] = img_dtype
        self._config["raw_img_shape_x"] = img_shape[1]
        self._config["raw_img_shape_y"] = img_shape[0]

    def _calculate_final_image_shape(self):
        """
        Process the ROI inputs and store the ROI.
        """
        _binning = self.get_param_value("binning")
        if self.get_param_value("use_roi"):
            self.__check_roi_for_consistency()
            _x0, _x1, _y0, _y1 = self.__get_modulated_roi()
            _final_shape = ((_y1 - _y0) // _binning, (_x1 - _x0) // _binning)
            _roi = (slice(_y0, _y1), slice(_x0, _x1))
        else:
            _final_shape = (self.raw_size_y // _binning, self.raw_size_x // _binning)
            _roi = None
        self._config["roi"] = _roi
        self._config["final_shape"] = _final_shape

    def __check_roi_for_consistency(self):
        """
        Check the ROI for consistency.

        Raises
        ------
        UserConfigError
            If the ROI boundaries are not consistent.
        """
        _warning = ""
        _x0, _x1, _y0, _y1 = self.__get_modulated_roi()
        if _x1 < _x0:
            _warning += f"ROI x-range incorrect: [{_x0}, {_x1}]. "
        if _y1 < _y0:
            _warning += f"ROI y-range incorrect: [{_y0}, {_y1}]. "
        if _warning:
            raise UserConfigError(_warning)

    def __get_modulated_roi(self) -> tuple[int, int, int, int]:
        """
        Get the ROI modulated by the image size.

        Returns
        -------
        tuple
            The tuple with the (x0, x1, y0, y1) indices.
        """
        _nx = self.raw_size_x
        _ny = self.raw_size_y
        _x0 = self._get_param_value_with_modulo("roi_xlow", _nx)
        _x1 = self._get_param_value_with_modulo("roi_xhigh", _nx, none_low=False)
        _y0 = self._get_param_value_with_modulo("roi_ylow", _ny)
        _y1 = self._get_param_value_with_modulo("roi_yhigh", _ny, none_low=False)
        return _x0, _x1, _y0, _y1
