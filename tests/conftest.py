# This file is part of pydidas.
#
# Copyright 2025 - 2026, Helmholtz-Zentrum Hereon
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
The conftest module for pytest fixtures used across multiple test modules.
"""

__author__ = "Malte Storm"
__copyright__ = "Copyright 2025 - 2026, Helmholtz-Zentrum Hereon"
__license__ = "GPL-3.0-only"
__maintainer__ = "Malte Storm"
__status__ = "Production"
__all__ = []


import random
import shutil
import tempfile
from pathlib import Path

import numpy as np
import pytest

from pydidas.contexts import Scan
from pydidas.contexts.diff_exp.diff_exp import DiffractionExperiment
from pydidas.core.utils import get_random_string
from pydidas.plugins import PluginCollection
from pydidas.workflow import ProcessingTree
from pydidas_qtcore import PydidasQApplication


PLUGIN_COLL = PluginCollection()
PLUGIN_COLL.verify_is_initialized()


@pytest.fixture(scope="session", autouse=True)
def temp_path():
    """
    The temporary path fixture for tests needing a temp directory.

    This fixture creates a single temporary directory for the entire test session.
    """
    _path = Path(tempfile.mkdtemp())
    yield _path
    shutil.rmtree(_path)


@pytest.fixture
def empty_temp_path():
    """
    The temporary path fixture for tests needing an empty temp directory.

    This fixture creates a new temporary directory for each test function.
    """
    _path = Path(tempfile.mkdtemp())
    yield _path
    shutil.rmtree(_path)


@pytest.fixture(scope="session")
def qapp_cls():
    return PydidasQApplication


@pytest.fixture
def random_scan() -> Scan:
    """Create a Scan with random parameters."""
    _scan = Scan()
    _scan.set_param_value("scan_dim", 3)
    for d in range(3):
        _scan.set_param_value(f"scan_dim{d}_n_points", random.choice([3, 5, 7, 8]))
        _scan.set_param_value(f"scan_dim{d}_delta", random.choice([0.1, 0.5, 1, 1.5]))
        _scan.set_param_value(f"scan_dim{d}_offset", random.choice([-0.1, 0.5, 1]))
        _scan.set_param_value(f"scan_dim{d}_label", get_random_string(12))
        _scan.set_param_value(f"scan_dim{d}_unit", get_random_string(3))
    return _scan


@pytest.fixture
def random_diff_exp() -> DiffractionExperiment:
    """Create a DiffractionExperiment with random parameters."""
    _exp = DiffractionExperiment()
    _exp.set_param_value("xray_wavelength", random.choice([0.1, 0.5, 1, 1.5]))
    _exp.set_param_value("detector_name", get_random_string(6))
    _exp.set_param_value("detector_npixx", random.randint(512, 1024))
    _exp.set_param_value("detector_npixy", random.randint(512, 1024))
    _pxsize = np.round(50 + 200 * random.random(), 3)
    _exp.set_param_value("detector_pxsizex", _pxsize)
    _exp.set_param_value("detector_pxsizey", _pxsize)
    _exp.set_param_value("detector_dist", 0.1 + 5 * random.random())
    _exp.set_param_value("detector_poni1", -0.5 + random.random())
    _exp.set_param_value("detector_poni2", -0.5 + random.random())
    _exp.set_param_value("detector_rot1", 0.1 * (-0.5 + random.random()))
    _exp.set_param_value("detector_rot2", 0.1 * (-0.5 + random.random()))
    _exp.set_param_value("detector_rot3", 0.1 * (-0.5 + random.random()))
    return _exp


@pytest.fixture
def test_tree() -> ProcessingTree:
    """Fixture to create a test ProcessingTree."""
    _tree = ProcessingTree()
    for _class_name in [
        "FrameLoader",
        "PyFAIazimuthalIntegration",
        "Crop1dData",
        "FitSinglePeak",
    ]:
        _plugin_class = PLUGIN_COLL.get_plugin_by_name(_class_name)
        _tree.create_and_add_node(_plugin_class())
    _plugin_class = PLUGIN_COLL.get_plugin_by_name("Sum2dData")
    _tree.create_and_add_node(_plugin_class(), parent=_tree.nodes[0])
    return _tree
