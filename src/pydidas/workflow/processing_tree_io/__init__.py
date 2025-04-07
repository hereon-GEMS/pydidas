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
The pydidas.workflow.processing_tree_io package includes importers/exporters for the
WorkflowTree in different formats as well as a registry metaclass to handle actual
imports/exports.
"""

__author__ = "Malte Storm"
__copyright__ = "Copyright 2023 - 2025, Helmholtz-Zentrum Hereon"
__license__ = "GPL-3.0-only"
__maintainer__ = "Malte Storm"
__status__ = "Production"


from . import processing_tree_io_hdf5, processing_tree_io_yaml
from .processing_tree_io_base import *
from .processing_tree_io_meta import *


__all__ = processing_tree_io_meta.__all__ + processing_tree_io_base.__all__

del (
    processing_tree_io_base,
    processing_tree_io_meta,
    processing_tree_io_yaml,
    processing_tree_io_hdf5,
)
