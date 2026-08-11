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

"""Unit tests for pydidas modules."""

__author__ = "Malte Storm"
__copyright__ = "Copyright 2023 - 2026, Helmholtz-Zentrum Hereon"
__license__ = "GPL-3.0-only"
__maintainer__ = "Malte Storm"
__status__ = "Production"


import pytest

from pydidas.workflow.processing_tree_io import ProcessingTreeIoBase


def test_export_to_file() -> None:
    with pytest.raises(NotImplementedError):
        ProcessingTreeIoBase.export_to_file("something", tree=None)  # type: ignore[arg-type]


def test_import_from_file() -> None:
    with pytest.raises(NotImplementedError):
        ProcessingTreeIoBase.import_from_file("something")


if __name__ == "__main__":
    pytest.main([__file__])
