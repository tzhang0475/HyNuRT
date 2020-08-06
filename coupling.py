#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# File              : coupling.py
# Author            : tzhang
# Date              : 27.07.2020
# Last Modified Date: 06.08.2020
# Last Modified By  : tzhang

#from eco_analysis import *

import numpy as np
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

        name_comp = cp.get_comp_name(sys_config)
        num_char = cp.get_comp_char(sys_config)

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
    def model_cp_data(e_to_grid_array,e_to_h2_array,e_abandon_array,m_h2_array):
        dataflow = []

        # total electricity to grid, in MWh
        e_to_grid = e_to_grid_array[-1]
        # total electricity to pem, in MWh
        e_to_h2 = e_to_h2_array[-1]
        # total abndoned energy
        e_abandon = e_abandon_array[-1]
        # total h2 produced, in kg
        m_h2 = m_h2_array[-1]

        # merge to data array
        dataflow.append(e_to_grid)
        dataflow.append(e_to_h2)
        dataflow.append(e_abandon)
        dataflow.append(m_h2)
    
        return dataflow

    # rescale data to annual data according to time
    def data_scale(dataflow,t_scale):
        dataflow_new = []
        
        for data in dataflow:
            data_new = data * t_scale
            dataflow_new.append(data_new)

        return dataflow_new

    # merge case_data of different inFiles to get average
    def case_data_ave(case_dict):

        case_data = []

        for key in case_dict.keys():
            try:
                case_array
            except NameError:
                case_array = np.zeros((len(case_dict[key]),5))

            data = np.asarray(case_dict[key], dtype = float)
            case_array = case_array + data

        case_array = case_array/len(case_dict)

        for data in case_array:
            data = list(data)
            case_data.append(data)

        return case_data

    # convert case data to lifetime data
    def case_lifetime_convert(lifetime_scale,cases,case_data):
        case_lifetime = []
        
        for data in lifetime_scale[1:]:
            sys_data = data[1:]
            if sum(sys_data) == 0.0:
                data_flow = [0.0,0.0,0.0,0.0,0.0]
                case_lifetime.append(data_flow)
            else:
                idx = cases.index(sys_data)
                data_flow = case_data[idx-1]
                case_lifetime.append(data_flow)
        
        return case_lifetime

    # creat array for electricity price to grid, electricity price to h2, h2_price with constant base value
    def cal_price_array(lifetime_scale,price_e_base,price_ePEM_base,price_h2_base,e_inflation=None,ePEM_fluctuation=None,h2_fluctuation=None):

        # check if price model exsits
        if e_inflation == None:
            e_inflation = 1.0

        if ePEM_fluctuation == None:
            ePEM_fluctuation = 1.0

        if h2_fluctuation == None:
            h2_fluctuation = 1.0

        price_e = []
        price_ePEM = []
        price_h2 = []

        for i in range(1,len(lifetime_scale)):
            price_e_year = price_e_base * e_inflation**(i-1)
            price_ePEM_year = price_ePEM_base * ePEM_fluctuation**(i-1)
            price_h2_year = price_h2_base * h2_fluctuation**(i-1)
            
            price_e.append(price_e_year)
            price_ePEM.append(price_ePEM_year)
            price_h2.append(price_h2_year)


        return price_e,price_ePEM,price_h2

    # calculate array for energy coupling
    def cal_energy_array(case_lifetime):

        e_to_grid = []
        e_to_h2 = []
        e_ab = []
        m_h2 = []

        for i in range(len(case_lifetime)):
            e_to_grid.append(case_lifetime[i][0])
            e_to_h2.append(case_lifetime[i][1])
            e_ab.append(case_lifetime[i][2])
            m_h2.append(case_lifetime[i][3])

        return e_to_grid,e_to_h2,e_ab,m_h2

    # calculate system utilization factor
    def cal_f_uti(lifetime_scale,e_to_grid,e_to_h2):
        f_uti_array = []
        # hours in a year
        hours = 365 * 24
        # get array of utilization factor
        for i in range(1,len(lifetime_scale)):
            # energy produced with installed capacity
            if lifetime_scale[i][-2] != 0.0:
                e_capa = lifetime_scale[i][-2] * hours
                f = (e_to_grid[i-1]+e_to_h2[i-1])/e_capa
                f_uti_array.append(f)

        f_uti = sum(f_uti_array)/len(f_uti_array)

        return f_uti


