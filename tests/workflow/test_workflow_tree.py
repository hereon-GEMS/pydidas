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

from pydidas.core import Singleton
from pydidas.workflow import ProcessingTree, WorkflowTree


def test_init():
    tree = WorkflowTree()
    assert isinstance(tree, ProcessingTree)
    assert isinstance(tree, WorkflowTree)
    assert Singleton._instances[WorkflowTree] is tree


def test_hash():
    tree = WorkflowTree()
    assert isinstance(hash(tree), int)


def test_copy():
    tree = WorkflowTree()
    tree_copy = tree.copy()
    assert isinstance(tree_copy, ProcessingTree)
    assert not isinstance(tree_copy, WorkflowTree)
    assert tree_copy is not tree


def test__repeated_calls():
    tree = WorkflowTree()
    tree2 = WorkflowTree()
    assert tree is tree2
    assert id(tree) == id(tree2)


if __name__ == "__main__":
    pytest.main([__file__])
