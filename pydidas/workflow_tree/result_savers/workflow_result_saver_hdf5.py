# This file is part of pydidas.

# pydidas is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.

# Pydidas is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE. See the
# GNU General Public License for more details.

# You should have received a copy of the GNU General Public License
# along with Pydidas. If not, see <http://www.gnu.org/licenses/>.
"""
Module with the WorkflowTreeExporterBase class which exporters should inherit
from.
"""

__author__      = "Malte Storm"
__copyright__   = "Copyright 2021, Malte Storm, Helmholtz-Zentrum Hereon"
__license__ = "GPL-3.0"
__version__ = "0.0.1"
__maintainer__ = "Malte Storm"
__status__ = "Development"
__all__ = ['WorkflowResultSaverHdf5']



from .workflow_result_saver_base import WorkflowResultSaverBase


class WorkflowResultSaverHdf5(WorkflowResultSaverBase):
    """
    Base class for WorkflowTree exporters.
    """
    extensions = ['HDF5']
    format_name = 'HDF5'

    @classmethod
    def export_to_file(cls, filename, tree, **kwargs):
        """
        Write the content to a file.

        This method needs to be implemented by the concrete subclass.

        Parameters
        ----------
        filename : str
            The filename of the file to be written.
        content : type
            The content in any format.
        """

