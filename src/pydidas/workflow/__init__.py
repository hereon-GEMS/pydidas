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
The workflow package defines classes to create and manage the workflow and
to import / export.
"""

__author__ = "Malte Storm"
__copyright__ = "Copyright 2023 - 2025, Helmholtz-Zentrum Hereon"
__license__ = "GPL-3.0-only"
__maintainer__ = "Malte Storm"
__status__ = "Production"


from . import result_io, processing_tree_io  # noqa : I001
from .generic_node import *
from .generic_tree import *
from .plugin_position_node import *
from .processing_results import *
from .processing_tree import *
from .workflow_node import *
from .workflow_results import *
from .workflow_results_selector import *
from .workflow_tree import *


__all__ = ["result_io", "processing_tree_io"] + (
    generic_node.__all__
    + generic_tree.__all__
    + plugin_position_node.__all__
    + processing_results.__all__
    + processing_tree.__all__
    + workflow_node.__all__
    + workflow_results.__all__
    + workflow_results_selector.__all__
    + workflow_tree.__all__
)

del (
    generic_node,
    generic_tree,
    plugin_position_node,
    processing_results,
    processing_tree,
    workflow_node,
    workflow_results,
    workflow_results_selector,
    workflow_tree,
)
