# This file is part of pydidas.
#
# pydidas is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
#
# Pydidas is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE. See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with Pydidas. If not, see <http://www.gnu.org/licenses/>.
"""
Module with the WorkflowTreeIoBase class which exporters/importerss should
inherit from.
"""

__author__ = "Malte Storm"
__copyright__ = "Copyright 2021, Malte Storm, Helmholtz-Zentrum Hereon"
__license__ = "GPL-3.0"
__version__ = "0.1.0"
__maintainer__ = "Malte Storm"
__status__ = "Development"
__all__ = ['WorkflowTreeIoBase']

from ...core.io_registry import GenericIoBase
from .workflow_tree_io_meta import WorkflowTreeIoMeta


class WorkflowTreeIoBase(GenericIoBase,
                         metaclass=WorkflowTreeIoMeta):
    """
    Base class for WorkflowTree exporters.
    """
    extensions = []
    format_name = 'unknown'
