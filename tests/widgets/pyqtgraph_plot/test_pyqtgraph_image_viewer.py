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


"""Unit tests for pydidas.widgets.pyqtgraph_plot.pyqtgraph_image_viewer."""

__author__ = "Malte Storm"
__copyright__ = "Copyright 2026, Helmholtz-Zentrum Hereon"
__license__ = "GPL-3.0-only"
__maintainer__ = "Malte Storm"
__status__ = "Production"


import numpy as np
import pytest

from pydidas.widgets.pyqtgraph_plot.pyqtgraph_image_viewer import PyQtGraphImageViewer
from pydidas_qtcore import PydidasQApplication


@pytest.fixture
def viewer(qapp):
    _viewer = PyQtGraphImageViewer()
    yield _viewer
    _viewer.deleteLater()
    PydidasQApplication.instance().processEvents()


@pytest.fixture
def ctrl(viewer):
    return viewer._widgets["control_panel"]


@pytest.fixture
def imageview(viewer):
    return viewer._widgets["imageview"]


@pytest.mark.gui
def test_init__creates_without_error(qapp):
    _viewer = PyQtGraphImageViewer()
    _viewer.deleteLater()
    PydidasQApplication.instance().processEvents()


@pytest.mark.gui
def test_init__has_required_child_widgets(viewer):
    for _key in [
        "imageview",
        "control_panel",
        "button_toggle_control_panel",
        "label_image_data",
    ]:
        assert _key in viewer._widgets


@pytest.mark.gui
def test_init__config_visible_is_true(viewer):
    assert viewer._config_visible is True


@pytest.mark.gui
def test_init__control_panel_is_visible(viewer, ctrl):
    assert not ctrl.isHidden()


@pytest.mark.gui
def test_init__without_support_test_image__no_generate_button(qapp):
    _viewer = PyQtGraphImageViewer(support_test_image=False)
    assert "generate_image" not in _viewer._widgets
    _viewer.deleteLater()
    PydidasQApplication.instance().processEvents()


@pytest.mark.gui
def test_init__with_support_test_image__has_generate_button(qapp):
    _viewer = PyQtGraphImageViewer(support_test_image=True)
    assert "generate_image" in _viewer._widgets
    _viewer.deleteLater()
    PydidasQApplication.instance().processEvents()


@pytest.mark.gui
def test_wiring__sig_new_image_op__reaches_imageview(viewer, ctrl, imageview):
    ctrl.sig_new_image_op.emit("Rot 180deg")
    from pydidas.core.constants.image_ops import IMAGE_OPS

    assert imageview._image_op is IMAGE_OPS["Rot 180deg"]


@pytest.mark.gui
def test_wiring__sig_new_threshold__low_reaches_imageview(viewer, ctrl, imageview):
    ctrl.sig_new_threshold.emit("low", "3.5")
    assert imageview._thresholds[0] == pytest.approx(3.5)


@pytest.mark.gui
def test_wiring__sig_new_threshold__high_reaches_imageview(viewer, ctrl, imageview):
    ctrl.sig_new_threshold.emit("high", "7.5")
    assert imageview._thresholds[1] == pytest.approx(7.5)


@pytest.mark.gui
def test_wiring__sig_new_roi_boundary__reaches_imageview(viewer, ctrl, imageview):
    ctrl.sig_new_roi_boundary.emit("xlow", "20")
    assert imageview._crop_roi.x.start == 20


@pytest.mark.gui
def test_wiring__sig_new_zoom_boundary__reaches_imageview(viewer, ctrl, imageview):
    ctrl.sig_new_zoom_boundary.emit("xlow", "8")
    assert imageview._zoom_roi.x.start == 8


@pytest.mark.gui
def test_wiring__sig_reset_thresholds__resets_imageview_thresholds(
    viewer, ctrl, imageview
):
    ctrl.sig_new_threshold.emit("low", "1.0")
    ctrl.sig_new_threshold.emit("high", "9.0")
    ctrl.sig_reset_thresholds.emit()
    assert imageview._thresholds == [None, None]


@pytest.mark.gui
def test_wiring__sig_new_circle_radius__reaches_imageview(viewer, ctrl, imageview):
    ctrl.sig_new_circle_radius.emit(42)
    assert imageview._markers.circle_r == 42


@pytest.mark.gui
def test_wiring__sig_marker_lock_state__true_reaches_imageview(viewer, ctrl, imageview):
    ctrl.sig_marker_lock_state.emit(1)
    assert imageview._flags.lock_marker_pos is True


@pytest.mark.gui
def test_wiring__sig_marker_lock_state__false_reaches_imageview(
    viewer, ctrl, imageview
):
    ctrl.sig_marker_lock_state.emit(0)
    assert imageview._flags.lock_marker_pos is False


@pytest.mark.gui
def test_wiring__sig_marker_pos__reaches_imageview(viewer, ctrl, imageview):
    ctrl.sig_marker_pos.emit(30, 55)
    assert imageview._markers.x_raw == 30
    assert imageview._markers.y_raw == 55


@pytest.mark.parametrize(
    "scale, flag_name",
    [
        ("logarithmic", "use_log_scale"),
        ("arcsinh", "use_arcsinh_scale"),
        ("linear", "use_lin_scale"),
    ],
)
@pytest.mark.gui
def test_wiring__sig_use_scale__sets_correct_flag(
    viewer, ctrl, imageview, scale, flag_name
):
    ctrl.sig_use_scale.emit(scale)
    assert getattr(imageview._flags, flag_name) is True


@pytest.mark.gui
def test_wiring__sig_pixel_description__updates_label(viewer, imageview):
    imageview.sig_pixel_description.emit("x=10 y=20 v=5.00")
    assert viewer._widgets["label_image_data"].text() == "x=10 y=20 v=5.00"


@pytest.mark.gui
def test_wiring__sig_new_zoom_bounds__updates_ctrl_panel_params(
    viewer, ctrl, imageview
):
    imageview.sig_new_zoom_bounds.emit([5, 50, 10, 80])
    assert ctrl.get_param_value("zoom_xlow") == 5
    assert ctrl.get_param_value("zoom_xhigh") == 50
    assert ctrl.get_param_value("zoom_ylow") == 10
    assert ctrl.get_param_value("zoom_yhigh") == 80


@pytest.mark.gui
def test_wiring__sig_new_histogram_levels__updates_ctrl_panel_thresholds(
    viewer, ctrl, imageview
):
    imageview.sig_new_histogram_levels.emit(1.5, 8.5)
    assert ctrl.get_param_value("colormap_val_low") == pytest.approx(1.5)
    assert ctrl.get_param_value("colormap_val_high") == pytest.approx(8.5)


@pytest.mark.gui
def test_wiring__sig_image_statistics__updates_ctrl_panel_stats(
    viewer, ctrl, imageview
):
    imageview.sig_image_statistics.emit(1.0, 9.0, 5.0, 2.0)
    assert ctrl.get_param_value("image_stats_min") == pytest.approx(1.0)
    assert ctrl.get_param_value("image_stats_max") == pytest.approx(9.0)
    assert ctrl.get_param_value("image_stats_mean") == pytest.approx(5.0)
    assert ctrl.get_param_value("image_stats_std") == pytest.approx(2.0)


@pytest.mark.gui
def test_wiring__sig_reset_zoom__resets_ctrl_panel_zoom_params(viewer, ctrl, imageview):
    imageview.sig_new_zoom_bounds.emit([5, 50, 10, 80])
    imageview.sig_reset_zoom.emit()
    assert ctrl.get_param_value("zoom_xlow") == 0
    assert ctrl.get_param_value("zoom_xhigh") is None
    assert ctrl.get_param_value("zoom_ylow") == 0
    assert ctrl.get_param_value("zoom_yhigh") is None


@pytest.mark.gui
def test_wiring__sig_new_marker_position__updates_ctrl_panel_params(
    viewer, ctrl, imageview
):
    imageview.sig_new_marker_position.emit(15, 25)
    assert ctrl.get_param_value("marker_x") == 15
    assert ctrl.get_param_value("marker_y") == 25


@pytest.mark.gui
def test_set_image__stores_image_in_imageview(viewer, imageview):
    _img = np.ones((20, 20), dtype=float)
    viewer.set_image(_img)
    assert imageview._image.current is not None


@pytest.mark.gui
def test_set_image__raw_equals_input(viewer, imageview):
    _img = np.arange(1.0, 401.0).reshape(20, 20)
    viewer.set_image(_img)
    np.testing.assert_array_equal(imageview._image.raw, _img)


@pytest.mark.gui
def test_show_image__is_alias_for_set_image(viewer):
    assert type(viewer).show_image is type(viewer).set_image


@pytest.mark.gui
def test_generate_image__produces_non_none_image(qapp):
    _viewer = PyQtGraphImageViewer(support_test_image=True)
    _viewer.generate_image()
    assert _viewer._widgets["imageview"]._image.current is not None
    _viewer.deleteLater()
    PydidasQApplication.instance().processEvents()


@pytest.mark.gui
def test_generate_image__produces_500x500_image(qapp):
    _viewer = PyQtGraphImageViewer(support_test_image=True)
    _viewer.generate_image()
    assert _viewer._widgets["imageview"]._image.raw.shape == (500, 500)
    _viewer.deleteLater()
    PydidasQApplication.instance().processEvents()


@pytest.mark.gui
def test_toggle_control_panel__first_call_hides_panel(viewer, ctrl):
    viewer.toggle_control_panel()
    assert not ctrl.isVisible()


@pytest.mark.gui
def test_toggle_control_panel__first_call_sets_config_false(viewer):
    viewer.toggle_control_panel()
    assert viewer._config_visible is False


@pytest.mark.gui
def test_toggle_control_panel__first_call_changes_button_text(viewer):
    viewer.toggle_control_panel()
    assert viewer._widgets["button_toggle_control_panel"].text() == "Show control panel"


@pytest.mark.gui
def test_toggle_control_panel__second_call_shows_panel(viewer, ctrl):
    viewer.toggle_control_panel()
    viewer.toggle_control_panel()
    assert not ctrl.isHidden()


@pytest.mark.gui
def test_toggle_control_panel__second_call_restores_config_true(viewer):
    viewer.toggle_control_panel()
    viewer.toggle_control_panel()
    assert viewer._config_visible is True


@pytest.mark.gui
def test_toggle_control_panel__second_call_restores_button_text(viewer):
    viewer.toggle_control_panel()
    viewer.toggle_control_panel()
    assert viewer._widgets["button_toggle_control_panel"].text() == "Hide control panel"


if __name__ == "__main__":
    pytest.main([__file__])
