# This file is part of pydidas.
#
# Copyright 2024, Helmholtz-Zentrum Hereon
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
__copyright__ = "Copyright 2024, Helmholtz-Zentrum Hereon"
__license__ = "GPL-3.0-only"
__maintainer__ = "Malte Storm"
__status__ = "Production"

import json
import os
from pathlib import Path
import sys

_current_path = Path(os.getcwd())
_new_version = "--new-version" in sys.argv

if not _new_version:
    sys.exit(0)

with open(_current_path.joinpath("stable_version.txt"), "r") as f:
    _current_version = f.read().strip()

with open(_current_path.joinpath("pydata_version_switcher.json"), "r") as f:
    _json_content = json.load(f)

for _item in _json_content:
    if _item["version"] == _current_version:
        print(
            f"Version {_current_version} already exists in pydata_version_switcher.json"
        )
        sys.exit(0)

_new_item = None
for _item in _json_content:
    if _item.get("name", "None") == "latest release":
        _new_item = {
            "version": _item["version"],
            "url": _item["url"].replace("stable", _item["version"]),
        }
        _item["version"] = _current_version
        _json_content.insert(1, _new_item)
        break

if _new_item is None:
    print(
        "Could not find the `latest release` key in pydata_version_switcher.json\n"
        "Please check the file content and try again."
    )
    sys.exit(1)

with open(_current_path.joinpath("pydata_version_switcher.json"), "w") as f:
    json.dump(_json_content, f, indent=4)
