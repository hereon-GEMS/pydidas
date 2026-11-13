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


"""
Module with the _ImageView which is a subclassed pyqtgraph ImageView.
"""

__author__ = "Malte Storm"
__copyright__ = "Copyright 2026, Helmholtz-Zentrum Hereon"
__license__ = "GPL-3.0-only"
__maintainer__ = "Malte Storm"
__status__ = "Production"
__all__ = ["_ImageView"]


import warnings
from collections.abc import Callable
from typing import Literal

import numpy as np
import pyqtgraph
from pyqtgraph import ImageItem, ImageView
from pyqtgraph.graphicsItems import GraphicsWidget
from qtpy import QtCore, QtGui, QtWidgets

from pydidas.core.constants.image_ops import IMAGE_OPS
from pydidas.widgets.pyqtgraph_plot._pyqtgraph_utils import (
    DisplaySettings,
    ImageData,
    ImageViewFlags,
    Markers,
    RegionOfInterest,
    point_delta,
)


class _ImageView(ImageView):
    """
    A subclassed pyqtgraph ImageView with additional functionality for
    handling persistent zoom and ROI settings, as well as additional signals for
    pixel description, zoom bounds, histogram levels, image statistics, and
    marker position.
    """

    sig_pixel_description = QtCore.Signal(str)
    sig_new_zoom_bounds = QtCore.Signal(list)
    sig_new_histogram_levels = QtCore.Signal(float, float)
    sig_image_statistics = QtCore.Signal(float, float, float, float)
    sig_reset_zoom = QtCore.Signal()
    sig_new_marker_position = QtCore.Signal(int, int)

    def __init__(
        self,
        parent: QtWidgets.QWidget | None = None,
    ) -> None:
        self._imageItem = pyqtgraph.ImageItem(np.zeros((2048, 2048)))
        ImageView.__init__(
            self,
            parent=parent,
            name="_ImageView",
            imageItem=self._imageItem,
        )
        self.autoRange()
        self.autoLevels()

        # Additional dataclasses used for internal state management:
        self._markers = Markers()
        self._display = DisplaySettings()
        self._crop_roi = RegionOfInterest()
        self._zoom_roi = RegionOfInterest()
        self._image = ImageData()
        self._flags = ImageViewFlags()
        self._thresholds: list[float | None] = [None, None]
        self._image_op: Callable | None = None

        # Modify the default behavior of the ImageView:
        self.setMinimumSize(500, 500)
        self.ui.roiBtn.setVisible(False)
        self._imageItem.mouseClickEvent = self._imageItem_mouseClickEvent
        self._imageItem.hoverEvent = self._imageItem_mouseHoverEvent
        self._imageItem.mousePressEvent = self._imageItem_mousePressEvent
        self._imageItem.mouseReleaseEvent = self._imageItem_mouseReleaseEvent
        # Consume pyqtgraph-level drag events on the image item so they do not
        # propagate to the ViewBox, which would pan/zoom the viewport after our
        # own drag-to-zoom handling has already called autoRange().
        self._imageItem.mouseDragEvent = lambda ev: ev.accept()
        self.ui.graphicsView.setBackground("#EEEEEE")
        self._context_menu = QtWidgets.QMenu(self)
        self._reset_zoom_action = self._context_menu.addAction("Reset zoom")
        self._set_up_markers()
        self._set_up_histogram_widget()

    @property
    def image_x0(self) -> int:
        """Get the lower x boundary of the image."""
        return self._crop_roi.x0 + self._zoom_roi.x0

    @property
    def image_y0(self) -> int:
        """Get the lower y boundary of the image."""
        return self._crop_roi.y0 + self._zoom_roi.y0

    @QtCore.Slot()
    def threshold_reset(self) -> None:
        """Reset the thresholds to None."""
        self.autoRange()
        self.autoLevels()
        self._thresholds = [None, None]
        self.show_image(self._image.raw)

    def show_context_menu(self, pos: QtCore.QPointF) -> None:
        """
        Show the context menu for the _ImageView.

        Parameters
        ----------
        pos : QtCore.QPointF
            The position of the mouse event.
        """
        # The position of the pixel with respect to the widget itself:
        _pixel_pos_in_widget = self.getImageItem().mapToScene(pos.toPoint())
        _global_pos = self.mapToGlobal(_pixel_pos_in_widget.toPoint())

        self._flags.context_menu_open = True
        action = self._context_menu.exec_(_global_pos)
        if action == self._reset_zoom_action:
            self.sig_reset_zoom.emit()
            self._zoom_roi.x = slice(0, None)
            self._zoom_roi.y = slice(0, None)
            self.show_image(self._image.raw)
            self._flags.context_menu_open = False

    def set_image_zoom(self, x0: int, x1: int, y0: int, y1: int) -> None:
        """
        Set the zoom for the _ImageView.

        Please check the 'set_slice' method for the full documentation.
        """
        self.set_slice("zoom", x0, x1, y0, y1)

    def set_image_roi(self, x0: int, x1: int, y0: int, y1: int) -> None:
        """
        Set the region of interest for the _ImageView.

        Please check the 'set_slice' method for the full documentation.
        """
        self.set_slice("roi", x0, x1, y0, y1)

    def set_slice(
        self, roi_type: Literal["zoom", "roi"], x0: int, x1: int, y0: int, y1: int
    ) -> None:
        """
        Set the region of interest for the _ImageView.

        Parameters
        ----------
        roi_type : Literal["zoom", "roi"]
            The type of the region of interest. Must be either "zoom" or "roi".
        x0 : int
            The lower x boundary.
        x1 : int
            The upper x boundary.
        y0 : int
            The lower y boundary.
        y1 : int
            The upper y boundary.
        """
        _roi = self._crop_roi if roi_type == "roi" else self._zoom_roi
        _roi.x = slice(x0, max(x1, x0 + 2))
        _roi.y = slice(y0, max(y1, y0 + 2))
        self.show_image(self._image.raw)

    @QtCore.Slot(int)
    def set_circle_radius(self, radius: int) -> None:
        """
        Set the radius of the circle for the _ImageView.

        Parameters
        ----------
        radius : int
            The radius of the circle.
        """
        self._markers.circle_r = radius
        self.show_image(self._image.raw)

    @QtCore.Slot(str, str)
    def set_image_zoom_param(
        self,
        param: Literal["x0", "xlow", "x1", "xhigh", "y0", "ylow", "y1", "yhigh"],
        value_str: str,
    ) -> None:
        """
        Set the zoom for the _ImageView.

        Please see the 'set_slice_param' method for the full documentation.
        """
        self.set_slice_param("zoom", param, value_str)

    @QtCore.Slot(str, str)
    def set_image_roi_param(
        self,
        param: Literal["x0", "xlow", "x1", "xhigh", "y0", "ylow", "y1", "yhigh"],
        value_str: str,
    ) -> None:
        """
        Set the region of interest for the _ImageView.

        Please see the 'set_slice_param' method for the full documentation.
        """
        self.set_slice_param("crop", param, value_str)

    def set_slice_param(
        self,
        slice_type: Literal["zoom", "crop"],
        param: Literal["x0", "xlow", "x1", "xhigh", "y0", "ylow", "y1", "yhigh"],
        value_str: str,
    ) -> None:
        """
        Modify the slice for the _ImageView.

        Parameters
        ----------
        slice_type : Literal["zoom", "crop"]
            The type of the slice to be modified. Must be either "zoom" or "crop".
        param : Literal["x0", "xlow", "x1", "xhigh", "y0", "ylow", "y1", "yhigh"],
            The parameter to be set. x0 and xlow correspond to the lower
            x boundary, x1 and xhigh to the upper x boundary. The same goes
            for the y boundaries, respectively.
        value_str : str
            The string representation of the value to be set for the parameter.
            None will disable the respective ROI boundary.
        """
        _value = None if value_str in ["None", "nan"] else int(value_str)
        _roi = getattr(self, f"_{slice_type}_roi")
        if param.startswith("x"):
            _slice = _roi.x
            if param.endswith(("0", "low")):
                _slice = slice(_value, _slice.stop)
            else:
                _slice = slice(_slice.start, _value)
            _roi.x = _slice
        else:
            _slice = _roi.y
            if param.endswith(("0", "low")):
                _slice = slice(_value, _slice.stop)
            else:
                _slice = slice(_slice.start, _value)
            _roi.y = _slice
        self.show_image(self._image.raw)

    @QtCore.Slot(str, str)
    def set_threshold(self, param: Literal["low", "high"], value: str) -> None:
        """
        Set the threshold for the _ImageView.

        Parameters
        ----------
        param : Literal["low", "high"]
            The threshold parameter to be set. Must be either "low" or "high".
        value : str
            The string representation of the value to be set for the threshold.
            It can be either a numerical value of None, where the latter will
            disable the threshold.
        """
        value = float(value) if value not in ["None", "nan"] else None
        _index = 0 if param == "low" else 1
        self._thresholds[_index] = value
        if None in self._thresholds:
            self.autoLevels()
            return
        self.setLevels(min=self._thresholds[0], max=self._thresholds[1])

    @QtCore.Slot(str)
    def set_image_operation(self, op_name: str) -> None:
        """
        Set the operation to be applied to the camera image.

        This method allows to specify and rotations and flips to be used.

        Parameters
        ----------
        op_name : str
            The name of the operation to be applied.
        """
        if op_name == "None":
            self._image_op = None
        else:
            self._image_op = IMAGE_OPS[op_name]
        self.show_image(self._image.raw)

    @QtCore.Slot(int, int)
    def set_marker_position(self, xpos: int, ypos: int) -> None:
        """
        Set the position of the marker which defines the center
        of the cross and optionally circle.

        Parameters
        ----------
        xpos : int
            The x position of the marker.
        ypos : int
            The y position of the marker.
        """
        self._markers.x_raw = xpos
        self._markers.y_raw = ypos
        self._adjust_markers()

    @QtCore.Slot(str)
    def set_scale(self, scale: str) -> None:
        """
        Set the scale for the image.

        Parameters
        ----------
        scale : str
            The scale to be set. Must be either "linear", "logarithmic", or "arcsinh".
        """
        self._flags.use_log_scale = scale.lower() == "logarithmic"
        self._flags.use_arcsinh_scale = scale.lower() == "arcsinh"
        self._flags.use_lin_scale = scale.lower() == "linear"
        self.show_image(self._image.raw)

    @QtCore.Slot(int)
    def set_marker_pos_lock(self, flag: int | bool) -> None:
        """
        Set the lock for the marker position which prevents the
        marker from being moved by mouse clicks.

        Parameters
        ----------
        flag : int or bool
            The flag to enable or disable the lock.
        """
        self._flags.lock_marker_pos = bool(flag)

    def show_image(self, image: np.ndarray | None) -> None:
        """
        Show the given image in the _ImageView.

        Parameters
        ----------
        image : np.ndarray or None
            The image to be shown. If None, the method will return directly.
        """
        if image is None:
            self.clear()
            self._image.raw = None
            self._image.current = None
        else:
            image = self._get_preprocessed_image(image)
            self._flags.auto_update = True
            self.setImage(image, autoLevels=None in self._thresholds, autoRange=True)
            self._flags.auto_update = False
            if image.size > 0:
                self._calculate_image_statistics()
        self._adjust_markers()
        self.autoRange()

    set_image = show_image

    def closeEvent(self, event: QtGui.QCloseEvent) -> None:
        self._clean_up()
        super().closeEvent(event)

    def deleteLater(self) -> None:
        self._clean_up()
        super().deleteLater()

    def _set_up_markers(self) -> None:
        """Set up the implemented marker behavior."""
        _view = self.getView()
        # Invisible rect that clips all marker children to the image bounds.
        # ItemClipsChildrenToShape requires Qt-level parentage, which is why
        # the flag on ViewBox itself has no effect (addItem uses childGroup).
        self._markers_clip = QtWidgets.QGraphicsRectItem(
            0, 0, self._image.xsize, self._image.ysize
        )
        self._markers_clip.setPen(pyqtgraph.mkPen(None))
        self._markers_clip.setFlag(
            QtWidgets.QGraphicsItem.ItemClipsChildrenToShape, True
        )
        _view.addItem(self._markers_clip)

        for _marker in [
            self._markers.circle,
            self._markers.line_col,
            self._markers.line_row,
            self._markers.selection,
        ]:
            _marker.setVisible(False)
            _marker.setParentItem(self._markers_clip)

    def _set_up_histogram_widget(self) -> None:
        self._histo_widget = self.getHistogramWidget()
        self._histo_widget.setBackground("#EEEEEE")
        self._histo_widget.sigLevelChangeFinished.connect(self._process_level_changed)

    @QtCore.Slot(object)
    def _process_level_changed(self, hist_widget: GraphicsWidget) -> None:
        """
        Process a level change in the histrogram widget.

        Parameters
        ----------
        hist_widget : GraphicsWidget
            The histogram widget.
        """
        if self._image.current is None or self._flags.auto_update:
            return
        _levels = hist_widget.getLevels()  # type: ignore[attr-defined]
        self._thresholds = list(_levels)
        self.sig_new_histogram_levels.emit(*_levels)

    @QtCore.Slot(QtGui.QMouseEvent)
    def _imageItem_mouseHoverEvent(self, event: QtGui.QMouseEvent) -> None:
        """Mouse move event handler for the _ImageView."""
        if event.isExit():  # type: ignore[attr-defined]
            self.sig_pixel_description.emit("")
        elif self._image.current is not None:
            _pos = event.pos()
            _ix = int(_pos.x())
            _iy = int(_pos.y())
            # pyqtgraph can return positions outside the image bounds,
            # so these need to be checked before accessing the image array:
            if 0 <= _ix < self._image.xsize and 0 <= _iy < self._image.ysize:
                _value = self._image.current[_iy, _ix]
                _ix += self._zoom_roi.x0
                _iy += self._zoom_roi.y0
                self.sig_pixel_description.emit(
                    f"x [px] = {_ix:4d}\ty [px] = {_iy:4d}\tPixel value = {_value:.2f}"
                )
            if self._markers.selection.isVisible():
                self._markers.selection.setSize(  # type: ignore[arg-type]
                    point_delta(_pos, self._press_pos)  # type: ignore[arg-type]
                )
        ImageItem.hoverEvent(self._imageItem, event)

    @QtCore.Slot(QtGui.QMouseEvent)
    def _imageItem_mouseClickEvent(self, event: QtGui.QMouseEvent) -> None:
        """Mouse click event handler."""
        pos = event.pos()
        if event.button() == QtCore.Qt.LeftButton and not self._flags.lock_marker_pos:
            self._markers.y_raw = pos.y() + self.image_y0
            self._markers.x_raw = pos.x() + self.image_x0
            self._adjust_markers()
            self.sig_new_marker_position.emit(
                int(np.round(self._markers.x_raw, 0)),
                int(np.round(self._markers.y_raw, 0)),
            )
        event.accept()

    @QtCore.Slot(QtGui.QMouseEvent)
    def _imageItem_mousePressEvent(self, event: QtGui.QMouseEvent) -> None:
        """Mouse press event handler for the _ImageView."""
        if self._flags.context_menu_open:
            event.ignore()
            return
        if event.button() == QtCore.Qt.LeftButton:
            self._press_pos = event.pos()
            self._markers.selection.setVisible(True)
            self._markers.selection.setPos(self._press_pos)
            self._markers.selection.setSize((0, 0))
            event.accept()
        if event.button() == QtCore.Qt.RightButton:
            self.show_context_menu(event.pos())  # type: ignore[arg-type]

    @QtCore.Slot(QtGui.QMouseEvent)
    def _imageItem_mouseReleaseEvent(self, event: QtGui.QMouseEvent) -> None:
        """Mouse release event handler for the _ImageView."""
        if self._markers.selection.isVisible():
            self._markers.selection.setVisible(False)
        if self._flags.context_menu_open:
            self._flags.context_menu_open = False
            event.ignore()
            return
        if event.button() == QtCore.Qt.LeftButton:
            _pos = event.pos()
            _dx, _dy = point_delta(_pos, self._press_pos)  # type: ignore[arg-type]
            _delta = (_dx**2 + _dy**2) ** 0.5
            if _delta < 2:
                self._imageItem_mouseClickEvent(event)
            else:
                _xpos_raw = sorted([_pos.x(), self._press_pos.x()])
                _xpos = [
                    int(self._zoom_roi.x0 + max(0, _xpos_raw[0])),
                    int(self._zoom_roi.x0 + min(self._image.xsize, _xpos_raw[1])),
                ]
                _ypos_raw = sorted([_pos.y(), self._press_pos.y()])
                _ypos = [
                    int(self._zoom_roi.y0 + max(0, _ypos_raw[0])),
                    int(self._zoom_roi.y0 + min(self._image.ysize, _ypos_raw[1])),
                ]
                self.set_image_zoom(*_xpos, *_ypos)
                self.sig_new_zoom_bounds.emit(_xpos + _ypos)
        ImageItem.mouseReleaseEvent(self._imageItem, event)  # type: ignore[arg-type]

    def _get_preprocessed_image(self, image: np.ndarray) -> np.ndarray:
        """
        Get the preprocessed image based on the raw image and the current settings.

        Parameters
        ----------
        image : np.ndarray
            The raw image.

        Returns
        -------
        np.ndarray
            The preprocessed image.
        """
        self._image.raw = image.copy()
        _image = image.copy()
        if self._image_op is not None:
            _image = self._image_op(_image)
        _image = _image[*self._crop_roi.slices]
        _image = _image[*self._zoom_roi.slices]
        if self._flags.use_log_scale:
            # set the minimum for clipping to a value that is 1/3  of the
            # maximum in log space to have a reasonable dynamic range
            # for the log scale:
            _amin = np.exp(-np.log((_image.max()) / 3))
            _image = np.clip(_image, a_min=_amin, a_max=None)
            _image = np.log(_image)
        elif self._flags.use_arcsinh_scale:
            _image = np.arcsinh(_image)
        self._image.current = _image
        self._image.size = _image.shape
        return _image

    def _adjust_markers(self) -> None:
        """Adjust the markers to the current image size."""
        self._markers_clip.setVisible(self._image.current is not None)
        if self._image.current is None:
            return
        self._markers_clip.setRect(0, 0, self._image.xsize, self._image.ysize)
        self._markers.line_col.setSize((0.0, self._image.ysize))
        self._markers.line_col.setPos(self._markers.x_raw - self.image_x0, 0)
        self._markers.line_col.setVisible(
            self.image_x0 <= self._markers.x_raw <= self.image_x0 + self._image.xsize
        )
        self._markers.line_row.setPos(0, self._markers.y_raw - self.image_y0)
        self._markers.line_row.setSize((self._image.xsize, 0.0))
        self._markers.line_row.setVisible(
            self.image_y0 <= self._markers.y_raw <= self.image_y0 + self._image.ysize
        )
        self._markers.circle.setVisible(self._markers.circle_r > 0)
        if self._markers.circle_r == 0:
            return
        self._markers.circle.setPos(
            self._markers.x_raw - self.image_x0 - self._markers.circle_r,
            self._markers.y_raw - self.image_y0 - self._markers.circle_r,
        )
        self._markers.circle.setSize(
            (2 * self._markers.circle_r, 2 * self._markers.circle_r)
        )
        for _handle in self._markers.circle.getHandles():
            self._markers.circle.removeHandle(_handle)

    def _calculate_image_statistics(self) -> None:
        """Calculate and emit image statistics for the current image."""
        if self._image.current is None or self._image.current.size == 0:
            return
        _min = np.round(np.min(self._image.current), 3)
        _max = np.round(np.max(self._image.current), 3)
        _mean = np.round(np.mean(self._image.current), 3)
        _std = np.round(np.std(self._image.current), 3)
        self.sig_image_statistics.emit(_min, _max, _mean, _std)

    def _clean_up(self) -> None:
        """Clean up the PydidasImageViewer."""
        _view = self.getView()
        _view.removeItem(self._markers_clip)
        for _item in [
            self._markers.line_col,
            self._markers.line_row,
            self._markers.circle,
            self._markers.selection,
        ]:
            _item.deleteLater()
        with warnings.catch_warnings(action="ignore", category=RuntimeWarning):
            for _signal in [
                self.sig_pixel_description,
                self.sig_new_zoom_bounds,
                self.sig_new_histogram_levels,
                self.sig_image_statistics,
                self.sig_reset_zoom,
            ]:
                try:
                    _signal.disconnect()
                except TypeError:
                    pass
