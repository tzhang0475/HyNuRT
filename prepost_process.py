#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# File              : prepost_process.py
# Author            : tzhang
# Date              : 25.11.2019
# Last Modified Date: 29.09.2020
# Last Modified By  : tzhang

from matplotlib import pyplot as plt
import numpy as np
import pandas as pd
import os
import sys
import datetime as dt

"""

a tool for read input data

"""
class dataReader:
    def __init__(self,inputfile):

        self.inputfile = inputfile
        self.log = 'run.log'

        # case title
        self.title = 'default'
        self.label = 'system'

        # grid variables 
        self.dataMode = 0
        self.inFile_Array = []
        self.multiplier = 1.0   # set default value

        # system config variables
        self.components = []
        self.num_chars = []
        self.unit_power = []
        self.n_units = []
        self.lifetimes = []
        self.con_time = []

        self.sys_lifteime = 0

        # simulation behavior control variable
        self.time_interval = 0.0
        self.auto_con = 1       # set default value
        self.len_time = 0

        # marco econamic data 
        self.dollar_year = 2018     # set defalt value

        self.r_discount = 0.0
        #self.r_inflation = 0.0

        self.price_e_base = 0.0
        self.price_ePEM_base = 0.0
        self.h2_base = 0.0

        # wind data 
        self.v_max = 0.0
        self.v_mean = 0.0
        self.n_range = 0

        # wind turbine tech data
        self.d_wing = 0.0
        self.J_turbine = 0.0
        self.h_hub = 0.0

        self.cut_in = 0.0
        self.cut_out = 0.0

        self.loc_type = 1   # set default value

        # wind turbine eco data
        self.w_cost_kW = 0.0
        self.w_om_cost_MWh = 0.0
        self.w_dcms_cost_MWh = 0.0


        # Nuclear Power Plant tech data
        self.LF_lim = 0.0

        # Nuclear Power Plant eco data
        self.FOAK = 1       # set default value
        
        self.nu_om_cost_MWh = 0.0
        self.nu_fuel_cost_MWh = 0.0
        self.nu_dcms_cost_MWh = 0.0

        self.eta_direct = 0.51  # set default value, oecd nea value, large uncentainty
        self.eta_indirect = 0.51    # set defualt value, oecd nea value, large uncentainty

        # Nuclear Power Plant learning factor parameters
        # default values are set
        self.x_learn = 0.15
        self.y_learn = 0.74
        self.z_learn = 0.82
        self.k_learn = 0.02

        self.r_learning = 0.0

        # PEM tech data
        self.theta_m = 0.0
        self.A_m = 0.0
        self.T_op = 0.0

        self.P_h2 = 0.0
        self.P_o2 = 0.0
        self.P_h2o = 0.0

        self.alpha_an = 0.5
        self.alpha_cat = 0.5

        self.i0_an = 0.0
        self.i0_cat = 0.0

        self.iter_max = 5000    # set default value

        self.Pmin_unit = 0.0

        self.m_store = 0.0      # set default value

        # PEM eco data
        self.capex_kW = 0.0
        self.cap_op_ratio = 0.0
    
    def _read_input_(self):
        inData = []
        with open(self.inputfile,'r') as f:
            for line in f:
                line = line.partition('#')[0]
                line = line.rstrip()

                if line.rstrip():
                    inData.append(line)
        f.close()

        return inData


    def _log_init_(self,inData):
        
        with open(self.log,'w+') as f:
            f.write(' *** ')
            f.write(str(dt.datetime.now()))
            f.write(' *** ')
            f.write('\n')

            f.write('\n')
            f.write(' ********* CLEAN INPUT FILE *********')
            f.write('\n')
            for line in inData:
                f.write(line)
                f.write('\n')
            f.write(' ********* CLEAN INPUT FILE *********')
            f.write('\n')

            f.write('\n')
            f.write(' ********* WARNING WHILE READ INPUT *********')
            f.write('\n')

        f.close()

    def _get_info_(self,inData):
        f = open(self.log,'a')

        if any('title' in line for line in inData):
            for line in inData:
                if 'title' in line:
                    title = str(line.split('=')[-1].lstrip().rstrip())
                    self.title = title
        else:
            f.write ('MESSAGE: Model title set as "default"!\n')
            f.write('\n')
            print ('MESSAGE: Model title set as "default"!\n')

        if any('label' in line for line in inData):
            for line in inData:
                if 'label' in line:
                    label = str(line.split('=')[-1].lstrip().rstrip())
                    self.label = label
        else:
            f.write ('MESSAGE: Model label set as "system"!\n')
            f.write('\n')
            print ('MESSAGE: Model label set as "system"!\n')

        f.close()


    def _grid_data_(self,inData):

        f = open(self.log,'a')

        if any('dataMode' in line for line in inData):
            for line in inData:
                if 'dataMode' in line:
                    dataMode = int(line.split('=')[-1].lstrip().rstrip())
                    self.dataMode = dataMode
        else:
            f.write ('ERROR: Please define the grid dataMode!\n')
            f.write('\n')
            print ('ERROR: Please define the grid dataMode!\n')
            sys.exit()
        
        if dataMode == 0:
            if any('inFile' in line for line in inData):
                inFile_Array = []
                for line in inData:
                    if 'inFile' in line:
                        dataRead = line.split('=')[-1]

                        for data in dataRead.split(','):
                            inFile_Array.append(str(data.lstrip().rstrip()))

                        self.inFile_Array = inFile_Array
            else:
                f.write ('ERROR: Please define inFile!\n')
                f.write('\n')
                print ('ERROR: Please define inFile!\n')
                sys.exit()

            if any('multiplier' in line for line in inData):
                for line in inData:
                    if 'multiplier' in line:
                        multiplier = float(line.split('=')[-1].lstrip().rstrip())
                        self.multiplier = multiplier
            else:
                f.write ('ERROR: Please define multiplier!\n')
                f.write('\n')
                print ('ERROR: Please define multiplier!\n')
                sys.exit()

        f.close()

    def _system_data_(self,inData):

        f = open(self.log,'a')

        if any('components' in line for line in inData):
            for line in inData:
                if 'components' in line:
                    components = []
                    dataRead = line.split('=')[-1]
                    for data in dataRead.split(','):
                        components.append(data.lstrip().rstrip())

                    self.components = components
        else:
            f.write ('ERROR: Please define components!\n')
            f.write('\n')
            print ('ERROR: Please define components!\n')
            sys.exit()

        if any('num_chars' in line for line in inData):
            for line in inData:
                if 'num_chars' in line:
                    num_chars = []
                    dataRead = line.split('=')[-1]
                    for data in dataRead.split(','):
                        num_chars.append(str(data.lstrip().rstrip()))

                    self.num_chars = num_chars
        else:
            f.write ('ERROR: Please define num_chars!\n')
            f.write('\n')
            print ('ERROR: Please define num_chars!\n')
            sys.exit()

        if any('unit_power' in line for line in inData):
            for line in inData:
                if 'unit_power' in line:
                    unit_power = []
                    dataRead = line.split('=')[-1]
                    for data in dataRead.split(','):
                        unit_power.append(float(data.lstrip().rstrip()))

                    self.unit_power = unit_power
        else:
            f.write ('ERROR: Please define unit_power\n')
            f.write('\n')
            print ('ERROR: Please define unit_power\n')
            sys.exit()

        if any('n_units' in line for line in inData):
            for line in inData:
                if 'n_units' in line:
                    n_units = []
                    dataRead = line.split('=')[-1]
                    for data in dataRead.split(','):
                        n_units.append(int(data.lstrip().rstrip()))

                    self.n_units = n_units
        else:
            f.write ('ERROR: Please define n_unitsi\n')
            f.write('\n')
            print ('ERROR: Please define n_units\n')
            sys.exit()

        if any('lifetimes' in line for line in inData):
            for line in inData:
                if 'lifetimes' in line:
                    lifetimes = []
                    dataRead = line.split('=')[-1]
                    for data in dataRead.split(','):
                        lifetimes.append(int(data.lstrip().rstrip()))

                    self.lifetimes = lifetimes
        else:
            print ('ERROR: Please define lifetimes\n')
            f.write ('ERROR: Please define lifetimes\n')
            f.write('\n')
            sys.exit()

        if any('con_time' in line for line in inData):
            for line in inData:
                if 'con_time' in line:
                    con_time = []
                    dataRead = line.split('=')[-1]
                    for data in dataRead.split(','):
                        con_time.append(int(data.lstrip().rstrip()))

                    self.con_time = con_time
        else:
            f.write ('ERROR: Please define con_time!\n')
            f.write('\n')
            print ('ERROR: Please define con_time!\n')
            sys.exit()

        if any('sys_lifetime' in line for line in inData):
            for line in inData:
                if 'sys_lifetime' in line:
                    sys_lifetime = int(line.split('=')[-1])
                    self.sys_lifetime = sys_lifetime
        else:
            f.write ('ERROR: Please define sys_lifetime!\n')
            f.write('\n')
            print ('ERROR: Please define sys_lifetime!\n')
            sys.exit()

        f.close()

    def _system_control_(self,inData):
        
        f = open(self.log,'a')

        if any('time_interval' in line for line in inData):
            for line in inData:
                if 'time_interval' in line:
                    time_interval = float(line.split('=')[-1].lstrip().rstrip())
                    self.time_interval = time_interval
        else:
            f.write ('MESSAGE: time_interval not defined!\n')
            f.write('\n')
            print ('MESSAGE: time_interval not defined!\n')


        if any('auto_con' in line for line in inData):
            for line in inData:
                if 'auto_con' in line:
                    auto_con = int(line.split('=')[-1].lstrip().rstrip())
                    self.auto_con = auto_con
        else:
            f.write ('WARNING: auto_con not defined!\n')
            f.write ('MESSAGE: auto construction sequence applied!\n')
            f.write('\n')
            print ('WARNING: auto_con not defined!\n')
            print ('MESSAGE: auto construction sequence applied!\n')

        if any('len_time' in line for line in inData):
            for line in inData:
                if 'len_time' in line:
                    len_time = int(line.split('=')[-1].lstrip().rstrip())
                    self.len_time = len_time
        else:
            f.write ('WARNING: auto_con not defined!\n')
            f.write ('MESSAGE: auto construction sequence applied!\n')
            f.write('\n')
            print ('WARNING: auto_con not defined!\n')
            print ('MESSAGE: auto construction sequence applied!\n')

        f.close()

    def _eco_base_(self,inData):

        f = open(self.log,'a')

        if any('dollar_year' in line for line in inData):
            for line in inData:
                if 'dollar_year' in line:
                    dollar_year = int(line.split('=')[-1].lstrip().rstrip())
                    self.dollar_year = dollar_year
        else:
            f.write ('WARNING: dollar_year not defined!\n')
            f.write ('MESSAGE: use dollar value of year 2018!\n')
            f.write('\n')
            print ('WARNING: dollar_year not defined!\n')
            print ('MESSAGE: use dollar value of year 2018!\n')

        if any('r_discount' in line for line in inData):
            for line in inData:
                if 'r_discount' in line:
                    r_discount = float(line.split('=')[-1].lstrip().rstrip())
                    self.r_discount = r_discount
        else:
            f.write ('WARNING: r_discount not defined!\n')
            f.write ('MESSAGE: zero discount rate is applied!\n')
            f.write('\n')
            print ('WARNING: r_discount not defined!\n')
            print ('MESSAGE: zero discount rate is applied!\n')

#        if any('r_inflation' in line for line in inData):
#            for line in inData:
#                if 'r_inflation' in line:
#                    r_inflation = float(line.split('=')[-1].lstrip().rstrip())
#                    self.r_inflation = r_inflation
#        else:
#            f.write ('WARNING: r_inflation not defined!\n')
#            f.write ('MESSAGE: zero inflation rate is applied!\n')
#            f.write('\n')
#            print ('WARNING: r_inflation not defined!\n')
#            print ('MESSAGE: zero inflation rate is applied!\n')

        if any('price_e_base' in line for line in inData):
            for line in inData:
                if 'price_e_base' in line:
                    price_e_base = float(line.split('=')[-1].lstrip().rstrip())
                    self.price_e_base = price_e_base
        else:
            f.write ('WARNING: price_e_base not defined!\n')
            f.write('\n')
            print ('WARNING: price_e_base not defined!\n')

        if any('price_ePEM_base' in line for line in inData):
            for line in inData:
                if 'price_ePEM_base' in line:
                    price_ePEM_base = float(line.split('=')[-1].lstrip().rstrip())
                    self.price_ePEM_base = price_ePEM_base
        else:
            f.write ('WARNING: price_ePEM_base not defined!\n')
            f.write('\n')
            print ('WARNING: price_ePEM_base not defined!\n')

        if any('price_h2_base' in line for line in inData):
            for line in inData:
                if 'price_h2_base' in line:
                    price_h2_base = float(line.split('=')[-1].lstrip().rstrip())
                    self.price_h2_base = price_h2_base
        else:
            f.write ('WARNING: price_h2_base not defined!\n')
            f.write('\n')
            print ('WARNING: price_h2_base not defined!\n')

        f.close()
    
    def _wind_data_(self,inData):

        f = open(self.log,'a')

        if any('v_max' in line for line in inData):
            for line in inData:
                if 'v_max' in line:
                    v_max = float(line.split('=')[-1].lstrip().rstrip())
                    self.v_max = v_max
        else:
            f.write ('WARNING: v_max not defined!\n')
            f.write('\n')
            print ('WARNING: v_max not defined!\n')

        if any('v_mean' in line for line in inData):
            for line in inData:
                if 'v_mean' in line:
                    v_mean = float(line.split('=')[-1].lstrip().rstrip())
                    self.v_mean = v_mean
        else:
            f.write ('WARNING: v_mean not defined!\n')
            f.write('\n')
            print ('WARNING: v_mean not defined!\n')

        if any('n_range' in line for line in inData):
            for line in inData:
                if 'n_range' in line:
                    n_range = int(line.split('=')[-1].lstrip().rstrip())
                    self.n_range = n_range
        else:
            f.write ('WARNING: n_range not defined!\n')
            f.write('\n')
            print ('WARNING: n_range not defined!\n')

        f.close()

    def _wind_turbine_data_(self,inData):

        f = open(self.log,'a')

        if any('d_wing' in line for line in inData):
            for line in inData:
                if 'd_wing' in line:
                    d_wing = float(line.split('=')[-1].lstrip().rstrip())
                    self.d_wing = d_wing
        else:
            f.write ('WARNING: d_wing not defined!\n')
            f.write('\n')
            print ('WARNING: d_wing not defined!\n')

        if any('J_turbine' in line for line in inData):
            for line in inData:
                if 'J_turbine' in line:
                    J_turbine = float(line.split('=')[-1].lstrip().rstrip())
                    self.J_turbine = J_turbine
        else:
            f.write ('WARNING: J_turbine not defined!\n')
            f.write('\n')
            print ('WARNING: J_turbine not defined!\n')

        if any('h_hub' in line for line in inData):
            for line in inData:
                if 'h_hub' in line:
                    h_hub = float(line.split('=')[-1].lstrip().rstrip())
                    self.h_hub = h_hub
        else:
            f.write ('WARNING: h_hub not defined!\n')
            f.write('\n')
            print ('WARNING: h_hub not defined!\n')

        if any('cut_in' in line for line in inData):
            for line in inData:
                if 'cut_in' in line:
                    cut_in = float(line.split('=')[-1].lstrip().rstrip())
                    self.cut_in = cut_in
        else:
            f.write ('WARNING: cut_in not defined!\n')
            f.write('\n')
            print ('WARNING: cut_in not defined!\n')

        if any('cut_out' in line for line in inData):
            for line in inData:
                if 'cut_out' in line:
                    cut_out = float(line.split('=')[-1].lstrip().rstrip())
                    self.cut_out = cut_out
        else:
            f.write ('WARNING: cut_out not defined!\n')
            f.write('\n')
            print ('WARNING: cut_out not defined!\n')

        f.close()

    def _wind_eco_data_(self,inData):
        f = open(self.log,'a')

        if any('loc_type' in line for line in inData):
            for line in inData:
                if 'loc_type' in line:
                    loc_type = int(line.split('=')[-1].lstrip().rstrip())
                    self.loc_type = loc_type
        else:
            f.write ('WARNING: loc_type not defined!\n')
            f.write ('MESSAGE: use default type land wind farm!\n')
            f.write('\n')
            print ('WARNING: cut_out not defined!\n')
            print ('MESSAGE: use default type land wind farm!\n')

        if any('w_cost_kW' in line for line in inData):
            for line in inData:
                if 'w_cost_kW' in line:
                    w_cost_kW = float(line.split('=')[-1].lstrip().rstrip())
                    self.w_cost_kW = w_cost_kW
        else:
            f.write ('WARNING: w_cost_kW not defined!\n')
            f.write('\n')
            print ('WARNING: w_cost_kW not defined!\n')

        if any('w_om_cost_MWh' in line for line in inData):
            for line in inData:
                if 'w_om_cost_MWh' in line:
                    w_om_cost_MWh = float(line.split('=')[-1].lstrip().rstrip())
                    self.w_om_cost_MWh = w_om_cost_MWh
        else:
            f.write ('WARNING: w_om_cost_MWh not defined!\n')
            f.write('\n')
            print ('WARNING: w_om_cost_MWh not defined!\n')

        if any('w_dcms_cost_MWh' in line for line in inData):
            for line in inData:
                if 'w_dcms_cost_MWh' in line:
                    w_dcms_cost_MWh = float(line.split('=')[-1].lstrip().rstrip())
                    self.w_dcms_cost_MWh = w_dcms_cost_MWh
        else:
            f.write ('WARNING: w_dcms_cost_MWh not defined!\n')
            f.write('\n')
            print ('WARNING: w_dcms_cost_MWh not defined!\n')

        f.close()

    def _npp_tech_data_(self,inData):

        f = open(self.log,'a')

        if any('LF_lim' in line for line in inData):
            for line in inData:
                if 'LF_lim' in line:
                    LF_lim = float(line.split('=')[-1].lstrip().rstrip())
                    self.LF_lim = LF_lim
        else:
            f.write ('WARNING: LF_lim not defined!\n')
            f.write('\n')
            print ('WARNING: LF_lim not defined!\n')

    def _npp_eco_data_(self,inData):

        f = open(self.log,'a')

        if any('nu_om_cost_MWh' in line for line in inData):
            for line in inData:
                if 'nu_om_cost_MWh' in line:
                    nu_om_cost_MWh = float(line.split('=')[-1].lstrip().rstrip())
                    self.nu_om_cost_MWh = nu_om_cost_MWh
        else:
            f.write ('WARNING: nu_om_cost_MWh not defined!\n')
            f.write('\n')
            print ('WARNING: nu_om_cost_MWh not defined!\n')

        if any('nu_fuel_cost_MWh' in line for line in inData):
            for line in inData:
                if 'nu_fuel_cost_MWh' in line:
                    nu_fuel_cost_MWh = float(line.split('=')[-1].lstrip().rstrip())
                    self.nu_fuel_cost_MWh = nu_fuel_cost_MWh
        else:
            f.write ('WARNING: nu_fuel_cost_MWh not defined!\n')
            f.write('\n')
            print ('WARNING: nu_fuel_cost_MWh not defined!\n')

        if any('nu_dcms_cost_MWh' in line for line in inData):
            for line in inData:
                if 'nu_dcms_cost_MWh' in line:
                    nu_dcms_cost_MWh = float(line.split('=')[-1].lstrip().rstrip())
                    self.nu_dcms_cost_MWh = nu_dcms_cost_MWh
        else:
            f.write ('WARNING: nu_dcms_cost_MWh not defined!\n')
            f.write('\n')
            print ('WARNING: nu_dcms_cost_MWh not defined!\n')

        f.close()

    def _npp_eco_data_para_(self,inData):

        f = open(self.log,'a')

        if any('FOAK' in line for line in inData):
            for line in inData:
                if 'FOAK' in line:
                    FOAK = int(line.split('=')[-1].lstrip().rstrip())
                    self.FOAK = FOAK
        else:
            f.write ('WARNING: FOAK not defined!\n')
            f.write ('MESSAGE: default set npp as FOAK!\n')
            f.write('\n')
            print ('WARNING: FOAK not defined!\n')
            print ('MESSAGE: default set npp as FOAK!\n')

        if any('eta_direct' in line for line in inData):
            for line in inData:
                if 'eta_direct' in line:
                    eta_direct = float(line.split('=')[-1].lstrip().rstrip())
                    self.eta_direct = eta_direct
        else:
            f.write ('WARNING: eta_direct not defined!\n')
            f.write ('MESSAGE: default set eta_direct = 0.51!\n')
            f.write('\n')
            print ('WARNING: eta_direct not defined!\n')
            print ('MESSAGE: default set eta_direct = 0.51!\n')

        if any('eta_indirect' in line for line in inData):
            for line in inData:
                if 'eta_indirect' in line:
                    eta_direct = float(line.split('=')[-1].lstrip().rstrip())
                    self.eta_direct = eta_direct
        else:
            f.write ('WARNING: eta_indirect not defined!\n')
            f.write ('MESSAGE: default set eta_indirect = 0.51!\n')
            f.write('\n')
            print ('WARNING: eta_indirect not defined!\n')
            print ('MESSAGE: default set eta_indirect = 0.51!\n')

        if any('eta_indirect' in line for line in inData):
            for line in inData:
                if 'eta_indirect' in line:
                    eta_direct = float(line.split('=')[-1].lstrip().rstrip())
                    self.eta_direct = eta_direct
        else:
            f.write ('WARNING: eta_indirect not defined!\n')
            f.write ('MESSAGE: default set eta_indirect = 0.51!\n')
            f.write('\n')
            print ('WARNING: eta_indirect not defined!\n')
            print ('MESSAGE: default set eta_indirect = 0.51!\n')

        if any('x_learn' in line for line in inData):
            for line in inData:
                if 'x_learn' in line:
                    x_learn = float(line.split('=')[-1].lstrip().rstrip())
                    self.x_learn = x_learn
        else:
            f.write ('WARNING: x_learn not defined!\n')
            f.write ('MESSAGE: default set x_learn = 0.15!\n')
            f.write('\n')
            print ('WARNING: x_learn not defined!\n')
            print ('MESSAGE: default set x_learn = 0.15!\n')

        if any('y_learn' in line for line in inData):
            for line in inData:
                if 'y_learn' in line:
                    y_learn = float(line.split('=')[-1].lstrip().rstrip())
                    self.y_learn = y_learn
        else:
            f.write ('WARNING: y_learn not defined!\n')
            f.write ('MESSAGE: default set y_learn = 0.74!\n')
            f.write('\n')
            print ('WARNING: y_learn not defined!\n')
            print ('MESSAGE: default set y_learn = 0.74!\n')

        if any('z_learn' in line for line in inData):
            for line in inData:
                if 'z_learn' in line:
                    z_learn = float(line.split('=')[-1].lstrip().rstrip())
                    self.z_learn = z_learn
        else:
            f.write ('WARNING: z_learn not defined!\n')
            f.write ('MESSAGE: default set z_learn = 0.82!\n')
            f.write('\n')
            print ('WARNING: z_learn not defined!\n')
            print ('MESSAGE: default set z_learn = 0.82!\n')

        if any('k_learn' in line for line in inData):
            for line in inData:
                if 'k_learn' in line:
                    k_learn = float(line.split('=')[-1].lstrip().rstrip())
                    self.k_learn = k_learn
        else:
            f.write ('WARNING: k_learn not defined!\n')
            f.write ('MESSAGE: default set k_learn = 0.15!\n')
            f.write('\n')
            print ('WARNING: k_learn not defined!\n')
            print ('MESSAGE: default set k_learn = 0.15!\n')

        if any('r_learning' in line for line in inData):
            for line in inData:
                if 'r_learning' in line:
                    r_learning = float(line.split('=')[-1].lstrip().rstrip())
                    self.r_learning = r_learning
        else:
            f.write ('WARNING: r_learn not defined!\n')
            f.write('\n')
            print ('WARNING: r_learn not defined!\n')


        f.close()
    
    def _PEM_data_(self,inData):
        
        f = open(self.log,'a')

        if any('theta_m' in line for line in inData):
            for line in inData:
                if 'theta_m' in line:
                    theta_m = float(line.split('=')[-1].lstrip().rstrip())
                    self.theta_m = theta_m
        else:
            f.write ('WARNING: theta_m not defined!\n')
            f.write('\n')
            print ('WARNING: theta_m not defined!\n')

        if any('A_m' in line for line in inData):
            for line in inData:
                if 'A_m' in line:
                    A_m = float(line.split('=')[-1].lstrip().rstrip())
                    self.A_m = A_m
        else:
            f.write ('WARNING: A_m not defined!\n')
            f.write('\n')
            print ('WARNING: A_m not defined!\n')

        if any('T_op' in line for line in inData):
            for line in inData:
                if 'T_op' in line:
                    T_op = float(line.split('=')[-1].lstrip().rstrip())
                    self.T_op = T_op
        else:
            f.write ('WARNING: T_op not defined!\n')
            f.write('\n')
            print ('WARNING: T_op not defined!\n')

        if any('P_h2' in line for line in inData):
            for line in inData:
                if 'P_h2' in line:
                    P_h2 = float(line.split('=')[-1].lstrip().rstrip())
                    self.P_h2 = P_h2
        else:
            f.write ('WARNING: P_h2 not defined!\n')
            f.write('\n')
            print ('WARNING: P_h2 not defined!\n')


        if any('P_o2' in line for line in inData):
            for line in inData:
                if 'P_o2' in line:
                    P_o2 = float(line.split('=')[-1].lstrip().rstrip())
                    self.P_o2 = P_o2
        else:
            f.write ('WARNING: P_o2 not defined!\n')
            f.write('\n')
            print ('WARNING: P_o2 not defined!\n')

        if any('P_h2o' in line for line in inData):
            for line in inData:
                if 'P_h2o' in line:
                    P_h2o = float(line.split('=')[-1].lstrip().rstrip())
                    self.P_h2o = P_h2o
        else:
            f.write ('WARNING: P_h2o not defined!\n')
            f.write('\n')
            print ('WARNING: P_h2o not defined!\n')


        if any('alpha_an' in line for line in inData):
            for line in inData:
                if 'alpha_an' in line:
                    alpha_an = float(line.split('=')[-1].lstrip().rstrip())
                    self.alpha_an = alpha_an
        else:
            f.write ('WARNING: alpha_an not defined!\n')
            f.write('\n')
            print ('WARNING: alpha_an not defined!\n')


        if any('alpha_cat' in line for line in inData):
            for line in inData:
                if 'alpha_cat' in line:
                    alpha_cat = float(line.split('=')[-1].lstrip().rstrip())
                    self.alpha_cat = alpha_cat
        else:
            f.write ('WARNING: alpha_cat not defined!\n')
            f.write('\n')
            print ('WARNING: alpha_cat not defined!\n')

        if any('i0_an' in line for line in inData):
            for line in inData:
                if 'i0_an' in line:
                    i0_an = float(line.split('=')[-1].lstrip().rstrip())
                    self.i0_an = i0_an
        else:
            f.write ('WARNING: i0_an not defined!\n')
            f.write('\n')
            print ('WARNING: i0_an not defined!\n')


        if any('i0_cat' in line for line in inData):
            for line in inData:
                if 'i0_cat' in line:
                    i0_cat = float(line.split('=')[-1].lstrip().rstrip())
                    self.i0_cat = i0_cat
        else:
            f.write ('WARNING: i0_cat not defined!\n')
            f.write('\n')
            print ('WARNING: i0_cat not defined!\n')

        if any('iter_max' in line for line in inData):
            for line in inData:
                if 'iter_max' in line:
                    iter_max = int(line.split('=')[-1].lstrip().rstrip())
                    self.iter_max = iter_max
        else:
            f.write ('WARNING: iter_max not defined!\n')
            f.write ('MESSAGE: default set iter_max = 5000!\n')
            f.write('\n')
            print ('WARNING: iter_max not defined!\n')
            print ('MESSAGE: default set iter_max = 5000!\n')
        f.close()

    def _PEM_eco_data_(self,inData):
        f = open(self.log,'a')

        if any('Pmin_unit' in line for line in inData):
            for line in inData:
                if 'Pmin_unit' in line:
                    Pmin_unit = float(line.split('=')[-1].lstrip().rstrip())
                    self.Pmin_unit = Pmin_unit
        else:
            f.write ('WARNING: Pmin_unit not defined!\n')
            for data in self.num_chars:
                if data == '10':
                    idx = self.num_chars.index('10')
            P_pem = self.unit_power[idx]

            Pmin_unit = P_pem * 0.1
            f.write ('MESSAGE: default set P MIN unit as 10% of MAX!\n')
            f.write ('MESSAGE: Pmin_unit = '+str(Pmin_unit)+'\n')
            f.write('\n')
            print ('MESSAGE: default set P MIN unit as 10% of MAX!\n')
            print ('MESSAGE: Pmin_unit = ',str(Pmin_unit),'\n')

        if any('m_store' in line for line in inData):
            for line in inData:
                if 'm_store' in line:
                    m_store = float(line.split('=')[-1].lstrip().rstrip())
                    self.m_store = m_store
        else:
            f.write ('WARNING: m_store not defined!\n')
            f.write ('MESSAGE: default set no initial hydrogen!\n')
            f.write('\n')
            print ('WARNING: m_store not defined!\n')
            print ('MESSAGE: default set no initial hydrogen!\n')

        if any('capex_kW' in line for line in inData):
            for line in inData:
                if 'capex_kW' in line:
                    capex_kW = float(line.split('=')[-1].lstrip().rstrip())
                    self.capex_kW = capex_kW
        else:
            f.write ('WARNING: capex_kW not defined!\n')
            f.write('\n')
            print ('WARNING: capex_kW not defined!\n')

        if any('cap_op_ratio' in line for line in inData):
            for line in inData:
                if 'cap_op_ratio' in line:
                    cap_op_ratio = float(line.split('=')[-1].lstrip().rstrip())
                    self.capex = cap_op_ratio
        else:
            f.write ('WARNING: cap_op_ratio not defined!\n')
            f.write('\n')
            print ('WARNING: cap_op_ratio not defined!\n')

        f.close()

    def read(self):
        inData = self._read_input_()
        self._log_init_(inData)
        self._get_info_(inData)        
        self._grid_data_(inData)        
        self._system_data_(inData)  
        self._system_control_(inData)  
        self._eco_base_(inData)

        if '00' in self.num_chars:
            self._npp_tech_data_(inData)
            self._npp_eco_data_(inData)
            self._npp_eco_data_para_(inData)


        if '01' in self.num_chars:
            self._wind_data_(inData)
            self._wind_turbine_data_(inData)
            self._wind_eco_data_(inData)

        if '10' in self.num_chars:
            self._PEM_data_(inData)
            self._PEM_eco_data_(inData)

"""

a tool for control model behavior

"""
class mod_control:
    # a function to modify the input file
    def mod_input(inputfile,keyword,value_new):

        inbak = inputfile+'.bak'

        inData = []
        with open(inputfile,'r') as f:
            data_ori = f.readlines()
        f.close()

        for line in data_ori:
            line = line.partition('#')[0]
            line = line.rstrip()

            if line.rstrip():
                inData.append(line)

        if not os.path.isfile(inbak):
            with open(inbak,'w') as f:
                for line in data_ori:
                    f.write(line)
        if any(keyword in line for line in inData):
            f = open(inputfile,'w+')
            for line in inData:
                if keyword in line:
                    f.write(keyword)
                    f.write(' = ')
                    if isinstance(value_new,list):
                        value_str = [str(value) for value in value_new]
                        value_array = ', '.join(value_str)
                        f.write(value_array)
                    else:
                        f.write(str(value_new))
                    f.write('\n')
                else:
                    f.write(line)
                    f.write('\n')
            f.close()
        else:
            print ('Error: Keyword not defined!\n')

    def mod_run(modelname,inputfile):

        cmd = 'python '+str(modelname)+' '+str(inputfile) #+ ' > run_data.log'

        print ('\n')
        print ('*** RUN THE MODEL ***')

        os.system(cmd)

    def mod_cmd(modelname,inputfile):

        cmd = 'python '+str(modelname)+' '+str(inputfile) + ' > run_data.log'

        return cmd 

"""

a tool for post-process

"""
class post_process:

    # plot the grid demand and the system generatrion
    def plt_grid_balance(label,time,P_demand,P_to_grid):
        plt.figure(figsize = (22,8))
        plt.plot(time,P_demand, linewidth = 4, color = 'g',label = 'grid demand')
        plt.plot(time,P_to_grid,linewidth = 4, color = 'r', label = 'system deliver')
        plt.xticks(fontsize = '20')
        plt.yticks(fontsize = '20')
        plt.legend()
        plt.xlabel('Time (min)',fontsize = '20')
        plt.xlim(left = 0.0)
        plt.ylabel('Power (MW)', fontsize = '20')
        plt.legend(prop = {'size':20})
        plt.grid(linestyle='--',linewidth = '1')

        pltName = 'grid_blance_'+label+'.png'
        plt.savefig(pltName,dpi = 100)

        plt.clf()
        plt.close(pltName)

    # plot the un-satisfied demand
    def plt_grid_unfit(infile_labels,time_dict,P_demand_dict,P_to_grid_dict):

        for key in P_demand_dict.keys():
            n_cases = len(P_demand_dict[key])
            break
        key_list = list(P_demand_dict.keys())
        
        for n in range(n_cases):
            case_label = 'case_'+str(n+1)

            plt.figure(figsize = (24,6))
            for key in P_demand_dict.keys():
                idxkey = key_list.index(key)
                
                # convert time to days
                days = []
                for i in range(len(time_dict[key][n])):
                    day = time_dict[key][n][i]/1440.0
                    days.append(day)

                # calculate unfiteed power
                unfitted_power = []
                for j in range(len(time_dict[key][n])):
                    dP = P_demand_dict[key][n][j] - P_to_grid_dict[key][n][j]
                    if dP < 1e-10:
                        dP = 0.0
                    unfitted_power.append(dP)
    
                plt.plot(days,unfitted_power, linewidth = 4,color = np.random.rand(3,),label = str(infile_labels[idxkey]))
   
            plt.xticks(fontsize = '20')
            plt.yticks(fontsize = '20')
            plt.rc('font',size=16)
            plt.legend()
            plt.legend(prop = {'size':20})
            plt.xlabel('Time (min)',fontsize = '20')
            plt.xlim(left = 0.0)
            plt.ylabel('Power (MW)', fontsize = '20')
            plt.grid(linestyle='--',linewidth = '1')
    
            pltName = 'unfitted_'+case_label+'.png'
            plt.savefig(pltName,dpi = 100)
    
            plt.clf()
            plt.close(pltName)

    # plot h2 storage of different months 
    def plt_h2_storage(infile_labels,time_dict,h2_dict):

        for key in h2_dict.keys():
            n_cases = len(h2_dict[key])
            break
        key_list = list(h2_dict.keys())
        
        for n in range(n_cases):
            case_label = 'case_'+str(n+1)

            plt.figure(figsize = (14,6))
            for key in h2_dict.keys():
                idxkey = key_list.index(key)

                # convert time to days
                days = []
                for i in range(len(time_dict[key][n])):
                    day = time_dict[key][n][i]/1440.0
                    days.append(day)

                plt.plot(time_dict[key][n],h2_dict[key][n][0:len(time_dict[key][n])], linewidth = 4,color = np.random.rand(3,),label = str(infile_labels[idxkey]))
   
            plt.xticks(fontsize = '20')
            plt.yticks(fontsize = '20')
            plt.ticklabel_format(axis='y',style='sci',scilimits=(3,3))
            plt.rc('font',size=16)
            plt.legend()
            plt.legend(prop = {'size':20})
            plt.xlabel('Time (min)',fontsize = '20')
            plt.xlim(left = 0.0)
            plt.ylabel('Hydrogen Storage (kg)', fontsize = '20')
            plt.grid(linestyle='--',linewidth = '1')
    
            pltName = 'h2_store_'+case_label+'.png'
            plt.savefig(pltName,dpi = 100)
    
            plt.clf()
            plt.close(pltName)


    # plot the stored mass of hydrogen
    def plt_h2_stored(label,time,m_stored_data):
        plt.figure(figsize = (12,8))
        plt.plot(time,m_stored_data[0:-1], color = 'k')
        plt.xlabel('Time (min)',fontsize = '16')
        plt.xlim(left = 0.0)
        plt.ylabel('Hydrogen Storage (kg)', fontsize = '16')
        plt.grid(linestyle='--',linewidth = '1')

        pltName = 'hydrogen_storage'+'_'+label+'.png'
        plt.savefig(pltName,dpi = 100)
        plt.close(pltName)


    # plot the abandoned power 
    def plt_power_abandon(label,time,P_abandon):
        plt.figure(figsize = (12,8))
        plt.plot(time,P_abandon, color = 'c')
        plt.xlabel('Time (min)',fontsize = '16')
        plt.xlim(left = 0.0)
        plt.ylabel('Power (MW)', fontsize = '16')
        plt.grid(linestyle='--',linewidth = '1')

        pltName = 'power_abondoned'+label+'.png'
        plt.savefig(pltName,dpi = 100)
        plt.close(pltName)

    # plot cash flow of a unit n years
    def plt_cashflow(n_year,cashflow,label):
        
        year = np.arange(0,n_year,1) 

        plt.figure(figsize = (14,8))
        plt.plot(year,cashflow, color = 'firebrick',linewidth = '4',marker = 'o', markersize = '5')
        plt.xticks(fontsize = '20')
        plt.yticks(fontsize = '20')
        plt.xlabel('year',fontsize = '20')
        plt.xlim(left = 0.0)
        plt.ylabel('Cash Flow ($ in Million)', fontsize = '20')
        plt.grid(linestyle='--',linewidth = '1')

        pltName = label+'_'+'cashflow.png'
        plt.savefig(pltName,dpi = 100)
        plt.close(pltName)

    # plot cash flow of a system with n components and cash flow of each unit in the system
    def plt_sys_cashflow(n_year,cashflow,cashdic):

        year = np.arange(0,n-year,1)
        
        plt.figure(figsize = (14,8))

        # plot overall system cash flow
        plt.plot(year,cashflow, color = 'firebrick',linewidth = '4',marker = 'o', markersize = '5', label = 'system')

        # plot cash flow of each component
        for key in cashdic.keys():
            plt.plot(year,cashflow[key],linewidth = '2', lable = key)

        plt.xlabel('year',fontsize = '16')
        plt.xlim(left = 0.0)
        plt.ylabel('Cash Flow ($ in Million)', fontsize = '16')
        plt.grid(linestyle='--',linewidth = '1')

    # plot the progress of GA optimization
    def plt_GA(best_score_progress):
        plt.plot (best_score_progress)
        plt.xlabel('Generation')
        plt.ylabel('Best score (% target)')
        pName = 'GA_opti.png'
        plt.savefig(pName,dpi = 100)
        plt.show()
        plt.close(pName)



    # cash flow data writer
    def writer_cashflow(cashflow,label):
        
        datafile = 'cashflow_'+label+'.txt'

        with open(datafile,"w+") as f:
            f.write('#year'+'    '+'cash flow'+'    ')
            f.write('\n')
            
            for i in range(len(cashflow)):
                f.write(str(i)+'    ')
                f.write(str(cashflow[i])+'      ')
                f.write('\n')
        f.close()

    # write system performance data to text file
    def data_performance(label,time,P_demand,P_coupled,P_to_grid,P_to_h2sys,P_abandon,M_stored_data):
        datafile = 'data_performance_'+label+'.txt'

        with open(datafile, 'w+') as f:
            f.write('time'+'    ')
            f.write('grid demand'+'      ')
            f.write('wind-nuclear generated'+'      ')
            f.write('power to grid'+'      ')
            f.write('power to h2 system'+'      ')
            f.write('abandoned power'+'      ')
            f.write('stored hydrogen'+'      ')
            f.write('\n')

            for i in range(len(time)):
                f.write(str('%.2f'%time[i])+'    ')
                f.write(str('%.2f'%P_demand[i])+'    ')
                f.write(str('%.2f'%P_coupled[i])+'    ')
                f.write(str('%.2f'%P_to_grid[i])+'    ')
                f.write(str('%.2f'%P_to_h2sys[i])+'    ')
                f.write(str('%.2f'%P_abandon[i])+'    ')
                f.write(str('%.3f'%M_stored_data[i])+'    ')
                f.write('\n')

        f.close()

    # write system performance data to excel file
    def excel_performance(label,time,P_demand,P_coupled,P_to_grid,P_to_h2sys,P_abandon,e_acc_to_grid,e_acc_to_h2sys,e_acc_from_h2sys,e_acc_net_h2sys,e_acc_abandon,m_stored_data):
        datafile = 'data_performance_'+label+'.xlsx'
        sheetname1 = 'power_'+label
        sheetname2 = 'energy_'+label

        # remove exists file 
        if os.path.isfile(datafile):
            os.remove(datafile)

        # write data to xlsx file
        df1 = pd.DataFrame({'time':time,\
                        'grid demand (MW)':P_demand,\
                        'wind-nuclear generated (MW)': P_coupled,\
                        'power to grid (MW)':P_to_grid,\
                        'power to h2 system (MW)':P_to_h2sys,\
                        'abandoned power (MW)':P_abandon})
        df2 = pd.DataFrame({'time':time,\
                        'accumulated energy to grid (MWh)':e_acc_to_grid,\
                        'accumulated energy to h2 system (MWh)':e_acc_to_h2sys,\
                        'accumulated energy from h2 system (MWh)': e_acc_from_h2sys,\
                        'accumulated net energy to h2 system (MWh)':e_acc_net_h2sys,\
                        'accumulated abondoned energy (MWh)':e_acc_abandon,\
                        'stored hydrogen (kg)':m_stored_data})

        writer = pd.ExcelWriter(datafile, engine='xlsxwriter')

        df1.to_excel(writer,sheet_name = sheetname1)
        df2.to_excel(writer,sheet_name = sheetname2)

        workbook = writer.book
        worksheet1 = writer.sheets[sheetname1]
        worksheet2 = writer.sheets[sheetname2]

        # set format of data
        form1 = workbook.add_format({'num_format':'0.0'})
        form2 = workbook.add_format({'num_format':'0.00'})
        form3 = workbook.add_format({'num_format':'0.000'})

        # add format
        worksheet1.set_column('B:B',15,form1)
        worksheet1.set_column('C:G',30,form2)

        worksheet2.set_column('B:B',15,form1)
        worksheet2.set_column('C:G',40,form2)
        worksheet2.set_column('H:H',30,form3)

        writer.save()

    # write lifetime performance data to excel file
    def excel_lifetime(lifetime_scale,e_to_grid,e_to_h2,e_ab,m_h2):
        datafile = 'system_lifetime_performance.xlsx'
        sheetname = 'performance'

        npp_switch = False
        wind_switch = False
        PV_switch = False
        PEM_switch = False

        # remove exists file 
        if os.path.isfile(datafile):
            os.remove(datafile)

        year = []
        capacity = []

        for data in lifetime_scale[0]:
            if data == '00':
                npp = []
                col_npp = lifetime_scale[0].index(data)
                npp_switch = True
            elif data == '01':
                wind = []
                col_wind = lifetime_scale[0].index(data)
                wind_switch = True
            elif data == '02':
                PV = []
                col_PV = lifetime_scale[0].index(data)
                PV_switch = True
            elif data == '10':
                PEM = []
                col_PEM = lifetime_scale[0].index(data)
                PEM_switch = True

        for data in lifetime_scale[1:]:
            year.append(data[0])
            if npp_switch:
                npp.append(data[col_npp])
            if wind_switch:
                wind.append(data[col_wind])
            if PV_switch:
                PV.append(data[col_PV])
            if PEM_switch:
                PEM.append(data[col_PEM])
            capacity.append(data[-2])

        df = pd.DataFrame({'year':year})

        if npp_switch:
            df['NPP units'] = npp
        if wind_switch:
            df['wind farm units'] = wind
        if PV_switch:
            df['photovoltage units'] = PV
        if PEM_switch:
            df['PEM units'] = PEM
        
        df['installed capacity'] = capacity

        df['energy to grid (MWh)'] = e_to_grid 
        df['energy to h2 system (MWh)'] = e_to_h2
        df['energy to abandoned (MWh)'] = e_ab 
        df['h2 produced (kg)'] = m_h2 



        writer = pd.ExcelWriter(datafile, engine='xlsxwriter')

        df.to_excel(writer,sheet_name = sheetname)

        workbook = writer.book
        worksheet = writer.sheets[sheetname]

        # set format of data
        form1 = workbook.add_format({'num_format':'0'})
        form2 = workbook.add_format({'num_format':'0.0'})
        form3 = workbook.add_format({'num_format':'0.000'})

        # add format
        worksheet.set_column('B:E',10,form1)
        worksheet.set_column('F:F',30,form2)
        
        worksheet.set_column('G:J',30,form3)

        writer.save()

    # write lifetime performance data to text file
    def data_lifetime(label,lifetime_scale,e_to_grid,e_to_h2,e_ab,m_h2):
        datafile = 'system_lifetime_performance'+'_'+label+'.txt'

        npp_switch = False
        wind_switch = False
        PV_switch = False
        PEM_switch = False

        # remove exists file 
        if os.path.isfile(datafile):
            os.remove(datafile)

        year = []
        capacity = []

        for data in lifetime_scale[0]:
            if data == '00':
                npp = []
                col_npp = lifetime_scale[0].index(data)
                npp_switch = True
            elif data == '01':
                wind = []
                col_wind = lifetime_scale[0].index(data)
                wind_switch = True
            elif data == '02':
                PV = []
                col_PV = lifetime_scale[0].index(data)
                PV_switch = True
            elif data == '10':
                PEM = []
                col_PEM = lifetime_scale[0].index(data)
                PEM_switch = True

        for data in lifetime_scale[1:]:
            year.append(data[0])
            if npp_switch:
                npp.append(data[col_npp])
            if wind_switch:
                wind.append(data[col_wind])
            if PV_switch:
                PV.append(data[col_PV])
            if PEM_switch:
                PEM.append(data[col_PEM])
            capacity.append(data[-2])

        with open(datafile,'w') as f:
            f.write('year'+'    ')

            if npp_switch:
                f.write('NPP units'+'   ')
            if wind_switch:
                f.write('wind turbine units'+'   ')
            if PV_switch:
                f.write('PV units'+'   ')
            if PEM_switch:
                f.write('PEM units'+'   ')
            f.write('Installed Capacity (MW)'+'   ')
            f.write('Energy to grid (MWh)'+'   ')
            f.write('Energy to h2 system (MWh)'+'   ')
            f.write('Energy abandoned (MWh)'+'   ')
            f.write('h2 produced (kg)'+'   ')
            f.write('\n')

            for i in range(len(year)):
                f.write(str(year[i])+'     ')
                if npp_switch:
                    f.write(str(npp[i])+'   ')
                if wind_switch:
                    f.write(str(wind[i])+'   ')
                if PV_switch:
                    f.write(str(PV[i])+'   ')
                if PEM_switch:
                    f.write(str(PEM[i])+'   ')
            
                f.write(str('%.1f'%capacity[i])+'   ')
                f.write(str('%.2f'%e_to_grid[i])+'   ')
                f.write(str('%.2f'%e_to_h2[i])+'   ')
                f.write(str('%.2f'%e_ab[i])+'   ')
                f.write(str('%.3f'%m_h2[i])+'   ')
                f.write('\n')



    # select data according to time interval, time_interval in unit of minute 
    def data_opti(time,time_interval,\
            P_demand,P_coupled,P_to_grid,P_to_h2sys,P_abandon,\
            e_acc_to_grid,e_acc_to_h2sys,e_acc_from_h2sys,e_acc_net_h2sys,e_acc_abandon,\
            m_stored_data):

        # select index of requested data
        idx_array = [0]
        for i in range(1,len(time)-1):
            if time[i]%time_interval == 0:
                idx_array.append(i)
            elif time[i-1]%time_interval > time[i]%time_interval and time[i]%time_interval < time[i+1]:
                idx_array.append(i)
        idx_array.append(len(time)-1)
        # new array for selected data
        time_slct = []
        P_demand_slct = []
        P_coupled_slct = []
        P_to_grid_slct = []
        P_to_h2sys_slct = []
        P_abandon_slct = []
        m_stored_data_slct = []

        e_acc_to_grid_slct = []
        e_acc_to_h2sys_slct = []
        e_acc_from_h2sys_slct = []
        e_acc_net_h2sys_slct = []
        e_acc_abandon_slct = []

        for idx in idx_array:
            time_slct.append(time[idx])

            P_demand_slct.append(P_demand[idx])
            P_coupled_slct.append(P_coupled[idx])
            P_to_grid_slct.append(P_to_grid[idx])
            P_to_h2sys_slct.append(P_to_h2sys[idx])
            P_abandon_slct.append(P_abandon[idx])
            m_stored_data_slct.append(m_stored_data[idx])

            e_acc_to_grid_slct.append(e_acc_to_grid[idx])
            e_acc_to_h2sys_slct.append(e_acc_to_h2sys[idx])
            e_acc_from_h2sys_slct.append(e_acc_from_h2sys[idx])
            e_acc_net_h2sys_slct.append(e_acc_net_h2sys[idx])
            e_acc_abandon_slct.append(e_acc_abandon[idx])

        return time_slct,\
                P_demand_slct,P_coupled_slct,P_to_grid_slct,P_to_h2sys_slct,P_abandon_slct,\
                e_acc_to_grid_slct,e_acc_to_h2sys_slct,e_acc_from_h2sys_slct,e_acc_net_h2sys_slct,e_acc_abandon_slct,\
                m_stored_data_slct




