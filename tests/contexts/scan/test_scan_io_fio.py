# This file is part of pydidas.
#
# Copyright 2023 - 2024, Helmholtz-Zentrum Hereon
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
__copyright__ = "Copyright 2023 - 2024, Helmholtz-Zentrum Hereon"
__license__ = "GPL-3.0-only"
__maintainer__ = "Malte Storm"
__status__ = "Production"


import os

import pytest, tempfile



from pydidas.contexts import ScanContext
from pydidas.contexts.scan import Scan
from pydidas.contexts.scan.scan_io_fio import ScanIoFio

from pydidas.core import UserConfigError

@pytest.fixture
def create_scan_io_fio():
    return ScanIoFio(), ScanContext()

def test_import_from_file__validation(create_scan_io_fio):
    scaniofio, SCAN = create_scan_io_fio
    _test_dir = os.path.dirname(os.path.dirname(os.path.dirname(__file__)))
    filenames = [_test_dir+r'\_data\test_single_fio.fio']
    
    scaniofio.import_from_file(filenames, scan=SCAN)
    
    assert SCAN.get_param_value("scan_dim0_offset")==10.0
    assert SCAN.get_param_value("scan_dim0_delta")==2.0
    assert SCAN.get_param_value("scan_dim0_label")=='cube1_x'
    assert SCAN.get_param_value("scan_dim0_n_points")==34


def test_import_from_files__validation(create_scan_io_fio):
    scaniofio, SCAN = create_scan_io_fio
    _test_dir = os.path.dirname(os.path.dirname(os.path.dirname(__file__)))
    filenames = [os.path.join(_test_dir,'_data','test_mult_fio',s) \
                 for s in os.listdir(_test_dir+r'\_data\test_mult_fio')]
    scaniofio.import_from_file(filenames, scan=SCAN)

    assert 9.9<SCAN.get_param_value("scan_dim0_offset")<10.1
    assert 2.05<SCAN.get_param_value("scan_dim0_delta")<2.15
    assert SCAN.get_param_value("scan_dim0_label")=='cube1_y'
    assert SCAN.get_param_value("scan_dim0_n_points")==10


    assert SCAN.get_param_value("scan_dim1_offset")==10.0
    assert 2.<SCAN.get_param_value("scan_dim1_delta")<2.1
    assert SCAN.get_param_value("scan_dim1_label")=='cube1_x'
    assert SCAN.get_param_value("scan_dim1_n_points")==34
    
def test_import_from_file__corrupt_file(create_scan_io_fio):
    scaniofio, SCAN = create_scan_io_fio
    # _test_dir = os.path.dirname(os.path.dirname(os.path.dirname(__file__)))
    # filenames = [_test_dir+r'\_data\test_single_fio.fio']
    _tmppath = tempfile.mkdtemp()
    _tmpfile = tempfile.mkstemp(dir=_tmppath)
    print(_tmpfile)
    with pytest.raises(UserConfigError):
        scaniofio.import_from_file([_tmpfile[1]], scan=SCAN)
    assert scaniofio.imported_params == {}
    os.close(_tmpfile[0])
    os.remove(_tmpfile[1])
    
    os.rmdir(_tmppath)

pytest.main()

##SCAN = ScanContext()

