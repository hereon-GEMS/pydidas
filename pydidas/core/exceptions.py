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

"""
Module with pydidas custom Exceptions which are used throughout the package.
"""

__author__ = "Malte Storm"
__copyright__ = "Copyright 2021-2022, Malte Storm, Helmholtz-Zentrum Hereon"
__license__ = "GPL-3.0"
__maintainer__ = "Malte Storm"
__status__ = "Development"
__all__ = [
    "PydidasGuiError",
    "PydidasConfigError",
    "UserConfigError",
]


class PydidasGuiError(Exception):
    """
    PydidasGuiError is used for any specific issues with the graphical user interface.
    """


class PydidasConfigError(Exception):
    """
    PydidasConfigError is used when the configuration (e.g. with Parameters) cannot
    be processed.
    """


class UserConfigError(Exception):
    """
    UserConfigErrors can be raised if the input cannot be processed. The exception
    handling for UserConfigErrors is different from the generic exception handling
    to allow pydidas to raise less severe Exceptions in case of configuration
    isues caused by the user.
    """
