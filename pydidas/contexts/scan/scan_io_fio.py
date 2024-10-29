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

"""
Module with the ScanIoYaml class which is used to import and export
ScanContext metadata from a YAML file.
"""

__author__ = "Malte Storm"
__copyright__ = "Copyright 2024, Helmholtz-Zentrum Hereon"
__license__ = "GPL-3.0-only"
__maintainer__ = "Malte Storm"
__status__ = "Production"
__all__ = ["ScanIoFio"]


from typing import Union

import yaml
import numpy as np

from pydidas.core.constants import YAML_EXTENSIONS
from pydidas.contexts.scan import Scan
from pydidas.contexts.scan.scan_context import ScanContext
from pydidas.contexts.scan.scan_io_base import ScanIoBase


SCAN = ScanContext()


class ScanIoFio(ScanIoBase):
    """
    YAML importer/exporter for Scan objects.
    """

    extensions = ['fio']
    format_name = "FIO"

    @classmethod
    def export_to_file(cls, filename: str, **kwargs: dict):
        """
        Write the ScanTree to a file.

        Parameters
        ----------
        filename : str
            The filename of the file to be written.
        """
        _scan = kwargs.get("scan", SCAN)
        cls.check_for_existing_file(filename, **kwargs)
        tmp_params = _scan.get_param_values_as_dict(filter_types_for_export=True)
        with open(filename, "w") as stream:
            yaml.safe_dump(tmp_params, stream)
    
    @classmethod
    def import_from_file(cls, filename: str, scan: Union[Scan, None] = None):
        """
        Restore the ScanContext from a FIO file.

        Parameters
        ----------
        filename : str
            The filename of the file to be written.
        scan : Union[None, pydidas.contexts.scan.Scan], optional
            The Scan instance to be updated. If None, the ScanContext instance is used.
            The default is None.
        """
        _scan = SCAN if scan is None else scan
        with open(filename[0], "r") as stream: 
            try:
                for item in stream.read().split("\n"):
                    if ("scan") in item:
                        scan_motor_name = item.split(' ')[1]
                        len_scan = int(item.split(' ')[4])
                        str_scan_pars =  [float(i) for i in item.split(' ')[2:]]
                        start_scan = str_scan_pars[0]
                        end_scan = str_scan_pars[1]
                        step_scan = (str_scan_pars[1]-str_scan_pars[0])/(str_scan_pars[2])
                        # scan_pos = numpy.linspace(start_scan,end_scan,int(str_scan_pars[2])+1)
                        _scan.set_param_value("scan_dim0_delta",step_scan)
                        _scan.set_param_value("scan_dim0_n_points",len_scan)
                        _scan.set_param_value("scan_dim0_offset",start_scan) 
                        _scan.set_param_value("scan_dim0_label",scan_motor_name) 
            except yaml.YAMLError as yerr:
                cls.imported_params = {}
                raise yaml.YAMLError from yerr
            
        try:
            _scan.set_param_value("scan_dim",2)
            num_motors = 0
            with open(filename[0], "r") as stream:
                for item in stream.read().split("\n"):
                    if "=" in item:
                        if 'nan' not in item:            
                            varnum = item.split(' = ')
                            varnum[1] = float(varnum[1])
                            num_motors +=1
            arr_motor_names = ["" for x in range(num_motors)]
            arr_motor_pos = np.ones((num_motors,len(filename)))
            i_scan = 0
            for f in filename:
                str_r = open(f).read()
                i_arr_motors = 0
                for item in str_r.split("\n"):
                    if "=" in item:
                        if 'nan' not in item:
                            varnum = item.split(' = ')
                            varnum[1] = float(varnum[1])
                            arr_motor_names[i_arr_motors] =      tuple(varnum)[0]
                            arr_motor_pos[i_arr_motors,i_scan] = tuple(varnum)[1]
                            i_arr_motors+=1                
                i_scan+=1
            motors_moved_ind_arr = np.unique(np.where(np.diff(arr_motor_pos,axis=1)!=0)[0],\
                             return_counts=True)
            motors_moved_ind = motors_moved_ind_arr[0][np.argsort(motors_moved_ind_arr[1][:2])]
            
            scan_motor_index = arr_motor_names.index(scan_motor_name)
            motor_moved_scans_ind = np.setdiff1d(motors_moved_ind,[scan_motor_index])[0]
            scsp = arr_motor_pos[motor_moved_scans_ind]
            _scan.set_param_value("scan_dim1_delta",(scsp[-1]-scsp[0])/(len(scsp)-1))
            _scan.set_param_value("scan_dim1_n_points",len(scsp))
            _scan.set_param_value("scan_dim1_offset",scsp[0]) 
            _scan.set_param_value("scan_dim1_label",str(arr_motor_names[motor_moved_scans_ind]))
        except:
            pass

        # assert isinstance(cls.imported_params, dict)
        # cls._verify_all_entries_present()
        # cls._write_to_scan_settings(scan=_scan)