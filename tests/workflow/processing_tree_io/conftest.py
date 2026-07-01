# This file is part of pydidas.
#
# Copyright 2026, Helmholtz-Zentrum Hereon
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
__copyright__ = "Copyright 2026, Helmholtz-Zentrum Hereon"
__license__ = "GPL-3.0-only"
__maintainer__ = "Malte Storm"
__status__ = "Production"


import pytest

from pydidas.plugins import PluginCollection
from pydidas.workflow import ProcessingTree


PLUGIN_COLL = PluginCollection()


@pytest.fixture
def test_tree() -> ProcessingTree:
    """Fixture to create a test ProcessingTree."""
    _tree = ProcessingTree()
    for _class_name in ["FrameLoader", "PyFAIazimuthalIntegration", "MaskImage"]:
        _plugin_class = PLUGIN_COLL.get_plugin_by_name(_class_name)
        _tree.create_and_add_node(_plugin_class())
    _plugin_class = PLUGIN_COLL.get_plugin_by_name("Sum2dData")
    _tree.create_and_add_node(_plugin_class(), parent=_tree.nodes[0])
    return _tree
