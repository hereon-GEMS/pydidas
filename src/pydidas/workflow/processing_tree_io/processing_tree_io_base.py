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
Module with the ProcessingTreeIoBase class which exporters/importerss should
inherit from.
"""

__author__ = "Malte Storm"
__copyright__ = "Copyright 2023 - 2026, Helmholtz-Zentrum Hereon"
__license__ = "GPL-3.0-only"
__maintainer__ = "Malte Storm"
__status__ = "Production"
__all__ = ["ProcessingTreeIoBase"]


from pathlib import Path
from typing import TYPE_CHECKING, Any, ClassVar

from pydidas.core.io_registry import GenericIoBase
from pydidas.workflow.processing_tree_io.processing_tree_io_meta import (
    ProcessingTreeIoMeta,
)


if TYPE_CHECKING:
    from pydidas.workflow.processing_tree import ProcessingTree


class ProcessingTreeIoBase(GenericIoBase, metaclass=ProcessingTreeIoMeta):
    """
    Base class for WorkflowTree exporters.

    This class defines the format_name and extensions attributes for all
    ProcessingTreeIo classes.
    """

    extensions: ClassVar[list[str]] = []
    format_name: ClassVar[str] = "unknown"

    @staticmethod
    def export_to_file(  # type: ignore[override]
        filename: Path | str, tree: "ProcessingTree", **kwargs: Any
    ) -> None:  # type: ignore[override]
        """
        Write the content to a file.

        This method needs to be implemented by the concrete subclass.

        Parameters
        ----------
        filename : Path or str
            The filename of the file to be written.
        tree : ProcessingTree
            The workflow tree instance.
        **kwargs : Any
            Additional keyword arguments.
        """
        raise NotImplementedError

    @staticmethod
    def import_from_file(  # type: ignore[override]
        filename: Path | str, **kwargs: Any
    ) -> "ProcessingTree":
        """
        Restore the content from a file.

        This method needs to be implemented by the concrete subclass.

        Parameters
        ----------
        filename : Path or str
            The filename of the file to be read.
        **kwargs : Any
            Additional keyword arguments.

        Returns
        -------
        ProcessingTree
            The restored ProcessingTree.
        """
        raise NotImplementedError
