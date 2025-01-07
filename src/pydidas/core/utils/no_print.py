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

"""
Module with the NoPrint class which allows to perform operations with hiding outputs
to sys.stdout.
"""

__author__ = "Malte Storm"
__copyright__ = "Copyright 2023 - 2025, Helmholtz-Zentrum Hereon"
__license__ = "GPL-3.0-only"
__maintainer__ = "Malte Storm"
__status__ = "Production"
__all__ = ["NoPrint"]


import sys
from io import StringIO


class NoPrint:
    """
    A ContextManager used to redirect standard output to a discarded dummy.

    Is it designed to be used in a "with NoPrint():" statement.

    Example
    -------
    >>> with NoPrint():
    >>>     obj.method_which_would_generate_output()
    """

    def __init__(self):
        self._generic_stdout = sys.stdout
        self._stdout = StringIO()

    def __enter__(self):
        """
        Override the standard sys.stdout.
        """
        sys.stdout = self._stdout

    def __exit__(self, type_, value, traceback):
        """
        Restore the standard sys.stdout.
        """
        sys.stdout = self._generic_stdout
