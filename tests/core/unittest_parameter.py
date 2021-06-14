import unittest
from numbers import Integral, Real

from pydidas.core import  Parameter


class TestParameter(unittest.TestCase):

    def setUp(self):
        ...

    def tearDown(self):
        ...

    def test_creation(self):
        obj = Parameter('Test0', int, default=12)
        self.assertIsInstance(obj, Parameter)

    def test_creation_no_arguments(self):
        with self.assertRaises(TypeError):
            obj = Parameter()

    def test_creation_with_meta_dict(self):
        obj = Parameter('Test0', int, dict(default=12))
        self.assertIsInstance(obj, Parameter)

    def test_creation_missing_default(self):
        with self.assertRaises(TypeError):
            obj = Parameter('Test0', int)

    def test_creation_wrong_choices(self):
        with self.assertRaises(ValueError):
            obj = Parameter('Test0', int, default=12,
                            choices=[0, 10])

    def test_creation_choices_wrong_type(self):
        with self.assertRaises(TypeError):
            obj = Parameter('Test0', int, default=12,
                            choices=12)

    def test_creation_wrong_datatype(self):
        with self.assertRaises(TypeError):
            obj = Parameter('Test0', int, default='12')

    def test_call(self):
        obj = Parameter('Test0', int, default=12)
        self.assertEqual(obj(), 12)

    def test_name(self):
        obj = Parameter('Test0', int, default=12)
        self.assertEqual(obj.name, 'Test0')

    def test_refkey(self):
        obj = Parameter('Test0', int, default=12)
        self.assertEqual(obj.refkey, 'Test0')

    def test_refkey_ii(self):
        obj = Parameter('Test0', int, default=12, refkey='key')
        self.assertEqual(obj.refkey, 'key')

    def test_default(self):
        obj = Parameter('Test0', int, default=12)
        self.assertEqual(obj.default, 12)

    def test_default_with_different_value(self):
        obj = Parameter('Test0', int, default=12)
        obj.value = 0
        self.assertEqual(obj.default, 12)

    def test_unit(self):
        obj = Parameter('Test0', int, default=12, unit='The_unit')
        self.assertEqual(obj.unit, 'The_unit')

    def test_tooltip(self):
        obj = Parameter('Test0', int, default=12, unit='m', value=10,
                        tooltip='Test tooltip')
        self.assertEqual(obj.tooltip, 'Test tooltip (unit: m, type: integer)')

    def test_choices_setter(self):
        obj = Parameter('Test0', int, default=12, choices=[0,12])
        self.assertEqual(obj.choices, [0, 12])

    def test_choices_setter_update(self):
        obj = Parameter('Test0', int, default=12, choices=[0,12])
        obj.choices = [0, 12, 24]
        self.assertEqual(obj.choices, [0, 12, 24])

    def test_choices_setter_wrong_type(self):
        obj = Parameter('Test0', int, default=12, choices=[0,12])
        with self.assertRaises(TypeError):
            obj.choices = dict(a=0, b=12)

    def test_choices_setter_value_not_included(self):
        obj = Parameter('Test0', int, default=12, choices=[0,12])
        with self.assertRaises(ValueError):
            obj.choices = [0, 24]

    def test_choices_setter_wrong_entry(self):
        obj = Parameter('Test0', int, default=12, choices=[0,12])
        with self.assertRaises(ValueError):
            obj.choices = [12, '24']

    def test_optional(self):
        obj = Parameter('Test0', int, default=12)
        self.assertEqual(obj.optional, False)

    def test_optional_ii(self):
        obj = Parameter('Test0', int, default=12, optional=True)
        self.assertEqual(obj.optional, True)

    def test_type(self):
        obj = Parameter('Test0', int, default=12)
        self.assertEqual(obj.type, Integral)

    def test_type_ii(self):
        obj = Parameter('Test0', float, default=12)
        self.assertEqual(obj.type, Real)

    def test_get_value(self):
        obj = Parameter('Test0', int, default=12)
        self.assertEqual(obj.value, 12)

    def test_set_value(self):
        obj = Parameter('Test0', int, default=12)
        obj.value = 24
        self.assertEqual(obj.value, 24)

    def test_set_value_wrong_type(self):
        obj = Parameter('Test0', int, default=12)
        with self.assertRaises(ValueError):
            obj.value = '24'

    def test_set_value_wrong_choice(self):
        obj = Parameter('Test0', int, default=12, choices=[0, 12])
        with self.assertRaises(ValueError):
            obj.value = 24

    def test_restore_default(self):
        obj = Parameter('Test0', int, default=12)
        obj.value = 24
        obj.restore_default()
        self.assertEqual(obj.value, 12)

    def test_get_copy(self):
        obj = Parameter('Test0', int, default=12)
        copy = obj.get_copy()
        self.assertNotEqual(obj, copy)
        self.assertIsInstance(copy, Parameter)

    def test_dump(self):
        obj = Parameter('Test0', int, default=12)
        self.assertEqual(obj.name, 'Test0')
        dump = obj.dump()
        self.assertEqual(dump[0], 'Test0')
        self.assertEqual(dump[1], Integral)
        self.assertEqual(dump[2],  {'default': 12,
                                    'tooltip': '',
                                    'unit': '',
                                    'optional': False,
                                    'refkey': 'Test0',
                                    'choices': None,
                                    'value': 12})

    def test__copy__(self):
        import copy
        obj = Parameter('Test0', int, default=12)
        copy = copy.copy(obj)
        self.assertNotEqual(obj, copy)
        self.assertIsInstance(copy, Parameter)


if __name__ == "__main__":
    unittest.main()
