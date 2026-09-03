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


"""Module with the _ControlPanel to control image displays."""

__author__ = "Malte Storm"
__copyright__ = "Copyright 2026, Helmholtz-Zentrum Hereon"
__license__ = "GPL-3.0-only"
__maintainer__ = "Malte Storm"
__status__ = "Production"
__all__ = ["_ControlPanel"]

import warnings
from functools import partial
from typing import Any, Literal

from qtpy import QtCore
from qtpy.QtWidgets import QWidget

from pydidas.core import get_generic_param_collection
from pydidas.core.constants import POLICY_FIX_EXP
from pydidas.widgets import ScrollArea, WidgetWithParameters
from pydidas.widgets.data_viewer import DataAxisSelector


_SPACER_HEIGHT = 20


class _ControlPanel(WidgetWithParameters):
    """
    The _ControlPanel allows to control the image display parameters
    and to set the ROI and zoom.

    In addition, it allows to set a marker position and a circle radius
    for image processing and to display image statistics. The panel is
    designed to be used in a vertical layout.
    """

    default_params = get_generic_param_collection(
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
    )
    PARAM_METRIC_WIDTH = 35
    BUTTON_METRIC_WIDTH = 15
    PARAM_METRIC_WIDTH_WIDE = PARAM_METRIC_WIDTH + BUTTON_METRIC_WIDTH

    sig_new_roi_boundary = QtCore.Signal(str, str)
    sig_new_zoom_boundary = QtCore.Signal(str, str)
    sig_new_threshold = QtCore.Signal(str, str)
    sig_reset_thresholds = QtCore.Signal()
    sig_new_image_op = QtCore.Signal(str)
    sig_new_circle_radius = QtCore.Signal(int)
    sig_marker_lock_state = QtCore.Signal(int)
    sig_marker_pos = QtCore.Signal(int, int)
    sig_use_scale = QtCore.Signal(str)

    def __init__(self, **kwargs: Any) -> None:
        WidgetWithParameters.__init__(self, **kwargs)
        self.layout().setHorizontalSpacing(5)  # type: ignore[attr-defined]
        self.layout().setVerticalSpacing(5)  # type: ignore[attr-defined]
        self.set_default_params()
        self.create_spacer("left_spacer", fixedWidth=20, gridPos=(0, 0, 1, 1))
        self.create_empty_widget(
            "config",
            parent_widget=None,
            font_metric_width_factor=self.PARAM_METRIC_WIDTH_WIDE,
        )
        self.add_any_widget(
            "scroll_area",
            ScrollArea(resize_to_widget_width=True, widget=self._widgets["config"]),
            gridPos=(0, 1, 1, 1),
            sizePolicy=POLICY_FIX_EXP,
            stretch=(1, 0),
            minimumHeight=400,
        )
        _generic_kwargs = {
            "font_metric_width_factor": self.PARAM_METRIC_WIDTH_WIDE,
            "gridPos": (-1, 0, 1, 2),
            "parent_widget": "config",
        }
        _generic_kwargs_w_bold = _generic_kwargs | {"bold": True}

        self.create_label("label_roi", "Global image ROI:", **_generic_kwargs_w_bold)
        for _key in ["roi", "zoom"]:
            self.create_empty_widget(f"{_key}_container", **_generic_kwargs)
            for _suffix in ["xlow", "xhigh", "ylow", "yhigh"]:
                self.create_param_widget(
                    self.params[f"{_key}_{_suffix}"],
                    gridPos=(-1, 0, 1, 1),
                    font_metric_width_factor=self.PARAM_METRIC_WIDTH,
                    parent_widget=f"{_key}_container",
                )
                self.param_composite_widgets[f"{_key}_{_suffix}"].sig_new_value.connect(
                    partial(self._process_update, f"{_key}_{_suffix}")
                )
            self.create_button(
                f"reset_{_key}",
                f"Reset\n{'ROI' if _key == 'roi' else 'zoom'}",
                clicked=self._reset_roi if _key == "roi" else self._reset_zoom,
                font_metric_width_factor=self.BUTTON_METRIC_WIDTH - 1,
                gridPos=(0, 1, 4, 1),
                parent_widget=f"{_key}_container",
                sizePolicy=POLICY_FIX_EXP,
            )
        self.create_spacer(
            "spacer_0",
            gridPos=(-1, 0, 1, 1),
            fixedHeight=_SPACER_HEIGHT,
            parent_widget="config",
        )

        self.create_label("label_cmap", "Histogram scaling:", **_generic_kwargs_w_bold)
        for _key in ["colormap_val_low", "colormap_val_high"]:
            self.create_param_widget(self.params[_key], **_generic_kwargs)
            self.param_composite_widgets[_key].sig_new_value.connect(
                partial(self._process_cmap_threshold_update, _key)
            )
        self.create_button(
            "reset_threshold",
            "Reset thresholds",
            clicked=self._reset_thresholds,
            **_generic_kwargs,
        )
        self.create_spacer(
            None,
            gridPos=(-1, 0, 1, 1),
            fixedHeight=_SPACER_HEIGHT,
            parent_widget="config",
        )
        self.create_label("label_circle", "Image marker:", **_generic_kwargs_w_bold)
        for _key in ["marker_lock", "marker_x", "marker_y"]:
            self.create_param_widget(self.params[_key], **_generic_kwargs)
        self.param_composite_widgets["marker_lock"].sig_new_value.connect(
            self._process_marker_lock
        )
        for _key in ["marker_x", "marker_y"]:
            self.param_composite_widgets[_key].sig_new_value.connect(
                self._process_marker_pos
            )

        self.create_label(
            "label_circle_explanation",
            "Add circle with radius R at marker\n(a radius of 0 will hide the circle):",
            font_metric_height_factor=2,
            **_generic_kwargs,
        )
        self.add_any_widget(
            "circle_roi_radius",
            DataAxisSelector(0, font_metric_width_factor=self.PARAM_METRIC_WIDTH_WIDE),
            gridPos=(-1, 0, 1, 2),
            parent_widget="config",
        )
        self._widgets["circle_roi_radius"].layout().setColumnStretch(2, 0)
        self._widgets["circle_roi_radius"].set_axis_metadata(None, "", "", npoints=1000)
        for _key in ["label_axis", "combo_axis_use", "button_start", "button_end"]:
            self._widgets["circle_roi_radius"]._widgets[_key].setVisible(False)
        self._widgets["circle_roi_radius"].sig_new_slicing.connect(
            self._define_new_circle_radius
        )
        self.create_spacer(
            None,
            gridPos=(-1, 0, 1, 1),
            fixedHeight=_SPACER_HEIGHT,
            parent_widget="config",
        )
        self.create_label(
            "label_imageops", "Image operations", **_generic_kwargs_w_bold
        )
        for _key in ["composite_image_op", "use_scale"]:
            self.create_param_widget(self.params[_key], **_generic_kwargs)
        self.create_spacer(
            None,
            gridPos=(-1, 0, 1, 1),
            fixedHeight=_SPACER_HEIGHT,
            parent_widget="config",
        )
        self.create_label(
            "label_statistics",
            "Image statistics (for current view only):",
            **_generic_kwargs_w_bold,
        )
        for _key in [
            "image_stats_min",
            "image_stats_max",
            "image_stats_mean",
            "image_stats_std",
        ]:
            self.create_param_widget(
                self.params[_key], width_text=0.6, width_io=0.4, **_generic_kwargs
            )
            self.param_composite_widgets[_key].io_widget.setReadOnly(True)  # type: ignore[attr-defined]
        self.create_spacer(
            "spacer_2",
            gridPos=(-1, 0, 1, 1),
            fixedHeight=_SPACER_HEIGHT,
            parent_widget="config",
        )
        self.param_composite_widgets["composite_image_op"].sig_new_value.connect(
            self.sig_new_image_op
        )
        self.param_composite_widgets["use_scale"].sig_new_value.connect(
            self._process_scale
        )
        self.layout().setRowStretch(0, 1)  # type: ignore[attr-defined]

    @QtCore.Slot(int, int)
    def external_marker_pos_update(self, x: int, y: int) -> None:
        """
        Update the marker position from an external source.

        Parameters
        ----------
        x : int
            The new x position.
        y : int
            The new y position.
        """
        with QtCore.QSignalBlocker(self):
            self.set_param_and_widget_value("marker_x", x)
            self.set_param_and_widget_value("marker_y", y)

    @QtCore.Slot(list)
    def external_roi_update(self, new_roi_coords: list[int | None]) -> None:
        """
        Update the ROI from an external source.

        Parameters
        ----------
        new_roi_coords : list[int or None]
            The new ROI coordinates in the order [x0, x1, y0, y1]
        """
        self._external_update("roi", new_roi_coords)

    @QtCore.Slot(list)
    def external_zoom_update(self, new_zoom_coords: list[int | None]) -> None:
        """
        Update the zoom from an external source.

        Parameters
        ----------
        new_zoom_coords : list[int or None]
            The new zoom coordinates in the order [x0, x1, y0, y1]
        """
        self._external_update("zoom", new_zoom_coords)

    @QtCore.Slot()
    def external_zoom_reset(self) -> None:
        """Reset the zoom to the full image."""
        self.external_zoom_update([0, None, 0, None])

    @QtCore.Slot(float, float)
    def external_cmap_threshold_update(self, low: float, high: float) -> None:
        """
        Update the thresholds from an external source.

        Parameters
        ----------
        low : float
            The new low threshold.
        high : float
            The new high threshold.
        """
        with QtCore.QSignalBlocker(self):
            self.set_param_and_widget_value("colormap_val_low", low)
            self.set_param_and_widget_value("colormap_val_high", high)

    @QtCore.Slot(float, float, float, float)
    def process_image_statistics(
        self, min_val: float, max_val: float, mean: float, std: float
    ) -> None:
        """
        Process the image statistics.

        Parameters
        ----------
        min_val : float
            The minimum value in the image.
        max_val : float
            The maximum value in the image.
        mean : float
            The mean value in the image.
        std : float
            The standard deviation in the image.
        """
        self.set_param_and_widget_value("image_stats_min", min_val)
        self.set_param_and_widget_value("image_stats_max", max_val)
        self.set_param_and_widget_value("image_stats_mean", mean)
        self.set_param_and_widget_value("image_stats_std", std)

    def deleteLater(self) -> None:
        """Prepare the widget for deletion."""
        with warnings.catch_warnings(action="ignore", category=RuntimeWarning):
            for _signal in [
                self.sig_new_roi_boundary,
                self.sig_new_zoom_boundary,
                self.sig_new_threshold,
                self.sig_reset_thresholds,
                self.sig_new_image_op,
                self.sig_new_circle_radius,
                self.sig_marker_pos,
                self.sig_marker_lock_state,
                self.sig_use_scale,
            ]:
                try:
                    _signal.disconnect()
                except TypeError:
                    pass
        for child in self.findChildren(QWidget):  # type: ignore[arg-type]
            child.deleteLater()
        super().deleteLater()

    @QtCore.Slot(str, str)
    def _process_update(self, key: str, value: str) -> None:
        """
        Process an update of a ROI parameter.

        Parameters
        ----------
        key : str
            The key to identify the specific ROI boundary
        value : str
            The input value to be processed for the ROI boundary
        """
        _signal = (
            self.sig_new_roi_boundary
            if key.startswith("roi")
            else self.sig_new_zoom_boundary
        )
        key = key.removeprefix("roi_").removeprefix("zoom_")
        _signal.emit(key, value)

    @QtCore.Slot()
    def _reset_thresholds(self) -> None:
        """
        Reset the thresholds to the default values.
        """

        self.sig_reset_thresholds.emit()
        for _key in ["colormap_val_low", "colormap_val_high"]:
            self.set_param_and_widget_value(_key, None)

    @QtCore.Slot(str, str)
    def _process_cmap_threshold_update(self, key: str, value: str) -> None:
        """
        Process an update of a threshold parameter.

        Parameters
        ----------
        key : str
            The key to identify the specific threshold to be edited.
        value : str
            The input value to be processed for the threshold.
        """
        key = key.removeprefix("colormap_val_")
        self.sig_new_threshold.emit(key, value)

    @QtCore.Slot(int, str)
    def _define_new_circle_radius(self, ax: int, value: str) -> None:
        """
        Define the new circle radius.

        Parameters
        ----------
        ax : int
            The axis index of the circle. This is 0 and not used.
        value : str
            The new circle radius, as a string slice representation.
        """
        _radius = int(value.split(":")[0])
        self.sig_new_circle_radius.emit(_radius)

    @QtCore.Slot()
    def _reset_roi(self) -> None:
        """Reset the ROI to the full image."""
        self._reset_boundary("roi")

    @QtCore.Slot()
    def _reset_zoom(self) -> None:
        """Reset the zoom to the full image."""
        self._reset_boundary("zoom")

    def _reset_boundary(self, key: str) -> None:
        """
        Reset the boundary to the full image.

        Parameters
        ----------
        key : str
            The key to identify the specific boundary
        """
        _signal = (
            self.sig_new_roi_boundary if key == "roi" else self.sig_new_zoom_boundary
        )
        for _key in [f"{key}_xlow", f"{key}_xhigh", f"{key}_ylow", f"{key}_yhigh"]:
            _val = 0 if _key.endswith("low") else None
            self.set_param_and_widget_value(_key, _val)
            _signal.emit(_key.removeprefix(f"{key}_"), str(_val))

    @QtCore.Slot(str)
    def _process_marker_lock(self, value: str) -> None:
        """
        Process the marker lock.

        Parameters
        ----------
        value : str
            The marker lock value as string.
        """
        _lock = value.lower() == "true"
        for _key in ["marker_x", "marker_y"]:
            self.param_composite_widgets[_key].io_widget.setReadOnly(_lock)  # type: ignore[attr-defined]
        self.sig_marker_lock_state.emit(_lock)

    @QtCore.Slot(str)
    def _process_marker_pos(self, value: str) -> None:
        """
        Process the marker position.

        Parameters
        ----------
        value : str
            The new marker position.
        """
        self.sig_marker_pos.emit(
            int(self.get_param_value("marker_x")), int(self.get_param_value("marker_y"))
        )

    @QtCore.Slot(str)
    def _process_scale(self, value: str) -> None:
        """
        Process the new scale selection.

        Parameters
        ----------
        value : str
            The scale value as string.
        """
        self.sig_use_scale.emit(value)

    def _external_update(
        self, key: Literal["roi", "zoom"], new_coords: list[int | None]
    ) -> None:
        """
        Update the ROI or zoom from an external source.

        Parameters
        ----------
        key : Literal["roi", "zoom"]
            The key to identify the specific boundary
        new_coords : list[int or None]
            The new ROI coordinates in the order [x0, x1, y0, y1]
        """
        with QtCore.QSignalBlocker(self):
            for _index, _key in enumerate(
                [f"{key}_xlow", f"{key}_xhigh", f"{key}_ylow", f"{key}_yhigh"]
            ):
                self.set_param_and_widget_value(_key, new_coords[_index])
