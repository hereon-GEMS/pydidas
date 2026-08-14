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

"""Unit tests for _LazyPyfaiObject and the public pyFAI lazy proxies."""

__author__ = "Malte Storm"
__copyright__ = "Copyright 2026, Helmholtz-Zentrum Hereon"
__license__ = "GPL-3.0-only"
__maintainer__ = "Malte Storm"
__status__ = "Production"


import pytest

from pydidas.core.lazy_imports.lazy_objects import LazyObject
from pydidas.core.lazy_imports.pyFAI import (
    AzimuthalIntegrator,
    Detector,
    Geometry,
    PoniFile,
)


def test_detector_proxy__repr_before_resolution():
    proxy = LazyObject("pyFAI.detectors", "Detector")
    assert "pyFAI.detectors.Detector" in repr(proxy)


def test_detector_proxy__classmethod__before_resolution():
    from pyFAI.detectors import Detector as _RealDetector

    proxy = LazyObject("pyFAI.detectors", "Detector")
    _det = proxy.factory("Eiger9M")
    assert isinstance(_det, Detector)
    assert isinstance(_det, _RealDetector)


def test_detector_proxy__call_no_args_creates_detector():
    from pyFAI.detectors import Detector as _RealDetector

    det = Detector()
    assert isinstance(det, _RealDetector)


def test_detector_proxy__isinstance_with_proxy_is_true():
    det = Detector()
    assert isinstance(det, Detector)


def test_detector_proxy__isinstance_with_proxy_is_false_for_wrong_type():
    assert not isinstance(42, Detector)
    assert not isinstance("not a detector", Detector)


def test_geometry_proxy__call_with_kwargs():
    geo = Geometry(
        dist=0.1,
        poni1=0.0,
        poni2=0.0,
    )
    from pyFAI.geometry import Geometry as _RealGeometry

    assert isinstance(geo, _RealGeometry)
    assert isinstance(geo, Geometry)
    assert geo.dist == pytest.approx(0.1)


def test_geometry_proxy__isinstance_true():
    geo = Geometry()
    assert isinstance(geo, Geometry)


def test_ponifile_proxy__call_creates_ponifile(tmp_path):
    poni_content = (
        "Detector: detector\n"
        "Detector_config: {}\n"
        "Distance: 0.1\n"
        "Poni1: 0.0\n"
        "Poni2: 0.0\n"
        "Rot1: 0.0\n"
        "Rot2: 0.0\n"
        "Rot3: 0.0\n"
        "Wavelength: 1e-10\n"
    )
    poni_file = tmp_path / "test.poni"
    poni_file.write_text(poni_content)
    from pyFAI.io.ponifile import PoniFile as _RealPoniFile

    pf = PoniFile(data=str(poni_file))
    assert isinstance(pf, _RealPoniFile)
    assert isinstance(pf, PoniFile)


@pytest.mark.parametrize(
    "proxy,real_module,real_name",
    [
        (Detector, "pyFAI.detectors", "Detector"),
        (Geometry, "pyFAI.geometry", "Geometry"),
        (AzimuthalIntegrator, "pyFAI.integrator.azimuthal", "AzimuthalIntegrator"),
        (PoniFile, "pyFAI.io.ponifile", "PoniFile"),
    ],
)
def test_proxy__resolves_to_correct_real_class(proxy, real_module, real_name):
    import importlib

    real_cls = getattr(importlib.import_module(real_module), real_name)
    instance = proxy()
    assert type(instance).__name__ == real_name
    assert isinstance(instance, real_cls)
    assert isinstance(instance, proxy)


if __name__ == "__main__":
    pytest.main([__file__])
