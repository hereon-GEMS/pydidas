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


import logging
import shutil
import tempfile
from numbers import Real
from pathlib import Path

import numpy as np
import pyFAI
import pytest
from qtpy import QtTest

from pydidas import IS_QT6
from pydidas.contexts.diff_exp import (
    DiffractionExperiment,
)
from pydidas.core import UserConfigError


logger = logging.getLogger("pyFAI.detectors._common")
logger.setLevel(logging.CRITICAL)

_pyfai_geo_params = {
    "rot1": 12e-5,
    "rot2": 24e-4,
    "rot3": 0.421,
    "dist": 0.654,
    "poni1": 0.1,
    "poni2": 0.32,
}
_xpos = 1623.546
_ypos = 459.765
_det_dist = 0.12
_fit2d_beamcenter = (_xpos, _ypos, _det_dist)
_TEST_SHAPE = (1111, 999)


@pytest.fixture
def exp_with_Eiger9M():
    obj = DiffractionExperiment()
    obj.set_detector_params_from_name("Eiger 9M")
    return obj


@pytest.fixture(scope="module")
def temp_path():
    """Fixture to provide a temporary path for testing."""
    _path = Path(tempfile.mkdtemp())
    yield _path
    shutil.rmtree(_path)


def assert_beamcenter_okay(obj, accuracy=8):
    _rot1 = obj.get_param_value("detector_rot1")
    _rot2 = obj.get_param_value("detector_rot2")
    _poni1 = obj.get_param_value("detector_poni1")
    _poni2 = obj.get_param_value("detector_poni2")
    _z = obj.get_param_value("detector_dist")
    _beam_center_x = (_poni2 - _z * np.tan(_rot1)) / 75e-6
    _beam_center_y = (_poni1 + _z * np.tan(_rot2) / np.cos(_rot1)) / 75e-6
    assert _beam_center_y == pytest.approx(_ypos, abs=accuracy)
    assert _beam_center_x == pytest.approx(_xpos, abs=accuracy)


@pytest.mark.parametrize(
    "key, value, other_val",
    [["energy", 15.7, 0.78970806], ["wavelength", 0.98765, 12.5534517]],
)
def test_set_param__energy(key, value, other_val):
    obj = DiffractionExperiment()
    _spy = QtTest.QSignalSpy(obj.sig_params_changed)
    obj.set_param_value(f"xray_{key}", value)
    _other_key = "xray_energy" if key == "wavelength" else "xray_wavelength"
    assert obj.get_param_value(f"xray_{key}") == pytest.approx(value)
    assert obj.get_param_value(_other_key) == pytest.approx(other_val)
    _spy_result = _spy.count() if IS_QT6 else len(_spy)
    assert _spy_result == 1


@pytest.mark.parametrize("name", ["Eiger 9M", "Custom 9M"])
def test_set_param__detector_name(name):
    obj = DiffractionExperiment()
    obj.set_param_value("detector_npixx", _TEST_SHAPE[1])
    obj.set_param_value("detector_npixy", _TEST_SHAPE[0])
    _spy = QtTest.QSignalSpy(obj.sig_params_changed)
    obj.set_param_value("detector_name", name)
    assert obj.get_param_value("detector_name") == name
    assert obj.det_shape == (3269, 3110) if name == "Eiger 9M" else _TEST_SHAPE
    if name == "Eiger 9M":
        assert obj.get_param_value("detector_pxsizex") == pytest.approx(75)
        assert obj.get_param_value("detector_pxsizey") == pytest.approx(75)
    _spy_result = _spy.count() if IS_QT6 else len(_spy)
    assert _spy_result == 1


@pytest.mark.parametrize(
    "key,value",
    [
        ["detector_npixx", 999],
        ["detector_npixy", 1111],
        ["detector_pxsizex", 42.0],
        ["detector_pxsizey", 42.0],
    ],
)
@pytest.mark.parametrize("det_name", ["Eiger 9M", "Custom 9M"])
def test_set_param_detector__det_param(det_name, key, value):
    obj = DiffractionExperiment()
    _spy = QtTest.QSignalSpy(obj.sig_params_changed)
    obj.set_param_value("detector_name", det_name)
    obj.set_param_value(key, value)
    assert obj.get_param_value(key) == pytest.approx(value)
    assert (
        obj.get_param_value("detector_name") == det_name
        if det_name == "Custom 9M"
        else "Eiger 9M [modified]"
    )
    assert 2 == _spy.count() if IS_QT6 else len(_spy)


@pytest.mark.parametrize("key, value", [[k, v] for k, v in _pyfai_geo_params.items()])
def test_set_param__other(key, value):
    obj = DiffractionExperiment()
    _spy = QtTest.QSignalSpy(obj.sig_params_changed)
    obj.set_param_value(f"detector_{key}", value)
    assert obj.get_param_value(f"detector_{key}") == pytest.approx(value)
    _spy_result = _spy.count() if IS_QT6 else len(_spy)
    assert _spy_result == 1


@pytest.mark.parametrize("det_name", ["Eiger 9M", "Custom 9M"])
def test_get_detector(det_name):
    _pixelsize = 112.0
    obj = DiffractionExperiment()
    obj.set_param_value("detector_npixy", _TEST_SHAPE[0])
    obj.set_param_value("detector_npixx", _TEST_SHAPE[1])
    obj.set_param_value("detector_pxsizey", _pixelsize)
    obj.set_param_value("detector_pxsizex", _pixelsize)
    obj.set_param_value("detector_name", det_name)
    _target_pxsize = _pixelsize * 1e-6 if det_name == "Custom 9M" else 75e-6
    _det = obj.get_detector()
    assert isinstance(_det, pyFAI.detectors.Detector)
    assert _det.max_shape == _TEST_SHAPE if det_name == "Custom 9M" else (3269, 3110)
    assert _det.pixel1 == pytest.approx(_target_pxsize)
    assert _det.pixel2 == pytest.approx(_target_pxsize)


def test_det_shape__getter():
    obj = DiffractionExperiment()
    obj.set_param_value("detector_npixy", _TEST_SHAPE[0])
    obj.set_param_value("detector_npixx", _TEST_SHAPE[1])
    assert obj.det_shape == _TEST_SHAPE


@pytest.mark.parametrize("det_name", ["Eiger 9M", "Custom 9M"])
def test_det_shape__setter_w_custom_detector(det_name):
    obj = DiffractionExperiment()
    obj.set_param_value("detector_name", det_name)
    obj.det_shape = _TEST_SHAPE
    assert obj.det_shape == _TEST_SHAPE
    assert (
        obj.get_param_value("detector_name") == det_name
        if det_name == "Custom 9M"
        else "Eiger 9M [modified]"
    )


@pytest.mark.parametrize("det_name", ["Eiger 9M", "Custom 9M"])
@pytest.mark.parametrize("shape", [_TEST_SHAPE, (0, 0), (1111, 0), (0, 999)])
@pytest.mark.parametrize("pxsize", [(100, 100), (0, 0), (100, 0), (0, 100)])
def test_detector_is_valid__no_detector(det_name, shape, pxsize):
    obj = DiffractionExperiment()
    obj.set_param_value("detector_npixy", shape[0])
    obj.set_param_value("detector_npixx", shape[1])
    obj.set_param_value("detector_pxsizey", pxsize[0])
    obj.set_param_value("detector_pxsizex", pxsize[1])
    obj.set_param_value("detector_name", det_name)
    assert (
        obj.detector_is_valid == (0 not in shape and 0 not in pxsize)
        or det_name == "Eiger 9M"
    )


def test_as_pyfai_geometry(exp_with_Eiger9M):
    for _key, _val in _pyfai_geo_params.items():
        exp_with_Eiger9M.set_param_value(f"detector_{_key}", _val)
    _geo = exp_with_Eiger9M.as_pyfai_geometry()
    assert isinstance(_geo, pyFAI.geometry.Geometry)
    for _key, _val in _pyfai_geo_params.items():
        assert getattr(_geo, _key) == pytest.approx(_val)


def test_set_detector_params_from_name__wrong_name():
    obj = DiffractionExperiment()
    with pytest.raises(UserConfigError):
        obj.set_detector_params_from_name("no such detector")


def test_set_detector_params_from_name():
    _det = {"name": "Pilatus 300k", "pixsize": 172, "npixx": 487, "npixy": 619}
    obj = DiffractionExperiment()
    obj.set_detector_params_from_name(_det["name"])
    assert obj.get_param_value("detector_name") == _det["name"]
    assert obj.get_param_value("detector_pxsizex") == pytest.approx(_det["pixsize"])
    assert obj.get_param_value("detector_pxsizey") == pytest.approx(_det["pixsize"])
    assert obj.get_param_value("detector_npixy") == _det["npixy"]
    assert obj.get_param_value("detector_npixx") == _det["npixx"]


def test_set_beamcenter_from_fit2d_params__no_rot(exp_with_Eiger9M):
    exp_with_Eiger9M.set_beamcenter_from_fit2d_params(*_fit2d_beamcenter)
    assert_beamcenter_okay(exp_with_Eiger9M)


def test_set_beamcenter_from_fit2d_params__full_rot_degree(exp_with_Eiger9M):
    exp_with_Eiger9M.set_beamcenter_from_fit2d_params(
        *_fit2d_beamcenter, tilt=5, tilt_plane=270, rot_unit="degree"
    )
    assert_beamcenter_okay(exp_with_Eiger9M)


def test_set_beamcenter_from_fit2d_params_full_rot_rad(exp_with_Eiger9M):
    exp_with_Eiger9M.set_beamcenter_from_fit2d_params(
        *_fit2d_beamcenter, tilt=0.5, tilt_plane=1, rot_unit="rad"
    )
    assert_beamcenter_okay(exp_with_Eiger9M)


def test_as_fit2d_geometry_values(exp_with_Eiger9M):
    _f2d = exp_with_Eiger9M.as_fit2d_geometry_values()
    assert isinstance(_f2d, dict)


def test_as_fit2d_geometry_values__invalid_exp(exp_with_Eiger9M):
    exp_with_Eiger9M.set_param_value("detector_pxsizex", 0)
    with pytest.raises(UserConfigError):
        exp_with_Eiger9M.as_fit2d_geometry_values()


def test_update_from_diffraction_exp():
    obj = DiffractionExperiment()
    obj.set_param_value("detector_name", "Eiger 9M")
    _exp = DiffractionExperiment()
    _exp.update_from_diffraction_exp(obj)
    for _key, _val in obj.param_values.items():
        if isinstance(_val, Real):
            assert _val == pytest.approx(_exp.get_param_value(_key))
        else:
            assert _val == _exp.get_param_value(_key)


def test_update_from_pyfai_geometry__no_detector():
    obj = DiffractionExperiment()
    obj.set_param_value("detector_name", "Eiger 9M")
    _geo = pyFAI.geometry.Geometry()
    for _key, _val in _pyfai_geo_params.items():
        setattr(_geo, _key, _val)
    obj.update_from_pyfai_geometry(_geo)
    for _key, _val in _pyfai_geo_params.items():
        assert obj.get_param_value(f"detector_{_key}") == pytest.approx(_val)
    assert obj.get_param_value("detector_name") == "Eiger 9M"


def test_update_from_pyfai_geometry__custom_detector():
    obj = DiffractionExperiment()
    _det = pyFAI.detectors.Detector(pixel1=12e-6, pixel2=24e-6, max_shape=(1234, 567))
    _det.aliases = ["Dummy"]
    _geo = pyFAI.geometry.Geometry(**_pyfai_geo_params, detector=_det)
    obj.update_from_pyfai_geometry(_geo)
    for _key, _val in _pyfai_geo_params.items():
        assert obj.get_param_value(f"detector_{_key}") == pytest.approx(_val)
    for _key, _val in [
        ["pxsizex", _det.pixel2 * 1e6],
        ["pxsizey", _det.pixel1 * 1e6],
        ["npixx", _det.max_shape[1]],
        ["npixy", _det.max_shape[0]],
        ["name", "Dummy"],
    ]:
        assert obj.get_param_value(f"detector_{_key}") == pytest.approx(_val)


def test_update_from_pyfai_geometry__generic_detector():
    obj = DiffractionExperiment()
    _geo = pyFAI.geometry.Geometry(**_pyfai_geo_params, detector="Eiger 9M")
    _det = pyFAI.detector_factory("Eiger 9M")
    obj.update_from_pyfai_geometry(_geo)
    for _key, _val in _pyfai_geo_params.items():
        assert obj.get_param_value(f"detector_{_key}") == pytest.approx(_val)
    for _key, _val in [
        ["pxsizex", _det.pixel2 * 1e6],
        ["pxsizey", _det.pixel1 * 1e6],
        ["npixx", _det.max_shape[1]],
        ["npixy", _det.max_shape[0]],
        ["name", "Eiger 9M"],
    ]:
        assert obj.get_param_value(f"detector_{_key}") == pytest.approx(_val)


@pytest.mark.parametrize("ext", ["yaml", "poni", "h5"])
def test_import_from_file(exp_with_Eiger9M, temp_path, ext):
    _file_path = temp_path / f"test_import.{ext}"
    exp_with_Eiger9M.export_to_file(_file_path)
    _params = exp_with_Eiger9M.param_values
    exp_with_Eiger9M.restore_all_defaults(True)
    _spy = QtTest.QSignalSpy(exp_with_Eiger9M.sig_params_changed)
    exp_with_Eiger9M.import_from_file(_file_path)
    _spy_result = _spy.count() if IS_QT6 else len(_spy)
    for _key, _ref in _params.items():
        if isinstance(_ref, Real):
            assert exp_with_Eiger9M.get_param_value(_key) == pytest.approx(_ref)
        else:
            assert exp_with_Eiger9M.get_param_value(_key) == _ref


@pytest.mark.parametrize("ext", ["yaml", "poni", "h5"])
@pytest.mark.parametrize("det_name", ["Eiger 9M", "Custom 9M"])
def test_export_to_file(exp_with_Eiger9M, temp_path, ext, det_name):
    _file_path = temp_path / f"test_export_{det_name}.{ext}"
    exp_with_Eiger9M.set_param_value("detector_name", det_name)
    exp_with_Eiger9M.export_to_file(_file_path)
    assert _file_path.exists()
    with open(_file_path, "rb") as f:
        _content = f.read()
    assert len(_content) > 0


def test_beamcenter__not_set(exp_with_Eiger9M):
    _center = exp_with_Eiger9M.beamcenter
    assert _center.x == pytest.approx(0)
    assert _center.y == pytest.approx(0)


def test_beamcenter__set(exp_with_Eiger9M):
    _cx = 1248
    _cy = 1369.75
    exp_with_Eiger9M.set_param_value(
        "detector_poni1",
        _cy * exp_with_Eiger9M.get_param_value("detector_pxsizex") * 1e-6,
    )
    exp_with_Eiger9M.set_param_value(
        "detector_poni2",
        _cx * exp_with_Eiger9M.get_param_value("detector_pxsizey") * 1e-6,
    )
    _center = exp_with_Eiger9M.beamcenter
    assert _center.x == pytest.approx(_cx, 1e-2, 8)
    assert _center.y == pytest.approx(_cy, 1e-2, 8)


def test_hash(exp_with_Eiger9M):
    _copy = exp_with_Eiger9M.copy()
    assert hash(exp_with_Eiger9M) == hash(_copy)


# raise UserConfigError("Must finish work on tests")

if __name__ == "__main__":
    pytest.main()
