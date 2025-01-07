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

import shutil
import tempfile
import unittest
from pathlib import Path

import numpy as np
from qtpy import QtCore

from pydidas.contexts import ScanContext
from pydidas.core import FileReadError
from pydidas.plugins import BasePlugin
from pydidas.unittest_objects import LocalPluginCollection


COLLECTION = LocalPluginCollection()

SCAN = ScanContext()


class TestFioMcaLineSeriesLoader(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls._path = Path(tempfile.mkdtemp())
        cls._n_channels = 2048
        cls._n_dirs = 13
        cls._n_files = 11
        cls._n = cls._n_files * cls._n_dirs
        cls._header = (
            "!\n! Comments\n!\n%c\nPosition "
            + "{position:.2f}, Index {index:d}\n"
            + "!\n! Parameter\n%p\nSample_time = 5 \n!\n! Data \n%d\n"
            + " Col 1 dummy_spectrum FLOAT\n"
        )
        cls._data = np.repeat(
            np.arange(cls._n, dtype=np.uint16), cls._n_channels
        ).reshape((cls._n, cls._n_channels))
        cls._params = {}
        cls._global_fnames = {}
        cls._name_pattern = "test_#####"
        for _i in range(cls._n_dirs):
            _tmpname = cls._name_pattern.replace("#####", f"{1+_i:05d}")
            _dir = cls._path.joinpath(_tmpname)
            _dir.mkdir()
            for _ifile in range(cls._n_files):
                _fname = _dir.joinpath(f"{_tmpname}_mca_s{_ifile + 1}.fio")
                _global_index = _ifile + _i * cls._n_files
                cls._global_fnames[_global_index] = _fname
                with open(_fname, "w") as _file:
                    _file.write(cls._header.format(position=12 * _ifile, index=_ifile))
                    _file.write("\n".join(str(val) for val in cls._data[_global_index]))

    @classmethod
    def tearDownClass(cls):
        shutil.rmtree(cls._path)
        qs = QtCore.QSettings("Hereon", "pydidas")
        qs.remove("unittesting")

    def setUp(self):
        SCAN.restore_all_defaults(True)
        SCAN.set_param_value("scan_name_pattern", self._name_pattern)
        SCAN.set_param_value("scan_base_directory", self._path)
        SCAN.set_param_value("scan_start_index", 1)

    def tearDown(self):
        SCAN.restore_all_defaults(True)

    def create_standard_plugin(self):
        plugin = COLLECTION.get_plugin_by_name("FioMcaLineScanSeriesLoader")()
        for _key, _val in self._params.items():
            plugin.set_param_value(_key, _val)
        return plugin

    def test_creation(self):
        plugin = COLLECTION.get_plugin_by_name("FioMcaLineScanSeriesLoader")()
        self.assertIsInstance(plugin, BasePlugin)

    def test_update_filename_string(self):
        plugin = self.create_standard_plugin()
        plugin.update_filename_string()
        _fname = plugin.filename_string.format(index0=1, index1=2)
        self.assertTrue(Path(_fname).is_file())

    def test_check_files_per_directory__no_preset(self):
        plugin = self.create_standard_plugin()
        plugin.update_filename_string()
        plugin._check_files_per_directory()
        self.assertEqual(
            plugin.get_param_value("_counted_files_per_directory"), self._n_files
        )

    def test_check_files_per_directory__no_preset_wrong_dir(self):
        plugin = self.create_standard_plugin()
        plugin.update_filename_string()
        SCAN.set_param_value("scan_start_index", 12345)
        with self.assertRaises(FileReadError):
            plugin._check_files_per_directory()

    def test_check_files_per_directory__w_preset(self):
        _new_n_files = 7
        plugin = self.create_standard_plugin()
        plugin.set_param_value("files_per_directory", _new_n_files)
        plugin.update_filename_string()
        plugin._check_files_per_directory()
        self.assertEqual(
            plugin.get_param_value("_counted_files_per_directory"), _new_n_files
        )

    def test_determine_header_size(self):
        plugin = self.create_standard_plugin()
        plugin.update_filename_string()
        plugin._check_files_per_directory()
        plugin._determine_header_size()
        with open(plugin.get_filename(0), "r") as f:
            _n_header_lines = len(f.readlines()) - self._n_channels
        self.assertEqual(_n_header_lines, plugin._config["header_lines"])

    def test_determine_header_size__file_does_not_exist(self):
        plugin = self.create_standard_plugin()
        plugin.set_param_value("fio_suffix", "_something_s#.fio")
        plugin.update_filename_string()
        plugin._check_files_per_directory()
        with self.assertRaises(FileReadError):
            plugin._determine_header_size()

    def test_get_filename__start(self):
        plugin = self.create_standard_plugin()
        plugin.update_filename_string()
        _name = plugin.get_filename(0)
        self.assertEqual(Path(_name), self._global_fnames[0])

    def test_get_filename__second_dir(self):
        plugin = self.create_standard_plugin()
        plugin.update_filename_string()
        plugin._check_files_per_directory()
        _name = plugin.get_filename(self._n_files)
        self.assertEqual(Path(_name), self._global_fnames[self._n_files])

    def test_determine_roi__no_roi(self):
        plugin = self.create_standard_plugin()
        plugin.pre_execute()
        self.assertIsNone(plugin._config["roi"])

    def test_determine_roi__roi_no_abs_energy(self):
        plugin = self.create_standard_plugin()
        plugin.set_param_value("use_roi", True)
        plugin.set_param_value("roi_xlow", 128)
        plugin.set_param_value("roi_xhigh", 256)
        plugin.pre_execute()
        self.assertEqual(plugin._config["roi"], slice(128, 256))

    def test_get_frame__no_file(self):
        _i_image = 37
        plugin = self.create_standard_plugin()
        plugin.pre_execute()
        plugin.set_param_value("fio_suffix", "_something_s#.fio")
        plugin.update_filename_string()
        with self.assertRaises(FileReadError):
            _data, _ = plugin.get_frame(_i_image)

    def test_get_frame__no_energy_scale(self):
        _i_image = 37
        plugin = self.create_standard_plugin()
        plugin.pre_execute()
        _data, _ = plugin.get_frame(_i_image)
        self.assertTrue(np.all(_data == _i_image))
        self.assertTrue(np.allclose(_data.axis_ranges[0], np.arange(_data.size)))

    def test_get_frame__no_energy_scale_w_roi(self):
        _i_image = 37
        plugin = self.create_standard_plugin()
        plugin.set_param_value("use_roi", True)
        plugin.set_param_value("roi_xlow", 128)
        plugin.set_param_value("roi_xhigh", 256)
        plugin.pre_execute()
        _data, _ = plugin.get_frame(_i_image)
        self.assertTrue(np.all(_data == _i_image))
        self.assertTrue(np.allclose(_data.axis_ranges[0], np.arange(128, 256)))

    def test_get_frame__w_energy_scale(self):
        _i_image = 42
        _delta = 2.5
        _offset = 150
        plugin = self.create_standard_plugin()
        plugin.set_param_value("use_absolute_energy", True)
        plugin.set_param_value("energy_offset", _offset)
        plugin.set_param_value("energy_delta", _delta)
        plugin.pre_execute()
        _data, _ = plugin.get_frame(_i_image)
        self.assertTrue(np.all(_data == _i_image))
        self.assertTrue(
            np.allclose(_data.axis_ranges[0], np.arange(_data.size) * _delta + _offset)
        )

    def test_get_frame__w_energy_scale_and_roi(self):
        _i_image = 87
        _delta = 2.5
        _offset = 150

        plugin = self.create_standard_plugin()
        plugin.set_param_value("use_absolute_energy", True)
        plugin.set_param_value("energy_offset", _offset)
        plugin.set_param_value("energy_delta", _delta)
        plugin.set_param_value("use_roi", True)
        plugin.set_param_value("roi_xlow", 128)
        plugin.set_param_value("roi_xhigh", 256)
        plugin.pre_execute()
        _data, _ = plugin.get_frame(_i_image)
        self.assertTrue(np.all(_data == _i_image))
        self.assertTrue(
            np.allclose(_data.axis_ranges[0], np.arange(128, 256) * _delta + _offset)
        )

    def test_get_raw_input_size(self):
        plugin = self.create_standard_plugin()
        _n = plugin.get_raw_input_size()
        self.assertEqual(_n, self._n_channels)


if __name__ == "__main__":
    unittest.main()
