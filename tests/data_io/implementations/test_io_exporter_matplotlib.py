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
# Parts of this file have been created using AI tools.

"""Unit tests for pydidas.data_io.implementations.io_exporter_matplotlib module."""

__author__ = "Malte Storm"
__copyright__ = "Copyright 2026, Helmholtz-Zentrum Hereon"
__license__ = "GPL-3.0-only"
__maintainer__ = "Malte Storm"
__status__ = "Production"


from unittest.mock import patch

import numpy as np
import pytest

from tests.data_io.implementations.test_io_base import IoBaseTests

from pydidas.core import Dataset
from pydidas.data_io.implementations.io_exporter_matplotlib import IoExporterMatplotlib


@pytest.fixture
def io_class():
    return IoExporterMatplotlib


@pytest.fixture
def data_2d():
    return np.random.default_rng(0).random((20, 25))


@pytest.fixture
def data_1d():
    return np.random.default_rng(1).random(50)


class TestIoExporterMatplotlib(IoBaseTests):
    """Runs the generic IoBase tests against IoExporterMatplotlib."""


def test_class_dimensions():
    assert IoExporterMatplotlib.dimensions == [1, 2]


def test_class_extensions_export_empty():
    assert IoExporterMatplotlib.extensions_export == []


def test_class_extensions_import_empty():
    assert IoExporterMatplotlib.extensions_import == []


def test_export_to_file__dispatches_1d_to_plot(tmp_path, data_1d):
    with (
        patch.object(IoExporterMatplotlib, "export_matplotlib_plot") as mock_plot,
        patch.object(IoExporterMatplotlib, "export_matplotlib_figure") as mock_fig,
    ):
        IoExporterMatplotlib.export_to_file(tmp_path / "test.png", data_1d)
    mock_plot.assert_called_once()
    mock_fig.assert_not_called()


def test_export_to_file__dispatches_2d_to_figure(tmp_path, data_2d):
    with (
        patch.object(IoExporterMatplotlib, "export_matplotlib_plot") as mock_plot,
        patch.object(IoExporterMatplotlib, "export_matplotlib_figure") as mock_fig,
    ):
        IoExporterMatplotlib.export_to_file(tmp_path / "test.png", data_2d)
    mock_fig.assert_called_once()
    mock_plot.assert_not_called()


def test_export_matplotlib_figure__creates_file(tmp_path, data_2d):
    _fname = tmp_path / "fig.png"
    IoExporterMatplotlib.export_matplotlib_figure(_fname, data_2d)
    assert _fname.exists()


def test_export_matplotlib_figure__raises_if_file_exists(tmp_path, data_2d):
    _fname = tmp_path / "fig.png"
    IoExporterMatplotlib.export_matplotlib_figure(_fname, data_2d)
    with pytest.raises(FileExistsError):
        IoExporterMatplotlib.export_matplotlib_figure(_fname, data_2d)


def test_export_matplotlib_figure__overwrite(tmp_path, data_2d):
    _fname = tmp_path / "fig.png"
    IoExporterMatplotlib.export_matplotlib_figure(_fname, data_2d)
    IoExporterMatplotlib.export_matplotlib_figure(_fname, data_2d, overwrite=True)
    assert _fname.exists()


def test_export_matplotlib_figure__w_plain_ndarray(tmp_path):
    _fname = tmp_path / "fig_array.png"
    IoExporterMatplotlib.export_matplotlib_figure(
        _fname, np.random.default_rng(2).random((15, 20))
    )
    assert _fname.exists()


def test_export_matplotlib_figure__w_dataset(tmp_path):
    _fname = tmp_path / "fig_ds.png"
    IoExporterMatplotlib.export_matplotlib_figure(
        _fname, Dataset(np.random.default_rng(3).random((15, 20)))
    )
    assert _fname.exists()


def test_export_matplotlib_figure__w_colormap(tmp_path, data_2d):
    _fname = tmp_path / "fig_cmap.png"
    IoExporterMatplotlib.export_matplotlib_figure(_fname, data_2d, colormap="viridis")
    assert _fname.exists()


def test_export_matplotlib_figure__w_data_range(tmp_path, data_2d):
    _fname = tmp_path / "fig_range.png"
    IoExporterMatplotlib.export_matplotlib_figure(
        _fname, data_2d, data_range=(0.2, 0.8)
    )
    assert _fname.exists()


def test_export_matplotlib_plot__creates_file(tmp_path, data_1d):
    _fname = tmp_path / "plot.png"
    IoExporterMatplotlib.export_matplotlib_plot(_fname, data_1d)
    assert _fname.exists()


def test_export_matplotlib_plot__raises_if_file_exists(tmp_path, data_1d):
    _fname = tmp_path / "plot.png"
    IoExporterMatplotlib.export_matplotlib_plot(_fname, data_1d)
    with pytest.raises(FileExistsError):
        IoExporterMatplotlib.export_matplotlib_plot(_fname, data_1d)


def test_export_matplotlib_plot__overwrite(tmp_path, data_1d):
    _fname = tmp_path / "plot.png"
    IoExporterMatplotlib.export_matplotlib_plot(_fname, data_1d)
    IoExporterMatplotlib.export_matplotlib_plot(_fname, data_1d, overwrite=True)
    assert _fname.exists()


def test_export_matplotlib_plot__w_plain_ndarray(tmp_path):
    _fname = tmp_path / "plot_array.png"
    IoExporterMatplotlib.export_matplotlib_plot(
        _fname, np.random.default_rng(4).random(50)
    )
    assert _fname.exists()


def test_export_matplotlib_plot__w_dataset(tmp_path):
    _data = Dataset(np.random.default_rng(5).random(50))
    _data.update_axis_range(0, np.linspace(0, 10, 50))
    _fname = tmp_path / "plot_ds.png"
    IoExporterMatplotlib.export_matplotlib_plot(_fname, _data)
    assert _fname.exists()


def test_export_matplotlib_plot__w_data_range(tmp_path, data_1d):
    _fname = tmp_path / "plot_range.png"
    IoExporterMatplotlib.export_matplotlib_plot(_fname, data_1d, data_range=(0.2, 0.8))
    assert _fname.exists()


if __name__ == "__main__":
    pytest.main([__file__])
