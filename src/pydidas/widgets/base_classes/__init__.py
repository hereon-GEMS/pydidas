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
The base_reimplementations subpackage includes basic QtWidget
re-implementations with extended generic functionality that
 are used throughout the pydidas package.

These widgets are designed to provide scaling based on the system
font and font size to allow a scalability independent of the
monitor resolution.
"""

__author__ = "Malte Storm"
__copyright__ = "Copyright 2026, Helmholtz-Zentrum Hereon"
__license__ = "GPL-3.0-only"
__maintainer__ = "Malte Storm"
__status__ = "Production"


from .base_frame import BaseFrame
from .empty_widget import EmptyWidget
from .parameter_widget_mixin import ParameterWidgetMixIn
from .pydidas_scroll_area import PydidasScrollArea
from .pydidas_widget_mixin import PydidasWidgetMixIn
from .pydidas_window import PydidasWindow
from .widget_factory_mixin import WidgetFactoryMixIn
from .widget_with_parameters import WidgetWithParameters


__all__ = [
    "BaseFrame",
    "EmptyWidget",
    "ParameterWidgetMixIn",
    "PydidasScrollArea",
    "PydidasWidgetMixIn",
    "PydidasWindow",
    "WidgetFactoryMixIn",
    "WidgetWithParameters",
]
