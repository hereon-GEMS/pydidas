# This file is part of pydidas.
#
# Copyright 2025, Helmholtz-Zentrum Hereon
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
Module with the FioMcaLineScanSeriesLoader Plugin which can be used to load
MCA spectral data
"""

__author__ = "Malte Storm"
__copyright__ = "Copyright 2025, Helmholtz-Zentrum Hereon"
__license__ = "GPL-3.0-only"
__maintainer__ = "Malte Storm"
__status__ = "Production"
__all__ = ["FioMcaLoader"]


from pathlib import Path
from typing import Any

from pydidas.contexts import ScanContext
from pydidas.core import (
    Dataset,
    get_generic_param_collection,
)
from pydidas.core.utils import fio_utils as fio
from pydidas.plugins import InputPlugin
from pydidas.widgets.plugin_config_widgets.plugin_config_widget_with_custom_xscale import (
    PluginConfigWidgetWithCustomXscale,
)


SCAN = ScanContext()


class FioMcaLoader(InputPlugin):
    """
    Load 1d data from a series of .fio files with MCA data (in a single directory).

    This plugin is designed to allow loading .fio files written by Sardana which
    include a single row of data with the MCA spectrum.

    Please give the full path to the folder in the Scan settings and use
    a single hash key (#) in the filename pattern to indicate the index of the
    scan point (which do not have leading zeros).

    Please note that each instrument might have different data defined in the
    fio file format and not all data might be readable.

    Parameters
    ----------
    use_custom_xscale : bool, optional
        Keyword to toggle an absolute energy scale for the channels. If False,
        pydidas will simply use the channel number. The default is False.
    x0_offset : float, optional
        The offset for channel zero, if the absolute energy scale is used.
        This value must be given in eV. The default is 0.
    x_delta : float, optional
        The width of each energy channel. This value is given in units and only
        used when the absolute x-scale is enabled. The default is 1.
    x_label : str, optional
        The label for the x-axis of the plot. This is only used when the
        absolute x-scale is enabled. The default is "Energy".
    x_unit : str, optional
        The unit for the x-axis of the plot. This is only used when the
        absolute x-scale is enabled. The default is "eV".
    """

    plugin_name = "Fio MCA loader"
    base_output_data_dim = 1
    default_params = get_generic_param_collection(
        "use_custom_xscale",
        "x0_offset",
        "x_delta",
        "x_label",
        "x_unit",
    )
    has_unique_parameter_config_widget = True

    def __init__(self, *args: tuple, **kwargs: Any):
        super().__init__(*args, **kwargs)
        self._config.update({"header_lines": 0})

    def pre_execute(self):
        """
        Prepare loading spectra from a file series.
        """
        _index = 0 if Path(self.get_filename(0)).is_file() else 1
        InputPlugin.pre_execute(self)
        fio.update_config_from_fio_file(
            self.get_filename(_index), self._config, self.params
        )
        self._config["roi"] = self._get_own_roi()

    def get_frame(self, index: int, **kwargs: Any) -> tuple[Dataset, dict]:
        """
        Get the frame for the given index.

        Parameters
        ----------
        index : int
            The index of the scan point.
        **kwargs : Any
            Keyword arguments for loading frames.

        Returns
        -------
        dataset : Dataset
            The loaded dataset.
        kwargs : Any
            The updated kwargs.
        """
        _dataset = fio.load_fio_spectrum(self.get_filename(index), self._config)
        return _dataset, kwargs

    def get_parameter_config_widget(self):
        """Get the parameter config widget for the plugin."""
        return PluginConfigWidgetWithCustomXscale
