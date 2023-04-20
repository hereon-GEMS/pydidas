# This file is part of ...
#
# Copyright 2021-, Helmholtz-Zentrum Hereon
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
# along with ... If not, see <http://www.gnu.org/licenses/>.

"""
Module with the SelectPointsInImage class which allows to select points
in an image, for example to define the beamcenter.
"""

__author__ = "Malte Storm"
__copyright__ = "Copyright 2021-2022, Malte Storm, Helmholtz-Zentrum Hereon"
__license__ = "GPL-3.0"
__maintainer__ = "Malte Storm"
__status__ = "Development"
__all__ = ["SelectPointsInImage"]

from pathlib import Path

import numpy as np
from qtpy import QtCore, QtWidgets
from silx.gui.plot.items import Marker, Shape

from ...core import Parameter
from ...core.constants import PYDIDAS_COLORS, STANDARD_FONT_SIZE
from ...data_io import import_data
from ...widgets.factory import CreateWidgetsMixIn
from ...widgets.parameter_config import ParameterWidgetsMixIn
from ...widgets.silx_plot import PydidasPlot2D
from .table_with_xy_positions import TableWithXYPositions


class SelectPointsInImage(QtWidgets.QWidget, CreateWidgetsMixIn, ParameterWidgetsMixIn):
    """
    A widget which allows to select points in a given image.
    """

    container_width = 220

    def __init__(self, parent=None, **kwargs):
        QtWidgets.QWidget.__init__(self, parent)
        CreateWidgetsMixIn.__init__(self)
        ParameterWidgetsMixIn.__init__(self)
        self.setLayout(QtWidgets.QGridLayout())
        self._points = []
        self._image = None
        self.marker_color = Parameter(
            "marker_color",
            str,
            "orange",
            name="Marker color",
            choices=list(PYDIDAS_COLORS.keys()),
            tooltip="Set the display color for the markers of selected points.",
        )

        self.create_empty_widget(
            "left_container", fixedWidth=self.container_width, minimumHeight=400
        )
        self.create_spacer(None, fixedWidth=25, gridPos=(0, 1, 1, 1))
        self.add_any_widget(
            "plot",
            PydidasPlot2D(cs_transform=False),
            minimumWidth=700,
            minimumHeight=700,
            gridPos=(0, 2, 1, 1),
        )
        self.create_label(
            "label_title",
            "Select points in image:",
            fontsize=STANDARD_FONT_SIZE + 1,
            fixedWidth=self.container_width,
            bold=True,
            parent_widget=self._widgets["left_container"],
        )
        self.create_line("line_top", parent_widget=self._widgets["left_container"])
        self.create_param_widget(
            self.marker_color,
            halign_text=QtCore.Qt.AlignLeft,
            valign_text=QtCore.Qt.AlignBottom,
            width_total=self.container_width,
            width_io=100,
            width_text=120,
            width_unit=0,
            parent_widget=self._widgets["left_container"],
        )
        self.create_line("line_points", parent_widget=self._widgets["left_container"])
        self.create_label(
            "label_title",
            "Selected points",
            fontsize=STANDARD_FONT_SIZE,
            fixedWidth=self.container_width,
            underline=True,
            parent_widget=self._widgets["left_container"],
        )
        self.add_any_widget(
            "table",
            TableWithXYPositions(),
            parent_widget=self._widgets["left_container"],
            fixedWidth=self.container_width,
        )
        self.create_button(
            "but_delete_selected_points",
            "Delete selected points",
            fixedWidth=self.container_width,
            fixedHeight=25,
            parent_widget=self._widgets["left_container"],
        )
        self._widgets["but_delete_selected_points"].clicked.connect(
            self._widgets["table"].remove_selected_points
        )
        self._widgets["plot"].sigPlotSignal.connect(self._process_plot_signal)
        self.param_widgets["marker_color"].io_edited.connect(self._update_markers)
        self._widgets["table"].sig_new_selection.connect(self.__new_points_selected)
        self._widgets["table"].sig_remove_points.connect(self.__remove_points_from_plot)

    def open_image(self, filename, **kwargs):
        """
        Open an image with the given filename and display it in the plot.

        Parameters
        ----------
        filename : Union[str, Path]
            The filename and path.
        """
        self._image = import_data(filename, **kwargs)
        _path = Path(filename)
        self._widgets["plot"].plot_pydidas_dataset(self._image, title=_path.name)

    @QtCore.Slot(object)
    def __remove_points_from_plot(self, points):
        """
        Remove the selected points from the plot.

        Parameters
        ----------
        points : list
            List with tuples of the (x, y) position of the points.
        """
        for _point in points:
            self._points.remove(_point)
            self._widgets["plot"].removeMarker(f"marker_{_point[0]}_{_point[1]}")

    @QtCore.Slot(dict)
    def _process_plot_signal(self, event_dict):
        """
        Process events from the plot and filter and process mouse clicks.

        Parameters
        ----------
        event_dict : dict
            The silx event dictionary.
        """
        if (
            event_dict["event"] == "mouseClicked"
            and event_dict.get("button", "None") == "left"
        ):
            _color = PYDIDAS_COLORS[self.marker_color.value]
            _x = np.round(event_dict["x"], decimals=3)
            _y = np.round(event_dict["y"], decimals=3)
            if (_x, _y) in self._points:
                return
            self._widgets["plot"].addMarker(
                _x, _y, legend=f"marker_{_x}_{_y}", color=_color, symbol="x"
            )
            self._points.append((_x, _y))
            self._widgets["table"].add_point_to_table(_x, _y)

    @QtCore.Slot(str)
    def _update_markers(self, color):
        """
        Update the markers with a new color.

        Parameters
        ----------
        color : str
            The new color name.
        """
        _colorcode = PYDIDAS_COLORS[color]
        _items = self._widgets["plot"].getItems()
        for _item in _items:
            if isinstance(_item, (Marker, Shape)):
                _item.setColor(_colorcode)

    @QtCore.Slot(object)
    def __new_points_selected(self, points):
        """
        Process the signal that new points have been selected.
        """
        for _point in self._points:
            _label = f"marker_{_point[0]}_{_point[1]}"
            _marker = self._widgets["plot"]._getItem("marker", _label)
            _symbol = "o" if _point in points else "x"
            _marker.setSymbol(_symbol)

    def get_selected_points(self):
        """
        Get the selected points as two arrays for x- and y-coordinates.

        Returns
        -------
        x_positions : np.ndarray
            The x values of the selected points.
        y_positions : np.ndarray
            The y values of the selected points.
        """
        _n = len(self._points)
        _x = np.zeros((_n))
        _y = np.zeros((_n))
        for _index, (_xpos, _ypos) in enumerate(self._points):
            _x[_index] = _xpos
            _y[_index] = _ypos
        return _x, _y

    def set_beamcenter_marker(self, position):
        """
        Mark the beamcenter with a marker.
        """
        if position is None:
            self._widgets["plot"].remove(legend="beamcenter", kind="marker")
            return
        _color = PYDIDAS_COLORS[self.marker_color.value]
        self._widgets["plot"].addMarker(
            *position, legend="beamcenter", color=_color, symbol="+"
        )

    def show_outline(self, points):
        """
        Show an outline defined through the points.

        The outline can, for example, be a fitted circle or ellipse. The points must be
        given as a 2-tuple or None to clear the outline.

        Parameters
        ----------
        points : Union[None, tuple]
            The points for the outline in form of a tuple with x- and y- point
            positions. If None, the outline is cleared from the plot.
        """
        if points is None:
            self._widgets["plot"].remove(legend="outline", kind="item")
            return
        _color = PYDIDAS_COLORS[self.marker_color.value]
        self._widgets["plot"].addShape(
            points[0],
            points[1],
            legend="outline",
            color=_color,
            linestyle="--",
            fill=False,
            linewidth=2.0,
        )
