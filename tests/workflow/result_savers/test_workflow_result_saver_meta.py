# This file is part of pydidas.
#
# pydidas is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
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
__copyright__ = "Copyright 2021-2022, Malte Storm, Helmholtz-Zentrum Hereon"
__license__ = "GPL-3.0"
__maintainer__ = "Malte Storm"
__status__ = "Development"


import unittest

import numpy as np

from pydidas.core import Dataset
from pydidas.workflow import WorkflowTree, WorkflowResults
from pydidas.experiment import ScanSetup
from pydidas.workflow.result_savers import (
    WorkflowResultSaverBase,
    WorkflowResultSaverMeta,
)


TREE = WorkflowTree()
SCAN = ScanSetup()
RESULTS = WorkflowResults()
META = WorkflowResultSaverMeta


def export_frame_to_file(saver, index, frame_result_dict, **kwargs):
    saver._exported = {
        "index": index,
        "frame_results": frame_result_dict,
        "kwargs": kwargs,
    }


def export_full_data_to_file(saver, full_data):
    saver._exported = {"full_data": full_data}


def prepare_files_and_directories(saver, save_dir, shapes, labels, data_labels):
    saver._prepared = {
        "save_dir": save_dir,
        "shapes": shapes,
        "labels": labels,
        "data_labels": data_labels,
    }


def update_frame_metadata(saver, metadata):
    saver._metadata = metadata


class TestWorkflowResultsSaverMeta(unittest.TestCase):
    def setUp(self):
        self._meta_registry = META.registry.copy()
        META.reset()

    def tearDown(self):
        META.reset()
        META.registry = self._meta_registry

    def create_saver_class(self, title, ext):
        _cls = META(
            title.upper(),
            (WorkflowResultSaverBase,),
            dict(extensions=[ext.upper()], format_name=ext),
        )
        return _cls

    def get_save_dir_label_and_shapes(self):
        _save_dir = "dummy/directory/to/nowhere"
        _shapes = {1: (10, 10), 2: (11, 27)}
        _labels = {1: "unknown", 2: "result no 2"}
        _data_labels = {1: "Intensity", 2: "Area"}
        return _save_dir, _shapes, _labels, _data_labels

    def generate_test_metadata(self):
        _, _shapes, _, _ = self.get_save_dir_label_and_shapes()
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
        self.create_saver_class("SAVER", "Test")
        self.create_saver_class("SAVER2", "Test2")
        META.set_active_savers_and_title(["TEST", "TEST2"], _title)
        self.assertTrue("TEST" in META.active_savers)
        self.assertTrue("TEST2" in META.active_savers)
        self.assertEqual(META.scan_title, _title)

    def test_set_active_savers_and_title__not_registered(self):
        self.create_saver_class("SAVER", ".Test")
        with self.assertRaises(KeyError):
            META.set_active_savers_and_title(["TEST", "TEST2"])

    def test_export_frame_to_file(self):
        _index = 127
        _frame_results = {1: np.random.random((10, 10)), 2: np.random.random((11, 27))}
        _Saver = self.create_saver_class("SAVER", "Test")
        _Saver.export_frame_to_file = classmethod(export_frame_to_file)
        META.export_frame_to_file(_index, "TEST", _frame_results)
        self.assertTrue(
            np.equal(_Saver._exported["frame_results"][1], _frame_results[1]).all()
        )
        self.assertTrue(
            np.equal(_Saver._exported["frame_results"][2], _frame_results[2]).all()
        )

    def test_export_frame_to_active_savers(self):
        _index = 127
        _frame_results = {1: np.random.random((10, 10)), 2: np.random.random((11, 27))}
        _Saver = self.create_saver_class("SAVER", "Test")
        _Saver.export_frame_to_file = classmethod(export_frame_to_file)
        META.set_active_savers_and_title(["TEST"])
        META.export_frame_to_active_savers(_index, _frame_results)
        self.assertTrue(
            np.equal(_Saver._exported["frame_results"][1], _frame_results[1]).all()
        )
        self.assertTrue(
            np.equal(_Saver._exported["frame_results"][2], _frame_results[2]).all()
        )

    def test_push_frame_metadata_to_active_savers(self):
        _metadata = self.generate_test_metadata()
        _Saver = self.create_saver_class("SAVER", "Test")
        _Saver.update_frame_metadata = classmethod(update_frame_metadata)
        META.set_active_savers_and_title(["TEST"])
        META.push_frame_metadata_to_active_savers(_metadata)
        self.assertEqual(_Saver._metadata, _metadata)

    def test_export_full_data_to_active_savers(self):
        _results = {
            1: np.random.random((10, 10, 10)),
            2: np.random.random((11, 27, 25)),
        }
        _Saver = self.create_saver_class("SAVER", "Test")
        _Saver.export_full_data_to_file = classmethod(export_full_data_to_file)
        META.set_active_savers_and_title(["TEST"])
        META.export_full_data_to_active_savers(_results)
        self.assertTrue(np.equal(_Saver._exported["full_data"][1], _results[1]).all())
        self.assertTrue(np.equal(_Saver._exported["full_data"][2], _results[2]).all())

    def test_export_full_data_to_file(self):
        _frame_results = {
            1: np.random.random((10, 10, 10)),
            2: np.random.random((11, 27, 25)),
        }
        _Saver = self.create_saver_class("SAVER", "Test")
        _Saver.export_full_data_to_file = classmethod(export_full_data_to_file)
        META.export_full_data_to_file("TEST", _frame_results)
        self.assertTrue(
            np.equal(_Saver._exported["full_data"][1], _frame_results[1]).all()
        )
        self.assertTrue(
            np.equal(_Saver._exported["full_data"][2], _frame_results[2]).all()
        )

    def test_prepare_active_savers(self):
        _save_dir, _shapes, _labels, _data_labels = self.get_save_dir_label_and_shapes()
        _Saver = self.create_saver_class("SAVER", "Test")
        _Saver.prepare_files_and_directories = classmethod(
            prepare_files_and_directories
        )
        META.set_active_savers_and_title(["TEST"])
        META.prepare_active_savers(_save_dir, _shapes, _labels, _data_labels)
        self.assertEqual(_Saver._prepared["save_dir"], _save_dir)
        self.assertEqual(_Saver._prepared["shapes"], _shapes)
        self.assertEqual(_Saver._prepared["labels"], _labels)
        self.assertEqual(_Saver._prepared["data_labels"], _data_labels)

    def test_prepare_saver(self):
        _save_dir, _shapes, _labels, _data_labels = self.get_save_dir_label_and_shapes()
        _Saver = self.create_saver_class("SAVER", "Test")
        _Saver.prepare_files_and_directories = classmethod(
            prepare_files_and_directories
        )
        META.prepare_saver("TEST", _save_dir, _shapes, _labels, _data_labels)
        self.assertEqual(_Saver._prepared["save_dir"], _save_dir)
        self.assertEqual(_Saver._prepared["shapes"], _shapes)
        self.assertEqual(_Saver._prepared["labels"], _labels)
        self.assertEqual(_Saver._prepared["data_labels"], _data_labels)

    def test_prepare_saver__no_such_saver(self):
        _save_dir, _shapes, _labels, _data_labels = self.get_save_dir_label_and_shapes()
        with self.assertRaises(KeyError):
            META.prepare_saver("TEST", _save_dir, _shapes, _labels, _data_labels)


if __name__ == "__main__":
    unittest.main()
