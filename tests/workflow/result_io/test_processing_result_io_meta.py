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


import os
import shutil
import tempfile
import unittest

import numpy as np

from pydidas.contexts import DiffractionExperimentContext, ScanContext
from pydidas.core import Dataset, UserConfigError
from pydidas.workflow import ProcessingResults, WorkflowTree
from pydidas.workflow.result_io import ProcessingResultIoBase, ProcessingResultIoMeta


TREE = WorkflowTree()
EXP = DiffractionExperimentContext()
SCAN = ScanContext()
RESULTS = ProcessingResults()
META = ProcessingResultIoMeta


def export_frame_to_file(saver, index, frame_result_dict, **kwargs):
    saver._exported = {
        "index": index,
        "frame_results": frame_result_dict,
        "kwargs": kwargs,
    }


def export_full_data_to_file(saver, full_data, scan, squeeze: bool = False):
    saver._exported = {"full_data": full_data, "squeeze": squeeze}


def prepare_files_and_directories(
    saver,
    save_dir,
    node_info,
    scan_context=None,
    diffraction_exp_context=None,
    workflow_tree=None,
):
    saver._prepared = {
        "save_dir": save_dir,
        "node_info": node_info,
        "scan": scan_context,
        "exp": diffraction_exp_context,
        "tree": workflow_tree,
    }


def import_results(saver, fname):
    if os.path.basename(fname) == "node_01.TEST":
        _id = 1
    elif os.path.basename(fname) == "node_03.TEST":
        _id = 3
    _data = {
        1: Dataset(np.arange(100).reshape((10, 10)) + 42.1),
        3: Dataset(np.arange(400).reshape((20, 20)) - 1.2),
    }
    _node_info = {
        1: {
            "shape": (10, 10),
            "plugin_name": "Ye olde plugin",
            "data_label": "The data",
            "node_label": "SPAM SPAM SPAM",
        },
        3: {
            "shape": (20, 20),
            "plugin_name": "A new plugin",
            "data_label": "Label the data",
            "node_label": "HAM and EGGS",
        },
    }
    return _data[_id], _node_info[_id], SCAN, EXP, TREE


def update_metadata(saver, metadata, scan):
    saver._metadata = metadata


class TestProcessingResultsSaverMeta(unittest.TestCase):
    def setUp(self):
        self._meta_registry = META.registry.copy()
        self._dir = tempfile.mkdtemp()

        META.reset()

    def tearDown(self):
        META.reset()
        META.registry = self._meta_registry
        shutil.rmtree(self._dir)

    def create_saver_class(self, title, ext):
        _cls = META(
            title.upper(),
            (ProcessingResultIoBase,),
            dict(extensions=[ext.lower()], format_name=ext),
        )
        return _cls

    def get_save_dir_and_node_info(self):
        _save_dir = "dummy/directory/to/nowhere"
        _shapes = {1: (10, 10), 2: (11, 27)}
        _node_labels = {1: "unknown", 2: "result no 2"}
        _data_labels = {1: "Intensity", 2: "Area"}
        _plugin_names = {1: "ye olde plugin", 2: "SPAM SPAM SPAM"}
        _node_info = {
            _id: {
                "shape": _shapes[_id],
                "node_label": _node_labels[_id],
                "data_label": _data_labels[_id],
                "plugin_name": _plugin_names[_id],
            }
            for _id in _shapes.keys()
        }
        return _save_dir, _node_info

    def generate_test_metadata(self):
        _, _node_info = self.get_save_dir_and_node_info()
        _shapes = {_id: _node_info[_id]["shape"] for _id in _node_info}
        _res1 = Dataset(
            np.random.random(_shapes[1]),
            axis_units=["m", "mm"],
            axis_labels=["dim1", "dim 2"],
            axis_ranges=[
                np.arange(_shapes[1][0]),
                _shapes[1][1] - np.arange(_shapes[1][1]),
            ],
        )
        _res2 = Dataset(
            np.random.random(_shapes[2]),
            axis_units=["m", "Test"],
            axis_labels=["dim1", "2nd dim"],
            axis_ranges=[12 + np.arange(_shapes[2][0]), 4 + np.arange(_shapes[2][1])],
        )
        _meta1 = {
            "axis_units": _res1.axis_units,
            "axis_labels": _res1.axis_labels,
            "axis_ranges": _res1.axis_ranges,
        }
        _meta2 = {
            "axis_units": _res2.axis_units,
            "axis_labels": _res2.axis_labels,
            "axis_ranges": _res2.axis_ranges,
        }
        return {1: _meta1, 2: _meta2}

    def test_class_type(self):
        self.assertEqual(META.__class__, type)

    def test_class_attributes(self):
        self.assertTrue(hasattr(META, "registry"))
        self.assertTrue(hasattr(META, "active_savers"))

    def test_set_active_savers_and_title(self):
        _title = "no title"
        self.create_saver_class("SAVER", ".Test")
        self.create_saver_class("SAVER2", ".Test2")
        META.set_active_savers_and_title([".TEST", ".TEST2"], _title)
        self.assertTrue(".test" in META.active_savers)
        self.assertTrue(".test2" in META.active_savers)
        self.assertEqual(META.scan_title, _title)

    def test_set_active_savers_and_title__not_registered(self):
        self.create_saver_class("SAVER", ".Test")
        with self.assertRaises(UserConfigError):
            META.set_active_savers_and_title([".TEST", ".TEST2"])

    def test_export_frame_to_file(self):
        _index = 127
        _frame_results = {1: np.random.random((10, 10)), 2: np.random.random((11, 27))}
        _Saver = self.create_saver_class("SAVER", ".Test")
        _Saver.export_frame_to_file = classmethod(export_frame_to_file)
        META.export_frame_to_file(_index, ".TEST", _frame_results)
        self.assertTrue(
            np.equal(_Saver._exported["frame_results"][1], _frame_results[1]).all()
        )
        self.assertTrue(
            np.equal(_Saver._exported["frame_results"][2], _frame_results[2]).all()
        )

    def test_export_frame_to_active_savers(self):
        _index = 127
        _frame_results = {1: np.random.random((10, 10)), 2: np.random.random((11, 27))}
        _Saver = self.create_saver_class("SAVER", ".Test")
        _Saver.export_frame_to_file = classmethod(export_frame_to_file)
        META.set_active_savers_and_title([".TEST"])
        META.export_frame_to_active_savers(_index, _frame_results)
        self.assertTrue(
            np.equal(_Saver._exported["frame_results"][1], _frame_results[1]).all()
        )
        self.assertTrue(
            np.equal(_Saver._exported["frame_results"][2], _frame_results[2]).all()
        )

    def test_push_metadata_to_active_savers(self):
        _metadata = self.generate_test_metadata()
        _Saver = self.create_saver_class("SAVER", ".Test")
        _Saver.update_metadata = classmethod(update_metadata)
        META.set_active_savers_and_title([".TEST"])
        META.push_metadata_to_active_savers(_metadata)
        self.assertEqual(_Saver._metadata, _metadata)

    def test_export_full_data_to_active_savers(self):
        _results = {
            1: np.random.random((10, 10, 10)),
            2: np.random.random((11, 27, 25)),
        }
        _Saver = self.create_saver_class("SAVER", ".Test")
        _Saver.export_full_data_to_file = classmethod(export_full_data_to_file)
        META.set_active_savers_and_title([".TEST"])
        META.export_full_data_to_active_savers(_results)
        self.assertTrue(np.allclose(_Saver._exported["full_data"][1], _results[1]))
        self.assertTrue(np.allclose(_Saver._exported["full_data"][2], _results[2]))

    def test_export_full_data_to_file(self):
        _frame_results = {
            1: np.random.random((10, 10, 10)),
            2: np.random.random((11, 27, 25)),
        }
        _Saver = self.create_saver_class("SAVER", ".Test")
        _Saver.export_full_data_to_file = classmethod(export_full_data_to_file)
        META.export_full_data_to_file(".TEST", _frame_results)
        self.assertTrue(
            np.allclose(_Saver._exported["full_data"][1], _frame_results[1])
        )
        self.assertTrue(
            np.allclose(_Saver._exported["full_data"][2], _frame_results[2])
        )

    def test_prepare_active_savers(self):
        _save_dir, _node_info = self.get_save_dir_and_node_info()
        _Saver = self.create_saver_class("SAVER", ".Test")
        _Saver.prepare_files_and_directories = classmethod(
            prepare_files_and_directories
        )
        META.set_active_savers_and_title([".TEST"])
        META.prepare_active_savers(_save_dir, _node_info)
        self.assertEqual(_Saver._prepared["save_dir"], _save_dir)
        self.assertEqual(_Saver._prepared["node_info"], _node_info)

    def test_import_data_from_directory(self):
        _Saver = self.create_saver_class("SAVER", ".Test")
        _Saver.import_results_from_file = classmethod(import_results)
        for _id in [1, 3]:
            with open(os.path.join(self._dir, f"node_{_id:02d}.TEST"), "w") as _file:
                _file.write("dummy")
        _data, _node_info, _scan, exp, _tree = META.import_data_from_directory(
            self._dir
        )
        for _id in [1, 3]:
            self.assertTrue(
                np.allclose(
                    _data[_id], import_results(None, f"test/node_{_id:02d}.TEST")[0]
                )
            )
            self.assertEqual(
                _node_info[_id], import_results(None, f"test/node_{_id:02d}.TEST")[1]
            )
        self.assertEqual(_scan, import_results(None, f"test/node_{_id:02d}.TEST")[2])


if __name__ == "__main__":
    unittest.main()
