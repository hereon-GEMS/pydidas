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
Module with the ProcessingTreeIoBase class which exporters/importerss should
inherit from.
"""

__author__ = "Malte Storm"
__copyright__ = "Copyright 2023 - 2025, Helmholtz-Zentrum Hereon"
__license__ = "GPL-3.0-only"
__maintainer__ = "Malte Storm"
__status__ = "Production"
__all__ = ["ProcessingTreeIoBase"]


from pydidas.core.io_registry import GenericIoBase
from pydidas.workflow.processing_tree_io.processing_tree_io_meta import (
    ProcessingTreeIoMeta,
)


class ProcessingTreeIoBase(GenericIoBase, metaclass=ProcessingTreeIoMeta):
    """
    Base class for WorkflowTree exporters.

    This class defines the format_name and extensions attributes for all
    ProcessingTreeIo classes.
    """

    extensions = []
    format_name = "unknown"
