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
Module with the Sum2dData Plugin which can be used to sum over 2D data.
"""

__author__ = "Malte Storm"
__copyright__ = "Copyright 2024 - 2025, Helmholtz-Zentrum Hereon"
__license__ = "GPL-3.0-only"
__maintainer__ = "Malte Storm"
__status__ = "Production"
__all__ = ["AverageDataDimension"]


from pydidas.core import Dataset, get_generic_param_collection
from pydidas.plugins import ProcPlugin


class AverageDataDimension(ProcPlugin):
    """
    Sum up datapoints in a 2D dataset.

    This plugin creates a single datapoint from the 2D input data. It is not
    designed to handle higher-dimensional input data and accepts only 2D inputs.
    """

    plugin_name = "Average over data dimension"

    default_params = get_generic_param_collection("process_data_dim")

    def execute(self, data: Dataset, **kwargs: dict) -> tuple[Dataset, dict]:
        """
        Average over the given data dimension.

        Parameters
        ----------
        data : pydidas.core.Dataset
            The input Dataset
        **kwargs : dict
            Any calling keyword arguments.

        Returns
        -------
        pydidas.core.Dataset
            The data sum in form of an array of shape (1,).
        kwargs : dict
            Any calling kwargs, appended by any changes in the function.
        """
        return data.mean(axis=self.get_param_value("process_data_dim")), kwargs
