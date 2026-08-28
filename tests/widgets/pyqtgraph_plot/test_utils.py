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
#
# This file was created using an AI tool and was modified by
# the pydidas team.

"""Unit tests for pydidas.widgets.pyqtgraph_plot.utils."""

__author__ = "Malte Storm"
__copyright__ = "Copyright 2026, Helmholtz-Zentrum Hereon"
__license__ = "GPL-3.0-only"
__maintainer__ = "Malte Storm"
__status__ = "Production"


import numpy as np
import pytest
from pyqtgraph import ROI, CircleROI
from qtpy import QtCore

from pydidas.widgets.pyqtgraph_plot._pyqtgraph_utils import (
    DisplaySettings,
    ImageData,
    ImageViewFlags,
    Markers,
    RegionOfInterest,
    point_delta,
)


@pytest.mark.parametrize(
    "p1, p2, expected",
    [
        ((0.0, 0.0), (0.0, 0.0), (0.0, 0.0)),
        ((5.0, 3.0), (2.0, 1.0), (3.0, 2.0)),
        ((1.0, 1.0), (4.0, 6.0), (-3.0, -5.0)),
        ((0.0, 7.5), (3.5, 2.5), (-3.5, 5.0)),
    ],
)
def test_point_delta(p1, p2, expected):
    _pt1 = QtCore.QPointF(*p1)
    _pt2 = QtCore.QPointF(*p2)
    _dx, _dy = point_delta(_pt1, _pt2)
    assert _dx == pytest.approx(expected[0])
    assert _dy == pytest.approx(expected[1])


def test_point_delta__returns_tuple():
    _result = point_delta(QtCore.QPointF(1.0, 2.0), QtCore.QPointF(0.0, 0.0))
    assert isinstance(_result, tuple)
    assert len(_result) == 2


def test_image_view_flags__default_values():
    _flags = ImageViewFlags()
    assert _flags.auto_update is False
    assert _flags.use_log_scale is False
    assert _flags.use_arcsinh_scale is False
    assert _flags.use_lin_scale is True
    assert _flags.lock_marker_pos is False
    assert _flags.context_menu_open is False


def test_image_view_flags__set_log_scale_true():
    _flags = ImageViewFlags()
    _flags.use_log_scale = True
    assert _flags.use_log_scale is True
    assert _flags.use_arcsinh_scale is False
    assert _flags.use_lin_scale is False


def test_image_view_flags__set_arcsinh_scale_true():
    _flags = ImageViewFlags()
    _flags.use_arcsinh_scale = True
    assert _flags.use_arcsinh_scale is True
    assert _flags.use_log_scale is False
    assert _flags.use_lin_scale is False


def test_image_view_flags__set_lin_scale_true():
    _flags = ImageViewFlags()
    _flags.use_log_scale = True
    _flags.use_lin_scale = True
    assert _flags.use_lin_scale is True
    assert _flags.use_log_scale is False
    assert _flags.use_arcsinh_scale is False


@pytest.mark.parametrize(
    "first_scale, second_scale",
    [
        ("use_log_scale", "use_arcsinh_scale"),
        ("use_log_scale", "use_lin_scale"),
        ("use_arcsinh_scale", "use_log_scale"),
        ("use_arcsinh_scale", "use_lin_scale"),
        ("use_lin_scale", "use_log_scale"),
        ("use_lin_scale", "use_arcsinh_scale"),
    ],
)
def test_image_view_flags__scale_flags_are_mutually_exclusive(
    first_scale, second_scale
):
    _flags = ImageViewFlags()
    setattr(_flags, first_scale, True)
    setattr(_flags, second_scale, True)
    assert getattr(_flags, second_scale) is True
    assert getattr(_flags, first_scale) is False


def test_image_view_flags__verify_scale_flags_restores_lin_scale():
    _flags = ImageViewFlags()
    # Force all private flags off to trigger the fallback
    _flags._use_log_scale = False
    _flags._use_arcsinh_scale = False
    _flags._use_lin_scale = False
    _flags._verify_scale_flags()
    assert _flags.use_lin_scale is True


def test_image_data__default_values():
    _data = ImageData()
    assert _data.size == (2048, 2048)
    assert _data.raw is None
    assert _data.current is None


@pytest.mark.parametrize("height, width", [(100, 200), (512, 1024), (1, 1)])
def test_image_data__xsize_and_ysize(height, width):
    _data = ImageData(size=(height, width))
    assert _data.xsize == width
    assert _data.ysize == height


def test_image_data__default_xsize_ysize():
    _data = ImageData()
    assert _data.xsize == 2048
    assert _data.ysize == 2048


def test_image_data__raw_and_current_assignable():
    _data = ImageData()
    _arr = np.zeros((10, 10))
    _data.raw = _arr
    _data.current = _arr
    assert _data.raw is _arr
    assert _data.current is _arr


def test_roi__default_values():
    _roi = RegionOfInterest()
    assert _roi.x == slice(None, None)
    assert _roi.y == slice(None, None)


def test_roi__x0_with_none_start():
    _roi = RegionOfInterest()
    assert _roi.x0 == 0


def test_roi__y0_with_none_start():
    _roi = RegionOfInterest()
    assert _roi.y0 == 0


@pytest.mark.parametrize("x_start", [0, 5, 100, 1024])
def test_roi__x0_with_explicit_start(x_start):
    _roi = RegionOfInterest(x=slice(x_start, None))
    assert _roi.x0 == x_start


@pytest.mark.parametrize("y_start", [0, 5, 100, 1024])
def test_roi__y0_with_explicit_start(y_start):
    _roi = RegionOfInterest(y=slice(y_start, None))
    assert _roi.y0 == y_start


def test_roi__slices_returns_y_x_order():
    _y_slice = slice(10, 50)
    _x_slice = slice(20, 80)
    _roi = RegionOfInterest(x=_x_slice, y=_y_slice)
    _slices = _roi.slices
    assert _slices == (_y_slice, _x_slice)


def test_roi__slices_usable_for_array_indexing():
    _roi = RegionOfInterest(x=slice(1, 4), y=slice(0, 2))
    _arr = np.arange(25).reshape(5, 5)
    _result = _arr[_roi.slices]
    np.testing.assert_array_equal(_result, _arr[0:2, 1:4])


def test_roi__independent_instances():
    _roi1 = RegionOfInterest()
    _roi2 = RegionOfInterest()
    _roi1.x = slice(10, 20)
    assert _roi2.x == slice(None, None)


def test_display_settings__default_values():
    _ds = DisplaySettings()
    assert isinstance(_ds.crop_roi, RegionOfInterest)
    assert isinstance(_ds.zoom_roi, RegionOfInterest)
    assert _ds.thresholds == [None, None]


def test_display_settings__independent_roi_instances():
    _ds1 = DisplaySettings()
    _ds2 = DisplaySettings()
    _ds1.crop_roi.x = slice(10, 50)
    assert _ds2.crop_roi.x == slice(None, None)


def test_display_settings__independent_threshold_lists():
    _ds1 = DisplaySettings()
    _ds2 = DisplaySettings()
    _ds1.thresholds[0] = 1.0
    assert _ds2.thresholds[0] is None


# ---------------------------------------------------------------------------
# Markers  (requires QApplication for pyqtgraph ROI objects)
# ---------------------------------------------------------------------------


def test_markers__default_float_fields(qapp):
    _markers = Markers()
    assert _markers.x_raw == pytest.approx(0.0)
    assert _markers.y_raw == pytest.approx(0.0)
    assert _markers.circle_r == pytest.approx(0.0)


def test_markers__circle_is_circle_roi(qapp):
    _markers = Markers()
    assert isinstance(_markers.circle, CircleROI)


def test_markers__line_col_is_roi(qapp):
    _markers = Markers()
    assert isinstance(_markers.line_col, ROI)


def test_markers__line_row_is_roi(qapp):
    _markers = Markers()
    assert isinstance(_markers.line_row, ROI)


def test_markers__selection_is_roi(qapp):
    _markers = Markers()
    assert isinstance(_markers.selection, ROI)


def test_markers__independent_roi_instances(qapp):
    _m1 = Markers()
    _m2 = Markers()
    assert _m1.circle is not _m2.circle
    assert _m1.line_col is not _m2.line_col
    assert _m1.line_row is not _m2.line_row
    assert _m1.selection is not _m2.selection


if __name__ == "__main__":
    pytest.main([__file__])
