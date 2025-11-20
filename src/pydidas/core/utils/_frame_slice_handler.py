# This file is part of pydidas.
#
# Copyright 2025, Helmholtz-Zentrum Hereon
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
Module with the FrameSliceHandler class which allows to manage slicing data in 1 axis.
"""

__author__ = "Malte Storm"
__copyright__ = "Copyright 2025, Helmholtz-Zentrum Hereon"
__license__ = "GPL-3.0-only"
__maintainer__ = "Malte Storm"
__status__ = "Production"
__all__ = ["FrameSliceHandler"]

import warnings
from numbers import Integral

from pydidas.core import UserConfigError


class FrameSliceHandler:
    """
    Store frame selection information and handle the logic for slicing.

    This class supports only one axis being sliced at a time.
    """

    def __init__(
        self,
        axis: Integral | None = None,
        frame: Integral = 0,
        shape: tuple[Integral, ...] = (),
    ):
        # Set _frame and _axis first to have references in setters
        self._frame = 0
        self._axis = None
        self.shape = shape  # Use setter to validate shape first
        self.axis = axis
        self.frame = frame

    @property
    def axis(self) -> Integral | None:
        return self._axis

    @axis.setter
    def axis(self, value: Integral | None):
        if value is not None and (value < 0 or value >= self.ndim):
            raise UserConfigError(
                f"Axis {value} is out of bounds for data with {self.ndim} dimensions."
            )
        self._axis = value
        self._check_frame_index_in__bounds()

    @property
    def frame(self) -> int:
        return int(self._frame)

    @frame.setter
    def frame(self, value: Integral):
        if not isinstance(value, Integral):
            raise UserConfigError("Frame index must be an integer.")
        if self.axis is not None and (value < 0 or value >= self.shape[self.axis]):
            raise UserConfigError(
                f"Frame {value} is out of bounds for axis {self.axis} with size "
                f"{self.shape[self.axis]}."
            )
        self._frame = value

    @property
    def shape(self) -> tuple[Integral, ...]:
        return self._shape

    @shape.setter
    def shape(self, new_shape: tuple[Integral, ...]):
        if not isinstance(new_shape, tuple):
            raise UserConfigError("Shape must be a tuple of positive integers.")
        if not all(isinstance(dim, Integral) and dim > 0 for dim in new_shape):
            raise UserConfigError("All dimensions in shape must be positive integers.")
        self._shape = new_shape
        # Reset axis if it is out of bounds for the new shape
        if self.axis is not None and len(new_shape) <= self.axis:
            self._axis = 0
        self._check_frame_index_in__bounds()

    @property
    def ndim(self) -> int:
        return len(self._shape)

    @property
    def slice(self) -> tuple[slice | int, ...]:
        if self.axis is None:
            return slice(None)
        else:
            return tuple(
                self.frame if ax == self.axis else slice(None)
                for ax in range(self.axis + 1)
            )

    @property
    def indices(self) -> tuple[None | tuple[None | Integral], ...]:
        return None if self.axis is None else ((None,) * self.axis + (self.frame,))

    def _check_frame_index_in__bounds(self):
        if self._axis is not None and self._frame >= self.shape[self._axis]:
            self._frame = 0
            warnings.warn(
                "Frame index reset to 0 due to axis change and the current "
                "frame index being out of bounds for the new axis.",
                UserWarning,
            )
