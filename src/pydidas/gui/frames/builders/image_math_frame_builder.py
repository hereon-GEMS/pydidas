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
Module with the ImageMathFrameBuilder class which is used to populate
the ImageMathFrame with widgets.
"""

__author__ = "Malte Storm"
__copyright__ = "Copyright 2024 - 2025, Helmholtz-Zentrum Hereon"
__license__ = "GPL-3.0-only"
__maintainer__ = "Malte Storm"
__status__ = "Production"
__all__ = ["ImageMathFrameBuilder"]


from typing import Union

from qtpy import QtCore, QtGui, QtWidgets

from pydidas.core import constants
from pydidas.widgets import ScrollArea, misc
from pydidas.widgets.framework import BaseFrame
from pydidas.widgets.silx_plot import PydidasPlot2D


UFUNCS = ["absolute", "exp", "fmax", "fmin", "log", "log2", "log10", "power", "sqrt"]

LOCAL_SETTINGS = QtCore.QLocale(QtCore.QLocale.C)
LOCAL_SETTINGS.setNumberOptions(QtCore.QLocale.RejectGroupSeparator)

FLOAT_VALIDATOR = QtGui.QDoubleValidator()
FLOAT_VALIDATOR.setNotation(QtGui.QDoubleValidator.ScientificNotation)
FLOAT_VALIDATOR.setLocale(LOCAL_SETTINGS)


_kwargs_for_single_char_label = {
    "bold": True,
    "fontsize_offset": 1,
    "font_metric_width_factor": 0.7,
    "gridPos": (0, -1, 1, 1),
    "margin": 2,
    "minimum_width": 12,
}


class ImageMathFrameBuilder:
    """
    Create all widgets and initialize their state.

    Parameters
    ----------
    self : pydidas.gui.ImageMathFrame
        The ImageMathFrame instance.
    """

    _frame = None

    @classmethod
    def create_combo_button_row(
        cls,
        reference: str,
        label_text: str,
        combo_choices: list,
        button_text: str,
        button_icon: Union[None, str] = None,
    ):
        """
        Create a combined widget with label, combobox and a button.

        Parameters
        ----------
        reference : str
            The widget reference
        label_text : str
            The text for the label.
        combo_choices : list
            The choices to be displayed in the QComboBox.
        button_text : str
            The button text.
        button_icon : Union[None, str]
            The button icon.
        """
        cls._frame.create_empty_widget(
            reference,
            font_metric_width_factor=constants.FONT_METRIC_WIDE_CONFIG_WIDTH,
            parent_widget="left_container",
        )
        cls._frame.create_label(
            f"label_{reference}",
            label_text,
            font_metric_width_factor=constants.FONT_METRIC_WIDE_CONFIG_WIDTH / 2,
            parent_widget=reference,
            sizePolicy=constants.POLICY_MIN_MIN,
            wordWrap=False,
        )
        cls._frame.create_combo_box(
            f"combo_{reference}",
            font_metric_width_factor=constants.FONT_METRIC_WIDE_CONFIG_WIDTH / 3,
            gridPos=(0, 1, 1, 1),
            items=combo_choices,
            parent_widget=reference,
        )
        _kwargs = {
            "parent_widget": reference,
            "gridPos": (0, 2, 1, 1),
            "alignment": None,
            "sizePolicy": constants.POLICY_EXP_FIX,
        }
        if button_icon is not None:
            _kwargs["icon"] = button_icon
        cls._frame.create_button(f"but_{reference}", button_text, **_kwargs)

    @classmethod
    def populate_frame(cls, frame: BaseFrame):
        """
        Build the frame by creating all required widgets and placing them in the layout.

        Parameters
        ----------
        frame : BaseFrame
            The frame instance.
        """
        cls._frame = frame

        cls._frame.create_label(
            "title",
            "Image mathematics",
            bold=True,
            fontsize_offset=4,
            gridPos=(0, 0, 1, 5),
        )

        cls._input_images = tuple(
            f"Input image #{i}" for i in range(1, cls._frame.BUFFER_SIZE + 1)
        )
        cls._images = tuple(f"Image #{i}" for i in range(1, cls._frame.BUFFER_SIZE + 1))
        cls._all_images = ("Opened file",) + cls._input_images + cls._images
        cls._current_images = ("Current image",) + cls._input_images + cls._images

        cls._create_left_config()
        cls._create_input_widgets()
        cls._create_plot_widgets()
        cls._create_display_buffer_widgets()
        cls._create_image_operation_header()
        cls._create_elementary_arithmetic_widgets()
        cls._create_ufunc_widgets()
        cls._create_image_arithmetic_widgets()
        cls._create_export_widgets()

    @classmethod
    def _create_left_config(cls):
        """Create the left config section."""
        cls._frame.create_empty_widget(
            "left_container",
            font_metric_width_factor=constants.FONT_METRIC_WIDE_CONFIG_WIDTH,
            minimumHeight=600,
            parent_widget=None,
        )
        cls._frame.create_any_widget(
            "left_scroll_area",
            ScrollArea,
            layout_kwargs={"alignment": None},
            sizePolicy=constants.POLICY_FIX_EXP,
            stretch=(1, 0),
            widget=cls._frame._widgets["left_container"],
        )

    @classmethod
    def _create_input_widgets(cls):
        """Create the input widgets to select filenames or frames."""
        cls._frame.create_line("line_top", parent_widget="left_container")
        cls._frame.create_label(
            "label_open",
            "Open new image:",
            fontsize_offset=1,
            bold=True,
            parent_widget="left_container",
        )
        cls._frame.add_any_widget(
            "file_selector",
            misc.SelectImageFrameWidget(
                *cls._frame.params.values(),
                import_reference="ImageMathFrame__image_import",
            ),
            parent_widget="left_container",
        )
        cls._frame.create_spacer(None, parent_widget="left_container", fixedHeight=5)
        cls.create_combo_button_row(
            "store_input_image",
            "Store loaded image as ",
            cls._input_images,
            "Store",
            button_icon="qt-std::SP_CommandLink",
        )
        cls._frame.create_line("line_input", parent_widget="left_container")

    @classmethod
    def _create_plot_widgets(cls):
        """Create the required widgets for plotting the images."""
        cls._frame.create_any_widget("viewer", PydidasPlot2D, gridPos=(1, 1, 1, 1))

    @classmethod
    def _create_display_buffer_widgets(cls):
        """Create widgets to display images from the buffer."""
        cls._frame.create_spacer(None, parent_widget="left_container", fixedHeight=5)
        cls._frame.create_empty_widget(
            "display_from_buffer",
            parent_widget="left_container",
        )
        cls._frame.create_label(
            "label_display_from_buffer",
            "Display image:",
            bold=True,
            font_metric_width_factor=constants.FONT_METRIC_WIDE_CONFIG_WIDTH / 3,
            parent_widget="display_from_buffer",
            sizePolicy=constants.POLICY_MIN_MIN,
            wordWrap=False,
        )
        cls._frame.create_spacer(
            None,
            gridPos=(0, 1, 1, 1),
            parent_widget="display_from_buffer",
            policy=QtWidgets.QSizePolicy.Expanding,
            vertical_policy=QtWidgets.QSizePolicy.Fixed,
        )

        cls._frame.create_combo_box(
            "combo_display_image",
            alignment=constants.ALIGN_TOP_RIGHT,
            font_metric_width_factor=constants.FONT_METRIC_WIDE_CONFIG_WIDTH / 2,
            font_metric_height_factor=1,
            gridPos=(0, 2, 1, 1),
            items=cls._all_images,
            parent_widget="display_from_buffer",
        )

        cls._frame.create_line("line_buffer", parent_widget="left_container")

    @classmethod
    def _create_image_operation_header(cls):
        """Create the header for the image operations section."""
        cls._frame.create_label(
            "label_ops",
            "Image operations:",
            bold=True,
            fontsize_offset=1,
            parent_widget="left_container",
        )

    @classmethod
    def _create_ufunc_widgets(cls):
        """Create the required widgets to apply ufuncs to the images."""
        cls._frame.create_spacer(None, parent_widget="left_container", fixedHeight=10)
        cls._frame.create_label(
            "label_ops",
            "Apply operator to image:",
            bold=True,
            parent_widget="left_container",
        )
        cls._frame.create_empty_widget(
            "ops_operator",
            layout_kwargs={"horizontalSpacing": 2},
            parent_widget="left_container",
            toolTip=(
                "Apply an operator in the input image and store it as a new image. "
                "For reference on the individual functions, please refer to numpy's "
                "ufunc documentation https://numpy.org/doc/stable/reference/ufuncs.html"
            ),
        )
        cls._frame.create_combo_box(
            "ops_operator_target",
            font_metric_width_factor=constants.FONT_METRIC_WIDE_CONFIG_WIDTH / 4.8,
            gridPos=(0, 0, 1, 1),
            items=cls._images,
            parent_widget="ops_operator",
        )
        cls._frame.create_label(
            None, "=", parent_widget="ops_operator", **_kwargs_for_single_char_label
        )
        cls._frame.create_combo_box(
            "ops_operator_func",
            currentIndex=4,
            font_metric_width_factor=constants.FONT_METRIC_WIDE_CONFIG_WIDTH / 4.8,
            gridPos=(0, -1, 1, 1),
            items=UFUNCS,
            parent_widget="ops_operator",
        )
        cls._frame.create_label(
            None, " ( ", parent_widget="ops_operator", **_kwargs_for_single_char_label
        )
        cls._frame.create_combo_box(
            "combo_ops_operator_input",
            alignment=constants.ALIGN_CENTER_LEFT,
            font_metric_width_factor=constants.FONT_METRIC_WIDE_CONFIG_WIDTH / 3.5,
            gridPos=(0, -1, 1, 1),
            items=cls._current_images,
            parent_widget="ops_operator",
        )
        cls._frame.create_label(
            "label_ops_operator_sep",
            ", ",
            parent_widget="ops_operator",
            visible=False,
            **_kwargs_for_single_char_label,
        )
        cls._frame.create_lineedit(
            "io_ops_operator_input",
            font_metric_width_factor=constants.FONT_METRIC_WIDE_CONFIG_WIDTH / 9,
            gridPos=(0, -1, 1, 1),
            parent_widget="ops_operator",
            validator=FLOAT_VALIDATOR,
            visible=False,
        )
        cls._frame.create_label(
            "label_ops_operator_closing_bracket",
            ")",
            parent_widget="ops_operator",
            **_kwargs_for_single_char_label,
        )
        cls._frame.create_spacer(
            "spacer_operator_end",
            gridPos=(0, -1, 1, 1),
            parent_widget="ops_operator",
            policy=QtWidgets.QSizePolicy.Expanding,
            vertical_policy=QtWidgets.QSizePolicy.Fixed,
        )
        cls._frame.create_button(
            "but_ops_operator_execute",
            "Apply operator",
            alignment=constants.ALIGN_TOP_RIGHT,
            font_metric_width_factor=constants.FONT_METRIC_WIDE_CONFIG_WIDTH / 2.25,
            parent_widget="left_container",
        )

    @classmethod
    def _create_elementary_arithmetic_widgets(cls):
        """
        Create the required widgets to apply elementary arithmetic operations to images.
        """
        cls._frame.create_spacer(None, parent_widget="left_container", fixedHeight=10)
        cls._frame.create_label(
            "label_arithmetic",
            "Elementary arithmetic operations:",
            bold=True,
            parent_widget="left_container",
        )
        cls._frame.create_empty_widget(
            "ops_arithmetic",
            layout_kwargs={"horizontalSpacing": 2},
            parent_widget="left_container",
        )
        cls._frame.create_combo_box(
            "ops_arithmetic_target",
            font_metric_width_factor=constants.FONT_METRIC_WIDE_CONFIG_WIDTH / 4.8,
            gridPos=(0, 0, 1, 1),
            items=cls._images,
            parent_widget="ops_arithmetic",
        )
        cls._frame.create_label(
            None, "=", parent_widget="ops_arithmetic", **_kwargs_for_single_char_label
        )
        cls._frame.create_combo_box(
            "combo_ops_arithmetic_input",
            alignment=constants.ALIGN_CENTER_LEFT,
            font_metric_width_factor=constants.FONT_METRIC_WIDE_CONFIG_WIDTH / 3.2,
            gridPos=(0, -1, 1, 1),
            items=cls._current_images,
            parent_widget="ops_arithmetic",
        )
        cls._frame.create_combo_box(
            "combo_ops_arithmetic_operation",
            font_metric_width_factor=constants.FONT_METRIC_WIDE_CONFIG_WIDTH / 10,
            gridPos=(0, -1, 1, 1),
            items=["+", "-", "/", "x"],
            minimum_width=35,
            parent_widget="ops_arithmetic",
        )
        cls._frame.create_lineedit(
            "io_ops_arithmetic_input",
            font_metric_width_factor=constants.FONT_METRIC_WIDE_CONFIG_WIDTH / 4.8,
            font_metric_height_factor=1,
            gridPos=(0, -1, 1, 1),
            parent_widget="ops_arithmetic",
            validator=FLOAT_VALIDATOR,
        )
        cls._frame.create_spacer(
            "spacer_arithmetic_end",
            gridPos=(0, -1, 1, 1),
            parent_widget="ops_arithmetic",
            policy=QtWidgets.QSizePolicy.Expanding,
            vertical_policy=QtWidgets.QSizePolicy.Fixed,
        )
        cls._frame.create_button(
            "but_ops_arithmetic_execute",
            "Apply arithmetic operation",
            alignment=constants.ALIGN_TOP_RIGHT,
            font_metric_width_factor=constants.FONT_METRIC_WIDE_CONFIG_WIDTH / 2.25,
            parent_widget="left_container",
        )

    @classmethod
    def _create_image_arithmetic_widgets(cls):
        """
        Create the required widgets to apply elementary arithmetic operations to images.
        """
        cls._frame.create_spacer(None, parent_widget="left_container", fixedHeight=10)
        cls._frame.create_label(
            "label_image_arithmetic",
            "Arithmetic image operations:",
            bold=True,
            parent_widget="left_container",
        )
        cls._frame.create_empty_widget(
            "ops_image_arithmetic",
            parent_widget="left_container",
        )
        cls._frame.create_combo_box(
            "ops_image_arithmetic_target",
            font_metric_width_factor=constants.FONT_METRIC_WIDE_CONFIG_WIDTH / 4.8,
            items=cls._images,
            parent_widget="ops_image_arithmetic",
        )
        cls._frame.create_label(
            None,
            "=",
            parent_widget="ops_image_arithmetic",
            **_kwargs_for_single_char_label,
        )
        cls._frame.create_combo_box(
            "combo_ops_image_arithmetic_input_1",
            alignment=constants.ALIGN_CENTER_LEFT,
            font_metric_width_factor=constants.FONT_METRIC_WIDE_CONFIG_WIDTH / 3.5,
            gridPos=(0, -1, 1, 1),
            items=cls._current_images,
            parent_widget="ops_image_arithmetic",
        )
        cls._frame.create_combo_box(
            "combo_ops_image_arithmetic_operation",
            font_metric_width_factor=constants.FONT_METRIC_WIDE_CONFIG_WIDTH / 10,
            minimum_width=35,
            gridPos=(0, -1, 1, 1),
            items=["+", "-", "/", "x"],
            parent_widget="ops_image_arithmetic",
        )
        cls._frame.create_combo_box(
            "combo_ops_image_arithmetic_input_2",
            alignment=constants.ALIGN_CENTER_LEFT,
            font_metric_width_factor=constants.FONT_METRIC_WIDE_CONFIG_WIDTH / 3.5,
            gridPos=(0, -1, 1, 1),
            items=cls._current_images,
            parent_widget="ops_image_arithmetic",
        )

        cls._frame.create_spacer(
            "spacer_image_arithmetic_end",
            gridPos=(0, -1, 1, 1),
            parent_widget="ops_image_arithmetic",
            policy=QtWidgets.QSizePolicy.Expanding,
            vertical_policy=QtWidgets.QSizePolicy.Fixed,
        )
        cls._frame.create_button(
            "but_ops_image_arithmetic_execute",
            "Apply image arithmetic",
            alignment=constants.ALIGN_TOP_RIGHT,
            font_metric_width_factor=constants.FONT_METRIC_WIDE_CONFIG_WIDTH / 2.25,
            parent_widget="left_container",
        )

    @classmethod
    def _create_export_widgets(cls):
        """Create widgets for exporting the image."""
        cls._frame.create_spacer(None, parent_widget="left_container", fixedHeight=10)
        cls._frame.create_line("line_export", parent_widget="left_container")
        cls._frame.create_button(
            "but_export", "Export current image", parent_widget="left_container"
        )
