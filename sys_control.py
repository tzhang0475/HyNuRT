#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# File              : sys_control.py
# Author            : tzhang
# Date              : 24.11.2019
# Last Modified Date: 14.08.2020
# Last Modified By  : tzhang

import numpy as np

"""

a module account for system overall configuration

num_chars:
    00  nuclear power plant
    01  wind turbine
    02  solar panels (not yet implemented)

    10  PEM stacks

    20  hydrogen stoage (very simple mode currently)

"""
class sys_config:
    def __init__(self,components,num_chars,unit_power,n_units,lifetimes,con_time,sys_lifetime):
        config = {}

        # dictionary for the system configuration
        for i in range(len(components)):
            config[components[i]] = []
            config[components[i]].append(num_chars[i])     # characteristic number of each component
            config[components[i]].append(unit_power[i])     # nominal power of unit  of each component, in MW
            config[components[i]].append(n_units[i])         # number of units of each component
            config[components[i]].append(lifetimes[i])         # lifetime of each component
            config[components[i]].append(con_time[i])         # lifetime of each component

            # different lifetime of components causese re-construction of the components during the system life time. As an example, the lifetime of the system is 60 years, and the lifetime of wind turbines are 30 years, 60/30 = 2 batches are needed in the system; if the system liffetime is 50 year, wind turbines are 30 years, 50/30 = 2 batches are still needed in this case. However, this should be avoid in making the energy mix
            n_int = int(sys_lifetime/lifetimes[i])
            n_float = sys_lifetime/lifetimes[i]
            div = n_float - n_int
            if div > 0 or div < 0:
                n_batch = n_int + 1
            else:
                n_batch = n_int

            config[components[i]].append(n_batch)   # number of batches in the life cycle

        # system config data class
        self.config = config

        # lifetime of the system
        self.lifetime = sys_lifetime

"""

a test module 


components = ['SMR','wind','PEM','storage']
num_chars = ['00','01','10','20']
unit_power = [60.0,2.0,0.6,0.0]
n_units = [6,80,500,1]
lifetimes = [60,30,20,60]
con_time = [2,1,1,1]

sys_lifetime = 60

system = sys_config(components,num_chars,unit_power,n_units,lifetimes,con_time,sys_lifetime)


"""
"""

a module account for operating units of each components in lifetime according to construction plan
auto_con:
    1   automatic construction plan with pre-defined method
    0   manually read construction plan from file

"""
class con_plan(sys_config):
    def __init__(self,components,num_chars,unit_power,n_units,lifetimes,con_time,sys_lifetime):
        super().__init__(components,num_chars,unit_power,n_units,lifetimes,con_time,sys_lifetime)
        self.sys_scale = []         # array for system scaling data
        self.lifetime_scale = []      # array of construciton and operation schedule
        

    def _con_plan_auto_scale_(self):

        npp_in = False   # default no npp in the system
        sys_scale = []
        char = []

        # check whether there is nuclear power plant in the mix
        for key in self.config.keys():
            if '00' in self.config[key][0]:
                npp_in = True   # there is npp
                npp_key = key
                npp_unit = self.config[key][2]
                char.append(self.config[key][0])

        # construction plan when there is npp
        if npp_in:

            unit_renew = []
            unit_couple = []

            match_renew = []
            match_couple = []

            # matching scale of units, for example, 1 npp to 20 wind and 40 PEM
            for key in self.config.keys():
                if self.config[key][0].startswith('0') and self.config[key][0] != '00':
                    unit_renew.append(self.config[key][2])
                    match = int(self.config[key][2]/npp_unit)
                    match_renew.append(match)
                    char.append(self.config[key][0])
                elif self.config[key][0].startswith('1'):
                    unit_couple.append(self.config[key][2])
                    match = int(self.config[key][2]/npp_unit)
                    match_couple.append(match)
                    char.append(self.config[key][0])

            sys_scale.append(char)

            for i in range(self.config[npp_key][2]+1):
                scale = []

                comp_renew = []
                comp_couple = []
                if i != self.config[npp_key][2]:
                    for j in range(len(unit_renew)):
                        unit_curr = i * match_renew[j]
                        comp_renew.append(unit_curr)
                    for j in range(len(unit_couple)):
                        unit_curr = i * match_couple[j]
                        comp_couple.append(unit_curr)
                else:
                    for j in range(len(unit_renew)):
                        unit_last = unit_renew[j] 
                        comp_renew.append(unit_last)
                    for j in range(len(unit_couple)):
                        unit_last = unit_couple[j]
                        comp_couple.append(unit_last)

                scale.append(i)

                for n_uni in comp_renew:
                    scale.append(n_uni)

                for n_uni in comp_couple:
                    scale.append(n_uni)
        
                sys_scale.append(scale)

        # construction plan when there is no npp
        else:
            #########################
            #### to be developed ####
            #########################
            pass  


        return sys_scale       

    # calculate installed capacity and capacity ratio, only npp and renewables are accounted, pem or other compnents with char_num started other than 0 are not accounted
    def _cal_capacity_(self,sys_scale):
        unit_power = []
        n_units = []

        for key in self.config.keys():
            if self.config[key][0].startswith('0'):
                unit_power.append(self.config[key][1])
                n_units.append(self.config[key][2])


        # calculate nominal capacity
        nomi_power = 0.0
        for i in range(len(n_units)):
            power = n_units[i] * unit_power[i]
            nomi_power = nomi_power + power

        for i in range(1,len(sys_scale)):
            capacity = 0
            for j in range(len(unit_power)):
                capacity_comp = sys_scale[i][j] * unit_power[j]
                capacity = capacity + capacity_comp
            r_capa = capacity/nomi_power
            sys_scale[i].append(capacity)
            sys_scale[i].append(r_capa)

        return sys_scale

    # calculate scale data
    def cal_scale(self,auto_con):
        if auto_con == 1:
            sys_scale = self._con_plan_auto_scale_()
        else:
            #########################
            #### to be developed ####
            #########################
            print ('module under development')
            pass

        # calculate installed capacity and capacity ratio
        sys_scale = self._cal_capacity_(sys_scale)

        self.sys_scale = sys_scale

    # calculste construction schedule:
    def con_schedule(self,auto_con):

        if auto_con == 1:
            self._con_schedule_auto_()
        else:
            #########################
            #### to be developed ####
            #########################
            print ('module under development')
            pass


    # automatic form construction schedule
    def _con_schedule_auto_(self):
        con_time = []
        for key in self.config.keys():
            if self.config[key][0].startswith('0') or self.config[key][0].startswith('1'):
                data = []
                data.append(self.config[key][0])
                data.append(self.config[key][2])
                data.append(self.config[key][4])
                con_time.append(data)

        con_time_tmp = np.asarray(con_time,dtype=int)

        # char of core component
        char_comp = con_time[np.argmax(con_time_tmp[:,2])][0]
        # number of units of core component
        unit_comp = con_time[np.argmax(con_time_tmp[:,2])][1]
        # years needed for construction
        y_unit_construct = np.max(con_time_tmp[:,2])

        # calculate duration for construction
        y_construction = unit_comp * y_unit_construct


        # find the column of core comp in sys_scale array
        col = self.sys_scale[0].index(char_comp)

        col_other_comp = []
        for data in self.sys_scale[0]:
            if data != char_comp:
                idx = self.sys_scale[0].index(data)
                col_other_comp.append(idx)

        lifetime_scale = []
        
        name_idx = []
        # add index to column
        name_idx.append('year')
        
        for comp in self.sys_scale[0]:
            name_idx.append(comp)
        name_idx.append('capacity')
        name_idx.append('capacity ratio')
        
        lifetime_scale.append(name_idx)

        for i in range (self.lifetime + int(y_construction/2)):
#        for i in range (y_construction+2):
            data = []
            unit_done = min(int((i-1)/y_unit_construct),unit_comp)
            data.append(i)
            data.append(unit_done)
            # scale matching
            idx = [row[col] for row in self.sys_scale].index(unit_done)
            for j in col_other_comp:
                data.append(self.sys_scale[idx][j])

            # add insalled capacity and capacity ratio
            data.append(self.sys_scale[idx][-2])
            data.append(self.sys_scale[idx][-1])
            lifetime_scale.append(data)

        self.lifetime_scale = lifetime_scale


"""

a test module 

auto_con = 1
sys_con = con_plan(system,con_time)

sys_con.cal_scale(auto_con)
sys_con.con_schedule(auto_con)
print (sys_con.lifetime_scale)


"""

"""

a control module to balance energy between coupled system and hydrogen system

"""
class balancing:
    def __init__(self):
        self.dP = []

    # calculate the power from coupled nu-re system to h2 system (can be positive or negative)
    def cal_to_h2sys_virtual(self,P_coupled,P_demand,Pmin_cluster):
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
       # print (dP)
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

    # calculate the power to pem system
    def cal_to_h2sys(self,P_h2_produced,P_h2_consumed,P_abandon):
        P_to_h2sys_array = []
        
        for i in range(len(P_h2_consumed)):
            P_to_h2sys = P_h2_consumed[i] + P_abandon[i] - P_h2_produced[i]
            P_to_h2sys_array.append(P_to_h2sys)
        
        return P_to_h2sys_array

    # calculate ratio fit the demand
    def ratio_fit(self,P_demand,P_to_grid):
        ratio_list = []
        
        for i in range(len(P_demand)):
            ratio = P_to_grid[i]/P_demand[i]
            ratio_list.append(ratio)

        # calculate average ratio
        ratio_ave = sum(ratio_list)/len(ratio_list)

        return ratio_ave

    # calculate total energy send to grid
    def cal_e_acc_grid(self,P_to_grid,time):
        e_acc_to_grid = [0.0]

        for i in range(1,len(time)):
            e_grid = P_to_grid[i-1] * (time[i]-time[i-1]) * 60 # power produced in the period, MWs
            e_grid = e_grid/3600.0 # convert to MWh

            e_acc_grid = e_acc_to_grid[i-1] + e_grid
            e_acc_to_grid.append(e_acc_grid)

        return e_acc_to_grid

    # calculate total energy send to pem system
    def cal_e_acc_h2sys(self,P_to_h2sys,time):
        e_acc_to_h2sys = [0.0]
        e_acc_from_h2sys = [0.0]
        e_acc_net_h2sys = [0.0]

        for i in range(1,len(time)):
            e_h2 = P_to_h2sys[i-1] * (time[i]-time[i-1]) * 60  # please note the unit of time is min here
            e_h2 = e_h2/3600.0    # convert MWmin to MWh
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



