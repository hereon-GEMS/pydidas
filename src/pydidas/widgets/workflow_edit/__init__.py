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
Package with widgets required for editing the workflow and selecting plugins.
"""

__author__ = "Malte Storm"
__copyright__ = "Copyright 2023 - 2025, Helmholtz-Zentrum Hereon"
__license__ = "GPL-3.0-only"
__maintainer__ = "Malte Storm"
__status__ = "Production"


from . import plugin_collection_browser
from .plugin_collection_browser import *
from .plugin_in_workflow_box import *
from .select_new_plugin_widget import *
from .workflow_tree_canvas import *


__all__ = (
    plugin_collection_browser.__all__
    + plugin_in_workflow_box.__all__
    + select_new_plugin_widget.__all__
    + workflow_tree_canvas.__all__
)

# Clean up the namespace:
del (
    plugin_collection_browser,
    plugin_in_workflow_box,
    select_new_plugin_widget,
    workflow_tree_canvas,
)
