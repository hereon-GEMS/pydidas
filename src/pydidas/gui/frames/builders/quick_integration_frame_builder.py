# This file is part of pydidas.
#
# Copyright 2023 - 2025, Helmholtz-Zentrum Hereon
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
__copyright__ = "Copyright 2023 - 2025, Helmholtz-Zentrum Hereon"
__license__ = "GPL-3.0-only"
__maintainer__ = "Malte Storm"
__status__ = "Production"
__all__ = ["QuickIntegrationFrameBuilder"]


from qtpy import QtWidgets

from pydidas.core import constants
from pydidas.widgets import ScrollArea
from pydidas.widgets.misc import (
    PointsForBeamcenterWidget,
    SelectImageFrameWidget,
    ShowIntegrationRoiParamsWidget,
)
from pydidas.widgets.silx_plot import (
    PydidasPlot2DwithIntegrationRegions,
    PydidasPlotStack,
)


class QuickIntegrationFrameBuilder:
    """
    The QuickIntegrationFrameBuilder can be used to populate the QuickIntegrationFrame
    with widgets.
    """

    _frame = None

    @classmethod
    def _label_header(
        cls, parent_key: str = "config", size_offset: int = 1, **kwargs: dict
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
        return {
            "bold": True,
            "fontsize_offset": size_offset,
            "parent_widget": parent_key,
            **kwargs,
        }

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
            layout_kwargs=dict(
                contentsMargins=(10, 10, 10, 10),
                columnStretch=(1, 1),
                rowStretch=(0, 1),
            ),
            parent_widget=None,
        )
        cls._frame.add_any_widget(
            "input_plot",
            PydidasPlot2DwithIntegrationRegions(diffraction_exp=cls._frame._EXP),
            enabled=False,
            gridPos=(0, 1, 1, 1),
            minimumHeight=500,
            minimumWidth=500,
            parent_widget="tab_plot",
            sizePolicy=constants.POLICY_EXP_EXP,
        )
        cls._frame.add_any_widget(
            "input_beamcenter_points",
            PointsForBeamcenterWidget(cls._frame._widgets["input_plot"]),
            gridPos=(0, 0, 1, 1),
            parent_widget="tab_plot",
            visible=False,
        )
        cls._frame.create_any_widget(
            "result_plot",
            PydidasPlotStack,
            diffraction_exp=cls._frame._EXP,
            parent_widget=None,
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
        cls._frame.create_empty_widget(
            "config",
            font_metric_width_factor=constants.FONT_METRIC_PARAM_EDIT_WIDTH,
            init_layout=True,
            parent_widget=None,
            sizePolicy=constants.POLICY_FIX_EXP,
        )
        cls._frame.create_label(
            "label_title",
            "Quick integration\n",
            bold=True,
            fontsize_offset=4,
            font_metric_width_factor=constants.FONT_METRIC_PARAM_EDIT_WIDTH,
            parent_widget="config",
        )
        cls._frame.create_any_widget(
            "config_area",
            ScrollArea,
            gridPos=(1, 0, 1, 1),
            layout_kwargs={"alignment": None},
            sizePolicy=constants.POLICY_FIX_EXP,
            stretch=(1, 0),
            widget=cls._frame._widgets["config"],
        )
        cls._frame.create_label(None, "Input file:", **cls._label_header())
        cls._frame.add_any_widget(
            "file_selector",
            SelectImageFrameWidget(
                *cls._frame.params.values(),
                import_reference="QuickIntegrationFrame__image_import",
            ),
            parent_widget="config",
        )
        cls._frame.create_line(None, parent_widget="config")

    @classmethod
    def _create_exp_section_widgets(cls):
        """
        Create the widgets for the experimental section.
        """
        cls._frame.create_label(None, "Experiment description:", **cls._label_header())
        cls._frame.create_button(
            "copy_exp_context",
            "Copy expriment description from workflow setup",
            icon="pydidas::generic_copy",
            parent_widget="config",
        )
        cls._frame.create_button(
            "but_show_exp_section",
            "Show detailed experiment section",
            icon="qt-std::SP_TitleBarUnshadeButton",
            parent_widget="config",
            visible=True,
        )
        cls._frame.create_empty_widget(
            "exp_section", parent_widget="config", visible=False
        )
        cls._frame.create_button(
            "but_import_exp",
            "Import diffraction experimental parameters",
            icon="qt-std::SP_DialogOpenButton",
            parent_widget="exp_section",
        )
        cls._frame.create_label(
            None, "X-ray energy:", **cls._label_header("exp_section", 0)
        )
        cls._frame.create_param_widget(
            cls._frame.get_param("xray_energy"), parent_widget="exp_section"
        )
        cls._frame.create_param_widget(
            cls._frame.get_param("xray_wavelength"),
            parent_widget="exp_section",
        )
        cls._frame.create_label(
            None, "Detector:", **cls._label_header("exp_section", 0)
        )
        cls._frame.create_param_widget(
            cls._frame.get_param("detector_pxsize"),
            parent_widget="exp_section",
        )
        cls._frame.create_param_widget(
            cls._frame.get_param("detector_dist"), parent_widget="exp_section"
        )
        cls._frame.create_param_widget(
            cls._frame.get_param("detector_mask_file"),
            parent_widget="exp_section",
            linebreak=True,
        )
        cls._frame.create_spacer(None, fixedHeight=15, parent_widget="exp_section")
        cls._frame.create_button(
            "but_hide_exp_section",
            "Hide detailed experiment section",
            icon="qt-std::SP_TitleBarShadeButton",
            parent_widget="exp_section",
            visible=True,
        )
        cls._frame.create_param_widget(
            cls._frame.get_param("detector_model"),
            linebreak=True,
            parent_widget="config",
            visible=False,
        )
        cls._frame.create_spacer(None, fixedHeight=15, parent_widget="exp_section")

    @classmethod
    def _create_beamcenter_section_widgets(cls):
        """
        Create the widgets for the beamcenter section.
        """

        cls._frame.create_empty_widget(
            "beamcenter_section",
            parent_widget="config",
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
            parent_widget=cls._frame._widgets["beamcenter_section"],
        )
        cls._frame.create_button(
            "but_set_beamcenter",
            "Set selected point as beamcenter",
            parent_widget=cls._frame._widgets["beamcenter_section"],
            visible=False,
        )
        cls._frame.create_button(
            "but_fit_center_circle",
            "Fit beamcenter from points on circle",
            parent_widget=cls._frame._widgets["beamcenter_section"],
            visible=False,
        )
        cls._frame.create_button(
            "but_confirm_beamcenter",
            "Confirm beamcenter",
            icon="qt-std::SP_DialogApplyButton",
            parent_widget=cls._frame._widgets["beamcenter_section"],
            visible=False,
        )

        cls._frame.create_param_widget(
            cls._frame.get_param("beamcenter_x"),
            parent_widget="beamcenter_section",
        )
        cls._frame.create_param_widget(
            cls._frame.get_param("beamcenter_y"), parent_widget="beamcenter_section"
        )

    @classmethod
    def _create_integration_section_widgets(cls):
        """
        Create the widgets for the integration section.
        """
        cls._frame.create_empty_widget(
            "integration_header",
            parent_widget="config",
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
            parent_widget="config",
            visible=False,
        )
        cls._frame.create_button(
            "but_show_integration_section",
            "Show integration ROI section",
            icon="qt-std::SP_TitleBarUnshadeButton",
            parent_widget="config",
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
                plugin=cls._frame._plugins["generic"],
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
            icon="qt-std::SP_TitleBarShadeButton",
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
            parent_widget="config",
            visible=False,
        )

        cls._frame.create_line(
            None, parent_widget=cls._frame._widgets["run_integration"]
        )
        cls._frame.create_label(
            None, "Run integration", **cls._label_header("run_integration", 1)
        )
        cls._frame.create_param_widget(
            cls._frame.get_param("integration_direction"),
            parent_widget=cls._frame._widgets["run_integration"],
        )
        cls._frame.create_param_widget(
            cls._frame.get_param("azi_npoint"),
            parent_widget=cls._frame._widgets["run_integration"],
        )
        cls._frame.create_param_widget(
            cls._frame.get_param("rad_npoint"),
            parent_widget=cls._frame._widgets["run_integration"],
            visible=False,
        )
        cls._frame.create_button(
            "but_run_integration",
            "Run pyFAI integration",
            parent_widget=cls._frame._widgets["run_integration"],
        )
        cls._frame.create_spacer(None, fixedHeight=10)
