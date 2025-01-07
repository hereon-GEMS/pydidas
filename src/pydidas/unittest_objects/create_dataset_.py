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
The create_dataset module includes functions to create dataset objects with metadata
dynamically for unit-testing.

"""

__author__ = "Malte Storm"
__copyright__ = "Copyright  2024, Helmholtz-Zentrum Hereon"
__license__ = "GPL-3.0-only"
__maintainer__ = "Malte Storm"
__status__ = "Production"
__all__ = ["create_dataset"]


from typing import Optional, Union

import numpy as np

from pydidas.core import Dataset
from pydidas.core.utils import get_random_string


def create_dataset(
    ndim: int,
    dtype: Union[int, float] = int,
    shape: Optional[tuple[int]] = None,
    random_seed: Optional[int] = None,
) -> Dataset:
    """
    Create a Dataset object with random data and metadata.

    This single-use class is required to allow management of class attributes.

    Parameters
    ----------
    ndim : int
        The number of dimensions of the dataset.
    dtype : Union[int, float], optional
        The data type of the dataset. The default is int.
    shape : Optional[tuple[int]], optional
        The shape of the dataset. The default will create between 8 and 12 entries
        per dimension. The default is None.
    random_seed : Optional[int], optional
        The random seed for reproducibility. The default is None.

    Returns
    -------
    Dataset :
        A Dataset object with random data and metadata.
    """
    if dtype not in [int, float]:
        raise ValueError("Only int and float are supported data types.")
    if shape is None:
        shape = tuple([8 + (_i % 4) for _i in range(ndim)])
    if len(shape) != ndim:
        raise ValueError("The shape must have the same number of entries as ndim.")
    _generator = np.random.default_rng(random_seed)
    _data = (
        _generator.integers(0, 100, size=shape)
        if dtype is int
        else _generator.random(size=shape)
    )
    _ranges = [
        _generator.integers(1, 5, None) + (_generator.random() + 0.5) * np.arange(_s)
        for _s in shape
    ]
    return Dataset(
        _data,
        axis_ranges=_ranges,
        axis_labels=[get_random_string(8) for _ in range(ndim)],
        axis_units=[get_random_string(3) for _ in range(ndim)],
        data_label=get_random_string(8),
        data_unit=get_random_string(3),
    )
