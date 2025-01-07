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
Module with pydidas custom Exceptions which are used throughout the package.
"""

__author__ = "Malte Storm"
__copyright__ = "Copyright 2023 - 2025, Helmholtz-Zentrum Hereon"
__license__ = "GPL-3.0-only"
__maintainer__ = "Malte Storm"
__status__ = "Production"
__all__ = [
    "PydidasGuiError",
    "PydidasConfigError",
    "UserConfigError",
    "FileReadError",
]


class PydidasGuiError(Exception):
    """
    An Exception for handling problems in the pydidas GUI.

    PydidasGuiError is used for any specific issues with the graphical user interface.
    """


class PydidasConfigError(Exception):
    """
    PydidasConfigError is used to signal configuration errors.

    This exception is raised when the configuration (e.g. with Parameters) cannot
    be processed.
    """


class UserConfigError(Exception):
    """
    An Exception for signalling a bad configuration by the user.

    UserConfigErrors can be raised if the input cannot be processed. The exception
    handling for UserConfigErrors is different from the generic exception handling
    to allow pydidas to raise less severe Exceptions in case of configuration
    isues caused by the user.
    """

    def __repr__(self):
        """
        Explicitly handle the representation.

        This call is used to assert that the exception message is included with
        single quote marks.

        Returns
        -------
        str
            The representation string.
        """
        return f"UserConfigError('{str(self)}')"


class FileReadError(Exception):
    """
    An Exception for signalling an error in reading a file.

    FileReadError can be raised if the input cannot be processed. The exception
    handling for FileReadError is different from the generic exception handling
    to allow pydidas to raise less severe Exceptions in case of missing files
    etc.
    """

    def __repr__(self):
        """
        Explicitly handle the representation.

        This call is used to assert that the exception message is included with
        single quote marks.

        Returns
        -------
        str
            The representation string.
        """
        return f"FileReadError('{str(self)}')"
