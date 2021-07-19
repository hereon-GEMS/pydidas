"""
Unittests for the CompositeImage class from the pydidas.core module.
"""

import os
import tempfile
import shutil
import unittest

import numpy as np
from PyQt5 import QtCore

from pydidas.core import CompositeImage
from pydidas._exceptions import AppConfigError

class TestCompositeImage(unittest.TestCase):

    def setUp(self):
        self._path = tempfile.mkdtemp()


    def tearDown(self):
        shutil.rmtree(self._path)
        del self._path

    def test_creation(self):
        obj = CompositeImage()
        self.assertIsInstance(obj, CompositeImage)

    def test_creation_with_params(self):
        obj = CompositeImage(image_shape=(20, 20), composite_nx=5,
                             composite_ny=5, datatype=float,
                             threshold_low=np.nan, threshold_high=1)
        self.assertIsInstance(obj, CompositeImage)
        self.assertIsInstance(obj.image, np.ndarray)

    def test_create_new_image(self):
        obj = CompositeImage(image_shape=(20, 20), composite_nx=5,
                             composite_ny=5, datatype=float,
                             threshold_low=np.nan, threshold_high=1)
        obj.set_param_value('composite_nx', 10)
        obj.create_new_image()
        self.assertEqual(obj.image.shape, (100, 200))

    def test_insert_image(self):
        obj = CompositeImage(image_shape=(20, 20), composite_nx=5,
                             composite_ny=5, datatype=float,
                             threshold_low=np.nan, threshold_high=1)
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
        obj = CompositeImage(image_shape=(20, 20), composite_nx=5,
                             composite_ny=5, datatype=float,
                             threshold_low=np.nan, threshold_high=np.nan)
        img = (np.random.random((20, 20)) - 0.5) * 100
        obj.insert_image(img, 0)
        _fname = os.path.join(self._path, 'test.npy')
        obj.save(_fname)
        _img = np.load(_fname)
        self.assertTrue((obj.image == _img).all())

    def test_export_npy(self):
        obj = CompositeImage(image_shape=(20, 20), composite_nx=5,
                             composite_ny=5, datatype=float,
                             threshold_low=np.nan, threshold_high=np.nan)
        img = (np.random.random((20, 20)) - 0.5) * 100
        obj.insert_image(img, 0)
        _fname = os.path.join(self._path, 'test.npy')
        obj.export(_fname)
        _img = np.load(_fname)
        self.assertTrue((obj.image == _img).all())

    def test__check_max_size_okay(self):
        obj = CompositeImage(image_shape=(20, 20), composite_nx=5,
                             composite_ny=5, datatype=float,
                             threshold_low=np.nan, threshold_high=np.nan)
        q_settings = QtCore.QSettings('Hereon', 'pydidas')
        old_maxsize = q_settings.value('global/mosaic_max_size')
        q_settings.setValue('global/mosaic_max_size', 100)
        obj._CompositeImage__check_max_size(95)
        if old_maxsize is not None:
            q_settings.setValue('global/mosaic_max_size', old_maxsize)

    def test__check_max_size_too_large(self):
        obj = CompositeImage(image_shape=(20, 20), composite_nx=5,
                             composite_ny=5, datatype=float,
                             threshold_low=np.nan, threshold_high=np.nan)
        q_settings = QtCore.QSettings('Hereon', 'pydidas')
        old_maxsize = float(q_settings.value('global/mosaic_max_size'))
        q_settings.setValue('global/mosaic_max_size', 100)
        with self.assertRaises(AppConfigError):
            obj._CompositeImage__check_max_size(105*1e6)
        if old_maxsize is not None:
            q_settings.setValue('global/mosaic_max_size', old_maxsize)


if __name__ == "__main__":
    unittest.main()
