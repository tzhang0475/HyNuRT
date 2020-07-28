#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# File              : sys_control.py
# Author            : tzhang
# Date              : 24.11.2019
# Last Modified Date: 27.07.2020
# Last Modified By  : tzhang

"""

a control module to balance energy between coupled system and hydrogen system

"""
class balancing:
    def __init__(self):
        self.dP = []

    # calculate the power from coupled nu-re system to h2 system (can be positive or negative)
    def cal_to_h2sys(self,P_coupled,P_demand,Pmin_cluster):
        P_to_h2sys_array = []

        balancing._dP_cal_(self,P_coupled,P_demand)


        for i in range(len(self.dP)):
            if self.dP[i] >= Pmin_cluster:
                P_to_h2sys = balancing._full_electrolysis_(self,i)
            elif self.dP[i] >= 0 and self.dP[i] < Pmin_cluster:
                P_to_h2sys = balancing._partial_electrolysis_(self,i)
            else:
                P_to_h2sys = balancing._full_fuelcell_(self,i)

            P_to_h2sys_array.append(P_to_h2sys)


        return P_to_h2sys_array

    # calculated the delta between coupled nuclear-wind system and the grid demand
    def _dP_cal_(self,P_coupled,P_demand):
        dP = P_coupled - P_demand
        dP = list(dP)
        print (dP)
        self.dP = dP

    # calculate the power to hydrogen system if residual power is larger than the minimum opearion demand
    def _full_electrolysis_(self,i):
        P_nure_to_h2sys = self.dP[i]

        return P_nure_to_h2sys

    # calulate the power to the hydrogen system when the residual power can only run some electrolysis
    def _partial_electrolysis_(self,i):
        P_nure_to_h2sys = self.dP[i]

        return P_nure_to_h2sys
    # calulate the power demand from the hydrogen system when coupled system at low production rate
    def _full_fuelcell_(self,i):
        P_nure_to_h2sys = self.dP[i]
        
        return P_nure_to_h2sys


    # calculate the power to the grid
    def cal_to_grid(self,P_coupled,P_h2_produced,P_h2_consumed):
        P_to_grid = P_coupled + P_h2_produced - P_h2_consumed

        return P_to_grid

    # calculate total energy send to grid
    def cal_e_acc_grid(self,P_to_grid,time):
        e_acc_to_grid = [0.0]

        for i in range(1,len(time)):
            e_grid = P_to_grid[i-1] * (time[i]-time[i-1]) # please note the unit of time is min
            e_grid = e_grid/60.0 # convert MWmin to MWh

            e_acc_grid = e_acc_to_grid[i-1] + e_grid
            e_acc_to_grid.append(e_acc_grid)

        return e_acc_to_grid

    # calculate total energy send to pem system
    def cal_e_acc_h2sys(self,P_to_h2sys,time):
        e_acc_to_h2sys = [0.0]
        e_acc_from_h2sys = [0.0]
        e_acc_net_h2sys = [0.0]

        for i in range(1,len(time)):
            e_h2 = P_to_h2sys[i-1] * (time[i]-time[i-1])  # please note the unit of time is min here
            e_h2 = e_h2/60.0    # convert MWmin to MWh
            if e_h2 > 0:
                e_acc_h2 = e_acc_to_h2sys[i-1] + e_h2
                e_acc_to_h2sys.append(e_acc_h2)
                e_acc_from_h2sys.append(e_acc_from_h2sys[i-1])
            elif e_h2 < 0:
                e_acc_h2 = e_acc_from_h2sys[i-1] + e_h2
                e_acc_to_h2sys.append(e_acc_to_h2sys[i-1])
                e_acc_from_h2sys.append(e_acc_h2)
            else:
                e_acc_to_h2sys.append(e_acc_to_h2sys[i-1])
                e_acc_from_h2sys.append(e_acc_from_h2sys[i-1])

            e_acc_net = e_acc_net_h2sys[i-1] + e_h2
            e_acc_net_h2sys.append(e_acc_net)

        return e_acc_to_h2sys,e_acc_from_h2sys,e_acc_net_h2sys



