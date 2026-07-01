# This file is part of pydidas.
#
# Copyright 2023 - 2026, Helmholtz-Zentrum Hereon
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
Module with the ProcessingTreeIoMeta class which is used for creating
exporter/importer classes and registering them.
"""

__author__ = "Malte Storm"
__copyright__ = "Copyright 2023 - 2026, Helmholtz-Zentrum Hereon"
__license__ = "GPL-3.0-only"
__maintainer__ = "Malte Storm"
__status__ = "Production"
__all__ = ["ProcessingTreeIoMeta"]


from pathlib import Path
from typing import TYPE_CHECKING, Any, ClassVar

from pydidas.core.io_registry import GenericIoMeta
from pydidas.core.utils import get_extension


if TYPE_CHECKING:
    from pydidas.workflow.processing_tree import ProcessingTree


class ProcessingTreeIoMeta(GenericIoMeta):
    """
    Metaclass for WorkflowTree exporters and importers which holds the
    registry with all associated file extensions for exporting WorkflowTrees.
    """

    registry: ClassVar[dict[str, type["ProcessingTreeIoMeta"]]] = {}

    @classmethod
    def export_to_file(  # type: ignore[override]
        cls, filename: Path | str, tree: "ProcessingTree", **kwargs: Any
    ) -> None:
        """
        Call the export_to_file method associated with extension of the filename.

        Parameters
        ----------
        filename : Path or str
            The full filename and path.
        tree : ProcessingTree
            The instance of the ProcessingTree.
        **kwargs : Any
            Any kwargs which should be passed to the underlying exporter.
        """
        _extension = get_extension(filename)
        cls.verify_extension_is_registered(_extension)
        _io_class = cls.registry[_extension]
        _io_class.export_to_file(filename, tree, **kwargs)

    @classmethod
    def import_from_file(  # type: ignore[override]
        cls, filename: Path | str
    ) -> "ProcessingTree":
        """
        Call the concrete import_from_file method in the subclass registered
        to the extension of the filename.

        Parameters
        ----------
        filename : Path or str
            The full filename and path.

        Returns
        -------
        ProcessingTree
            The new ProcessingTree instance.
        """
        _extension = get_extension(filename)
        cls.verify_extension_is_registered(_extension)
        _io_class = cls.registry[_extension]
        _tree = _io_class.import_from_file(filename)
        return _tree
