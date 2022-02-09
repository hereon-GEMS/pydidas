# This file is part of pydidas.
#
# pydidas is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
#
# Pydidas is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE. See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with Pydidas. If not, see <http://www.gnu.org/licenses/>.

"""
File_config holds information about extension names and filename formatting.
"""

__author__ = "Malte Storm"
__copyright__ = "Copyright 2021, Malte Storm, Helmholtz-Zentrum Hereon"
__license__ = "GPL-3.0"
__version__ = "0.1.0"
__maintainer__ = "Malte Storm"
__status__ = "Development"
__all__ = ['HDF5_EXTENSIONS', 'NUMPY_EXTENSIONS', 'BINARY_EXTENSIONS',
           'TIFF_EXTENSIONS', 'JPG_EXTENSIONS', 'FABIO_EXTENSIONS',
           'YAML_EXTENSIONS', 'FILENAME_DELIMITERS']


HDF5_EXTENSIONS = ['.h5', '.hdf', '.nxs', '.hdf5', '.HDF5']

NUMPY_EXTENSIONS = ['.npy', '.np', '.npz']

BINARY_EXTENSIONS = ['.raw', '.bin']

TIFF_EXTENSIONS = ['.tif', '.tiff']

JPG_EXTENSIONS = ['.jpg', '.jpeg']

FABIO_EXTENSIONS = ['.edf', '.mccd', '.mar3450', '.f2d', '.cbf']

YAML_EXTENSIONS = ['.yaml', '.yml']

FILENAME_DELIMITERS = '\.|_|-| '
