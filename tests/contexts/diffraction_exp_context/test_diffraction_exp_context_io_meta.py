# This file is part of pydidas.
#
# Copyright 2021-, Helmholtz-Zentrum Hereon
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
__copyright__ = "Copyright 2021-, Helmholtz-Zentrum Hereon"
__license__ = "GPL-3.0-only"
__maintainer__ = "Malte Storm"
__status__ = "Development"


import unittest

from pydidas.contexts.diffraction_exp_context import (
    DiffractionExperiment,
    DiffractionExperimentContext,
    DiffractionExperimentContextIoBase,
    DiffractionExperimentContextIoMeta,
)


EXP = DiffractionExperimentContext()
EXP_IO_META = DiffractionExperimentContextIoMeta
EXP_IO_META.clear_registry()


class TestIo(DiffractionExperimentContextIoBase):
    extensions = ["test"]
    format_name = "Test"

    @classmethod
    def reset(cls):
        cls.imported = False
        cls.exported = False
        cls.export_filename = None
        cls.import_filename = None
        cls.diffraction_exp = None

    @classmethod
    def export_to_file(cls, filename, **kwargs):
        cls.exported = True
        cls.export_filename = filename

    @classmethod
    def import_from_file(cls, filename, diffraction_exp=None):
        cls.imported = True
        cls.diffraction_exp = EXP if diffraction_exp is None else diffraction_exp
        cls.import_filename = filename


class TestExperimentSettingsIoMeta(unittest.TestCase):
    def setUp(self):
        TestIo.reset()

    def tearDown(self):
        EXP.restore_all_defaults(True)

    def test_export_to_file(self):
        _fname = "test.test"
        EXP_IO_META.export_to_file(_fname)
        self.assertTrue(TestIo.exported)
        self.assertEqual(TestIo.export_filename, _fname)

    def test_import_from_file__generic(self):
        _fname = "test.test"
        EXP_IO_META.import_from_file(_fname)
        self.assertTrue(TestIo.imported)
        self.assertEqual(TestIo.import_filename, _fname)
        self.assertEqual(TestIo.diffraction_exp, EXP)

    def test_import_from_file__given_Exp(self):
        _exp = DiffractionExperiment()
        _fname = "test.test"
        EXP_IO_META.import_from_file(_fname, diffraction_exp=_exp)
        self.assertTrue(TestIo.imported)
        self.assertEqual(TestIo.import_filename, _fname)
        self.assertEqual(TestIo.diffraction_exp, _exp)


if __name__ == "__main__":
    unittest.main()
    EXP_IO_META.clear_registry()
