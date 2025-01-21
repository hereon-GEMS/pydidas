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
Package with modified widgets required for creating the pydidas graphical user
interface.
"""

__author__ = "Malte Storm"
__copyright__ = "Copyright 2023 - 2025, Helmholtz-Zentrum Hereon"
__license__ = "GPL-3.0-only"
__maintainer__ = "Malte Storm"
__status__ = "Production"


from .font_scaling_toolbar import *
from .pydidas_frame_stack import *
from .pydidas_status_widget import *
from .pydidas_window import *
from pydidas.widgets.framework.base_frame import *
from pydidas.widgets.framework.base_frame_with_app import *


__all__ = (
    base_frame.__all__
    + base_frame_with_app.__all__
    + font_scaling_toolbar.__all__
    + pydidas_status_widget.__all__
    + pydidas_frame_stack.__all__
    + pydidas_window.__all__
)

del (
    base_frame,
    base_frame_with_app,
    font_scaling_toolbar,
    pydidas_status_widget,
    pydidas_frame_stack,
    pydidas_window,
)
