# This file is part of pydidas.
#
# Copyright 2026, Helmholtz-Zentrum Hereon
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


"""Module with utils for the _ImageView."""

__author__ = "Malte Storm"
__copyright__ = "Copyright 2026, Helmholtz-Zentrum Hereon"
__license__ = "GPL-3.0-only"
__maintainer__ = "Malte Storm"
__status__ = "Production"
__all__ = [
    "DisplaySettings",
    "ImageData",
    "ImageViewFlags",
    "Markers",
    "RegionOfInterest",
    "point_delta",
]


from dataclasses import dataclass, field

import numpy as np
import pyqtgraph
from pyqtgraph import ROI, CircleROI
from qtpy import QtCore

from pydidas.core.constants import COLOR_HEREON_BLUE, COLOR_HEREON_RED


_MARKER_PEN = pyqtgraph.mkPen(color=COLOR_HEREON_RED, width=2)
_THIN_MARKER_PEN = pyqtgraph.mkPen(color=COLOR_HEREON_RED, width=1.5)
_ROI_PEN = pyqtgraph.mkPen(color=COLOR_HEREON_BLUE, width=2)


def point_delta(point1: QtCore.QPointF, point2: QtCore.QPointF) -> tuple[float, float]:
    """
    Calculate the delta between two points.

    Parameters
    ----------
    point1 : QtCore.QPointF
        The first point.
    point2 : QtCore.QPointF
        The second point.

    Returns
    -------
    float, float
        The x and y deltas between the two points.
    """
    return (point1.x() - point2.x()), (point1.y() - point2.y())


@dataclass
class ImageViewFlags:
    """A dataclass to hold flags for the _ImageView."""

    auto_update: bool = False
    _use_log_scale: bool = False
    _use_arcsinh_scale: bool = False
    _use_lin_scale: bool = True
    lock_marker_pos: bool = False
    context_menu_open: bool = False

    @property
    def use_log_scale(self) -> bool:
        """Get the log scale flag."""
        return self._use_log_scale

    @use_log_scale.setter
    def use_log_scale(self, value: bool):
        """Set the log scale flag."""
        self._use_log_scale = value
        if value:
            self._use_arcsinh_scale = False
            self._use_lin_scale = False
        self._verify_scale_flags()

    @property
    def use_arcsinh_scale(self) -> bool:
        """Get the arcsinh scale flag."""
        return self._use_arcsinh_scale

    @use_arcsinh_scale.setter
    def use_arcsinh_scale(self, value: bool):
        """Set the arcsinh scale flag."""
        self._use_arcsinh_scale = value
        if value:
            self._use_log_scale = False
            self._use_lin_scale = False
        self._verify_scale_flags()

    @property
    def use_lin_scale(self) -> bool:
        """Get the linear scale flag."""
        return self._use_lin_scale

    @use_lin_scale.setter
    def use_lin_scale(self, value: bool):
        """Set the linear scale flag."""
        self._use_lin_scale = value
        if value:
            self._use_log_scale = False
            self._use_arcsinh_scale = False
        self._verify_scale_flags()

    def _verify_scale_flags(self):
        """Verify that only one scale flag is set to True."""
        if not (self._use_log_scale or self._use_arcsinh_scale or self._use_lin_scale):
            self._use_lin_scale = True


@dataclass
class ImageData:
    """A dataclass to hold the image data for the _ImageView."""

    size: tuple[int, int] = (2048, 2048)
    raw: np.ndarray | None = None
    current: np.ndarray | None = None

    @property
    def xsize(self) -> int:
        """Get the width of the current image."""
        return self.size[1]

    @property
    def ysize(self) -> int:
        """Get the height of the current image."""
        return self.size[0]


@dataclass
class RegionOfInterest:
    """A dataclass to hold the region of interest slice data."""

    x: slice = field(default_factory=lambda: slice(None, None))
    y: slice = field(default_factory=lambda: slice(None, None))

    @property
    def x0(self) -> int:
        """Get the lower x boundary."""
        return 0 if self.x.start is None else self.x.start

    @property
    def y0(self) -> int:
        """Get the lower y boundary."""
        return 0 if self.y.start is None else self.y.start

    @property
    def slices(self) -> tuple[slice, slice]:
        """Get the (y, x) slices for array indexing."""
        return self.y, self.x


@dataclass
class DisplaySettings:
    """A dataclass to hold display settings for the _ImageView."""

    crop_roi: RegionOfInterest = field(default_factory=RegionOfInterest)
    zoom_roi: RegionOfInterest = field(default_factory=RegionOfInterest)
    thresholds: list[float | None] = field(default_factory=lambda: [None, None])


@dataclass
class Markers:
    """A dataclass to hold marker items for the _ImageView."""

    x_raw: float = 0.0
    y_raw: float = 0.0
    circle_r: float = 0.0
    circle: CircleROI = field(
        default_factory=lambda: CircleROI(
            (0, 0),
            size=(1, 1),
            movable=False,
            resizable=False,
            pen=_MARKER_PEN,
            hoverPen=_MARKER_PEN,
        )
    )
    line_col: ROI = field(
        default_factory=lambda: ROI(
            (0, 0),
            size=(0.0, 1.0),
            movable=False,
            resizable=False,
            pen=_THIN_MARKER_PEN,
        )
    )
    line_row: ROI = field(
        default_factory=lambda: ROI(
            (0, 0),
            size=(0.0, 1.0),
            movable=False,
            resizable=False,
            pen=_THIN_MARKER_PEN,
        )
    )
    selection: ROI = field(
        default_factory=lambda: ROI((0, 0), size=(0, 0), pen=_ROI_PEN)
    )
