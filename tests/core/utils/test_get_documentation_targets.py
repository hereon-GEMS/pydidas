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

"""Unit tests for pydidas.core.utils.get_documentation_targets."""

__author__ = "Malte Storm"
__copyright__ = "Copyright 2024 - 2026, Helmholtz-Zentrum Hereon"
__license__ = "GPL-3.0-only"
__maintainer__ = "Malte Storm"
__status__ = "Production"


from pathlib import Path

import pytest

from pydidas.core.utils import (
    DOC_BUILD_PATH,
    DOC_HOME_ADDRESS,
    DOC_HOME_FILENAME_STR,
    DOC_HOME_QURL,
    DOC_SOURCE_DIRECTORY,
)
from pydidas.core.utils import (
    get_documentation_targets as doc_targets,
)
from pydidas.core.utils.file_utils import path_as_formatted_str
from pydidas.core.utils.get_documentation_targets import (
    doc_path_for_gui_manual,
    doc_qurl_for_gui_manual,
    doc_qurl_for_rel_address,
)


def _expected_gui_fname_str(name: str, class_type: str) -> str:
    return path_as_formatted_str(
        DOC_BUILD_PATH / "html" / "manuals" / "gui" / f"{class_type}s" / f"{name}.html"
    )


def test_documentation_constants_are_consistent_with_module_location():
    """Ensure module constants are internally consistent and valid file URLs."""
    assert DOC_BUILD_PATH == (Path(doc_targets.__file__).parents[2] / "sphinx")
    assert DOC_SOURCE_DIRECTORY == (Path(doc_targets.__file__).parents[2] / "docs")

    expected_home = path_as_formatted_str(DOC_BUILD_PATH / "html" / "index.html")
    assert DOC_HOME_FILENAME_STR == expected_home
    assert DOC_HOME_ADDRESS == f"file:///{expected_home}"
    assert DOC_HOME_QURL.isValid()
    assert DOC_HOME_QURL.toString() == DOC_HOME_ADDRESS


@pytest.mark.parametrize("class_type", ["frame", "window"])
@pytest.mark.parametrize("name", ["MainWindow", "My_Frame"])
def test_doc_path_for_gui_manual(name, class_type):
    _expected = _expected_gui_fname_str(name, class_type)
    assert doc_path_for_gui_manual(name, class_type) == Path(_expected)


@pytest.mark.parametrize("class_type", ["frame", "window"])
@pytest.mark.parametrize("name", ["MainWindow", "My_Frame"])
def test_doc_qurl_for_gui_manual(name, class_type):
    _expected = _expected_gui_fname_str(name, class_type)
    _qurl = doc_qurl_for_gui_manual(name, class_type)
    assert _qurl.isValid()
    assert _qurl.toLocalFile() == _expected


@pytest.mark.parametrize("address", ["man/gui/intro.html", Path("man/gui/intro.html")])
def test_doc_qurl_for_rel_address(address):
    _qurl = doc_qurl_for_rel_address(address)

    _expected = path_as_formatted_str(
        DOC_BUILD_PATH / "html" / "man" / "gui" / "intro.html"
    )
    assert _qurl.isValid()
    assert _qurl.isValid()
    assert _qurl.toLocalFile() == _expected


def test_doc_qurl_for_rel_address__test_empty_relative_address():
    _qurl = doc_qurl_for_rel_address("")

    _expected = path_as_formatted_str(DOC_BUILD_PATH / "html")
    assert _qurl.isValid()
    assert _qurl.toLocalFile() == _expected


if __name__ == "__main__":
    pytest.main([__file__])
