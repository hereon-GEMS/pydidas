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


import gc
import random
import shutil
import tempfile
from pathlib import Path

import numpy as np
import pytest
import qtpy

from pydidas import unittest_objects
from pydidas.contexts import Scan
from pydidas.contexts.diff_exp.diff_exp import DiffractionExperiment
from pydidas.core.utils import get_random_string
from pydidas.plugins import PluginCollection
from pydidas.workflow import ProcessingTree
from pydidas_qtcore import PydidasQApplication


if qtpy.API_NAME in ("PyQt5", "PyQt6"):

    @pytest.fixture(scope="session", autouse=True)
    def _disable_cyclic_gc_for_qt_safety():
        """
        Guard against unsafe cyclic-garbage-collector-triggered Qt destruction.

        PyQt5/PySide QObjects (widgets, signals, ...) must only ever be destroyed
        via explicit `deleteLater()`/`close()` or plain refcounting, never via
        Python's cyclic garbage collector. Across the (large) GUI test suite, some
        widget fixtures leave widgets in reference cycles (e.g. via
        ``signal.connect(self.some_method)`` self-connections, or signal spies
        holding references), so plain refcounting never frees them. Left to
        accumulate, a cyclic collection pass eventually frees a whole batch of
        such long-lived QObjects together, at an unpredictable point during an
        unrelated test's setup or teardown. Finalizing multiple QObjects that way
        is not safe with either binding and reliably causes a segmentation fault
        when running the full GUI test suite (though not when running individual
        test files in isolation, since not enough cyclic garbage accumulates to
        trigger a collection).



        The two supported Qt bindings differ in a critical way that requires two
        different mitigation strategies:

        - With **PyQt5** (sip), simply disabling the cyclic collector for the
          whole session (``gc.disable()``) is sufficient and safe: nothing in
          PyQt5/sip forces an explicit collection, so with automatic collection
          disabled, cyclic garbage is just never reclaimed within the
          (short-lived) test process, and all QObjects are still freed normally
          via refcounting when possible.
        - With **PySide6** (shiboken), ``gc.disable()`` alone does *not* help:
          shiboken's binding manager explicitly forces a Python garbage
          collection pass (bypassing the ``gc.enabled`` flag, which only gates
          *automatic* triggering) at its own, internal, wrapper-object-count
          based thresholds, in order to resolve reference cycles between Python
          QObject wrappers and their C++ parent/child hierarchy. This was
          confirmed empirically: with ``gc.disable()`` active for the whole
          session, the full GUI suite still crashed with "Garbage-collecting"
          showing in the fault handler's traceback. Since these forced passes
          cannot be prevented, the mitigation instead keeps each pass small and
          safe by proactively running ``gc.collect()`` after *every* test (once
          that test's own widgets have already been explicitly closed and
          deleted via the normal Qt-safe path), so there is essentially always
          only a small, test-local amount of cyclic garbage for any collection
          pass (ours or shiboken's own forced one) to reclaim, rather than a
          large, cross-test backlog accumulated over the whole session. Note
          that proactively calling ``gc.collect()`` after every test is *not*
          safe to do for PyQt5 (verified empirically to reintroduce the
          segfault), since PyQt5/sip's unsafety is not about batch size, but
          about cyclic-GC-triggered destruction happening at all.

        Fixing the individual leaking fixtures (as already done for several
        files) is still the preferred long-term remedy to reduce how much cyclic
        garbage accumulates in the first place; this fixture remains as a
        backstop for leaks not yet found.
        """
        gc.disable()
        yield
        gc.enable()


if qtpy.API_NAME in ("PySide6", "PySide2"):

    @pytest.fixture(autouse=True)
    def _collect_garbage_after_each_test_for_shiboken_safety(request):
        """
        Proactively run a small, isolated garbage collection after each test.

        See the docstring of ``_disable_cyclic_gc_for_qt_safety`` for the full
        rationale. This fixture only takes effect for shiboken-based bindings
        (PySide2/PySide6), where an explicit, frequent, small ``gc.collect()``
        after each test avoids letting cyclic garbage accumulate into a large
        backlog that shiboken's own forced (and otherwise uncontrollable)
        internal collection passes would later reclaim all at once, which was
        observed to segfault. For PyQt5/sip, this fixture deliberately does
        nothing, since calling `gc.collect()` there is unsafe regardless of
        batch size.

        The collection is additionally restricted to tests marked with
        ``@pytest.mark.gui``, since only those tests are expected to create
        QObject-related cyclic garbage in the first place; this keeps the
        (comparatively slow) explicit collection restricted to GUI-related
        tests, avoiding a large runtime cost across the full, mostly-non-GUI
        default test suite.
        """
        yield
        if request.node.get_closest_marker("gui"):
            gc.collect()


@pytest.fixture(scope="session", autouse=True)
def patch_plugin_collection():
    _pc = PluginCollection()
    _path = Path(unittest_objects.__file__).parent
    if _path not in _pc.registered_paths:
        _pc.find_and_register_plugins(_path)
    yield
    if _path in _pc.registered_paths:
        _pc.unregister_plugin_path(_path)


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
    random.seed(a="pydidas testing seed")
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
        _pc = PluginCollection()
        _plugin_class = _pc.get_plugin_by_name(_class_name)
        _tree.create_and_add_node(_plugin_class())
    _plugin_class = _pc.get_plugin_by_name("Sum2dData")
    _tree.create_and_add_node(_plugin_class(), parent=_tree.nodes[0])
    return _tree


@pytest.fixture
def dummy_tree() -> ProcessingTree:
    """Fixture to create a test ProcessingTree with dummy plugins."""
    _pc = PluginCollection()
    _tree = ProcessingTree()
    _tree.create_and_add_node(unittest_objects.DummyLoader())
    _tree.create_and_add_node(unittest_objects.DummyProc())
    _tree.create_and_add_node(unittest_objects.DummyProc(), parent=_tree.root)
    return _tree
