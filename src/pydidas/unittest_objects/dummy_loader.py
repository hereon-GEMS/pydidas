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
The dummy_loader module includes the DummyLoader class which can be used to
test workflows and Plugins without any file system operations.
"""

__author__ = "Malte Storm"
__copyright__ = "Copyright 2023 - 2025, Helmholtz-Zentrum Hereon"
__license__ = "GPL-3.0-only"
__maintainer__ = "Malte Storm"
__status__ = "Production"
__all__ = ["DummyLoader"]


import numpy as np

from pydidas.core import Dataset, Parameter, ParameterCollection, get_generic_parameter
from pydidas.plugins import InputPlugin


class DummyLoader(InputPlugin):
    """
    A dummy Plugin to test Input in WorkflowTrees without actual file system
    operations.
    """

    plugin_name = "Dummy loader Plugin"

    default_params = ParameterCollection(
        Parameter(
            "image_height",
            int,
            10,
            name="The image height",
            tooltip="The height of the image.",
        ),
        Parameter(
            "image_width",
            int,
            10,
            name="The image width",
            tooltip="The width of the image.",
        ),
        get_generic_parameter("filename"),
    )

    def __init__(self, *args: tuple, **kwargs: dict):
        InputPlugin.__init__(self, *args, **kwargs)
        self._pre_executed = False
        self._config["input_available"] = 12

    def __reduce__(self):
        """
        Reduce the DummyLoader for Pickling.

        Returns
        -------
        dummy_getter : callable
            The callable function to create a new instance.
        tuple
            The arguments for plugin_getter. This is only the class name.
        dict
            The state to set the state of the new object.
        """
        from pydidas.unittest_objects.dummy_getter_ import dummy_getter

        return dummy_getter, (self.__class__.__name__,), self.__getstate__()

    def prepare_carryon_check(self):
        """
        Prepare the checks of the multiprocessing carryon.

        By default, this gets and stores the file target size for live
        processing.
        """
        self._config["file_size"] = self.get_first_file_size()
        self._config["carryon_checked"] = True

    def get_first_file_size(self) -> int:
        """
        Reimplement the "get_first_file_size" and return a dummy value.

        Returns
        -------
        int
            The dummy file size.
        """
        return 1

    def get_filename(self, index: int) -> int:
        """
        Get the filename associated with the input index.

        The DummyLoader simply uses the input index and returns it directly.

        Parameters
        ----------
        index : int
            The input index.

        Returns
        -------
        index : int
            The input index.
        """
        return index

    def input_available(self, index: int) -> bool:
        """
        Check if input is available for the given index.

        A config setting can be used to determine the cut-off point up to which
        input is available and the method returns True.

        Parameters
        ----------
        index : Union[int, None]
            The input index to be checked.

        Returns
        -------
        bool
            The input available flag.
        """
        if index is None:
            return False
        return index <= self._config["input_available"]

    def pre_execute(self):
        """
        Run the pre-execution routine and store a variable that this method
        has been called.
        """
        self._pre_executed = True

    def execute(self, index: int, **kwargs: dict) -> tuple[Dataset, dict]:
        """
        Execute the actual computations.

        This method will create a new Dataset with random data.

        Parameters
        ----------
        index : int
            The input index. This is not used except to store the index in the
            kwargs dictionary.
        **kwargs : dict
            The kwargs dictionary with the input keyword arguments.

        Returns
        -------
        pydidas.core.Dataset
            The random image data.
        kwargs : dict
            The updated input kwargs dictionary.
        """
        _width = self.get_param_value("image_width")
        _height = self.get_param_value("image_height")
        _data = np.random.random((_height, _width))
        _data[_data == 0] = 0.0001
        kwargs.update(dict(index=index))
        return Dataset(
            _data,
            axis_labels=["ax0", "ax 1"],
            axis_units=["u 0", "unit #1"],
            axis_ranges=[0.5 * np.arange(_height) - 2, 1.4 * np.arange(_width)],
            data_label="Dummy data",
            data_unit="data U",
        ), kwargs
