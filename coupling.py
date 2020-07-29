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
    def __init__(self):
        self.r_scale = 0.0

    # a module to transfer period performance data to comparable annular performance data
    def timescale_trans(self,time):
        # min in a year, neglect leap year
        min_year = 365 * 24 * 60

        # get calculated performance data time scale, in min
        time_cal = time[-1]

        # ratio between calculated time and annular time
        r_scale = min_year/time_cal

        self.r_scale = r_scale

    # obtain component name in the system
    def get_comp_name(self,sys_config):
        name_comp = []
        for key in sys_config.keys():
            name_comp.append(key)

        return name_comp

    # obtain component char number in the system
    def get_comp_char(self,sys_config):
        num_char = []
        for key in sys_config.keys():
            num_char.append(sys_config[key][0])

        return num_char

    # create class mapping of economic modules
    def mapping_eco(self,sys_config,smr_eco=None,wfarm_eco=None,PV_eco=None,PEM_eco=None):
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



    # a module calculating 
