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
The parametrized_sub_tests_ module includes the parametrized_sub_tests decorator to
use
by the __reduce__ methods of the DummyPlugins to allow pickling.
"""

__author__ = "Malte Storm"
__copyright__ = "Copyright 2021-2022, Malte Storm, Helmholtz-Zentrum Hereon"
__license__ = "GPL-3.0"
__maintainer__ = "Malte Storm"
__status__ = "Development"
__all__ = ["parametrized_sub_tests"]


import functools


def parametrized_sub_tests(param_dict_list):
    """
    Decorates a test case to run it as a set of subtests.

    Parameters
    ----------
    param_dict_list : list
        A list with dictionary entries for the keyword arguments for each case.
    """

    def decorator(func):
        @functools.wraps(func)
        def wrapped(self):
            for _param_dict in param_dict_list:
                with self.subTest(**_param_dict):
                    func(self, **_param_dict)

        return wrapped

    return decorator
