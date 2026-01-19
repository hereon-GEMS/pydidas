# This file is part of pydidas.
#
# Copyright 2025 - 2026, Helmholtz-Zentrum Hereon
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
Module with pydidas unittests
"""

__author__ = "Malte Storm"
__copyright__ = "Copyright 2025 - 2026, Helmholtz-Zentrum Hereon"
__license__ = "GPL-3.0-only"
__maintainer__ = "Malte Storm"
__status__ = "Production"


import os
import subprocess
import sys

import pytest


def import_test_code(qt_api) -> str:
    return f"""
    import os
    os.environ["QT_API"] = {repr(qt_api or "pyside6")}
    import qtpy
    import pydidas_qtcore
    expected = {repr(qt_api or "pyside6")}
    assert qtpy.API == expected, f"Expected {{expected}}, got {{qtpy.API}}"
    print(f"OK: {{qtpy.API}}")
    """.replace("\n    ", "\n")


@pytest.mark.slow
@pytest.mark.parametrize("ENV_QT_API", ["pyqt5", "pyside6", None])
@pytest.mark.parametrize("SYS_FLAGS", [[], ["--QT5"], ["--qt5"]])
def test_qtcore_bindings(ENV_QT_API, SYS_FLAGS):
    """
    Test that the correct Qt bindings are used based on environment
    variable and system flags.
    """
    env = os.environ.copy()
    if ENV_QT_API is not None:
        env["QT_API"] = ENV_QT_API
    elif "QT_API" in env:
        del env["QT_API"]

    _test_code = import_test_code(ENV_QT_API)
    _result = subprocess.run(
        [sys.executable, "-c", _test_code], env=env, capture_output=True, text=True
    )
    assert _result.returncode == 0, f"Failed: {_result.stderr}"


if __name__ == "__main__":
    pytest.main([__file__])
