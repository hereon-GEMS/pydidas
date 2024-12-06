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
Module with the ScanIoFio class which is used to importscan axes from fio file(s).
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
from typing import Self

from pydidas.core.constants import YAML_EXTENSIONS
from pydidas.contexts.scan import Scan
from pydidas.contexts.scan.scan_context import ScanContext
from pydidas.contexts.scan.scan_io_base import ScanIoBase
from pydidas.core import UserConfigError

SCAN = ScanContext()


class ScanIoFio(ScanIoBase):
    """
    FIO importer/exporter for Scan objects.
    """

    extensions = ['fio']
    format_name = "FIO"
    def __init__(self):
        return
    
    
    @classmethod    
    def import_from_file(cls, filename: list[str], scan: Union[Scan, None] = None):
        scan = SCAN if scan is None else scan
        if len(filename)==1:
            cls.import_single_fio(filename, scan)
        else:
            cls.import_multiple_fio(filename, scan)
    
    @classmethod
    def import_single_fio(cls,filename: list[str], scan: Union[Scan, None] = None):
        _scan = SCAN if scan is None else scan
        with open(filename[0], "r") as stream: 
            file_lines = stream.read().split("\n")
            try:
                for item in file_lines:
                    if ("ascan") in item:
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
                        return
                    if ("dscan") in item:
                        scan_motor_name = item.split(' ')[1]
                        len_scan = int(item.split(' ')[4])
                        str_scan_pars =  [float(i) for i in item.split(' ')[2:]]
                        step_scan = (str_scan_pars[1]-str_scan_pars[0])/(str_scan_pars[2])
                        flag=0
                        # _scan.set_param_value("scan_dim0_offset",float(file_lines[-3].split(' ')[1]))
                        for i_end in [1,2,3,4,5]:
                            if flag==0:    
                                try:
                                    for i_line in [1,2,3,4,5]:
                                        if flag==0:
                                            end_scan = float(file_lines[-i_end].split(' ')[i_line])
                                        flag=1
                                except:
                                    pass
                        start_scan = end_scan-step_scan*(len_scan)
                        
                        scan_pos = np.linspace(start_scan,end_scan,int(str_scan_pars[2])+1)
                        _scan.set_param_value("scan_dim0_delta",step_scan)
                        _scan.set_param_value("scan_dim0_n_points",len_scan)
                        _scan.set_param_value("scan_dim0_offset",start_scan) 
                        _scan.set_param_value("scan_dim0_label",scan_motor_name) 
                        return
                raise UserConfigError("No scan command found.")
            except yaml.YAMLError as yerr:
                cls.imported_params = {}
                raise yaml.YAMLError from yerr
    
    @classmethod
    def import_multiple_fio(cls,filename: list[str], scan: Union[Scan, None] = None):
        _scan = SCAN if scan is None else scan
        with open(filename[0], "r") as stream: 
            file_lines = stream.read().split("\n")
            try:
                for item in file_lines:
                    if ("ascan") in item:
                        scan_motor_name = item.split(' ')[1]
                        len_scan = int(item.split(' ')[4])
                        str_scan_pars =  [float(i) for i in item.split(' ')[2:]]
                        start_scan = str_scan_pars[0]
                        end_scan = str_scan_pars[1]
                        step_scan = (str_scan_pars[1]-str_scan_pars[0])/(str_scan_pars[2])
                        # scan_pos = numpy.linspace(start_scan,end_scan,int(str_scan_pars[2])+1)
                        
                    if ("dscan") in item:
                        scan_motor_name = item.split(' ')[1]
                        len_scan = int(item.split(' ')[4])
                        str_scan_pars =  [float(i) for i in item.split(' ')[2:]]
                        step_scan = (str_scan_pars[1]-str_scan_pars[0])/(str_scan_pars[2])
                        flag=0
                        # _scan.set_param_value("scan_dim0_offset",float(file_lines[-3].split(' ')[1]))
                        for i_end in [1,2,3,4,5]:
                            if flag==0:    
                                try:
                                    for i_line in [1,2,3,4,5]:
                                        if flag==0:
                                            end_scan = float(file_lines[-i_end].split(' ')[i_line])
                                        flag=1
                                except:
                                    pass
                        start_scan = end_scan-step_scan*(len_scan)
                        
                        scan_pos = np.linspace(start_scan,end_scan,int(str_scan_pars[2])+1)
                # raise UserConfigError("No scan command found.")
            except yaml.YAMLError as yerr:
                cls.imported_params = {}
                raise yaml.YAMLError from yerr
        
        try:
            _scan.set_param_value("scan_dim",2)
            _scan.set_param_value("scan_dim1_delta",step_scan)
            _scan.set_param_value("scan_dim1_n_points",len_scan)
            _scan.set_param_value("scan_dim1_offset",start_scan) 
            _scan.set_param_value("scan_dim1_label",scan_motor_name)
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
            _scan.set_param_value("scan_dim0_delta",(scsp[-1]-scsp[0])/(len(scsp)-1))
            _scan.set_param_value("scan_dim0_n_points",len(scsp))
            _scan.set_param_value("scan_dim0_offset",scsp[0]) 
            _scan.set_param_value("scan_dim0_label",str(arr_motor_names[motor_moved_scans_ind]))
        except yaml.YAMLError as yerr:
            cls.imported_params = {}
            raise yaml.YAMLError from yerr
             
        # SCAN = scan 