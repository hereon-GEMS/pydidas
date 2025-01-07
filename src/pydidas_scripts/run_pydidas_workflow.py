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
The run_workflow script allows to run pydidas workflows in the console.
"""

__author__ = "Malte Storm"
__copyright__ = "Copyright 2024 - 2025, Helmholtz-Zentrum Hereon"
__license__ = "GPL-3.0-only"
__maintainer__ = "Malte Storm"
__status__ = "Production"
__all__ = []


import sys

from pydidas.apps import ExecuteWorkflowRunner
from pydidas.core import FileReadError, UserConfigError
from pydidas.core.utils import print_warning, timed_print


def run_workflow():
    """
    Run a pydidas workflow in the console.

    This function is a wrapper for the ExecuteWorkflowRunner in pydidas.
    For running multiple workflows in a batch, please consider creating your
    own script.
    """
    verbose = "--verbose" in sys.argv
    timed_print(
        "Processing of pydidas workflow started. Starting ExecuteWorkflowRunner.",
        new_lines=1,
        verbose=verbose,
    )
    runner = ExecuteWorkflowRunner()
    try:
        runner.check_all_args_okay()
        runner.update_contexts_from_stored_args()
        timed_print(
            "Starting ExecuteWorkflowRunner main processing.",
            new_lines=1,
            verbose=verbose,
        )
        runner.execute_workflow_in_apprunner()
    except (UserConfigError, FileReadError, KeyboardInterrupt) as _error:
        _error_text = _error.args[0]
        if "\n" in _error_text:
            _error_text = _error_text.split("\n")
        print_warning(_error_text, leading_dash=False, severe=True)
        return
    timed_print(
        "Finished ExecuteWorkflowRunner processing.", new_lines=1, verbose=verbose
    )


if __name__ == "__main__":
    run_workflow()
