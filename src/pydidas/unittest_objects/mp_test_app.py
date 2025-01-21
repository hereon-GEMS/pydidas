# This file is part of pydidas.
#
# Copyright 2024 - 2025, Helmholtz-Zentrum Hereon
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
Module with the MpTestApp class which allows to test a dummy application in
real multiprocessing.
"""

__author__ = "Malte Storm"
__copyright__ = "Copyright 2024 - 2025, Helmholtz-Zentrum Hereon"
__license__ = "GPL-3.0-only"
__maintainer__ = "Malte Storm"
__status__ = "Production"
__all__ = ["MpTestApp"]


import time

import numpy as np
from qtpy import QtCore

from pydidas.core import BaseApp, get_generic_param_collection
from pydidas.managers import CompositeImageManager


def get_test_image(index: int, **kwargs: dict) -> np.ndarray:
    """
    Get a random test image.

    This function aims to mimic a real file loading and hence it has a
    dummy variable for an index.

    Parameters
    ----------
    index : int
        The index. Not used within the function but the pydidas architecture
        expects it.
    **kwargs : dict
        A dictionary with additional keyword arguments.

    Returns
    -------
    np.ndarray
        A two-dimension array with random numbers.

    """
    _shape = kwargs.get("shape", (20, 20))
    return np.random.random(_shape) + 1e-5


class MpTestApp(BaseApp):
    """
    A test Application for multiprocessing.
    """

    default_params = get_generic_param_collection(
        "hdf5_first_image_num", "hdf5_last_image_num"
    )

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.set_default_params()
        self._composite = None
        self._config.update(
            {
                "n_image": None,
                "datatype": None,
                "mp_post_run_called": False,
                "calls": 0,
                "min_index": 0,
                "max_index": 40,
            }
        )

    def multiprocessing_pre_run(self):
        """
        The pre-run method sets up the tasks and creates a compositite image.
        """
        self._config["mp_tasks"] = range(
            self._config["min_index"], self._config["max_index"]
        )
        self._composite = CompositeImageManager(
            image_shape=(20, 20),
            composite_nx=10,
            composite_ny=int(np.ceil((self._config["max_index"]) / 10)),
            composite_dir="x",
            datatype=np.float64,
        )
        self._config["run_prepared"] = True

    def multiprocessing_get_tasks(self) -> list[int, ...]:
        """
        Get the tasks of the Application.

        In the case of the MpTestApp, this is a list of indices to be inserted
        into the multiprocessing queue.

        Returns
        -------
        range
            The range of tasks.
        """
        return self._config["mp_tasks"]

    def multiprocessing_carryon(self) -> bool:
        """
        Check for carryon calls.

        For testing, this method will alternate to yield True and False replies
        to the query.

        Returns
        -------
        bool
            The flag whether data is available or not.
        """
        self._config["calls"] += 1
        if self._config["calls"] % 2:
            time.sleep(0.001)
            return False
        return True

    def multiprocessing_func(self, index: int) -> np.ndarray:
        """
        Perform the multiprocessing computation.

        The MpTestApp will only return a random image.

        Parameters
        ----------
        index : int
            The input index of the image.

        Returns
        -------
        image : np.ndarray
            The image data.
        """
        _fname, _kwargs = "dummy", {"shape": (20, 20)}
        _image = get_test_image(_fname, **_kwargs)
        return _image

    @QtCore.Slot(object, object)
    def multiprocessing_store_results(self, index: int, image: np.ndarray):
        """
        Store the result of the multiprocessing function call.

        The MpTestApp will insert the random image into the composite.

        Parameters
        ----------
        index : int
            The image index. This determines the position in the composite
            image.
        image : np.ndarray
            The image data.
        """
        self._composite.insert_image(image, index - self._config["min_index"])

    def multiprocessing_post_run(self):
        """
        Call post-run operations.

        The MpTestApp will only store an internal variable to document that
        this method has been called.
        """
        self._config["mp_post_run_called"] = True
