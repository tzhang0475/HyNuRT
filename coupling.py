#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# File              : coupling.py
# Author            : tzhang
# Date              : 27.07.2020
# Last Modified Date: 30.07.2020
# Last Modified By  : tzhang

#from eco_analysis import *
        
"""

a module to couple data between system performance and economic analysis

"""
class cp:
#    def __init__(self):
#        pass

    # a module to transfer period performance data to comparable annular performance data
    def time_scale_trans(time):
        # min in a year, neglect leap year
        min_year = 365 * 24 * 60

        # get calculated performance data time scale, in min
        time_cal = time[-1]

        # ratio between calculated time and annular time
        t_scale = min_year/time_cal

        return t_scale

    # obtain component name in the system
    def get_comp_name(sys_config):
        name_comp = []
        for key in sys_config.keys():
            name_comp.append(key)

        return name_comp

    # obtain component char number in the system
    def get_comp_char(sys_config):
        num_char = []
        for key in sys_config.keys():
            num_char.append(sys_config[key][0])

        return num_char

    # create class mapping of economic modules
    def mapping_eco(sys_config,smr_eco=None,wfarm_eco=None,PV_eco=None,PEM_eco=None):
        post_char = "_eco"

        name_comp = self.get_comp_name(sys_config)
        num_char = self.get_comp_char(sys_config)

        eco_map = []
        for i in range(len(name_comp)):
            map_char = name_comp[i]+post_char

            if num_char[i] == '00':
                classmap = {map_char:smr_eco}
                eco_map.append(classmap)
            elif num_char[i] == '01':
                classmap = {map_char:wfarm_eco}
                eco_map.append(classmap)
            elif num_char[i] == '02':
                classmap = {map_char:PV_eco}
                eco_map.append(classmap)
            elif num_char[i] == '10':
                classmap = {map_char:PEM_eco}
                eco_map.append(classmap)
            elif num_char[i] == '20':
                # under development
                pass

        return eco_map


    # calculating scales to be calculate in the lifetime of the system
    def case_to_cal(lifetime_scale):
        cases = []
        # add case index
        cases.append(lifetime_scale[0][1:])

        for i in range(1,len(lifetime_scale)):
            scale_data = lifetime_scale[i][1:]
            sum_data = sum(scale_data)
            if scale_data not in cases and sum_data != 0.0:
                cases.append(scale_data)
            else:
                pass

        return cases

    # obtain data from performance model to economic model
    def model_cp_data(e_to_grid_array,e_to_h2_array,m_h2_array):
        dataflow = []

        # total electricity to grid, in MWh
        e_to_grid = e_to_grid_array[-1]
        # total electricity to pem, in MWh
        e_to_h2 = e_to_h2_array[-1]
        # total h2 produced, in kg
        m_h2 = m_h2_array[-1]

        # merge to data array
        dataflow.append(e_to_grid)
        dataflow.append(e_to_h2)
        dataflow.append(m_h2)
    
        return dataflow

    # rescale data to annual data according to time
    def data_scale(dataflow,t_scale):
        dataflow_new = []
        
        for data in dataflow:
            data_new = data * t_scale
            dataflow_new.append(data_new)

        return dataflow_new

    # convert case data to lifetime data
    def case_lifetime_convert(lifetime_scale,cases,case_data):
        case_lifetime = []
        
        for data in lifetime_scale[1:]:
            sys_data = data[1:]
            if sum(sys_data) == 0.0:
                data_flow = [0.0,0.0,0.0,0.0]
                case_lifetime.append(data_flow)
            else:
                idx = cases.index(sys_data)
                data_flow = case_data[idx-1]
                case_lifetime.append(data_flow)
        
        return case_lifetime
