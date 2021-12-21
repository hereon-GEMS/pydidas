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
__copyright__ = "Copyright 2021, Malte Storm, Helmholtz-Zentrum Hereon"
__license__ = "GPL-3.0"
__version__ = "0.0.1"
__maintainer__ = "Malte Storm"
__status__ = "Development"


import os
import tempfile
import shutil
import unittest
import copy

import numpy as np
from PyQt5 import QtCore

from pydidas.image_io import CompositeImage
from pydidas.core import AppConfigError


class TestCompositeImage(unittest.TestCase):

    def setUp(self):
        self._path = tempfile.mkdtemp()
        q_settings = QtCore.QSettings('Hereon', 'pydidas')
        self._maxsize = float(q_settings.value('global/mosaic_max_size'))
        self._border = float(q_settings.value('global/mosaic_border_width'))

    def tearDown(self):
        shutil.rmtree(self._path)
        del self._path

    def get_default_object(self):
        obj = CompositeImage(image_shape=(20, 20), composite_nx=5,
                     composite_ny=5, datatype=float,
                     threshold_low=np.nan, threshold_high=1)
        return obj

    def test_creation(self):
        obj = CompositeImage()
        self.assertIsInstance(obj, CompositeImage)

    def test_creation_with_params(self):
        obj = self.get_default_object()
        self.assertIsInstance(obj, CompositeImage)
        self.assertIsInstance(obj.image, np.ndarray)

    def test_check_config_wrong_params(self):
        obj = CompositeImage(image_shape=(20, 20), composite_nx=-2,
                             composite_ny=-2, datatype=float,
                             threshold_low=np.nan, threshold_high=1)
        self.assertFalse(obj._CompositeImage__check_config())

    def test_verify_config_wrong_params(self):
        obj = CompositeImage(image_shape=(20, 20), composite_nx=-2,
                             composite_ny=-2, datatype=float,
                             threshold_low=np.nan, threshold_high=1)
        with self.assertRaises(ValueError):
            obj._CompositeImage__verify_config()

    def test_create_new_image(self):
        obj = self.get_default_object()
        obj.set_param_value('composite_nx', 10)
        obj.create_new_image()
        _shape = obj.get_param_value('image_shape')
        _size = (_shape[0] * obj.get_param_value('composite_ny')
                 + (obj.get_param_value('composite_ny') - 1) * self._border,
                 _shape[1] * obj.get_param_value('composite_nx')
                 + (obj.get_param_value('composite_nx') - 1) * self._border)
        self.assertEqual(obj.image.shape, _size)

    def test_insert_image(self):
        obj = self.get_default_object()
        img = np.random.random((20, 20))
        obj.insert_image(img, 0)
        self.assertTrue((obj.image[:20, :20] == img).all())

    def test_insert_image_into_empty_array(self):
        obj = self.get_default_object()
        obj._CompositeImage__image = None
        img = np.random.random((20, 20))
        obj.insert_image(img, 0)
        self.assertTrue((obj.image[:20, :20] == img).all())

    def test_insert_image_comp_dir_y(self):
        obj = self.get_default_object()
        obj.set_param_value('composite_dir', 'y')
        img = np.random.random((20, 20))
        obj.insert_image(img, 0)
        self.assertTrue((obj.image[:20, :20] == img).all())

    def test_apply_threshold_no_limits(self):
        obj = CompositeImage(image_shape=(20, 20), composite_nx=5,
                             composite_ny=5, datatype=float,
                             threshold_low=np.nan, threshold_high=np.nan)
        img = (np.random.random((20, 20)) - 0.5) * 100
        obj.insert_image(img, 0)
        obj.apply_thresholds()
        self.assertTrue((obj.image[:20, :20] == img).all())

    def test_apply_threshold_low_limit_only(self):
        obj = CompositeImage(image_shape=(20, 20), composite_nx=5,
                             composite_ny=5, datatype=float,
                             threshold_low=np.nan, threshold_high=np.nan)
        img = (np.random.random((20, 20)) - 0.5) * 100
        obj.insert_image(img, 0)
        obj.apply_thresholds(low = 0)
        self.assertTrue(np.amin(obj.image[:20, :20]) >= 0.)

    def test_apply_threshold_high_limit_only(self):
        obj = CompositeImage(image_shape=(20, 20), composite_nx=5,
                             composite_ny=5, datatype=float,
                             threshold_low=np.nan, threshold_high=np.nan)
        img = (np.random.random((20, 20)) - 0.5) * 100
        obj.insert_image(img, 0)
        obj.apply_thresholds(high=5)
        self.assertTrue(np.amax(obj.image[:20, :20]) <= 5.)

    def test_save(self):
        obj = self.get_default_object()
        img = (np.random.random((20, 20)) - 0.5) * 100
        obj.insert_image(img, 0)
        _fname = os.path.join(self._path, 'test.npy')
        obj.save(_fname)
        _img = np.load(_fname)
        self.assertTrue((obj.image == _img).all())

    def test_export_npy(self):
        obj = self.get_default_object()
        img = (np.random.random((20, 20)) - 0.5) * 100
        obj.insert_image(img, 0)
        _fname = os.path.join(self._path, 'test.npy')
        obj.export(_fname)
        _img = np.load(_fname)
        self.assertTrue((obj.image == _img).all())

    def test_set_default_qsettings(self):
        obj = self.get_default_object()
        q_settings = QtCore.QSettings('Hereon', 'pydidas')
        _maxsize = float(q_settings.value('global/mosaic_max_size'))
        self.assertEqual(obj.get_param_value('mosaic_max_size'),
                         _maxsize)

    def test_set_default_qsettings__overwrite(self):
        _maxsize_test = 150
        obj = CompositeImage(image_shape=(20, 20), composite_nx=5,
                     composite_ny=5, datatype=float,
                     threshold_low=np.nan, threshold_high=1,
                     mosaic_max_size=_maxsize_test)
        self.assertEqual(obj.get_param_value('mosaic_max_size'),
                         _maxsize_test)

    def test_check_max_size_okay(self):
        obj = self.get_default_object()
        q_settings = QtCore.QSettings('Hereon', 'pydidas')
        old_maxsize = q_settings.value('global/mosaic_max_size')
        q_settings.setValue('global/mosaic_max_size', 100)
        obj._CompositeImage__check_max_size((19e3, 5e3))
        if old_maxsize is not None:
            q_settings.setValue('global/mosaic_max_size', old_maxsize)

    def test_check_max_size_too_large(self):
        obj = self.get_default_object()
        q_settings = QtCore.QSettings('Hereon', 'pydidas')
        old_maxsize = float(q_settings.value('global/mosaic_max_size'))
        q_settings.setValue('global/mosaic_max_size', 100)
        with self.assertRaises(AppConfigError):
            obj._CompositeImage__check_max_size((21e3, 5e3))
        if old_maxsize is not None:
            q_settings.setValue('global/mosaic_max_size', old_maxsize)

    def test_property_shape(self):
        obj = self.get_default_object()
        _shape = obj.get_param_value('image_shape')
        _size = (_shape[0] * obj.get_param_value('composite_ny')
                 + (obj.get_param_value('composite_ny') - 1) * self._border,
                 _shape[1] * obj.get_param_value('composite_nx')
                 + (obj.get_param_value('composite_nx') - 1) * self._border)
        self.assertEqual(obj.shape,_size)

    def test_property_shape_empty(self):
        obj = self.get_default_object()
        obj._CompositeImage__image = None
        self.assertEqual(obj.shape, (0, 0))

    def test_copy(self):
        obj = self.get_default_object()
        obj2 = copy.copy(obj)
        self.assertIsInstance(obj2, CompositeImage)
        self.assertNotEqual(obj, obj2)


if __name__ == "__main__":
    unittest.main()
