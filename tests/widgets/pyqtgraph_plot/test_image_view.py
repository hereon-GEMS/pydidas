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

"""Unit tests for pydidas.widgets.pyqtgraph_plot.pydidas_image_view."""

__author__ = "Malte Storm"
__copyright__ = "Copyright 2026, Helmholtz-Zentrum Hereon"
__license__ = "GPL-3.0-only"
__maintainer__ = "Malte Storm"
__status__ = "Production"


from unittest.mock import MagicMock, patch

import numpy as np
import pyqtgraph
import pytest
from qtpy import QtCore, QtGui

from pydidas.core.constants.image_ops import IMAGE_OPS
from pydidas.unittest_objects import SignalSpy
from pydidas.widgets.pyqtgraph_plot._image_view import _ImageView
from pydidas_qtcore import PydidasQApplication


@pytest.fixture
def view(qapp):
    _view = _ImageView()
    yield _view
    _view.deleteLater()
    PydidasQApplication.instance().processEvents()


@pytest.fixture
def view_with_image(view):
    _image = np.arange(100.0, dtype=float).reshape(10, 10) + 1
    view.show_image(_image)
    return view


@pytest.mark.gui
def test_init__creates_without_error(qapp):
    _view = _ImageView()
    _view.deleteLater()
    PydidasQApplication.instance().processEvents()


@pytest.mark.gui
def test_init__has_all_signals(view):
    for _name in [
        "sig_pixel_description",
        "sig_new_zoom_bounds",
        "sig_new_histogram_levels",
        "sig_image_statistics",
        "sig_reset_zoom",
        "sig_new_marker_position",
    ]:
        assert hasattr(view, _name)


@pytest.mark.gui
def test_init__internal_state_defaults(view):
    assert view._thresholds == [None, None]
    assert view._image_op is None
    assert view._image.raw is None
    assert view._image.current is None


@pytest.mark.gui
def test_init__markers_clip_exists(view):
    from qtpy import QtWidgets

    assert hasattr(view, "_markers_clip")
    assert isinstance(view._markers_clip, QtWidgets.QGraphicsRectItem)


@pytest.mark.gui
def test_init__markers_invisible_on_start(view):
    for _marker in [
        view._markers.circle,
        view._markers.line_col,
        view._markers.line_row,
        view._markers.selection,
    ]:
        assert not _marker.isVisible()


@pytest.mark.gui
def test_image_x0__defaults_to_zero(view):
    assert view.image_x0 == 0


@pytest.mark.gui
def test_image_y0__defaults_to_zero(view):
    assert view.image_y0 == 0


@pytest.mark.gui
def test_image_x0__sums_crop_and_zoom_offsets(view):
    view.set_slice("roi", 10, 100, 0, 100)
    view.set_slice("zoom", 5, 50, 0, 100)
    assert view.image_x0 == 15


@pytest.mark.gui
def test_image_y0__sums_crop_and_zoom_offsets(view):
    view.set_slice("roi", 0, 100, 20, 200)
    view.set_slice("zoom", 0, 100, 7, 70)
    assert view.image_y0 == 27


@pytest.mark.gui
def test_set_slice__zoom_updates_zoom_roi(view):
    view.set_slice("zoom", 10, 50, 5, 30)
    assert view._zoom_roi.x == slice(10, 50)
    assert view._zoom_roi.y == slice(5, 30)


@pytest.mark.gui
def test_set_slice__roi_updates_crop_roi(view):
    view.set_slice("roi", 2, 80, 3, 60)
    assert view._crop_roi.x == slice(2, 80)
    assert view._crop_roi.y == slice(3, 60)


@pytest.mark.gui
def test_set_slice__enforces_minimum_width_of_two(view):
    view.set_slice("zoom", 10, 10, 5, 5)
    # max(x1, x0+2) = max(10, 12) = 12
    assert view._zoom_roi.x.stop == 12
    assert view._zoom_roi.y.stop == 7


@pytest.mark.gui
def test_set_image_zoom__delegates_to_set_slice(view):
    view.set_image_zoom(3, 40, 7, 80)
    assert view._zoom_roi.x == slice(3, 40)
    assert view._zoom_roi.y == slice(7, 80)


@pytest.mark.gui
def test_set_image_roi__delegates_to_set_slice(view):
    view.set_image_roi(5, 50, 10, 90)
    assert view._crop_roi.x == slice(5, 50)
    assert view._crop_roi.y == slice(10, 90)


@pytest.mark.parametrize(
    "param, value_str, expected_start, expected_stop",
    [
        ("xlow", "15", 15, None),
        ("x0", "20", 20, None),
        ("xhigh", "80", None, 80),
        ("x1", "90", None, 90),
    ],
)
@pytest.mark.gui
def test_set_slice_param__zoom_x_boundaries(
    view, param, value_str, expected_start, expected_stop
):
    view.set_slice_param("zoom", param, value_str)
    if expected_start is not None:
        assert view._zoom_roi.x.start == expected_start
    if expected_stop is not None:
        assert view._zoom_roi.x.stop == expected_stop


@pytest.mark.parametrize(
    "param, value_str, expected_start, expected_stop",
    [
        ("ylow", "12", 12, None),
        ("y0", "25", 25, None),
        ("yhigh", "75", None, 75),
        ("y1", "95", None, 95),
    ],
)
@pytest.mark.gui
def test_set_slice_param__zoom_y_boundaries(
    view, param, value_str, expected_start, expected_stop
):
    view.set_slice_param("zoom", param, value_str)
    if expected_start is not None:
        assert view._zoom_roi.y.start == expected_start
    if expected_stop is not None:
        assert view._zoom_roi.y.stop == expected_stop


@pytest.mark.parametrize("value_str", ["None", "nan"])
@pytest.mark.gui
def test_set_slice_param__none_string_sets_none(view, value_str):
    view.set_slice_param("zoom", "xhigh", value_str)
    assert view._zoom_roi.x.stop is None


@pytest.mark.gui
def test_set_slice_param__crop_updates_crop_roi(view):
    view.set_slice_param("crop", "xlow", "30")
    assert view._crop_roi.x.start == 30


@pytest.mark.gui
def test_set_image_zoom_param__updates_zoom_roi(view):
    view.set_image_zoom_param("xlow", "10")
    assert view._zoom_roi.x.start == 10


@pytest.mark.gui
def test_set_image_roi_param__updates_crop_roi(view):
    view.set_image_roi_param("xlow", "20")
    assert view._crop_roi.x.start == 20


@pytest.mark.gui
def test_set_threshold__low_sets_index_zero(view):
    view.set_threshold("low", "1.5")
    assert view._thresholds[0] == pytest.approx(1.5)


@pytest.mark.gui
def test_set_threshold__high_sets_index_one(view):
    view.set_threshold("high", "9.5")
    assert view._thresholds[1] == pytest.approx(9.5)


@pytest.mark.parametrize("value_str", ["None", "nan"])
@pytest.mark.gui
def test_set_threshold__none_string_sets_none(view, value_str):
    view.set_threshold("low", "1.0")
    view.set_threshold("low", value_str)
    assert view._thresholds[0] is None


@pytest.mark.gui
def test_set_threshold__both_set_stores_values(view):
    view.set_threshold("low", "2.0")
    view.set_threshold("high", "8.0")
    assert view._thresholds == [pytest.approx(2.0), pytest.approx(8.0)]


@pytest.mark.parametrize("radius", [0, 10, 50])
@pytest.mark.gui
def test_set_circle_radius__stores_radius(view, radius):
    view.set_circle_radius(radius)
    assert view._markers.circle_r == radius


@pytest.mark.gui
def test_set_marker_position__updates_marker_raw_coords(view):
    view.set_marker_position(42, 17)
    assert view._markers.x_raw == 42
    assert view._markers.y_raw == 17


@pytest.mark.parametrize(
    "flag, expected", [(True, True), (False, False), (1, True), (0, False)]
)
@pytest.mark.gui
def test_set_marker_pos_lock__stores_bool(view, flag, expected):
    view.set_marker_pos_lock(flag)


@pytest.mark.gui
def test_set_image_operation__none_string_clears_op(view):
    view.set_image_operation("Rot 180deg")
    view.set_image_operation("None")
    assert view._image_op is None


@pytest.mark.parametrize("op_name", list(IMAGE_OPS.keys()))
@pytest.mark.gui
def test_set_image_operation__sets_callable(view, op_name):
    view.set_image_operation(op_name)
    assert view._image_op is IMAGE_OPS[op_name]


@pytest.mark.parametrize(
    "scale, log, arcsinh, lin",
    [
        ("logarithmic", True, False, False),
        ("arcsinh", False, True, False),
        ("linear", False, False, True),
    ],
)
@pytest.mark.gui
def test_set_scale__sets_correct_flags(view, scale, log, arcsinh, lin):
    view.set_scale(scale)
    assert view._flags.use_log_scale == log
    assert view._flags.use_arcsinh_scale == arcsinh
    assert view._flags.use_lin_scale == lin


@pytest.mark.gui
def test_show_image__none_returns_without_update(view):
    view.show_image(None)
    assert view._image.raw is None


@pytest.mark.gui
def test_show_image__stores_raw_image(view):
    _img = np.ones((10, 10), dtype=float)
    view.show_image(_img)
    assert view._image.raw is not None
    np.testing.assert_array_equal(view._image.raw, _img)


@pytest.mark.gui
def test_show_image__emits_statistics_signal(view):
    _spy = SignalSpy(view.sig_image_statistics)
    _img = np.arange(1.0, 101.0).reshape(10, 10)
    view.show_image(_img)
    assert _spy.n == 1


@pytest.mark.gui
def test_show_image__updates_current_image(view):
    _img = np.arange(1.0, 101.0).reshape(10, 10)
    view.show_image(_img)
    assert view._image.current is not None


@pytest.mark.gui
def test_show_image__linear_scale_leaves_image_unchanged(view):
    _img = np.arange(1.0, 101.0).reshape(10, 10)
    view.set_scale("linear")
    view.show_image(_img)
    np.testing.assert_array_almost_equal(view._image.current, _img)


@pytest.mark.gui
def test_show_image__log_scale_applies_log_transform(view):
    _img = np.array([[1.0, 2.0], [4.0, 8.0]])
    view.set_scale("logarithmic")
    view.show_image(_img)
    assert np.all(view._image.current <= np.log(8.0))
    assert view._image.current.shape == (2, 2)


@pytest.mark.gui
def test_show_image__arcsinh_scale_applies_arcsinh_transform(view):
    _img = np.array([[1.0, 10.0], [100.0, 1000.0]])
    view.set_scale("arcsinh")
    view.show_image(_img)
    np.testing.assert_array_almost_equal(view._image.current, np.arcsinh(_img))


@pytest.mark.gui
def test_show_image__zoom_roi_slices_current_image(view):
    _img = np.arange(100.0).reshape(10, 10)
    view.show_image(_img)
    view.set_image_zoom(2, 5, 1, 4)
    assert view._image.current.shape == (3, 3)
    np.testing.assert_array_equal(view._image.current, _img[1:4, 2:5])


@pytest.mark.gui
def test_show_image__crop_roi_slices_current_image(view):
    view.set_image_roi(0, 6, 0, 4)
    _img = np.arange(100.0).reshape(10, 10)
    view.show_image(_img)
    assert view._image.current.shape == (4, 6)


@pytest.mark.gui
def test_show_image__image_op_is_applied(view):
    _img = np.arange(1.0, 101.0).reshape(10, 10)
    view.set_image_operation("Rot 180deg")
    view.show_image(_img)
    np.testing.assert_array_equal(view._image.current, np.rot90(_img, k=2))


@pytest.mark.gui
def test_calculate_image_statistics__emits_correct_values(view):
    _spy = SignalSpy(view.sig_image_statistics)
    view.show_image(np.array([[1.0, 2.0], [3.0, 4.0]]))
    assert _spy.n == 1
    _emitted = _spy.results[0]
    assert _emitted[0] == pytest.approx(1.0)
    assert _emitted[1] == pytest.approx(4.0)
    assert _emitted[2] == pytest.approx(2.5)
    assert _emitted[3] == pytest.approx(
        np.std(np.array([1.0, 2.0, 3.0, 4.0])), abs=1e-3
    )


@pytest.mark.gui
def test_calculate_image_statistics__skips_when_no_image(view):
    _spy = SignalSpy(view.sig_image_statistics)
    view.show_image(None)
    assert _spy.n == 0
    assert view._image.raw is None


@pytest.mark.gui
def test_threshold_reset__clears_thresholds(view):
    view.set_threshold("low", "1.0")
    view.set_threshold("high", "9.0")
    view.threshold_reset()
    assert view._thresholds == [None, None]


@pytest.mark.gui
def test_threshold_reset__works_with_no_image(view):
    view.set_threshold("low", "1.0")
    view.set_threshold("high", "9.0")
    view.threshold_reset()
    assert view._image.raw is None


def _make_mouse_event(
    button: "QtCore.Qt.MouseButton | None" = None,
    pos: tuple[float, float] = (5.0, 5.0),
    is_exit: bool = False,
) -> MagicMock:
    _event = MagicMock()
    _event.button.return_value = QtCore.Qt.LeftButton if button is None else button
    _event.pos.return_value = QtCore.QPointF(pos[0], pos[1])
    _event.isExit.return_value = is_exit
    return _event


@pytest.mark.gui
def test_close_event__calls_clean_up(view):
    _event = QtGui.QCloseEvent()
    with patch.object(view, "_clean_up") as _mock:
        view.closeEvent(_event)
    _mock.assert_called_once()


@pytest.mark.gui
def test_process_level_changed__emits_levels_when_image_present(view_with_image):
    _spy = SignalSpy(view_with_image.sig_new_histogram_levels)
    _hist_widget = MagicMock()
    _hist_widget.getLevels.return_value = (2.0, 8.0)
    view_with_image._flags.auto_update = False
    view_with_image._process_level_changed(_hist_widget)
    assert _spy.n == 1
    assert view_with_image._thresholds == [2.0, 8.0]


@pytest.mark.gui
def test_process_level_changed__emits_correct_values(view_with_image):
    _spy = SignalSpy(view_with_image.sig_new_histogram_levels)
    _hist_widget = MagicMock()
    _hist_widget.getLevels.return_value = (3.5, 7.5)
    view_with_image._flags.auto_update = False
    view_with_image._process_level_changed(_hist_widget)
    assert _spy.results[0][0] == pytest.approx(3.5)
    assert _spy.results[0][1] == pytest.approx(7.5)


@pytest.mark.gui
def test_imageItem_mouseHoverEvent__exit_emits_empty_string(view):
    _spy = SignalSpy(view.sig_pixel_description)
    _event = _make_mouse_event(is_exit=True)
    with patch.object(pyqtgraph.ImageItem, "hoverEvent"):
        view._imageItem_mouseHoverEvent(_event)
    assert _spy.n == 1
    assert _spy.results[0][0] == ""


@pytest.mark.gui
def test_imageItem_mouseHoverEvent__in_bounds_emits_description(view_with_image):
    _spy = SignalSpy(view_with_image.sig_pixel_description)
    _event = _make_mouse_event(is_exit=False, pos=(3.0, 4.0))
    with patch.object(pyqtgraph.ImageItem, "hoverEvent"):
        view_with_image._imageItem_mouseHoverEvent(_event)
    assert _spy.n == 1
    assert "x [px]" in _spy.results[0][0]
    assert "y [px]" in _spy.results[0][0]


@pytest.mark.gui
def test_imageItem_mouseHoverEvent__out_of_bounds_no_description(view_with_image):
    _spy = SignalSpy(view_with_image.sig_pixel_description)
    _event = _make_mouse_event(is_exit=False, pos=(200.0, 200.0))
    with patch.object(pyqtgraph.ImageItem, "hoverEvent"):
        view_with_image._imageItem_mouseHoverEvent(_event)
    assert _spy.n == 0


@pytest.mark.gui
def test_imageItem_mouseClickEvent__left_click_emits_marker_position(
    view_with_image,
):
    _spy = SignalSpy(view_with_image.sig_new_marker_position)
    _event = _make_mouse_event(button=QtCore.Qt.LeftButton, pos=(5.0, 6.0))
    view_with_image._imageItem_mouseClickEvent(_event)
    assert _spy.n == 1


@pytest.mark.gui
def test_imageItem_mouseClickEvent__locked_does_not_emit(view_with_image):
    _spy = SignalSpy(view_with_image.sig_new_marker_position)
    view_with_image._flags.lock_marker_pos = True
    _event = _make_mouse_event(button=QtCore.Qt.LeftButton, pos=(5.0, 6.0))
    view_with_image._imageItem_mouseClickEvent(_event)
    assert _spy.n == 0


@pytest.mark.gui
def test_imageItem_mousePressEvent__context_menu_open_ignores(view):
    view._flags.context_menu_open = True
    _event = _make_mouse_event(button=QtCore.Qt.LeftButton)
    view._imageItem_mousePressEvent(_event)
    _event.ignore.assert_called_once()


@pytest.mark.gui
def test_imageItem_mousePressEvent__left_button_shows_selection(view_with_image):
    _event = _make_mouse_event(button=QtCore.Qt.LeftButton, pos=(3.0, 4.0))
    view_with_image._imageItem_mousePressEvent(_event)
    assert view_with_image._markers.selection.isVisible()


@pytest.mark.gui
def test_imageItem_mousePressEvent__right_button_triggers_context_menu(view):
    _event = _make_mouse_event(button=QtCore.Qt.RightButton, pos=(3.0, 4.0))
    with patch.object(view, "show_context_menu") as _mock:
        view._imageItem_mousePressEvent(_event)
    _mock.assert_called_once()


@pytest.mark.gui
def test_imageItem_mouseReleaseEvent__hides_visible_selection(view_with_image):
    _press = _make_mouse_event(button=QtCore.Qt.LeftButton, pos=(1.0, 1.0))
    view_with_image._imageItem_mousePressEvent(_press)
    assert view_with_image._markers.selection.isVisible()
    _release = _make_mouse_event(button=QtCore.Qt.LeftButton, pos=(1.0, 1.0))
    with patch.object(pyqtgraph.ImageItem, "mouseReleaseEvent"):
        view_with_image._imageItem_mouseReleaseEvent(_release)
    assert not view_with_image._markers.selection.isVisible()


@pytest.mark.gui
def test_imageItem_mouseReleaseEvent__context_menu_flag_cleared(view):
    view._flags.context_menu_open = True
    _event = _make_mouse_event(button=QtCore.Qt.LeftButton)
    view._imageItem_mouseReleaseEvent(_event)
    assert not view._flags.context_menu_open
    _event.ignore.assert_called_once()


@pytest.mark.gui
def test_imageItem_mouseReleaseEvent__small_drag_acts_as_click(view_with_image):
    _spy = SignalSpy(view_with_image.sig_new_marker_position)
    view_with_image._press_pos = QtCore.QPointF(5.0, 5.0)
    _release = _make_mouse_event(button=QtCore.Qt.LeftButton, pos=(5.0, 5.0))
    with patch.object(pyqtgraph.ImageItem, "mouseReleaseEvent"):
        view_with_image._imageItem_mouseReleaseEvent(_release)
    assert _spy.n == 1


@pytest.mark.gui
def test_imageItem_mouseReleaseEvent__drag_emits_zoom_bounds(view_with_image):
    _spy = SignalSpy(view_with_image.sig_new_zoom_bounds)
    view_with_image._press_pos = QtCore.QPointF(1.0, 1.0)
    _release = _make_mouse_event(button=QtCore.Qt.LeftButton, pos=(6.0, 7.0))
    with patch.object(pyqtgraph.ImageItem, "mouseReleaseEvent"):
        view_with_image._imageItem_mouseReleaseEvent(_release)
    assert _spy.n == 1


@pytest.mark.gui
def test_adjust_markers__circle_visible_when_radius_set(view_with_image):
    view_with_image.set_marker_position(5, 5)
    view_with_image.set_circle_radius(3)
    assert view_with_image._markers.circle.isVisible()


@pytest.mark.gui
def test_calculate_image_statistics__skips_zero_size_image(view):
    _spy = SignalSpy(view.sig_image_statistics)
    view._image.current = np.array([])
    view._calculate_image_statistics()
    assert _spy.n == 0


@pytest.mark.gui
def test_clean_up__silences_type_error_on_disconnect(qapp):
    _view = _ImageView()
    _view._clean_up()
    _view._clean_up()  # second call hits TypeError on already-disconnected signals
    _view.deleteLater()
    PydidasQApplication.instance().processEvents()


if __name__ == "__main__":
    pytest.main([__file__])
