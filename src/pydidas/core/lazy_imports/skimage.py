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

"""
The fabio module holds functions exposed by the fabio package, which
are lazily imported to reduce initial loading time.
"""

__author__ = "Malte Storm"
__copyright__ = "Copyright 2026, Helmholtz-Zentrum Hereon"
__license__ = "GPL-3.0-only"
__maintainer__ = "Malte Storm"
__status__ = "Production"
__all__ = ["TiffFileError", "imread", "imsave"]


from typing import TYPE_CHECKING

from pydidas.core.lazy_imports.lazy_objects import LazyObject


if TYPE_CHECKING:
    from skimage.io import imread, imsave
    from tifffile import TiffFileError
else:
    imsave = LazyObject("skimage.io", "imsave")
    imread = LazyObject("skimage.io", "imread")
    TiffFileError = LazyObject("tifffile", "TiffFileError")
