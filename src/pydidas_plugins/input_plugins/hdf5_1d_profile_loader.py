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
Module with the Hdf5singleFileLoader Plugin which can be used to load
images from single Hdf5 files.
"""

__author__ = "Malte Storm"
__copyright__ = "Copyright 2024 - 2025, Helmholtz-Zentrum Hereon"
__license__ = "GPL-3.0-only"
__maintainer__ = "Malte Storm"
__status__ = "Production"
__all__ = ["Hdf51dProfileLoader"]


from pydidas_plugins.input_plugins.hdf5_file_series_loader import Hdf5fileSeriesLoader

from pydidas.plugins import Input1dXRangeMixin


class Hdf51dProfileLoader(Input1dXRangeMixin, Hdf5fileSeriesLoader):
    """
    Load 1d profiles from Hdf5 data files.

    This class is designed to load image data from a series of hdf5 file. The file
    series is defined through the SCAN's base directory, filename pattern and
    start index.

    The final filename is
    <SCAN base directory>/<SCAN name pattern with index substituted for hashes>.

    The dataset in the Hdf5 file is defined by the hdf5_key Parameter.

    A region of interest and binning can be supplied to apply directly to the raw
    profile.
    """

    plugin_name = "HDF5 1d profile loader"
    base_output_data_dim = 1

    def pre_execute(self):
        """
        Prepare loading images from a file series.
        """
        super().pre_execute()
        self._standard_kwargs["forced_dimension"] = 1
