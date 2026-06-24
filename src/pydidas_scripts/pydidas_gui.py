# This file is part of pydidas.
#
# Copyright 2024 - 2026, Helmholtz-Zentrum Hereon
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
The pydidas_gui module includes a function to run the default pydidas processing GUI.
"""

__author__ = "Malte Storm"
__copyright__ = "Copyright 2024 - 2026, Helmholtz-Zentrum Hereon"
__license__ = "GPL-3.0-only"
__maintainer__ = "Malte Storm"
__status__ = "Production"
__all__ = []


import argparse
import sys

from pydidas_qtcore import PydidasSplashScreen


def _parse_gui_arguments() -> argparse.Namespace:
    """
    Parse command-line arguments for the pydidas GUI.

    Removes parsed arguments from sys.argv to prevent downstream parsers
    from encountering unrecognized argument errors.

    Returns
    -------
    argparse.Namespace
        The parsed arguments with attributes restore_state and export_exit_state.
    """
    parser = argparse.ArgumentParser(
        description="Launch the pydidas GUI with optional configuration.",
        prog="pydidas-gui",
        add_help=False,
    )
    parser.add_argument(
        "-restore_state",
        dest="restore_state",
        choices=["None", "exit", "saved"],
        default="exit",
        help=(
            "The state to restore on GUI startup. 'None' starts fresh, 'exit' "
            "restores the last exit state (default), and 'saved' restores the "
            "last saved state."
        ),
    )
    parser.add_argument(
        "-export_exit_state",
        dest="export_exit_state",
        type=_str_to_bool,
        default=True,
        help="Whether to export the GUI state on exit. Default is True.",
    )
    _args, _remaining = parser.parse_known_args()
    sys.argv = [sys.argv[0]] + _remaining
    return _args


def _str_to_bool(value: str) -> bool:
    """
    Convert a string representation of truth to bool.

    Parameters
    ----------
    value : str
        The string value to convert. Accepts "True", "False" (case-insensitive).

    Returns
    -------
    bool
        The boolean value.

    Raises
    ------
    argparse.ArgumentTypeError
        If the value is not a valid boolean string.
    """
    if isinstance(value, bool):
        return value
    if value.lower() in ("true", "yes", "1", "on"):
        return True
    if value.lower() in ("false", "no", "0", "off"):
        return False
    raise argparse.ArgumentTypeError(f"Boolean value expected. Got: {value}")


def open_gui() -> None:
    """
    Open the pydidas GUI.

    Accepts command-line arguments:

    restore_state : str
        The state to restore on GUI startup. Options are:

        - 'None': Start with a fresh state
        - 'exit': Restore the state from the last exit (default)
        - 'saved': Restore the last saved state

    export_exit_state : bool
        Flag whether to export the GUI state on exit. Default is True.
    """
    _args = _parse_gui_arguments()
    _splash = PydidasSplashScreen.instance()
    _splash.show_aligned_message("Importing packages")

    import pydidas.gui

    pydidas.gui.start_pydidas_gui(
        use_default_frames=True,
        splash_screen=_splash,
        restore_state=_args.restore_state,
        export_exit_state=_args.export_exit_state,
    )


def run_gui() -> None:
    """
    Alias for open_gui().

    This alias is provided for compatibility with scripted calls using the
    old 'run_gui' function name.
    """
    open_gui()


if __name__ == "__main__":
    open_gui()
