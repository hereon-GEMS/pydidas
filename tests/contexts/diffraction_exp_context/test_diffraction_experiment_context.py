# This file is part of pydidas.
#
# Copyright 2023, Helmholtz-Zentrum Hereon
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
__copyright__ = "Copyright 2023, Helmholtz-Zentrum Hereon"
__license__ = "GPL-3.0-only"
__maintainer__ = "Malte Storm"
__status__ = "Production"


import logging
import unittest

from pydidas.contexts.diffraction_exp_context import (
    DiffractionExperiment,
    DiffractionExperimentContext,
)


logger = logging.getLogger("pyFAI.detectors._common")
logger.setLevel(logging.CRITICAL)


class TestDiffractionExperimentContext(unittest.TestCase):
    def setUp(self):
        ...

    def tearDown(self):
        ...

    def test_creation(self):
        obj = DiffractionExperimentContext()
        self.assertIsInstance(obj, DiffractionExperiment)


if __name__ == "__main__":
    unittest.main()
