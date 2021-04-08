# -*- coding: utf-8 -*-
"""
Created on Thu Apr  1 13:49:10 2021

@author: ogurreck
"""

import numpy as np
from numbers import Integral

class DatasetConfigException(Exception):
    ...

class EmptyDataset(np.ndarray):
    def __new__(cls, *args, **kwargs):
        local_kws = kwargs.copy()
        for item in ['axis_labels', 'axis_scales', 'axis_units', 'image_id']:
            if item in kwargs.keys():
                del kwargs[item]
        obj = super().__new__(cls, *args, **kwargs)
        obj.axis_labels = local_kws.get('axis_labels', [])
        obj.axis_scales = local_kws.get('axis_scales', [])
        obj.axis_units = local_kws.get('axis_units', [])
        obj.image_id = local_kws.get('image_id', None)
        return obj

    def __array_finalize__(self, obj):
        if obj is None:
            return
        self.axis_labels = getattr(obj, 'axis_labels', [])
        self.axis_scales = getattr(obj, 'axis_scales', {})
        self.axis_units = getattr(obj, 'axis_units', [])
        self.image_id = getattr(obj, 'image_id', None)


class Dataset(EmptyDataset):
    def __new__(cls, array, axis_labels=None, axis_scales=None, axis_units=None, image_id=None):
        obj = np.asarray(array).view(cls)
        if axis_labels:
            cls.set_axis_labels(obj, axis_labels)
        if axis_scales:
            cls.set_axis_scales(obj, axis_scales)
        if axis_units:
            cls.set_axis_units(obj, axis_units)
        if image_id:
            cls.set_image_id(obj, image_id)
        return obj

    # def __array_finalize__(self, axis_labels=None, axis_scales=None, axis_units=None):
    #     if axis_labels:
    #         self.set_axis_labels(axis_labels)
    #     obj.dims = []
    #     obj.scales = {}
    #     return obj

    def set_axis_labels(self, labels):
        labels = list(labels)
        if len(labels) != self.ndim:
            raise DatasetConfigException('Length of labels does not match number of axes.')
        self.axis_labels = labels

    def set_axis_scales(self, scales):
        if set(scales.keys()) != set(np.arange(self.ndim)):
            raise DatasetConfigException('Axis scale keys do not match the axis dimensions')
        self.axis_scales = scales

    def set_axis_units(self, units):
        units = list(units)
        if len(units) != self.ndim:
            raise DatasetConfigException('Length of axis units does not match number of axes.')
        self.axis_units = units

    def set_image_id(self, image_id):
        if not isinstance(image_id, Integral):
            raise ValueError('Image id variable is not an integer.')
        self.image_id = image_id


