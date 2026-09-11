# This file is part of pydidas.
#
# Copyright 2026, Helmholtz-Zentrum Hereon
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

"""Unit tests for the widgets module."""

__author__ = "Malte Storm"
__copyright__ = "Copyright 2026, Helmholtz-Zentrum Hereon"
__license__ = "GPL-3.0-only"
__maintainer__ = "Malte Storm"
__status__ = "Production"


import subprocess
import sys

import pytest


def test_widgets_import__does_not_eagerly_load_heavy_deps():

    script = (
        "import sys; "
        "import pydidas; "
        "import pydidas.widgets; "
        "heavy = ['silx', 'fabio', 'skimage', 'matplotlib.pyplot', 'pyqtgraph']; "
        "loaded = [m for m in heavy if m in sys.modules]; "
        "print(loaded)"
    )
    result = subprocess.run(
        [sys.executable, "-c", script],
        capture_output=True,
        text=True,
        timeout=120,
        check=False,
    )
    assert result.returncode == 0, result.stderr
    assert result.stdout.strip() == "[]", (
        f"Unexpected eager imports after 'import pydidas': {result.stdout.strip()}"
    )


if __name__ == "__main__":
    pytest.main([__file__])
