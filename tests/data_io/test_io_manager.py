# This file is part of pydidas.
#
# Copyright 2023 - 2025, Helmholtz-Zentrum Hereon
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
__copyright__ = "Copyright 2023 - 2025, Helmholtz-Zentrum Hereon"
__license__ = "GPL-3.0-only"
__maintainer__ = "Malte Storm"
__status__ = "Production"

from typing import Literal

import numpy as np
import pytest

from pydidas.core import UserConfigError
from pydidas.core.utils import get_random_string
from pydidas.data_io import IoManager
from pydidas.data_io.implementations import IoBase


class _IoTestClass(IoBase):
    extensions_export = ["test", "export"]
    extensions_import = ["test", "import"]
    format_name = "_IoTestClass"

    @classmethod
    def export_to_file(cls, filename, data, **kwargs):
        cls._exported = [filename, data, kwargs]

    @classmethod
    def import_from_file(cls, filename, **kwargs):
        cls._imported = [filename, kwargs]
        return np.zeros((10, 10))


class _IoTestClassWithMetadataImporter(_IoTestClass):
    extensions_import = ["meta_test"]
    extensions_export = []
    format_name = "_IoTestClassWithMetadataImporter"
    allows_metadata_import = True

    @classmethod
    def read_metadata_from_file(cls, _, **kwargs):  # noqa
        return {"meta_data": True}


@pytest.fixture(autouse=True)
def clear_registry():
    stored_import = IoManager.registry_import.copy()
    stored_export = IoManager.registry_export.copy()
    IoManager.clear_registry()
    yield
    IoManager.registry_import = stored_import
    IoManager.registry_export = stored_export


@pytest.fixture
def io_manager_with_test_class(clear_registry):
    IoManager.register_class(_IoTestClass)
    return IoManager


def test_register_class_plain(io_manager_with_test_class):
    for _ext in _IoTestClass.extensions_export:
        assert IoManager.registry_export[_ext] == _IoTestClass
    for _ext in _IoTestClass.extensions_import:
        assert IoManager.registry_import[_ext] == _IoTestClass


def test_register_class_add_class_and_verify_entries_not_deleted():
    IoManager.registry_import = {".no_ext": None}
    IoManager.register_class(_IoTestClass)
    assert IoManager.registry_import[".no_ext"] is None


@pytest.mark.parametrize("mode", ["import", "export"])
def test_register_class__add_class_and_overwrite_old_entry(mode):
    _registry = getattr(IoManager, f"registry_{mode}")
    _registry["test"] = None
    IoManager.register_class(_IoTestClass, update_registry=True)
    assert getattr(IoManager, f"registry_{mode}")["test"] == _IoTestClass


@pytest.mark.parametrize("mode", ["import", "export"])
def test_register_class_add_and_keep_old_entry(mode):
    _registry = getattr(IoManager, f"registry_{mode}")
    _registry["test"] = None
    with pytest.raises(KeyError):
        IoManager.register_class(_IoTestClass, update_registry=False)


def test_clear_registry(io_manager_with_test_class):
    IoManager.clear_registry()
    assert IoManager.registry_import == {}
    assert IoManager.registry_export == {}


@pytest.mark.parametrize("mode", ["import", "export", "metadata"])
@pytest.mark.parametrize("ext", ["test", "export", "import", "never", "meta_test"])
def test_is_extension_registered(
    mode: Literal["import", "export", "metadata"], ext, io_manager_with_test_class
):
    IoManager.register_class(_IoTestClassWithMetadataImporter)
    _ref = (
        ext == "meta_test"
        if mode == "metadata"
        else (ext == "test" or mode == ext or (mode == "import" and ext == "meta_test"))
    )
    assert IoManager.is_extension_registered(ext, mode=mode) == _ref


@pytest.mark.parametrize("mode", ["import", "export"])
@pytest.mark.parametrize("ext", ["test", "export", "import", "never"])
def test_verify_extension_is_registered(
    mode: Literal["import", "export", "metadata"], ext, io_manager_with_test_class
):
    if ext == "test" or mode == ext:
        IoManager.verify_extension_is_registered(ext, mode=mode)
        assert True  # no exception raised
    else:
        with pytest.raises(UserConfigError):
            IoManager.verify_extension_is_registered(ext, mode=mode)


@pytest.mark.parametrize("mode", ["import", "export"])
def test_get_string_of_formats__empty(mode: Literal["import", "export"]):
    _str = IoManager.get_string_of_formats(mode=mode)
    assert _str == "All supported files ()"


@pytest.mark.parametrize("mode", ["import", "export"])
def test_get_string_of_formats__simple(
    mode: Literal["import", "export"], io_manager_with_test_class
):
    _str = IoManager.get_string_of_formats(mode=mode)
    for _ext in getattr(_IoTestClass, f"extensions_{mode}"):
        assert f"*.{_ext}" in _str


def test_export_to_file(io_manager_with_test_class):
    _fname = get_random_string(12) + ".test"
    _data = np.random.random((10, 10))
    _kws = dict(test_kw=True)
    IoManager.export_to_file(_fname, _data, **_kws)
    assert _IoTestClass._exported[0] == _fname
    assert np.allclose(_IoTestClass._exported[1], _data)
    assert _IoTestClass._exported[2] == _kws


def test_import_from_file(io_manager_with_test_class):
    _fname = get_random_string(12) + ".test"
    _kws = dict(test_kw=True)
    IoManager.import_from_file(_fname, **_kws)
    assert _IoTestClass._imported[0] == _fname
    assert _IoTestClass._imported[1] == _kws


def test_import_from_file__w_forced_dim_kw():
    _fname = get_random_string(12) + ".test"
    IoManager.register_class(_IoTestClass)
    with pytest.raises(UserConfigError):
        IoManager.import_from_file(_fname, forced_dimension=5)


@pytest.mark.parametrize("ext", ["meta_test", "test", "import", "export"])
def test_import_metadata_from_file(io_manager_with_test_class, ext):
    IoManager.register_class(_IoTestClassWithMetadataImporter)
    if ext == "meta_test":
        _metadata = IoManager.read_metadata_from_file(get_random_string(12) + f".{ext}")
        assert _metadata == {"meta_data": True}
    else:
        with pytest.raises(UserConfigError):
            IoManager.read_metadata_from_file(get_random_string(12) + f".{ext}")


if __name__ == "__main__":
    pytest.main()
