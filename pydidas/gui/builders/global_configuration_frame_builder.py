# This file is part of pydidas.
#
# pydidas is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
#
# Pydidas is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE. See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with Pydidas. If not, see <http://www.gnu.org/licenses/>.

"""
Module with the GlobalConfigurationFrameBuilder class which is used
to populate the GlobalConfigurationFrame with widgets.
"""

__author__ = "Malte Storm"
__copyright__ = "Copyright 2021-2022, Malte Storm, Helmholtz-Zentrum Hereon"
__license__ = "GPL-3.0"
__maintainer__ = "Malte Storm"
__status__ = "Development"
__all__ = ["GlobalConfigurationFrameBuilder"]

from qtpy import QtCore

from ...core import get_generic_param_collection
from ...core.constants import CONFIG_WIDGET_WIDTH, QSETTINGS_GLOBAL_KEYS
from ...widgets import BaseFrame


class GlobalConfigurationFrameBuilder(BaseFrame):
    """
    Create all widgets and initialize their state.

    Parameters
    ----------
    self : pydidas.gui.GlobalConfigurationFrame
        The GlobalConfigurationFrame instance.
    """

    TEXT_WIDTH = 180
    default_params = get_generic_param_collection(*QSETTINGS_GLOBAL_KEYS)

    def __init__(self, parent=None, **kwargs):
        BaseFrame.__init__(self, parent, **kwargs)
        self.set_default_params()

    def build_frame(self):
        """
        Populate the GlobalConfigurationFrame with widgets.
        """
        _twoline_options = dict(
            width_text=self.TEXT_WIDTH,
            linebreak=True,
            width_io=CONFIG_WIDGET_WIDTH - 20,
            width_total=CONFIG_WIDGET_WIDTH,
            halign_text=QtCore.Qt.AlignLeft,
            valign_text=QtCore.Qt.AlignBottom,
            width_unit=0,
        )
        _options = dict(
            width_text=self.TEXT_WIDTH,
            width_io=80,
            width_unit=40,
            width_total=CONFIG_WIDGET_WIDTH,
        )
        _section_options = dict(fontsize=13, bold=True, gridPos=(-1, 0, 1, 1))

        self.create_label(
            "title", "Global settings\n", fontsize=14, bold=True, gridPos=(0, 0, 1, 1)
        )
        self.create_button(
            "but_reset",
            "Restore defaults",
            icon=self.style().standardIcon(59),
            gridPos=(-1, 0, 1, 1),
            alignment=None,
        )
        self.create_label(
            "section_multiprocessing", "Multiprocessing settings", **_section_options
        )
        self.create_param_widget(self.get_param("mp_n_workers"), **_options)
        self.create_param_widget(self.get_param("shared_buffer_size"), **_options)
        self.create_param_widget(self.get_param("shared_buffer_max_n"), **_options)
        self.create_spacer("spacer_1")

        self.create_label("section_detector", "Detector settings", **_section_options)
        self.create_param_widget(self.get_param("det_mask"), **_twoline_options)
        self.create_param_widget(self.get_param("det_mask_val"), **_options)
        self.create_spacer("spacer_2")

        self.create_label(
            "section_mosaic", "Composite creator settings", **_section_options
        )
        self.create_param_widget(self.get_param("mosaic_border_width"), **_options)
        self.create_param_widget(self.get_param("mosaic_border_value"), **_options)
        self.create_param_widget(self.get_param("mosaic_max_size"), **_options)
        self.create_spacer("spacer_3")

        self.create_label("section_plotting", "Display settings", **_section_options)
        self.create_param_widget(self.get_param("plot_update_time"), **_options)
        self.create_param_widget(
            self.get_param("histogram_outlier_fraction"), **_options
        )
        self.create_spacer("spacer_4")

        self.create_label("section_plugins", "Plugins", **_section_options)
        self.create_param_widget(self.get_param("plugin_fit_std_threshold"), **_options)
        self.create_param_widget(self.get_param("plugin_path"), **_twoline_options)
        self.create_button("but_plugins", "Update plugin collection")
