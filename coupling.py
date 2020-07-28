#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# File              : coupling.py
# Author            : tzhang
# Date              : 27.07.2020
# Last Modified Date: 27.07.2020
# Last Modified By  : tzhang

        
"""

a module to couple data between system performance and economic analysis

"""
class couple:
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

    # a module calculating 
