# This file is part of pydidas.
#
# Copyright 2023, Helmholtz-Zentrum Hereon
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
Module with the QuickIntegrationFrameBuilder which populates the QuickIntegrationFrame
with the required plugins.
"""

__author__ = "Malte Storm"
__copyright__ = "Copyright 2023, Helmholtz-Zentrum Hereon"
__license__ = "GPL-3.0-only"
__maintainer__ = "Malte Storm"
__status__ = "Production"
__all__ = ["QuickIntegrationFrameBuilder"]


from qtpy import QtWidgets

from ....core import constants
from ....widgets import ScrollArea, get_pyqt_icon_from_str
from ....widgets.misc import (
    PointPositionTableWidget,
    SelectImageFrameWidget,
    ShowIntegrationRoiParamsWidget,
)
from ....widgets.silx_plot import PydidasPlot2DwithIntegrationRegions, PydidasPlotStack


class QuickIntegrationFrameBuilder:
    """
    The QuickIntegrationFrameBuilder can be used to populate the QuickIntegrationFrame
    with widgets.
    """

    _frame = None

    @classmethod
    def _1line_options(cls, parent_key: str = "config", **kwargs) -> dict:
        """
        Get the options for 1-line Parameter widgets.

        Parameters
        ----------
        parent_key : str
            The parent widget reference key.
        **kwargs : dict
            Any keywords to be added to the generic options.

        Returns
        -------
        dict
            The options dictionary.
        """
        _1line_options = (
            dict(
                width_text=cls._frame._config["scroll_width"] - 180,
                width_io=150,
                width_total=cls._frame._config["scroll_width"],
                parent_widget=cls._frame._widgets[parent_key],
            )
            | kwargs
        )
        return _1line_options

    @classmethod
    def _2line_options(cls, parent_key: str = "config", **kwargs) -> dict:
        """
        Get the options for 1-line Parameter widgets.

        Parameters
        ----------
        parent_key : str, optional
            The parent widget reference key. The default is "config".
        **kwargs : dict
            Any keywords to be added to the generic options.

        Returns
        -------
        dict
            The options dictionary.
        """
        _2line_options = (
            constants.DEFAULT_TWO_LINE_PARAM_CONFIG
            | {
                "width_total": cls._frame._config["scroll_width"],
                "width_io": cls._frame._config["scroll_width"] - 20,
                "parent_widget": cls._frame._widgets[parent_key],
            }
            | kwargs
        )
        return _2line_options

    @classmethod
    def _label_header(
        cls, parent_key: str = "config", size_offset: int = 1, **kwargs
    ) -> dict:
        """
        Get the options for header labels.

        Parameters
        ----------
        parent_key : str, optional
            The parent widget reference key. The default is "config".
        size_offset : int, optional
            The offset to the standard font size. The default is 1.
        **kwargs : dict
            Any additional options to be added.

        Returns
        -------
        dict
            The options dictionary.
        """
        _label_header = (
            dict(
                fontsize=constants.STANDARD_FONT_SIZE + size_offset,
                bold=True,
                fixedWidth=cls._frame._config["scroll_width"],
                parent_widget=cls._frame._widgets[parent_key],
            )
            | kwargs
        )
        return _label_header

    @classmethod
    def populate_frame(cls, frame):
        """
        Populate the given frame with widgets.

        Note: This method is reliant upon passing the correct type of frame.

        Parameters
        ----------
        frame : pydidas.gui.frames.QuickIntegrationFrame
            The frame to be populated.
        """
        cls._frame = frame

        cls._frame.add_any_widget(
            "tabs", QtWidgets.QTabWidget(), gridPos=(1, 1, 1, 1), minimumWidth=400
        )

        cls._create_plot_tabs()
        cls._create_config_widgets()
        cls._create_exp_section_widgets()
        cls._create_beamcenter_section_widgets()
        cls._create_integration_section_widgets()
        cls._create_run_integration_widgets()

    @classmethod
    def _create_plot_tabs(cls):
        """
        Create the tabs for the plots.
        """
        # Create tab widgets first because the config references the plot widget.
        cls._frame.create_empty_widget(
            "tab_plot",
            parent_widget=None,
            layout_kwargs=dict(
                contentsMargins=(10, 10, 10, 10),
                columnStretch=(1, 1),
                rowStretch=(0, 1),
            ),
        )
        cls._frame.add_any_widget(
            "input_plot",
            PydidasPlot2DwithIntegrationRegions(diffraction_exp=cls._frame._EXP),
            parent_widget=cls._frame._widgets["tab_plot"],
            gridPos=(0, 1, 1, 1),
            enabled=False,
            minimumHeight=500,
            minimumWidth=500,
            sizePolicy=constants.POLICY_EXP_EXP,
        )
        cls._frame.create_empty_widget(
            "input_plot_bc_selection",
            parent_widget=cls._frame._widgets["tab_plot"],
            gridPos=(0, 0, 1, 1),
            visible=False,
        )
        cls._frame.create_param_widget(
            cls._frame.get_param("overlay_color"),
            width_text=PointPositionTableWidget.widget_width - 90,
            width_io=90,
            width_unit=0,
            width_total=PointPositionTableWidget.widget_width,
            parent_widget=cls._frame._widgets["input_plot_bc_selection"],
            gridPos=(0, 0, 1, 1),
        )
        cls._frame.add_any_widget(
            "input_beamcenter_points",
            PointPositionTableWidget(cls._frame._widgets["input_plot"]),
            parent_widget=cls._frame._widgets["input_plot_bc_selection"],
            gridPos=(1, 0, 1, 1),
            fixedWidth=PointPositionTableWidget.widget_width,
        )
        cls._frame.create_any_widget(
            "result_plot",
            PydidasPlotStack,
            parent_widget=None,
            diffraction_exp=cls._frame._EXP,
        )

        cls._frame._widgets["tabs"].addTab(
            cls._frame._widgets["tab_plot"], "Input image"
        )
        cls._frame._widgets["tabs"].addTab(
            cls._frame._widgets["result_plot"], "Integration results"
        )

    @classmethod
    def _create_config_widgets(cls):
        """
        Create the config widgets and headers.
        """
        cls._frame.create_label(
            "label_title",
            "Quick integration\n",
            fontsize=constants.STANDARD_FONT_SIZE + 4,
            bold=True,
            gridPos=(0, 0, 1, 1),
            fixedWidth=cls._frame._config["scroll_width"],
        )
        cls._frame.create_empty_widget(
            "config",
            parent_widget=None,
            init_layout=True,
            sizePolicy=constants.POLICY_FIX_EXP,
            fixedWidth=cls._frame._config["scroll_width"],
        )
        cls._frame.create_any_widget(
            "config_area",
            ScrollArea,
            widget=cls._frame._widgets["config"],
            fixedWidth=cls._frame._config["scroll_width"] + 50,
            sizePolicy=constants.POLICY_FIX_EXP,
            gridPos=(1, 0, 1, 1),
            stretch=(1, 0),
            layout_kwargs={"alignment": None},
        )
        cls._frame.create_label(None, "Input file:", **cls._label_header())
        cls._frame.add_any_widget(
            "file_selector",
            SelectImageFrameWidget(
                *cls._frame.params.values(),
                import_reference="QuickIntegrationFrame__image_import",
                widget_width=cls._frame._config["scroll_width"],
            ),
            parent_widget=cls._frame._widgets["config"],
            fixedWidth=cls._frame._config["scroll_width"],
        )
        cls._frame.create_line(None, parent_widget=cls._frame._widgets["config"])

    @classmethod
    def _create_exp_section_widgets(cls):
        """
        Create the widgets for the experimental section.
        """
        cls._frame.create_label(None, "Experiment description:", **cls._label_header())
        cls._frame.create_button(
            "copy_exp_context",
            "Copy expriment description from workflow setup",
            icon=get_pyqt_icon_from_str("qta::fa.copy"),
            fixedWidth=cls._frame._config["scroll_width"],
            parent_widget=cls._frame._widgets["config"],
        )
        cls._frame.create_button(
            "but_show_exp_section",
            "Show detailed experiment section",
            icon=cls._frame.style().standardIcon(6),
            fixedWidth=cls._frame._config["scroll_width"],
            parent_widget=cls._frame._widgets["config"],
            visible=True,
        )
        cls._frame.create_empty_widget(
            "exp_section", parent_widget=cls._frame._widgets["config"], visible=False
        )
        cls._frame.create_button(
            "but_import_exp",
            "Import diffraction experimental parameters",
            icon=cls._frame.style().standardIcon(42),
            fixedWidth=cls._frame._config["scroll_width"],
            parent_widget=cls._frame._widgets["exp_section"],
        )
        cls._frame.create_label(
            None, "X-ray energy:", **cls._label_header("exp_section", 0)
        )
        cls._frame.create_param_widget(
            cls._frame.get_param("xray_energy"),
            **cls._1line_options("exp_section"),
        )
        cls._frame.create_param_widget(
            cls._frame.get_param("xray_wavelength"),
            **cls._1line_options("exp_section"),
        )
        cls._frame.create_label(
            None, "Detector:", **cls._label_header("exp_section", 0)
        )
        cls._frame.create_param_widget(
            cls._frame.get_param("detector_pxsize"),
            **cls._1line_options("exp_section"),
        )
        cls._frame.create_param_widget(
            cls._frame.get_param("detector_dist"),
            **cls._1line_options("exp_section"),
        )
        cls._frame.create_param_widget(
            cls._frame.get_param("detector_mask_file"),
            **cls._2line_options("exp_section"),
        )
        cls._frame.create_spacer(
            None, fixedHeight=15, parent_widget=cls._frame._widgets["exp_section"]
        )
        cls._frame.create_button(
            "but_hide_exp_section",
            "Hide detailed experiment section",
            icon=cls._frame.style().standardIcon(5),
            fixedWidth=cls._frame._config["scroll_width"],
            parent_widget=cls._frame._widgets["exp_section"],
            visible=True,
        )
        cls._frame.create_param_widget(
            cls._frame.get_param("detector_model"),
            **(cls._2line_options() | dict(visible=False)),
        )

        cls._frame.create_spacer(
            None, fixedHeight=15, parent_widget=cls._frame._widgets["exp_section"]
        )

    @classmethod
    def _create_beamcenter_section_widgets(cls):
        """
        Create the widgets for the beamcenter section.
        """

        cls._frame.create_empty_widget(
            "beamcenter_section",
            parent_widget=cls._frame._widgets["config"],
            visible=False,
        )
        cls._frame.create_line(
            None, parent_widget=cls._frame._widgets["beamcenter_section"]
        )
        cls._frame.create_label(
            None, "Beamcenter:", **cls._label_header("beamcenter_section", 1)
        )
        cls._frame.create_button(
            "but_select_beamcenter_manually",
            "Start graphical beamcenter selection",
            fixedWidth=cls._frame._config["scroll_width"],
            parent_widget=cls._frame._widgets["beamcenter_section"],
        )
        cls._frame.create_button(
            "but_set_beamcenter",
            "Set selected point as beamcenter",
            fixedWidth=cls._frame._config["scroll_width"],
            parent_widget=cls._frame._widgets["beamcenter_section"],
            visible=False,
        )
        cls._frame.create_button(
            "but_fit_center_circle",
            "Fit beamcenter from points on circle",
            fixedWidth=cls._frame._config["scroll_width"],
            parent_widget=cls._frame._widgets["beamcenter_section"],
            visible=False,
        )
        cls._frame.create_button(
            "but_confirm_beamcenter",
            "Confirm beamcenter",
            icon=cls._frame.style().standardIcon(45),
            fixedWidth=cls._frame._config["scroll_width"],
            parent_widget=cls._frame._widgets["beamcenter_section"],
            visible=False,
        )

        cls._frame.create_param_widget(
            cls._frame.get_param("beamcenter_x"),
            **cls._1line_options("beamcenter_section"),
        )
        cls._frame.create_param_widget(
            cls._frame.get_param("beamcenter_y"),
            **cls._1line_options("beamcenter_section"),
        )

    @classmethod
    def _create_integration_section_widgets(cls):
        """
        Create the widgets for the integration section.
        """
        cls._frame.create_empty_widget(
            "integration_header",
            parent_widget=cls._frame._widgets["config"],
            visible=False,
        )
        cls._frame.create_line(
            None, parent_widget=cls._frame._widgets["integration_header"]
        )
        cls._frame.create_label(
            "label_roi",
            "Integration ROI:",
            **cls._label_header("integration_header"),
        )
        cls._frame.create_empty_widget(
            "integration_section",
            parent_widget=cls._frame._widgets["config"],
            visible=False,
        )
        cls._frame.create_button(
            "but_show_integration_section",
            "Show integration ROI section",
            icon=cls._frame.style().standardIcon(6),
            fixedWidth=cls._frame._config["scroll_width"],
            parent_widget=cls._frame._widgets["config"],
            visible=False,
        )
        cls._frame.create_label(
            "label_overlay_color",
            "Integration ROI display color",
            **cls._label_header("integration_section", 0),
        )

        cls._frame.add_any_widget(
            "roi_selector",
            ShowIntegrationRoiParamsWidget(
                cls._frame._widgets["input_plot"],
                plugin=cls._frame._plugins["generic"],
                widget_width=cls._frame._config["scroll_width"],
                show_reset_button=False,
                add_bottom_spacer=False,
            ),
            parent_widget=cls._frame._widgets["integration_section"],
        )

        cls._frame.create_spacer(
            None,
            fixedHeight=15,
            parent_widget=cls._frame._widgets["integration_section"],
        )
        cls._frame.create_button(
            "but_hide_integration_section",
            "Hide integration ROI section",
            icon=cls._frame.style().standardIcon(5),
            fixedWidth=cls._frame._config["scroll_width"],
            parent_widget=cls._frame._widgets["integration_section"],
            visible=True,
        )
        cls._frame.create_spacer(
            None,
            fixedHeight=15,
            parent_widget=cls._frame._widgets["integration_section"],
        )

    @classmethod
    def _create_run_integration_widgets(cls):
        """
        Create the widgets for running the integration.
        """
        cls._frame.create_empty_widget(
            "run_integration",
            parent_widget=cls._frame._widgets["config"],
            visible=False,
        )
        _options = dict(
            width_text=cls._frame._config["scroll_width"] - 100,
            width_io=100,
            width_unit=0,
            width_total=cls._frame._config["scroll_width"],
            parent_widget=cls._frame._widgets["run_integration"],
        )

        cls._frame.create_line(
            None, parent_widget=cls._frame._widgets["run_integration"]
        )
        cls._frame.create_label(
            None, "Run integration", **cls._label_header("run_integration", 1)
        )
        cls._frame.create_param_widget(
            cls._frame.get_param("integration_direction"),
            width_text=cls._frame._config["scroll_width"] - 185,
            width_io=180,
            width_unit=0,
            width_total=cls._frame._config["scroll_width"],
            parent_widget=cls._frame._widgets["run_integration"],
        )
        cls._frame.create_param_widget(cls._frame.get_param("azi_npoint"), **_options)
        cls._frame.create_param_widget(
            cls._frame.get_param("rad_npoint"), **(_options | dict(visible=False))
        )
        cls._frame.create_button(
            "but_run_integration",
            "Run pyFAI integration",
            fixedWidth=cls._frame._config["scroll_width"],
            parent_widget=cls._frame._widgets["run_integration"],
        )
        cls._frame.create_spacer(None, fixedHeight=10)
