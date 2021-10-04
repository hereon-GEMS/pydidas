# This file is part of pydidas.

# pydidas is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.

# Pydidas is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE. See the
# GNU General Public License for more details.

# You should have received a copy of the GNU General Public License
# along with Pydidas. If not, see <http://www.gnu.org/licenses/>.

"""Unit tests for pydidas modules."""

__author__      = "Malte Storm"
__copyright__   = "Copyright 2021, Malte Storm, Helmholtz-Zentrum Hereon"
__license__ = "GPL-3.0"
__version__ = "0.0.1"
__maintainer__ = "Malte Storm"
__status__ = "Development"

import unittest
import tempfile
import shutil

from pydidas.unittest_objects.dummy_plugin_collection import (
    create_plugin_class)

from pydidas.plugins import BasePlugin
from pydidas.constants import BASE_PLUGIN
from pydidas.core import Parameter


class TestBasePlugin(unittest.TestCase):

    def setUp(self):
        self._pluginpath = tempfile.mkdtemp()
        self._class_names = []

    def tearDown(self):
        shutil.rmtree(self._pluginpath)

    def test_create_base_plugin(self):
        plugin = create_plugin_class(BASE_PLUGIN, BASE_PLUGIN)
        self.assertIsInstance(plugin(), BasePlugin)

    def test_get_class_description(self):
        plugin = create_plugin_class(BASE_PLUGIN, BASE_PLUGIN)
        _text = plugin.get_class_description()
        self.assertIsInstance(_text, str)

    def test_get_class_description_as_dict(self):
        plugin = create_plugin_class(BASE_PLUGIN, BASE_PLUGIN)
        _doc = plugin.get_class_description_as_dict()
        self.assertIsInstance(_doc, dict)
        for _key, _value in _doc.items():
            self.assertIsInstance(_key, str)
            self.assertIsInstance(_value, str)

    def test_class_atributes(self):
        plugin = create_plugin_class(BASE_PLUGIN, BASE_PLUGIN)
        for att in ('basic_plugin', 'plugin_type', 'plugin_name',
                    'default_params', 'generic_params', 'input_data_dim',
                    'output_data_dim'):
            self.assertTrue(hasattr(plugin, att))

    def test_calculate_result_shape__output_dim_neg1_no_input(self):
        plugin = create_plugin_class(BASE_PLUGIN, BASE_PLUGIN)()
        plugin.calculate_result_shape()
        self.assertIsNone(plugin._config['result_shape'])

    def test_calculate_result_shape__output_dim_neg1_input(self):
        _shape = (123, 534, 245)
        plugin = create_plugin_class(BASE_PLUGIN, BASE_PLUGIN)()
        plugin._config['input_shape'] = _shape
        plugin.calculate_result_shape()
        self.assertEqual(plugin._config['result_shape'], _shape)

    def test_calculate_result_shape__output_dim_pos_no_input(self):
        plugin = create_plugin_class(BASE_PLUGIN, BASE_PLUGIN)()
        plugin.output_data_dim = 2
        plugin.calculate_result_shape()
        self.assertEqual(plugin._config['result_shape'], (-1, -1))

    def test_calculate_result_shape__output_dim_pos_with_input(self):
        _shape = (123, 534, 245)
        plugin = create_plugin_class(BASE_PLUGIN, BASE_PLUGIN)()
        plugin._config['input_shape'] = _shape
        plugin.output_data_dim = 2
        plugin.calculate_result_shape()
        self.assertEqual(plugin._config['result_shape'], _shape)

    def test_result_shape__no_results(self):
        plugin = create_plugin_class(BASE_PLUGIN, BASE_PLUGIN)()
        self.assertIsNone(plugin.result_shape)

    def test_result_shape__with_results(self):
        _shape = (123, 534, 245)
        plugin = create_plugin_class(BASE_PLUGIN, BASE_PLUGIN)()
        plugin._config['input_shape'] = _shape
        self.assertEqual(plugin.result_shape, _shape)

    def test_input_shape_getter(self):
        _shape = (123, 534, 245)
        plugin = create_plugin_class(BASE_PLUGIN, BASE_PLUGIN)()
        plugin._config['input_shape'] = _shape
        self.assertEqual(plugin.input_shape, _shape)

    def test_input_shape_setter__wrong_type(self):
        _shape = 123
        plugin = create_plugin_class(BASE_PLUGIN, BASE_PLUGIN)()
        with self.assertRaises(TypeError):
            plugin.input_shape = _shape

    def test_input_shape_setter__input_data_dim_neg(self):
        _shape = (123, 534, 245)
        plugin = create_plugin_class(BASE_PLUGIN, BASE_PLUGIN)()
        plugin.input_shape = _shape
        self.assertEqual(_shape, plugin.input_shape)

    def test_input_shape_setter__input_data_dim_pos_and_different(self):
        _shape = (123, 534, 245)
        plugin = create_plugin_class(BASE_PLUGIN, BASE_PLUGIN)()
        plugin.input_data_dim = 2
        with self.assertRaises(ValueError):
            plugin.input_shape = _shape

    def test_input_shape_setter__input_data_dim_correct(self):
        _shape = (123, 534, 245)
        plugin = create_plugin_class(BASE_PLUGIN, BASE_PLUGIN)()
        plugin.input_data_dim = 3
        plugin.input_shape = _shape
        self.assertEqual(_shape, plugin.input_shape)

    def test_get_parameter_config_widget(self):
        plugin = create_plugin_class(BASE_PLUGIN, BASE_PLUGIN)()
        with self.assertRaises(NotImplementedError):
            plugin.get_parameter_config_widget()

    def test_has_unique_parameter_config_widget(self):
        plugin = create_plugin_class(BASE_PLUGIN, BASE_PLUGIN)()
        self.assertEqual(plugin.has_unique_parameter_config_widget, False)

    def test_pre_execute(self):
        plugin = create_plugin_class(BASE_PLUGIN, BASE_PLUGIN)()
        plugin.pre_execute()
        # assert no error

    def test_execute(self):
        plugin = create_plugin_class(BASE_PLUGIN, BASE_PLUGIN)()
        with self.assertRaises(NotImplementedError):
            plugin.execute(1)

    def test_init__plain(self):
        plugin = create_plugin_class(BASE_PLUGIN, BASE_PLUGIN)
        obj = plugin()
        self.assertIsInstance(obj, BasePlugin)

    def test_init__with_param(self):
        plugin = create_plugin_class(BASE_PLUGIN, BASE_PLUGIN)
        _param = Parameter('test', str, default='test')
        obj = plugin(_param)
        self.assertTrue('test' in obj.params)

    def test_init__with_param_overwriting_default(self):
        _original_param = Parameter('test', str, default='original test')
        plugin = create_plugin_class(BASE_PLUGIN, BASE_PLUGIN)
        plugin.default_params.add_param(_original_param)
        _param = Parameter('test', str, default='test')
        obj = plugin(_param)
        self.assertEqual(obj.get_param_value('test'), _param.value)


if __name__ == "__main__":
    unittest.main()
