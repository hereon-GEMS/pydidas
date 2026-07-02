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
The workflow_results module includes the ProcessingResults and WorkflowResults
singleton class for storing and accessing the composite results of the processing.
"""

__author__ = "Malte Storm"
__copyright__ = "Copyright 2026, Helmholtz-Zentrum Hereon"
__license__ = "GPL-3.0-only"
__maintainer__ = "Malte Storm"
__status__ = "Production"
__all__ = ["PluginResultInfo"]


from dataclasses import dataclass, field
from typing import Any


@dataclass
class PluginResultInfo:
    """
    A class for handling information of node results.

    In addition to the usual dataclass attributes, derived attributes
    for the squeezed result shape is implemented.
    """

    label: str = ""
    node_id: int | None = None
    plugin_name: str = ""
    result_title: str = ""
    result_metadata: dict[str, Any] = field(default_factory=dict)
    shape: tuple[int, ...] = field(default_factory=tuple)

    @property
    def squeezed_shape(self) -> tuple[int, ...]:
        """
        Get the squeezed shape of the result.

        Returns
        -------
        tuple[int, ...]
            The squeezed shape of the result.
        """
        return tuple(_n for _n in self.shape if _n > 1)
