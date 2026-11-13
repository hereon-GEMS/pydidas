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


"""Unit tests for pydidas.widgets.pyqtgraph_plot.vertical_image_control_panel."""

__author__ = "Malte Storm"
__copyright__ = "Copyright 2026, Helmholtz-Zentrum Hereon"
__license__ = "GPL-3.0-only"
__maintainer__ = "Malte Storm"
__status__ = "Production"


import pytest

from pydidas.unittest_objects import SignalSpy
from pydidas.widgets.pyqtgraph_plot._control_panel import (
    _ControlPanel,
)
from pydidas_qtcore import PydidasQApplication


@pytest.fixture
def panel(qapp):
    _panel = _ControlPanel()
    yield _panel
    _panel.deleteLater()
    PydidasQApplication.instance().processEvents()


def test_init__has_all_signals(panel):
    for _name in [
        "sig_new_roi_boundary",
        "sig_new_zoom_boundary",
        "sig_new_threshold",
        "sig_reset_thresholds",
        "sig_new_image_op",
        "sig_new_circle_radius",
        "sig_marker_lock_state",
        "sig_marker_pos",
        "sig_use_scale",
    ]:
        assert hasattr(panel, _name)


def test_init__has_all_params(panel):
    for _key in [
        "roi_xlow",
        "roi_xhigh",
        "roi_ylow",
        "roi_yhigh",
        "zoom_xlow",
        "zoom_xhigh",
        "zoom_ylow",
        "zoom_yhigh",
        "colormap_val_low",
        "colormap_val_high",
        "composite_image_op",
        "image_stats_min",
        "image_stats_max",
        "image_stats_mean",
        "image_stats_std",
        "marker_lock",
        "marker_x",
        "marker_y",
        "use_scale",
    ]:
        assert _key in panel.params


@pytest.mark.parametrize(
    "key, value, signal_name, expected_key",
    [
        ("roi_xlow", "42", "sig_new_roi_boundary", "xlow"),
        ("roi_xhigh", "100", "sig_new_roi_boundary", "xhigh"),
        ("roi_ylow", "10", "sig_new_roi_boundary", "ylow"),
        ("roi_yhigh", "200", "sig_new_roi_boundary", "yhigh"),
        ("zoom_xlow", "5", "sig_new_zoom_boundary", "xlow"),
        ("zoom_xhigh", "50", "sig_new_zoom_boundary", "xhigh"),
        ("zoom_ylow", "3", "sig_new_zoom_boundary", "ylow"),
        ("zoom_yhigh", "80", "sig_new_zoom_boundary", "yhigh"),
    ],
)
def test_process_update__emits_correct_signal(
    panel, key, value, signal_name, expected_key
):
    _spy = SignalSpy(getattr(panel, signal_name))
    panel._process_update(key, value)
    assert _spy.n == 1
    assert _spy.results[0][0] == expected_key
    assert _spy.results[0][1] == value


@pytest.mark.parametrize("key", ["roi_xlow", "roi_yhigh"])
def test_process_update__roi_key_does_not_emit_zoom_signal(panel, key):
    _spy = SignalSpy(panel.sig_new_zoom_boundary)
    panel._process_update(key, "10")
    assert _spy.n == 0


@pytest.mark.parametrize("key", ["zoom_xlow", "zoom_yhigh"])
def test_process_update__zoom_key_does_not_emit_roi_signal(panel, key):
    _spy = SignalSpy(panel.sig_new_roi_boundary)
    panel._process_update(key, "10")
    assert _spy.n == 0


def test_reset_thresholds__emits_signal(panel):
    _spy = SignalSpy(panel.sig_reset_thresholds)
    panel._reset_thresholds()
    assert _spy.n == 1


def test_reset_thresholds__resets_params(panel):
    panel.set_param_and_widget_value("colormap_val_low", 1.0)
    panel.set_param_and_widget_value("colormap_val_high", 2.0)
    panel._reset_thresholds()
    assert panel.get_param_value("colormap_val_low") is None
    assert panel.get_param_value("colormap_val_high") is None


@pytest.mark.parametrize(
    "key, expected_stripped",
    [
        ("colormap_val_low", "low"),
        ("colormap_val_high", "high"),
    ],
)
def test_process_cmap_threshold_update__emits_stripped_key(
    panel, key, expected_stripped
):
    _spy = SignalSpy(panel.sig_new_threshold)
    panel._process_cmap_threshold_update(key, "3.14")
    assert _spy.n == 1
    assert _spy.results[0][0] == expected_stripped
    assert _spy.results[0][1] == "3.14"


@pytest.mark.parametrize(
    "radius, value_str", [(0, "0:100"), (25, "25:500"), (100, "100:0")]
)
def test_define_new_circle_radius__emits_correct_radius(panel, radius, value_str):
    _spy = SignalSpy(panel.sig_new_circle_radius)
    panel._define_new_circle_radius(0, value_str)
    assert _spy.n == 1
    assert _spy.results[0][0] == radius


def test_reset_roi__emits_signal_four_times(panel):
    _spy = SignalSpy(panel.sig_new_roi_boundary)
    panel._reset_roi()
    assert _spy.n == 4


def test_reset_roi__emits_correct_values(panel):
    _spy = SignalSpy(panel.sig_new_roi_boundary)
    panel._reset_roi()
    _emissions = {r[0]: r[1] for r in _spy.results}
    assert _emissions["xlow"] == "0"
    assert _emissions["ylow"] == "0"
    assert _emissions["xhigh"] == "None"
    assert _emissions["yhigh"] == "None"


def test_reset_roi__resets_params(panel):
    panel.set_param_and_widget_value("roi_xlow", 10)
    panel.set_param_and_widget_value("roi_xhigh", 100)
    panel._reset_roi()
    assert panel.get_param_value("roi_xlow") == 0
    assert panel.get_param_value("roi_xhigh") is None
    assert panel.get_param_value("roi_ylow") == 0
    assert panel.get_param_value("roi_yhigh") is None


def test_reset_zoom__emits_signal_four_times(panel):
    _spy = SignalSpy(panel.sig_new_zoom_boundary)
    panel._reset_zoom()
    assert _spy.n == 4


def test_reset_zoom__emits_correct_values(panel):
    _spy = SignalSpy(panel.sig_new_zoom_boundary)
    panel._reset_zoom()
    _emissions = {r[0]: r[1] for r in _spy.results}
    assert _emissions["xlow"] == "0"
    assert _emissions["ylow"] == "0"
    assert _emissions["xhigh"] == "None"
    assert _emissions["yhigh"] == "None"


def test_reset_zoom__does_not_emit_roi_signal(panel):
    _spy = SignalSpy(panel.sig_new_roi_boundary)
    panel._reset_zoom()
    assert _spy.n == 0


def test_reset_roi__does_not_emit_zoom_signal(panel):
    _spy = SignalSpy(panel.sig_new_zoom_boundary)
    panel._reset_roi()
    assert _spy.n == 0


@pytest.mark.parametrize("value_str, expected_lock", [("True", True), ("False", False)])
def test_process_marker_lock__emits_signal(panel, value_str, expected_lock):
    _spy = SignalSpy(panel.sig_marker_lock_state)
    panel._process_marker_lock(value_str)
    assert _spy.n == 1
    assert bool(_spy.results[0][0]) == expected_lock


def test_process_marker_pos__emits_current_param_values(panel):
    panel.set_param_and_widget_value("marker_x", 15)
    panel.set_param_and_widget_value("marker_y", 30)
    _spy = SignalSpy(panel.sig_marker_pos)
    panel._process_marker_pos("ignored")
    assert _spy.n == 1
    assert _spy.results[0][0] == 15
    assert _spy.results[0][1] == 30


@pytest.mark.parametrize("scale_value", ["log", "linear", "arcsinh"])
def test_process_scale__emits_signal(panel, scale_value):
    _spy = SignalSpy(panel.sig_use_scale)
    panel._process_scale(scale_value)
    assert _spy.n == 1
    assert _spy.results[0][0] == scale_value


def test_external_marker_pos_update__updates_params(panel):
    panel.external_marker_pos_update(7, 13)
    assert panel.get_param_value("marker_x") == 7
    assert panel.get_param_value("marker_y") == 13


def test_external_marker_pos_update__no_signal_emitted(panel):
    _spy = SignalSpy(panel.sig_marker_pos)
    panel.external_marker_pos_update(7, 13)
    assert _spy.n == 0


def test_external_roi_update__updates_all_params(panel):
    panel.external_roi_update([10, 200, 20, 300])
    assert panel.get_param_value("roi_xlow") == 10
    assert panel.get_param_value("roi_xhigh") == 200
    assert panel.get_param_value("roi_ylow") == 20
    assert panel.get_param_value("roi_yhigh") == 300


def test_external_roi_update__accepts_none_values(panel):
    panel.external_roi_update([0, None, 0, None])
    assert panel.get_param_value("roi_xlow") == 0
    assert panel.get_param_value("roi_xhigh") is None


def test_external_roi_update__no_signal_emitted(panel):
    _spy = SignalSpy(panel.sig_new_roi_boundary)
    panel.external_roi_update([10, 200, 20, 300])
    assert _spy.n == 0


def test_external_zoom_update__updates_all_params(panel):
    panel.external_zoom_update([5, 100, 15, 150])
    assert panel.get_param_value("zoom_xlow") == 5
    assert panel.get_param_value("zoom_xhigh") == 100
    assert panel.get_param_value("zoom_ylow") == 15
    assert panel.get_param_value("zoom_yhigh") == 150


def test_external_zoom_update__no_signal_emitted(panel):
    _spy = SignalSpy(panel.sig_new_zoom_boundary)
    panel.external_zoom_update([5, 100, 15, 150])
    assert _spy.n == 0


def test_external_zoom_reset__sets_default_values(panel):
    panel.external_zoom_update([10, 50, 20, 80])
    panel.external_zoom_reset()
    assert panel.get_param_value("zoom_xlow") == 0
    assert panel.get_param_value("zoom_xhigh") is None
    assert panel.get_param_value("zoom_ylow") == 0
    assert panel.get_param_value("zoom_yhigh") is None


def test_external_zoom_reset__no_signal_emitted(panel):
    _spy = SignalSpy(panel.sig_new_zoom_boundary)
    panel.external_zoom_reset()
    assert _spy.n == 0


def test_external_cmap_threshold_update__updates_params(panel):
    panel.external_cmap_threshold_update(0.5, 9.5)
    assert panel.get_param_value("colormap_val_low") == pytest.approx(0.5)
    assert panel.get_param_value("colormap_val_high") == pytest.approx(9.5)


def test_external_cmap_threshold_update__no_signal_emitted(panel):
    _spy = SignalSpy(panel.sig_new_threshold)
    panel.external_cmap_threshold_update(0.5, 9.5)
    assert _spy.n == 0


def test_process_image_statistics__updates_all_params(panel):
    panel.process_image_statistics(1.0, 9.0, 5.0, 2.0)
    assert panel.get_param_value("image_stats_min") == pytest.approx(1.0)
    assert panel.get_param_value("image_stats_max") == pytest.approx(9.0)
    assert panel.get_param_value("image_stats_mean") == pytest.approx(5.0)
    assert panel.get_param_value("image_stats_std") == pytest.approx(2.0)


if __name__ == "__main__":
    pytest.main([__file__])
