# This file is part of pydidas.
#
# Copyright 2024 - 2025, Helmholtz-Zentrum Hereon
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
Script to reset all stored QSettings to default in case a setting breaks
the GUI startup.
"""

__author__ = "Malte Storm"
__copyright__ = "Copyright 2024 - 2025, Helmholtz-Zentrum Hereon"
__license__ = "GPL-3.0-only"
__maintainer__ = "Malte Storm"
__status__ = "Production"
__all__ = ["clear_local_settings"]


from qtpy.QtCore import QSettings


def clear_local_settings(confirm_finish: bool = True, verbose: bool = True):
    """
    Clear all stored pydidas QSettings registry values.

    Parameters
    ----------
    confirm_finish : bool, optional
        Flag to confirm the script is finished. The default is True.
    verbose : bool, optional
        Flag to print status messages. The default is True.
    """
    qs = QSettings("Hereon", "pydidas")
    qs.remove("")
    if verbose:
        print(
            "\n"
            + "=" * 80
            + "\n=== Successfully removed all pydidas registry settings,\n"
            + "=" * 80
            + "\n"
        )
    if confirm_finish:
        input("Press <Enter> to finish the registry cleanup. ")


if __name__ == "__main__":
    clear_local_settings()
