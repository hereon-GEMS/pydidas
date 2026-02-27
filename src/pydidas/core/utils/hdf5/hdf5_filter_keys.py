# This file is part of pydidas
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
# along with pydidas If not, see <http://www.gnu.org/licenses/>.

"""
Module with filter keys for the HDF5 dataset selector.

The filters are defined as a dictionary with the key being the path to the
dataset and the value being a description of the filter.
"""

__author__ = "Malte Storm"
__copyright__ = "Copyright 2026, Helmholtz-Zentrum Hereon"
__license__ = "GPL-3.0-only"
__maintainer__ = "Malte Storm"
__status__ = "Production"
__all__ = [
    "FILTER_KEYS",
    "FILTER_EXCEPTIONS",
    "FILTER_KEY_DEFAULT_ACTIVE",
    "FILTER_KEY_TITLE",
    "FILTER_KEY_TOOLTIP",
]


FILTER_KEYS = [
    "/entry/instrument/detector/",
    "/entry/instrument/detector/detectorSpecific/",
    "/entry/sample/",
]

FILTER_EXCEPTIONS = {
    "/entry/instrument/detector/": ["/entry/instrument/detector/data"],
    "/entry/instrument/detector/detectorSpecific/": [],
    "/entry/sample/": [],
}

FILTER_KEY_DEFAULT_ACTIVE = {
    "/entry/instrument/detector/": True,
    "/entry/instrument/detector/detectorSpecific/": False,
    "/entry/sample/": False,
}

FILTER_KEY_TITLE = {
    "/entry/instrument/detector/": " Hide `/entry/instrument/detector`\n keys",
    "/entry/instrument/detector/detectorSpecific/": (
        " Hide Dectris\n `detectorSpecific` keys"
    ),
    "/entry/sample/": " Hide `/entry/sample` keys",
}

FILTER_KEY_TOOLTIP = {
    "/entry/instrument/detector/": (
        "Hide all keys in the group `/entry/instrument/detector/` except for the "
        "dataset `/entry/instrument/detector/data`. The `/entry/instrument/detector/` "
        "group is used to store detector metadata. Some manufacturers/drivers (e.g. "
        "X-Spectrum for their Lambda detectors) store the image data in the "
        "`/entry/instrument/detector/data` dataset which is therefore not hidden "
        "by this filter."
    ),
    "/entry/instrument/detector/detectorSpecific/": (
        "Hide all keys in the group `/entry/instrument/detector/detectorSpecific/`. "
        "This group is used to store detector-module specific metadata for Dectris "
        "detectors (e.g. Eiger). Note that the filter for `/entry/instrument/"
        "detector/` also hides the keys in this group, if enabled."
    ),
    "/entry/sample/": (
        "Hide all keys in the group `/entry/sample/`. This group is used to store "
        "metadata about the sample, e.g. the sample name, the sample position, etc."
    ),
}
