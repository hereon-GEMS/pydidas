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
The extended_widgets subpackage includes basic widgets which have
been extended to provide additional functionality and/or a more
consistent look and feel.

These widgets are designed to provide scaling based on the system
font and font size to allow a scalability independent of the
monitor resolution.
"""

__author__ = "Malte Storm"
__copyright__ = "Copyright 2026, Helmholtz-Zentrum Hereon"
__license__ = "GPL-3.0-only"
__maintainer__ = "Malte Storm"
__status__ = "Production"


from .base_frame_with_app import BaseFrameWithApp
from .line_edit_with_icon import LineEditWithIcon
from .parameter_edit_canvas import ParameterEditCanvas
from .table_with_node_labels import TableWithNodeLabels
from .toggle_options_button import ToggleOptionsButton


__all__ = [
    "BaseFrameWithApp",
    "LineEditWithIcon",
    "ParameterEditCanvas",
    "TableWithNodeLabels",
    "ToggleOptionsButton",
]
