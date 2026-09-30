# This file is part of pydidas.
#
# Copyright 2023 - 2026, Helmholtz-Zentrum Hereon
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
Module with the ParameterEditCanvas class for handling Parameter widgets.
"""

__author__ = "Malte Storm"
__copyright__ = "Copyright 2023 - 2026, Helmholtz-Zentrum Hereon"
__license__ = "GPL-3.0-only"
__maintainer__ = "Malte Storm"
__status__ = "Production"
__all__ = ["ParameterEditCanvas"]


from typing import Any

from pydidas.core.constants import POLICY_MIN_MIN
from pydidas.widgets.base_classes import EmptyWidget, ParameterWidgetMixIn


class ParameterEditCanvas(ParameterWidgetMixIn, EmptyWidget):
    """
    The ParameterEditCanvas is widget for handling Parameter edit widgets.

    Parameters
    ----------
    **kwargs : Any
        Additional keyword arguments
    """

    def __init__(self, **kwargs: Any):
        EmptyWidget.__init__(self, **kwargs)
        ParameterWidgetMixIn.__init__(self)
        self.layout().setContentsMargins(0, 0, 0, 0)
        self.setSizePolicy(*POLICY_MIN_MIN)
