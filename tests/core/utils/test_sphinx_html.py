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

"""Unit tests for pydidas modules."""

__author__ = "Malte Storm"
__copyright__ = "Copyright 2024 - 2026, Helmholtz-Zentrum Hereon"
__license__ = "GPL-3.0-only"
__maintainer__ = "Malte Storm"
__status__ = "Production"


import copy
import io
import shutil
import sys
import warnings
from contextlib import redirect_stdout
from pathlib import Path
from unittest.mock import patch

import pytest

from pydidas import VERSION
from pydidas.core.utils import DOC_SOURCE_DIRECTORY, sphinx_html


@pytest.fixture
def setup_test_env(temp_path):
    """
    Set up test environment with temporary directories and sys.argv backup.
    """
    argv_backup = copy.copy(sys.argv)
    (temp_path / "docs" / "build").mkdir(parents=True, exist_ok=True)
    yield
    shutil.rmtree(temp_path / "docs")
    sys.argv = argv_backup


def test_check_sphinx_html_docs__generic_case(setup_test_env, temp_path) -> None:
    """Test check_sphinx_html_docs with existing docs-built.yml file."""
    with open(temp_path / "docs" / "build" / "docs-built.yml", "w") as f:
        f.write(f"{VERSION}: true")
    assert sphinx_html.check_sphinx_html_docs(temp_path / "docs" / "build")


def test_check_sphinx_html_docs__empty_folder(setup_test_env, temp_path) -> None:
    """Test check_sphinx_html_docs with empty folder."""
    assert not sphinx_html.check_sphinx_html_docs(temp_path / "docs" / "build")


def test_check_sphinx_html_docs__sphinx_running(setup_test_env, temp_path) -> None:
    """Test check_sphinx_html_docs when sphinx-build is running."""
    sys.argv.append("sphinx-build")
    assert not sphinx_html.check_sphinx_html_docs(temp_path / "docs" / "build")


@pytest.mark.slow
@patch("pydidas.core.utils.sphinx_html.subprocess.run")
def test_run_sphinx_html_build(mock_subprocess_run, setup_test_env, temp_path) -> None:
    """Test run_sphinx_html_build with mocked subprocess.run."""
    shutil.copytree(Path(DOC_SOURCE_DIRECTORY) / "src", temp_path / "docs" / "src")
    with warnings.catch_warnings(), io.StringIO() as buf, redirect_stdout(buf):
        warnings.simplefilter("ignore")
        sphinx_html.run_sphinx_html_build(build_dir=temp_path / "docs" / "html")
    mock_subprocess_run.assert_called_once()
    call_args = mock_subprocess_run.call_args[0][0]
    assert "sphinx" in call_args
    assert "-b" in call_args
    assert "html" in call_args


if __name__ == "__main__":
    pytest.main()
