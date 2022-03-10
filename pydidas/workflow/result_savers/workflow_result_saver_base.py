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
__copyright__ = "Copyright 2021-2022, Malte Storm, Helmholtz-Zentrum Hereon"
__license__ = "GPL-3.0"
__version__ = "0.1.1"
__maintainer__ = "Malte Storm"
__status__ = "Development"
__all__ = ['WorkflowResultSaverBase']

from ...core.io_registry import GenericIoBase
from .workflow_result_saver_meta import WorkflowResultSaverMeta


class WorkflowResultSaverBase(GenericIoBase,
                              metaclass=WorkflowResultSaverMeta):
    """
    Base class for WorkflowTree exporters.
    """
    extensions = []
    default_extension = ''
    format_name = 'unknown'
    scan_title = ''

    @classmethod
    def prepare_files_and_directories(cls, save_dir, shapes, labels):
        """
        Prepare the required files and directories to write the data to disk.

        Parameters
        ----------
        save_dir : Union[pathlib.Path, str]
            The full path for the data to be saved.
        shapes : dict
            The shapes of the results in form of a dictionary with nodeID
            keys and result values.
        labels : dict
            The labels of the results in form of a dictionary with nodeID
            keys and label values.
        """

    @classmethod
    def get_filenames_from_labels(cls, labels):
        """
        Get the directory names from labels.

        This method will assemble directory names which include the node ID,
        the Plugin label and the format name. Any spaces or escape characters
        will be converted to underscores.

        Parameters
        ----------
        labels : dict
            The labels of the results in form of a dictionary with nodeID
            keys and label values.
        Returns
        -------
        names : dict
            The dictionary of possible directory names.
        """
        _names = {}
        for _id, _label in labels.items():
            if _label is None or _label == '':
                _names[_id] = (f'node_{_id:02d}.{cls.default_extension}')
            else:
                for _key in [' ', '\n', '\t', '\r']:
                    _label = _label.replace(_key, '_')
                _names[_id] = (f'node_{_id:02d}_{_label}.'
                               f'{cls.default_extension}').replace('__', '_')
        return _names

    @classmethod
    def export_full_data_to_file(cls, full_data):
        """
        Export the full dataset to disk,

        Parameters
        ----------
        full_data : dict
            The result dictionary with nodeID keys and result values.
        """

    @classmethod
    def export_frame_to_file(cls, index, frame_result_dict, **kwargs):
        """
        Export the results of one frame and store them on disk.

        Parameters
        ----------
        index : int
            The frame index.
        frame_result_dict : dict
            The result dictionary with nodeID keys and result values.
        kwargs : dict
            Any kwargs which should be passed to the udnerlying exporter.
        """

    @classmethod
    def update_frame_metadata(cls, metadata):
        """
        Update the metadata of the individual frame.

        Parameters
        ----------
        metadata : dict
            The metadata dictionary with results of one frame for each node.
        """
