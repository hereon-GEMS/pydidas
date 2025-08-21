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
from pathlib import Path

import pyFAI
import pytest
from pyFAI.io.ponifile import PoniFile

from pydidas.contexts import DiffractionExperimentContext
from pydidas.contexts.diff_exp import DiffractionExperiment
from pydidas.contexts.diff_exp.diff_exp_io_poni import DiffractionExperimentIoPoni
from pydidas.core.constants import LAMBDA_IN_M_TO_E


EXP = DiffractionExperimentContext()
EXP_IO_PONI = DiffractionExperimentIoPoni

_logger = logging.getLogger("pyFAI.geometry")
_logger.setLevel(logging.CRITICAL)

_TEST_FILE_DIR = Path(__file__).parents[2] / "_data" / "diffraction_exp_io"
_pyfai_geo_params = {
    "rot1": 12e-5,
    "rot2": 24e-4,
    "rot3": 0.421,
    "dist": 0.654,
    "poni1": 0.1,
    "poni2": 0.32,
    "wavelength": 1.54e-10,
}
_custom_det_params = {
    "pixel1": 120e-6,
    "pixel2": 125e-6,
    "max_shape": (512, 1024),
}


@pytest.fixture(scope="module")
def temp_path():
    """
    Fixture to create a temporary directory for tests.
    """
    temp_path = Path(tempfile.mkdtemp())
    yield temp_path
    shutil.rmtree(temp_path)


@pytest.fixture(scope="module")
def eiger9m_poni_file(temp_path):
    geo = pyFAI.geometry.Geometry(detector="Eiger 9M", **_pyfai_geo_params)
    geo.save(temp_path / "eiger9m.poni")
    return temp_path / "eiger9m.poni"


@pytest.fixture
def exp():
    return DiffractionExperiment()


@pytest.fixture(scope="module")
def custom_det_poni_file(temp_path):
    det = pyFAI.detectors.Detector(**_custom_det_params)
    geo = pyFAI.geometry.Geometry(detector=det, **_pyfai_geo_params)
    geo.save(temp_path / "custom_detector.poni")
    with open(temp_path / "custom_detector.poni", "a") as f:
        f.write("\n# This file was created by pydidas.")
        f.write("\n# pydidas_det_name = Custom Detector 42")
    return temp_path / "custom_detector.poni"


def update_exp_with_config(exp: DiffractionExperiment):
    for _key, _val in _pyfai_geo_params.items():
        if _key == "wavelength":
            exp.set_param_value(f"xray_{_key}", _val)
        else:
            exp.set_param_value(f"detector_{_key}", _val)


def verify_imported_geo_params(exp: DiffractionExperiment):
    for param, val in [
        ("detector_dist", _pyfai_geo_params["dist"]),
        ("detector_poni1", _pyfai_geo_params["poni1"]),
        ("detector_poni2", _pyfai_geo_params["poni2"]),
        ("detector_rot1", _pyfai_geo_params["rot1"]),
        ("detector_rot2", _pyfai_geo_params["rot2"]),
        ("detector_rot3", _pyfai_geo_params["rot3"]),
        ("xray_wavelength", _pyfai_geo_params["wavelength"] * 1e10),
        ("xray_energy", LAMBDA_IN_M_TO_E / _pyfai_geo_params["wavelength"]),
    ]:
        assert exp.get_param_value(param) == pytest.approx(val)


def check_imported_geo_params(exp: DiffractionExperiment, _fname: str):
    geo = pyFAI.geometry.Geometry().load(PoniFile(_fname))
    for param, val in [
        ("detector_dist", geo.dist),
        ("detector_poni1", geo.poni1),
        ("detector_poni2", geo.poni2),
        ("detector_rot1", geo.rot1),
        ("detector_rot2", geo.rot2),
        ("detector_rot3", geo.rot3),
        ("xray_wavelength", geo.wavelength * 1e10),
        ("xray_energy", LAMBDA_IN_M_TO_E / geo.wavelength),
    ]:
        assert exp.get_param_value(param) == pytest.approx(val)
    assert exp.get_param_value("detector_npixx") == geo.detector.shape[1]
    assert exp.get_param_value("detector_npixy") == geo.detector.shape[0]
    assert exp.get_param_value("detector_pxsizex") == pytest.approx(
        geo.detector.pixel2 * 1e6
    )
    assert exp.get_param_value("detector_pxsizey") == pytest.approx(
        geo.detector.pixel1 * 1e6
    )


def test_import_from_file__standard_det(eiger9m_poni_file, exp):
    EXP_IO_PONI.import_from_file(eiger9m_poni_file, diffraction_exp=exp)
    det = pyFAI.detector_factory("Eiger 9M")
    verify_imported_geo_params(exp)
    assert exp.get_param_value("detector_name") == "Eiger 9M"
    assert exp.get_param_value("detector_npixx") == det.max_shape[1]
    assert exp.get_param_value("detector_npixy") == det.max_shape[0]
    assert exp.get_param_value("detector_pxsizex") == pytest.approx(det.pixel1 * 1e6)
    assert exp.get_param_value("detector_pxsizey") == pytest.approx(det.pixel2 * 1e6)


def test_update_geometry_from_pyFAI__custom_det(custom_det_poni_file, exp):
    EXP_IO_PONI.import_from_file(custom_det_poni_file, diffraction_exp=exp)
    verify_imported_geo_params(exp)
    assert exp.get_param_value("detector_name") == "Custom Detector 42"
    assert exp.get_param_value("detector_npixx") == _custom_det_params["max_shape"][1]
    assert exp.get_param_value("detector_npixy") == _custom_det_params["max_shape"][0]
    assert exp.get_param_value("detector_pxsizex") == pytest.approx(
        _custom_det_params["pixel2"] * 1e6
    )
    assert exp.get_param_value("detector_pxsizey") == pytest.approx(
        _custom_det_params["pixel1"] * 1e6
    )


# @pytest.mark.parametrize("det_name", ["Eiger 9M", "Eiger9m", "eiger 9m", "Eiger 9m"])
def test_export_to_file__standard_det(temp_path, exp):
    _fname = temp_path / "exported_poni.poni"
    exp.set_detector_params_from_name("Eiger 9M")
    update_exp_with_config(exp)
    EXP_IO_PONI.export_to_file(_fname, diffraction_exp=exp)
    check_imported_geo_params(exp, _fname)
    assert exp.get_param_value("detector_name") == "Eiger 9M"


def test_export_to_file__custom_det(temp_path, exp):
    _fname = temp_path / "custom_exported_poni.poni"
    exp.set_param_value("detector_name", "Custom Detector 42")
    exp.set_param_value("detector_npixx", _custom_det_params["max_shape"][1])
    exp.set_param_value("detector_npixy", _custom_det_params["max_shape"][0])
    exp.set_param_value("detector_pxsizex", _custom_det_params["pixel2"] * 1e6)
    exp.set_param_value("detector_pxsizey", _custom_det_params["pixel1"] * 1e6)
    update_exp_with_config(exp)
    EXP_IO_PONI.export_to_file(_fname, diffraction_exp=exp)
    check_imported_geo_params(exp, _fname)
    assert exp.get_param_value("detector_name") == "Custom Detector 42"


def test_update_geometry_from_pyFAI__wrong_type():
    with pytest.raises(TypeError):
        EXP_IO_PONI._update_geometry_from_pyFAI(12)


def test_update_detector_from_pyfai__wrong_type():
    with pytest.raises(TypeError):
        EXP_IO_PONI._update_detector_from_pyFAI(12)


if __name__ == "__main__":
    pytest.main()
