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
#
# This file was created using an AI tool and was modified by
# the pydidas team.

"""Tests for the PyFAIazimuthalSectorIntegration plugin."""

from collections.abc import Iterator
from pathlib import Path
from types import SimpleNamespace
from typing import Any
from unittest.mock import Mock, patch

import numpy as np
import pytest

from pydidas_plugins.proc_plugins.pyfai_azimuthal_sector_integration import (
    PyFAIazimuthalSectorIntegration,
)

from pydidas.contexts.diff_exp.diff_exp import DiffractionExperiment
from pydidas.core import Dataset, UserConfigError
from pydidas.core.constants.pyfai_names import pyFAI_METHOD, pyFAI_UNITS
from pydidas.core.lazy_imports.pyFAI import AzimuthalIntegrator
from pydidas.plugins import pyFAIintegrationBase


@pytest.fixture
def experiment(
    random_diff_exp: DiffractionExperiment,
) -> DiffractionExperiment:
    ### This test was written by an AI tool.
    random_diff_exp.set_param_values(
        detector_npixx=32,
        detector_npixy=32,
        detector_pxsizex=100,
        detector_pxsizey=100,
        detector_dist=0.1,
        detector_poni1=0.0016,
        detector_poni2=0.0016,
        detector_rot1=0,
        detector_rot2=0,
        detector_rot3=0,
        detector_mask_file=Path(),
        xray_wavelength=1,
    )
    return random_diff_exp


@pytest.fixture
def integration_backend() -> Iterator[tuple[Mock, list[Mock]]]:
    ### This fixture was written by an AI tool.
    integrators: list[Mock] = []

    def create_integrator(**kwargs: Any) -> Mock:
        index = len(integrators)
        integrator = Mock()
        integrator.detector = kwargs["detector"]

        def integrate(image: np.ndarray, npoints: int, **options: Any) -> Any:
            return SimpleNamespace(
                intensity=np.arange(npoints, dtype=float) + 10 * index,
                radial=np.linspace(0.1, 0.3, npoints),
            )

        integrator.integrate1d.side_effect = integrate
        integrators.append(integrator)
        return integrator

    with patch(
        "pydidas_plugins.proc_plugins.pyfai_azimuthal_sector_integration."
        "AzimuthalIntegrator",
        side_effect=create_integrator,
    ) as factory:
        yield factory, integrators


@pytest.fixture
def sector_plugin(
    experiment: DiffractionExperiment,
    integration_backend: tuple[Mock, list[Mock]],
) -> PyFAIazimuthalSectorIntegration:
    ### This fixture was written by an AI tool.
    return PyFAIazimuthalSectorIntegration(
        diffraction_exp=experiment,
        azi_sector_centers="-90; 0; 90; 270",
        azi_sector_width=20,
        rad_npoint=3,
        int_method="CSR",
    )


@pytest.fixture(params=[False, True], ids=["ndarray", "dataset"])
def image(request: pytest.FixtureRequest) -> np.ndarray:
    ### This fixture was written by an AI tool.
    values = np.arange(32 * 32, dtype=float).reshape(32, 32)
    if request.param:
        return Dataset(
            values,
            axis_labels=["detector y", "detector x"],
            axis_units=["pixel", "pixel"],
            data_label="input intensity",
        )
    return values


@pytest.fixture
def detector_mask(experiment: DiffractionExperiment, tmp_path: Path) -> np.ndarray:
    ### This fixture was written by an AI tool.
    mask = np.zeros((32, 32), dtype=np.uint8)
    mask[:4] = 1
    filename = tmp_path / "mask.npy"
    np.save(filename, mask)
    experiment.set_param_value("detector_mask_file", filename)
    return mask


def test_init__plugin_contract(sector_plugin: PyFAIazimuthalSectorIntegration) -> None:
    ### This test was written by an AI tool.
    assert isinstance(sector_plugin, pyFAIintegrationBase)
    assert sector_plugin.input_data_dim == 2
    assert sector_plugin.output_data_dim == 2
    assert sector_plugin.new_dataset
    assert sector_plugin.get_param_value("azi_sector_centers") == "-90; 0; 90; 270"
    assert sector_plugin.get_param_value("azi_sector_width") == 20
    assert sector_plugin.get_param_value("rad_npoint") == 3
    for refkey in ("azi_use_range", "azi_range_lower", "azi_range_upper", "azi_npoint"):
        assert refkey not in sector_plugin.params


def test_init__parameters_are_independent(experiment: DiffractionExperiment) -> None:
    ### This test was written by an AI tool.
    first = PyFAIazimuthalSectorIntegration(diffraction_exp=experiment)
    second = PyFAIazimuthalSectorIntegration(diffraction_exp=experiment)
    first.set_param_value("azi_sector_centers", "45")
    first.set_param_value("azi_sector_width", 5)
    assert second.get_param_value("azi_sector_centers") == "0; 90; 180; 270"
    assert second.get_param_value("azi_sector_width") == 20


@pytest.mark.parametrize(
    ("entries", "centers"),
    [
        ("12.5", [12.5]),
        (" 90 ; -45.5 ; 0 ", [90, -45.5, 0]),
        ("1e1; -2.5e1", [10, -25]),
        ("90; 0; 90", [90, 0, 90]),
    ],
)
def test_pre_execute__parses_centers_and_preserves_order(
    sector_plugin: PyFAIazimuthalSectorIntegration,
    integration_backend: tuple[Mock, list[Mock]],
    entries: str,
    centers: list[float],
) -> None:
    ### This test was written by an AI tool.
    sector_plugin.set_param_value("azi_sector_centers", entries)
    sector_plugin.pre_execute()
    result, _ = sector_plugin.execute(np.ones((32, 32)))
    np.testing.assert_array_equal(result.axis_ranges[0], centers)
    assert result.shape == (len(centers), 3)
    assert integration_backend[0].call_count == len(centers)


@pytest.mark.parametrize("entries", ["", " ", "a; 90", "0;;90", "0;", "0, 90"])
def test_pre_execute__invalid_centers(
    sector_plugin: PyFAIazimuthalSectorIntegration,
    integration_backend: tuple[Mock, list[Mock]],
    entries: str,
) -> None:
    ### This test was written by an AI tool.
    sector_plugin.set_param_value("azi_sector_centers", entries)
    with pytest.raises(
        UserConfigError, match="Could not convert the azimuthal sectors"
    ):
        sector_plugin.pre_execute()
    integration_backend[0].assert_not_called()


def test_pre_execute__passes_experiment_geometry(
    sector_plugin: PyFAIazimuthalSectorIntegration,
    experiment: DiffractionExperiment,
    integration_backend: tuple[Mock, list[Mock]],
) -> None:
    ### This test was written by an AI tool.
    experiment.set_param_values(
        detector_rot1=0.1, detector_rot2=-0.2, detector_rot3=0.3
    )
    sector_plugin.pre_execute()
    factory, _ = integration_backend
    assert factory.call_count == 4
    for call in factory.call_args_list:
        values = call.kwargs
        for key, param in (
            ("dist", "detector_dist"),
            ("poni1", "detector_poni1"),
            ("poni2", "detector_poni2"),
            ("rot1", "detector_rot1"),
            ("rot2", "detector_rot2"),
            ("rot3", "detector_rot3"),
        ):
            assert values[key] == experiment.get_param_value(param)
        assert values["wavelength"] == pytest.approx(1e-10)
        assert values["detector"].max_shape == (32, 32)
        assert values["detector"].pixel1 == pytest.approx(1e-4)
        assert values["detector"].pixel2 == pytest.approx(1e-4)


def test_pre_execute__reuses_integrators_for_unchanged_geometry(
    sector_plugin: PyFAIazimuthalSectorIntegration,
    integration_backend: tuple[Mock, list[Mock]],
) -> None:
    ### This test was written by an AI tool.
    sector_plugin.pre_execute()
    sector_plugin.pre_execute()
    assert integration_backend[0].call_count == 4


def test_pre_execute__rebuilds_integrators_for_changed_geometry(
    sector_plugin: PyFAIazimuthalSectorIntegration,
    experiment: DiffractionExperiment,
    integration_backend: tuple[Mock, list[Mock]],
) -> None:
    ### This test was written by an AI tool.
    sector_plugin.pre_execute()
    experiment.set_param_value("detector_dist", 0.25)
    sector_plugin.pre_execute()
    factory, integrators = integration_backend
    assert factory.call_count == 8
    sector_plugin.execute(np.ones((32, 32)))
    for integrator in integrators[:4]:
        integrator.integrate1d.assert_not_called()
    for integrator in integrators[4:]:
        integrator.integrate1d.assert_called_once()
    assert factory.call_args.kwargs["dist"] == 0.25


@pytest.mark.parametrize("azi_unit", ["chi / deg", "chi / rad"])
def test_pre_execute__updates_sector_bounds_without_rebuilding(
    sector_plugin: PyFAIazimuthalSectorIntegration,
    integration_backend: tuple[Mock, list[Mock]],
    azi_unit: str,
) -> None:
    ### This test was written by an AI tool.
    sector_plugin.pre_execute()
    centers = np.array([-60, -10, 40, 100])
    values = np.deg2rad(centers) if azi_unit == "chi / rad" else centers
    width = np.deg2rad(10) if azi_unit == "chi / rad" else 10
    sector_plugin.set_param_values(
        azi_unit=azi_unit,
        azi_sector_centers=";".join(str(c) for c in values),
        azi_sector_width=width,
    )
    sector_plugin.pre_execute()
    result, _ = sector_plugin.execute(np.ones((32, 32)))
    assert integration_backend[0].call_count == 4
    np.testing.assert_allclose(result.axis_ranges[0], values)
    np.testing.assert_allclose(
        [
            ai.integrate1d.call_args.kwargs["azimuth_range"]
            for ai in integration_backend[1]
        ],
        np.column_stack((centers - 5, centers + 5)),
    )


@pytest.mark.xfail(
    strict=True,
    reason="Integrator cache ignores changes in the number of sectors.",
)
@pytest.mark.parametrize("entries", ["0; 90", "0; 45; 90; 135; 180"])
def test_pre_execute__updates_number_of_sectors(
    sector_plugin: PyFAIazimuthalSectorIntegration, entries: str
) -> None:
    ### This test was written by an AI tool.
    sector_plugin.pre_execute()
    sector_plugin.set_param_value("azi_sector_centers", entries)
    sector_plugin.pre_execute()
    result, _ = sector_plugin.execute(np.ones((32, 32)))
    centers = [float(entry) for entry in entries.split(";")]
    assert result.shape == (len(centers), 3)
    np.testing.assert_array_equal(result.axis_ranges[0], centers)


def test_pre_execute__loads_mask_for_all_sectors(
    sector_plugin: PyFAIazimuthalSectorIntegration,
    integration_backend: tuple[Mock, list[Mock]],
    detector_mask: np.ndarray,
) -> None:
    ### This test was written by an AI tool.
    sector_plugin.pre_execute()
    for integrator in integration_backend[1]:
        integrator.set_mask.assert_called_once()
        np.testing.assert_array_equal(
            integrator.set_mask.call_args.args[0], detector_mask
        )


def test_pre_execute__missing_mask_raises(
    sector_plugin: PyFAIazimuthalSectorIntegration,
    experiment: DiffractionExperiment,
    tmp_path: Path,
) -> None:
    ### This test was written by an AI tool.
    experiment.set_param_value("detector_mask_file", tmp_path / "missing.npy")
    with pytest.raises(UserConfigError, match="Cannot load detector mask"):
        sector_plugin.pre_execute()


def test_pre_execute__wrong_mask_shape_raises(
    sector_plugin: PyFAIazimuthalSectorIntegration,
    experiment: DiffractionExperiment,
    tmp_path: Path,
) -> None:
    ### This test was written by an AI tool.
    filename = tmp_path / "wrong_shape.npy"
    np.save(filename, np.zeros((3, 5)))
    experiment.set_param_value("detector_mask_file", filename)
    with pytest.raises(UserConfigError, match="shape of the mask"):
        sector_plugin.pre_execute()


@pytest.mark.xfail(
    strict=True,
    reason="Removing the external mask does not clear cached integrator masks.",
)
def test_pre_execute__clears_removed_detector_mask(
    sector_plugin: PyFAIazimuthalSectorIntegration,
    experiment: DiffractionExperiment,
    integration_backend: tuple[Mock, list[Mock]],
    detector_mask: np.ndarray,
) -> None:
    ### This test was written by an AI tool.
    sector_plugin.pre_execute()
    experiment.set_param_value("detector_mask_file", Path())
    for integrator in integration_backend[1]:
        integrator.set_mask.reset_mock()
    sector_plugin.pre_execute()
    for integrator in integration_backend[1]:
        integrator.set_mask.assert_called_with(None)


@pytest.mark.parametrize("azi_unit", ["chi / deg", "chi / rad"])
def test_execute__sector_coordinates_match_unit(
    sector_plugin: PyFAIazimuthalSectorIntegration,
    integration_backend: tuple[Mock, list[Mock]],
    azi_unit: str,
    image: np.ndarray,
) -> None:
    ### This test was written by an AI tool.
    plugin = sector_plugin
    centers_deg = np.array([-90, 0, 90, 270])
    centers = np.deg2rad(centers_deg) if azi_unit == "chi / rad" else centers_deg
    width = np.deg2rad(20) if azi_unit == "chi / rad" else 20
    plugin.set_param_value("azi_unit", azi_unit)
    plugin.set_param_value("azi_sector_centers", ";".join(str(c) for c in centers))
    plugin.set_param_value("azi_sector_width", width)
    plugin.pre_execute()

    result, kwargs = plugin.execute(image)

    assert isinstance(result, Dataset)
    assert result.shape == (4, 3)
    np.testing.assert_allclose(result.axis_ranges[0], centers)
    assert result.axis_units[0] == azi_unit.split("/")[1].strip()
    np.testing.assert_array_equal(result.axis_ranges[1], [0.1, 0.2, 0.3])
    np.testing.assert_array_equal(
        result.array, np.arange(3)[None, :] + 10 * np.arange(4)[:, None]
    )
    assert kwargs == {}
    _, integrators = integration_backend
    np.testing.assert_allclose(
        [ai.integrate1d.call_args.kwargs["azimuth_range"] for ai in integrators],
        np.column_stack((centers_deg - 10, centers_deg + 10)),
    )
    for integrator in integrators:
        integrator.integrate1d.assert_called_once()
        passed_image = integrator.integrate1d.call_args.args[0]
        assert type(passed_image) is np.ndarray
        assert np.shares_memory(passed_image, image)
        np.testing.assert_array_equal(passed_image, image)


@pytest.mark.parametrize(
    "rad_unit", ["Q / nm^-1", "Q / A^-1", "2theta / deg", "2theta / rad", "r / mm"]
)
@pytest.mark.parametrize("int_method", ["CSR", "CSR full", "LUT", "LUT full"])
@pytest.mark.parametrize("correct_solid_angle", [0, 1])
def test_execute__integration_options_and_metadata(
    sector_plugin: PyFAIazimuthalSectorIntegration,
    integration_backend: tuple[Mock, list[Mock]],
    rad_unit: str,
    int_method: str,
    correct_solid_angle: int,
) -> None:
    ### This test was written by an AI tool.
    sector_plugin.set_param_values(
        rad_unit=rad_unit,
        rad_npoint=7,
        rad_use_range="Specify radial range",
        rad_range_lower=0.1,
        rad_range_upper=0.3,
        polarization_factor=0.75,
        correct_solid_angle=correct_solid_angle,
        int_method=int_method,
    )
    sector_plugin.pre_execute()
    result, _ = sector_plugin.execute(np.ones((32, 32)))
    assert result.shape == (4, 7)
    label, unit = (value.strip() for value in rad_unit.split("/"))
    assert result.axis_labels == {0: "chi", 1: label}
    assert result.axis_units == {0: "deg", 1: unit}
    assert result.data_label == "integrated intensity"
    assert result.data_unit == "counts"
    for integrator in integration_backend[1]:
        assert integrator.integrate1d.call_args.args[1] == 7
        options = integrator.integrate1d.call_args.kwargs
        assert options["unit"] == pyFAI_UNITS[rad_unit]
        assert options["radial_range"] == (0.1, 0.3)
        assert options["polarization_factor"] == 0.75
        assert options["correctSolidAngle"] == correct_solid_angle
        assert options["method"] == pyFAI_METHOD[int_method]


def test_execute__automatic_radial_range(
    sector_plugin: PyFAIazimuthalSectorIntegration,
    integration_backend: tuple[Mock, list[Mock]],
) -> None:
    ### This test was written by an AI tool.
    sector_plugin.set_param_value("rad_use_range", "Full detector")
    sector_plugin.pre_execute()
    sector_plugin.execute(np.ones((32, 32)))
    for integrator in integration_backend[1]:
        assert integrator.integrate1d.call_args.kwargs["radial_range"] is None


def test_execute__preserves_input_and_kwargs(
    sector_plugin: PyFAIazimuthalSectorIntegration, image: np.ndarray
) -> None:
    ### This test was written by an AI tool.
    sector_plugin.pre_execute()
    original = image.copy()
    context = {"frame": 7}
    result, kwargs = sector_plugin.execute(image, context=context, index=2)
    assert kwargs == {"context": context, "index": 2}
    assert kwargs["context"] is context
    assert not np.shares_memory(result, image)
    np.testing.assert_array_equal(image, original)
    if isinstance(image, Dataset):
        assert image.axis_labels == {0: "detector y", 1: "detector x"}
        assert image.axis_units == {0: "pixel", 1: "pixel"}
        assert image.data_label == "input intensity"


def test_execute__repeated_calls_produce_independent_results(
    sector_plugin: PyFAIazimuthalSectorIntegration,
    integration_backend: tuple[Mock, list[Mock]],
) -> None:
    ### This test was written by an AI tool.
    sector_plugin.pre_execute()
    first, first_kwargs = sector_plugin.execute(np.ones((32, 32)), index=0)
    original = first.array.copy()
    second, second_kwargs = sector_plugin.execute(np.zeros((32, 32)), index=1)
    np.testing.assert_array_equal(second.array, original)
    assert not np.shares_memory(first, second)
    second[:] = -1
    np.testing.assert_array_equal(first.array, original)
    assert first_kwargs == {"index": 0}
    assert second_kwargs == {"index": 1}
    for integrator in integration_backend[1]:
        assert integrator.integrate1d.call_count == 2
        np.testing.assert_array_equal(
            integrator.integrate1d.call_args.args[0], np.zeros((32, 32))
        )


def test_execute__propagates_integration_errors(
    sector_plugin: PyFAIazimuthalSectorIntegration,
    integration_backend: tuple[Mock, list[Mock]],
) -> None:
    ### This test was written by an AI tool.
    sector_plugin.pre_execute()
    integration_backend[1][0].integrate1d.side_effect = RuntimeError(
        "integration failed"
    )
    with pytest.raises(RuntimeError, match="integration failed"):
        sector_plugin.execute(np.ones((32, 32)))


def test_execute__custom_mask_applies_to_all_sectors(
    sector_plugin: PyFAIazimuthalSectorIntegration,
    integration_backend: tuple[Mock, list[Mock]],
) -> None:
    ### This test was written by an AI tool.
    sector_plugin.pre_execute()
    mask = np.eye(32, dtype=np.uint8)
    _, kwargs = sector_plugin.execute(np.ones((32, 32)), custom_mask=mask)
    assert kwargs["custom_mask"] is mask
    for integrator in integration_backend[1]:
        assert integrator.set_mask.call_args.args[0] is mask


def test_execute__restores_detector_mask_after_custom_mask(
    sector_plugin: PyFAIazimuthalSectorIntegration,
    integration_backend: tuple[Mock, list[Mock]],
    detector_mask: np.ndarray,
) -> None:
    ### This test was written by an AI tool.
    sector_plugin.pre_execute()
    sector_plugin.execute(np.ones((32, 32)), custom_mask=np.eye(32))
    sector_plugin.execute(np.ones((32, 32)))
    for integrator in integration_backend[1]:
        np.testing.assert_array_equal(
            integrator.set_mask.call_args.args[0], detector_mask
        )


@pytest.mark.xfail(
    strict=True,
    reason="The base plugin does not clear a custom mask without a detector mask.",
)
def test_execute__clears_custom_mask_without_detector_mask(
    sector_plugin: PyFAIazimuthalSectorIntegration,
    integration_backend: tuple[Mock, list[Mock]],
) -> None:
    ### This test was written by an AI tool.
    sector_plugin.pre_execute()
    sector_plugin.execute(np.ones((32, 32)), custom_mask=np.eye(32))
    for integrator in integration_backend[1]:
        integrator.set_mask.reset_mock()
    sector_plugin.execute(np.ones((32, 32)))
    for integrator in integration_backend[1]:
        integrator.set_mask.assert_called_with(None)


@pytest.mark.parametrize("azi_unit", ["chi / deg", "chi / rad"])
def test_execute__real_pyfai_matches_individual_sectors(
    experiment: DiffractionExperiment, azi_unit: str, image: np.ndarray
) -> None:
    ### This test was written by an AI tool.
    centers_deg = np.array([-90, 0, 90])
    centers = np.deg2rad(centers_deg) if azi_unit == "chi / rad" else centers_deg
    width = np.deg2rad(20) if azi_unit == "chi / rad" else 20
    plugin = PyFAIazimuthalSectorIntegration(
        diffraction_exp=experiment,
        azi_unit=azi_unit,
        azi_sector_centers=";".join(str(c) for c in centers),
        azi_sector_width=width,
        rad_npoint=8,
        rad_unit="2theta / deg",
        int_method="CSR",
        correct_solid_angle=False,
        polarization_factor=0,
    )
    plugin.pre_execute()
    result, _ = plugin.execute(image)
    reference = AzimuthalIntegrator(
        dist=0.1,
        poni1=0.0016,
        poni2=0.0016,
        detector=experiment.get_detector(),
        wavelength=1e-10,
    )
    raw_image = image.array if isinstance(image, Dataset) else image
    for index, center in enumerate(centers_deg):
        expected = reference.integrate1d(
            raw_image,
            8,
            azimuth_range=(center - 10, center + 10),
            unit="2th_deg",
            method=pyFAI_METHOD["CSR"],
            correctSolidAngle=False,
            polarization_factor=0,
        )
        np.testing.assert_allclose(result.array[index], expected.intensity)
        np.testing.assert_allclose(result.axis_ranges[1], expected.radial)
    assert result.shape == (3, 8)
    assert np.any(result.array > 0)
    np.testing.assert_allclose(result.axis_ranges[0], centers)
    assert result.axis_units == {0: azi_unit.split("/")[1].strip(), 1: "deg"}


if __name__ == "__main__":
    pytest.main([__file__])
