# This file is part of pydidas.
#
# Copyright 2023 - 2024, Helmholtz-Zentrum Hereon
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
__copyright__ = "Copyright 2023 - 2024, Helmholtz-Zentrum Hereon"
__license__ = "GPL-3.0-only"
__maintainer__ = "Malte Storm"
__status__ = "Production"


import copy
import pickle
import shutil
import tempfile
import unittest

import numpy as np

from pydidas.contexts import DiffractionExperimentContext
from pydidas.contexts.diff_exp import DiffractionExperiment
from pydidas.core import Parameter, UserConfigError, get_generic_parameter, utils
from pydidas.core.constants import BASE_PLUGIN
from pydidas.core.utils import rebin2d
from pydidas.data_io.utils import RoiSliceManager
from pydidas.plugins import BasePlugin
from pydidas.unittest_objects import create_plugin_class


EXP = DiffractionExperimentContext()


class TestLinkedObject:
    def __init__(self, params):
        self.params = params

    def get_param_value(self, key):
        return self.params.get_value(key)


class TestBasePlugin(unittest.TestCase):
    def setUp(self):
        self._pluginpath = tempfile.mkdtemp()
        self._class_names = []

    def tearDown(self):
        shutil.rmtree(self._pluginpath)

    def test_create_base_plugin(self):
        plugin = create_plugin_class(BASE_PLUGIN)
        self.assertIsInstance(plugin(), BasePlugin)

    def test_is_basic_plugin__this_class(self):
        for _plugin in [BasePlugin, BasePlugin()]:
            with self.subTest(plugin=_plugin):
                self.assertTrue(_plugin.is_basic_plugin())

    def test_is_basic_plugin__sub_class(self):
        _class = create_plugin_class(BASE_PLUGIN)
        for _plugin in [_class, _class()]:
            with self.subTest(plugin=_plugin):
                self.assertFalse(_plugin.is_basic_plugin())

    def test_input_data_property__None(self):
        plugin = create_plugin_class(BASE_PLUGIN)()
        self.assertIsNone(plugin.input_data)

    def test_input_data_property__value(self):
        _input = np.random.random((10, 10))
        plugin = create_plugin_class(BASE_PLUGIN)()
        plugin._config["input_data"] = _input
        self.assertTrue(np.allclose(plugin.input_data, _input))

    def test_store_input_data_copy(self):
        _input = np.random.random((10, 10))
        _kwargs = {"dummy": 2, "spam": "& ham", "42": True}
        _copy = copy.deepcopy(_input)
        plugin = create_plugin_class(BASE_PLUGIN)()
        plugin.store_input_data_copy(_input, **_kwargs)
        # change input to zeros to verify that a copy of the data has been stored:
        _input[:] = 0
        self.assertTrue(np.allclose(plugin._config["input_data"], _copy))
        self.assertEqual(plugin._config["input_kwargs"], _kwargs)
        self.assertTrue(np.sum(plugin._config["input_data"]) > 0)

    def test_get_class_description(self):
        plugin = create_plugin_class(BASE_PLUGIN)
        _text = plugin.get_class_description()
        self.assertIsInstance(_text, str)

    def test_get_class_description_as_dict(self):
        plugin = create_plugin_class(BASE_PLUGIN)
        _doc = plugin.get_class_description_as_dict()
        self.assertIsInstance(_doc, dict)
        for _key, _value in _doc.items():
            self.assertIsInstance(_key, str)
            self.assertIsInstance(_value, str)

    def test_class_atributes(self):
        plugin = create_plugin_class(BASE_PLUGIN)
        for att in (
            "plugin_type",
            "plugin_name",
            "default_params",
            "generic_params",
            "input_data_dim",
            "output_data_dim",
        ):
            self.assertTrue(hasattr(plugin, att))

    def test_get_single_ops_from_legacy__single_bin(self):
        _bin = 3
        _shape = (120, 120)
        _image = np.random.random((_shape))
        _final_image = rebin2d(_image, _bin)
        plugin = create_plugin_class(BASE_PLUGIN)()
        plugin._original_input_shape = _shape
        plugin._legacy_image_ops.append(["binning", _bin])
        _roi, _binning = plugin.get_single_ops_from_legacy()
        _new_image = rebin2d(_image[_roi], _binning)
        self.assertTrue(np.allclose(_final_image, _new_image))

    def test_get_single_ops_from_legacy__single_bin_with_crop(self):
        _bin = 3
        _shape = (121, 124)
        _image = np.random.random((_shape))
        _final_image = rebin2d(_image, _bin)
        plugin = create_plugin_class(BASE_PLUGIN)()
        plugin._legacy_image_ops.append(["binning", _bin])
        plugin._original_input_shape = _shape
        _roi, _binning = plugin.get_single_ops_from_legacy()
        _new_image = rebin2d(_image[_roi], _binning)
        self.assertTrue(np.allclose(_final_image, _new_image))

    def test_get_single_ops_from_legacy__multi_bin_with_crop(self):
        _bin = 3
        _bin2 = 4
        _bin3 = 2
        _shape = (1253, 1273)
        _image = np.random.random((_shape))
        _final_image = rebin2d(rebin2d(rebin2d(_image, _bin), _bin2), _bin3)
        plugin = create_plugin_class(BASE_PLUGIN)()
        plugin._original_input_shape = _shape
        plugin._legacy_image_ops.append(["binning", _bin])
        plugin._legacy_image_ops.append(["binning", _bin2])
        plugin._legacy_image_ops.append(["binning", _bin3])
        _roi, _binning = plugin.get_single_ops_from_legacy()
        _new_image = rebin2d(_image[_roi], _binning)
        self.assertTrue(np.allclose(_final_image, _new_image))

    def test_get_single_ops_from_legacy__roi(self):
        _roi1 = (5, 55, 5, 55)
        _rm = RoiSliceManager(roi=_roi1)
        _shape = (125, 125)
        _image = np.random.random((_shape))
        _final_image = _image[_rm.roi]
        plugin = create_plugin_class(BASE_PLUGIN)()
        plugin._legacy_image_ops.append(["roi", _roi1])
        plugin._original_input_shape = _shape
        _roi, _binning = plugin.get_single_ops_from_legacy()
        _new_image = rebin2d(_image[_roi], _binning)
        self.assertTrue(np.allclose(_final_image, _new_image))

    def test_get_single_ops_from_legacy__multi_roi(self):
        _roi1 = (5, -55, 5, -55)
        _roi2 = (3, 1235, 17, -5)
        _roi3 = (12, 758, 146, 745)
        _shape = (1257, 1235)
        _rm = RoiSliceManager(roi=_roi1, input_shape=_shape)
        _rm.apply_second_roi(_roi2)
        _rm.apply_second_roi(_roi3)
        _image = np.random.random((_shape))
        _final_image = _image[_rm.roi]
        plugin = create_plugin_class(BASE_PLUGIN)()
        plugin._legacy_image_ops.append(["roi", _roi1])
        plugin._legacy_image_ops.append(["roi", _roi2])
        plugin._legacy_image_ops.append(["roi", _roi3])
        plugin._original_input_shape = _shape
        _roi, _binning = plugin.get_single_ops_from_legacy()
        _new_image = rebin2d(_image[_roi], _binning)
        self.assertTrue(np.allclose(_final_image, _new_image))

    def test_get_single_ops_from_legacy__multi_roi_and_bin(self):
        _roi1 = (5, -55, 5, -55)
        _roi2 = (3, 436, 17, -5)
        _roi3 = (2, 12, 0, 5)
        _bin1 = 3
        _bin2 = 4
        _bin3 = 2
        _shape = (1257, 1235)
        _image = np.random.random((_shape))
        _final_image = _image[RoiSliceManager(roi=_roi1).roi]
        _final_image = rebin2d(_final_image, _bin1)
        _final_image = rebin2d(_final_image, _bin2)
        _final_image = _final_image[RoiSliceManager(roi=_roi2).roi]
        _final_image = _final_image[RoiSliceManager(roi=_roi3).roi]
        _final_image = rebin2d(_final_image, _bin3)
        plugin = create_plugin_class(BASE_PLUGIN)()
        plugin._legacy_image_ops.append(["roi", _roi1])
        plugin._legacy_image_ops.append(["binning", _bin1])
        plugin._legacy_image_ops.append(["binning", _bin2])
        plugin._legacy_image_ops.append(["roi", _roi2])
        plugin._legacy_image_ops.append(["roi", _roi3])
        plugin._legacy_image_ops.append(["binning", _bin3])
        plugin._original_input_shape = _shape
        _roi, _binning = plugin.get_single_ops_from_legacy()
        _new_image = rebin2d(_image[_roi], _binning)
        self.assertTrue(np.allclose(_final_image, _new_image))

    def test_get_own_roi(self):
        _this_roi = (3, 436, 17, 357)
        plugin = create_plugin_class(BASE_PLUGIN)()
        plugin.output_data_dim = 2
        for _name in ["use_roi", "roi_ylow", "roi_yhigh", "roi_xlow", "roi_xhigh"]:
            plugin.add_param(get_generic_parameter(_name))
        plugin.set_param_value("use_roi", True)
        plugin.set_param_value("roi_ylow", _this_roi[0])
        plugin.set_param_value("roi_yhigh", _this_roi[1])
        plugin.set_param_value("roi_xlow", _this_roi[2])
        plugin.set_param_value("roi_xhigh", _this_roi[3])
        plugin.input_shape = (1257, 1235)
        _roi = plugin._get_own_roi()
        self.assertEqual(_roi[0].start, _this_roi[0])
        self.assertEqual(_roi[0].stop, _this_roi[1])
        self.assertEqual(_roi[1].start, _this_roi[2])
        self.assertEqual(_roi[1].stop, _this_roi[3])

    def test_get_own_roi__w_high_output_dim_and_correct_roi_dim(self):
        _this_roi = (3, 436, 17, 357)
        plugin = create_plugin_class(BASE_PLUGIN)()
        plugin.output_data_dim = 3
        plugin._roi_data_dim = 2
        for _name in ["use_roi", "roi_ylow", "roi_yhigh", "roi_xlow", "roi_xhigh"]:
            plugin.add_param(get_generic_parameter(_name))
        plugin.set_param_value("use_roi", True)
        plugin.set_param_value("roi_ylow", _this_roi[0])
        plugin.set_param_value("roi_yhigh", _this_roi[1])
        plugin.set_param_value("roi_xlow", _this_roi[2])
        plugin.set_param_value("roi_xhigh", _this_roi[3])
        plugin.input_shape = (1257, 1235)
        _roi = plugin._get_own_roi()
        self.assertEqual(_roi[0].start, _this_roi[0])
        self.assertEqual(_roi[0].stop, _this_roi[1])
        self.assertEqual(_roi[1].start, _this_roi[2])
        self.assertEqual(_roi[1].stop, _this_roi[3])

    def test_update_legacy_image_ops_with_this_plugin__fresh(self):
        _roi1 = (5, -55, 5, -55)
        _this_roi = (slice(3, 436, None), slice(17, 967, None))
        _bin1 = 3
        _this_bin = 4
        _shape = (1257, 1235)
        plugin = create_plugin_class(BASE_PLUGIN)()
        plugin.output_data_dim = 2
        plugin.input_shape = _shape
        for _name in [
            "binning",
            "use_roi",
            "roi_ylow",
            "roi_yhigh",
            "roi_xlow",
            "roi_xhigh",
        ]:
            plugin.add_param(get_generic_parameter(_name))
        plugin.set_param_value("binning", _this_bin)
        plugin.set_param_value("use_roi", True)
        plugin.set_param_value("roi_ylow", _this_roi[0].start)
        plugin.set_param_value("roi_yhigh", _this_roi[0].stop)
        plugin.set_param_value("roi_xlow", _this_roi[1].start)
        plugin.set_param_value("roi_xhigh", _this_roi[1].stop)
        plugin._legacy_image_ops.append(["roi", _roi1])
        plugin._legacy_image_ops.append(["binning", _bin1])
        plugin.update_legacy_image_ops_with_this_plugin()
        self.assertEqual(plugin._legacy_image_ops_meta["num"], 2)
        self.assertTrue(plugin._legacy_image_ops_meta["included"])
        for _index, _item in enumerate(
            [
                ["roi", _roi1],
                ["binning", _bin1],
                ["roi", _this_roi],
                ["binning", _this_bin],
            ]
        ):
            self.assertEqual(plugin._legacy_image_ops[_index], _item)

    def test_apply_legacy_image_ops_to_data(self):
        _roi1 = (5, -55, 5, -55)
        _roi2 = (3, 436, 17, -5)
        _bin1 = 3
        _bin2 = 4
        _shape = (1257, 1235)
        _image = np.random.random((_shape))
        _final_image = _image[RoiSliceManager(roi=_roi1).roi]
        _final_image = rebin2d(_final_image, _bin1)
        _final_image = rebin2d(_final_image, _bin2)
        _final_image = _final_image[RoiSliceManager(roi=_roi2).roi]
        plugin = create_plugin_class(BASE_PLUGIN)()
        plugin._original_input_shape = _shape
        plugin._legacy_image_ops.append(["roi", _roi1])
        plugin._legacy_image_ops.append(["binning", _bin1])
        plugin._legacy_image_ops.append(["binning", _bin2])
        plugin._legacy_image_ops.append(["roi", _roi2])
        _new_image = plugin.apply_legacy_image_ops_to_data(_image)
        self.assertTrue(np.allclose(_final_image, _new_image))

    def test_calculate_result_shape__output_dim_neg1_no_input(self):
        plugin = create_plugin_class(BASE_PLUGIN)()
        plugin.calculate_result_shape()
        self.assertIsNone(plugin._config["result_shape"])

    def test_calculate_result_shape__output_dim_neg1_input(self):
        _shape = (123, 534, 245)
        plugin = create_plugin_class(BASE_PLUGIN)()
        plugin._config["input_shape"] = _shape
        plugin.calculate_result_shape()
        self.assertEqual(plugin._config["result_shape"], _shape)

    def test_calculate_result_shape__output_dim_pos_no_input(self):
        plugin = create_plugin_class(BASE_PLUGIN)()
        plugin.output_data_dim = 2
        plugin.calculate_result_shape()
        self.assertEqual(plugin._config["result_shape"], (-1, -1))

    def test_calculate_result_shape__output_dim_pos_with_input(self):
        _shape = (123, 534, 245)
        plugin = create_plugin_class(BASE_PLUGIN)()
        plugin._config["input_shape"] = _shape
        plugin.output_data_dim = 2
        plugin.calculate_result_shape()
        self.assertEqual(plugin._config["result_shape"], _shape)

    def test_result_shape__no_results(self):
        plugin = create_plugin_class(BASE_PLUGIN)()
        self.assertIsNone(plugin.result_shape)

    def test_result_shape__with_results(self):
        _shape = (123, 534, 245)
        plugin = create_plugin_class(BASE_PLUGIN)()
        plugin._config["input_shape"] = _shape
        plugin.calculate_result_shape()
        self.assertEqual(plugin.result_shape, _shape)

    def test_input_shape_getter(self):
        _shape = (123, 534, 245)
        plugin = create_plugin_class(BASE_PLUGIN)()
        plugin._config["input_shape"] = _shape
        self.assertEqual(plugin.input_shape, _shape)

    def test_input_shape_setter__wrong_type(self):
        _shape = 123
        plugin = create_plugin_class(BASE_PLUGIN)()
        with self.assertRaises(UserConfigError):
            plugin.input_shape = _shape

    def test_input_shape_setter__input_data_dim_None(self):
        _shape = (123, 456)
        plugin = create_plugin_class(BASE_PLUGIN)()
        plugin.input_data_dim = None
        with self.assertRaises(UserConfigError):
            plugin.input_shape = _shape

    def test_input_shape_setter__input_data_dim_neg(self):
        _shape = (123, 534, 245)
        plugin = create_plugin_class(BASE_PLUGIN)()
        plugin.input_shape = _shape
        self.assertEqual(_shape, plugin.input_shape)

    def test_input_shape_setter__input_data_dim_pos_and_different(self):
        _shape = (123, 534, 245)
        plugin = create_plugin_class(BASE_PLUGIN)()
        plugin.input_data_dim = 2
        with self.assertRaises(UserConfigError):
            plugin.input_shape = _shape

    def test_input_shape_setter__input_data_dim_correct(self):
        _shape = (123, 534, 245)
        plugin = create_plugin_class(BASE_PLUGIN)()
        plugin.input_data_dim = 3
        plugin.input_shape = _shape
        self.assertEqual(_shape, plugin.input_shape)

    def test_result_data_label__no_unit(self):
        _label = utils.get_random_string(10)
        plugin = create_plugin_class(BASE_PLUGIN)()
        plugin.output_data_label = _label
        self.assertEqual(plugin.result_data_label, _label)

    def test_result_data_label__w_unit(self):
        _label = utils.get_random_string(10)
        _unit = "nano Farad"
        plugin = create_plugin_class(BASE_PLUGIN)()
        plugin.output_data_label = _label
        plugin.output_data_unit = _unit
        self.assertEqual(plugin.result_data_label, f"{_label} / {_unit}")

    def test_result_title__no_node_id_no_label(self):
        plugin = create_plugin_class(BASE_PLUGIN)()
        self.assertEqual(plugin.result_title, f"[{plugin.plugin_name}] (node #-01)")

    def test_result_title__no_node_id_w_label(self):
        _label = utils.get_random_string(8)
        plugin = create_plugin_class(BASE_PLUGIN)()
        plugin.set_param_value("label", _label)
        self.assertEqual(plugin.result_title, f"{_label} (node #-01)")

    def test_result_title__no_label(self):
        plugin = create_plugin_class(BASE_PLUGIN)()
        plugin.node_id = 12
        self.assertEqual(plugin.result_title, f"[{plugin.plugin_name}] (node #012)")

    def test_result_title__w_label(self):
        _label = utils.get_random_string(8)
        plugin = create_plugin_class(BASE_PLUGIN)()
        plugin.node_id = 12
        plugin.set_param_value("label", _label)
        self.assertEqual(plugin.result_title, f"{_label} (node #012)")

    def test_get_parameter_config_widget(self):
        plugin = create_plugin_class(BASE_PLUGIN)()
        with self.assertRaises(NotImplementedError):
            plugin.get_parameter_config_widget()

    def test_has_unique_parameter_config_widget(self):
        plugin = create_plugin_class(BASE_PLUGIN)()
        self.assertEqual(plugin.has_unique_parameter_config_widget, False)

    def test_pre_execute(self):
        plugin = create_plugin_class(BASE_PLUGIN)()
        plugin.pre_execute()
        # assert no error

    def test_getstate(self):
        plugin = create_plugin_class(BASE_PLUGIN)()
        _state = plugin.__getstate__()
        for key, param in _state["params"].items():
            self.assertEqual(plugin.get_param_value(key), param.value)

    def test_setstate(self):
        plugin = create_plugin_class(BASE_PLUGIN)()
        _new_params = {
            utils.get_random_string(6): utils.get_random_string(12) for i in range(7)
        }
        for _key, _val in _new_params.items():
            plugin.add_param(Parameter(_key, str, ""))
        _state = {"params": plugin.params.copy()}
        for _key, _param in _new_params.items():
            _state["params"][_key].value = _new_params[_key]
        plugin.__setstate__(_state)
        for key, val in _new_params.items():
            self.assertEqual(plugin.get_param_value(key), val)

    def test_pickle(self):
        plugin = BasePlugin()
        _new_params = {
            utils.get_random_string(6): utils.get_random_string(12) for i in range(7)
        }
        for _key, _val in _new_params.items():
            plugin.add_param(Parameter(_key, str, _val))
        plugin2 = pickle.loads(pickle.dumps(plugin))
        for _key in plugin.params:
            self.assertEqual(
                plugin.get_param_value(_key), plugin2.get_param_value(_key)
            )

    def test_execute(self):
        plugin = create_plugin_class(BASE_PLUGIN)()
        with self.assertRaises(NotImplementedError):
            plugin.execute(1)

    def test_copy(self):
        plugin = create_plugin_class(BASE_PLUGIN)
        obj = plugin()
        obj.node_id = 42
        obj.set_param_value("label", "Test 12423536")
        cp = copy.copy(obj)
        self.assertEqual(obj.__class__, cp.__class__)
        self.assertEqual(obj.get_param_value("label"), cp.get_param_value("label"))

        self.assertNotEqual(id(obj.params), id(cp.params))
        self.assertEqual(obj.node_id, cp.node_id)

    def test_copy__with_linked_object(self):
        plugin = create_plugin_class(BASE_PLUGIN)
        obj = plugin()
        obj.dummy = TestLinkedObject(obj.params)
        obj.set_param_value("label", "Test 12423536")
        self.assertEqual(
            obj.dummy.get_param_value("label"), obj.get_param_value("label")
        )
        cp = copy.copy(obj)
        self.assertEqual(cp.dummy.get_param_value("label"), cp.get_param_value("label"))
        cp.set_param_value("label", "Test 12423536")
        self.assertEqual(cp.dummy.get_param_value("label"), cp.get_param_value("label"))

    def test_copy__with_exp_attribute(self):
        plugin = create_plugin_class(BASE_PLUGIN)
        obj = plugin()
        obj._EXP = EXP
        _copy = copy.copy(obj)
        self.assertEqual(obj._EXP, EXP)
        self.assertEqual(_copy._EXP, EXP)

    def test_copy__with_local_exp_attribute(self):
        plugin = create_plugin_class(BASE_PLUGIN)
        obj = plugin()
        obj._EXP = DiffractionExperiment()
        _copy = copy.copy(obj)
        self.assertNotEqual(obj._EXP, EXP)
        self.assertNotEqual(obj._EXP, _copy._EXP)
        self.assertNotEqual(_copy._EXP, EXP)

    def test_init__plain(self):
        plugin = create_plugin_class(BASE_PLUGIN)()
        self.assertIsInstance(plugin, BasePlugin)

    def test_init__with_param(self):
        _cls = create_plugin_class(BASE_PLUGIN)
        _param = Parameter("test", str, default="test")
        plugin = _cls(_param)
        self.assertTrue("test" in plugin.params)

    def test_init__with_param_overwriting_default(self):
        _original_param = Parameter("test", str, "original test")
        _cls = create_plugin_class(BASE_PLUGIN)
        _cls.default_params.add_param(_original_param)
        _param = Parameter("test", str, "test")
        plugin = _cls(_param)
        self.assertEqual(plugin.get_param_value("test"), _param.value)


if __name__ == "__main__":
    unittest.main()
