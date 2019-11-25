#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# File              : NuReModel.py
# Author            : tzhang
# Date              : 20.11.2019
# Last Modified Date: 25.11.2019
# Last Modified By  : tzhang

"""

a model of coupled nuclear-renewable system for a mircogrid

Nuclear: nuclear power plant with n Small Modular Reactor (SMR) module, each has a maximum capacity of n MW
Renewable: wind farm with n wind turbine, each wind turbine has maximum capacity of 2 MW, and the total capacity of the wind farm is n MW
Hydrogen Production and Comsumption: a cluster consisted of n cells, each cell has a maximum capacity of 0.3 MW and a minimum capacity of 0.05 MW

Grid Demand: the demand data is the acutal grid data of UK in Jan, 2018. The data is scaled to 0.5% to simulate the grid demand of a microgrid

"""
import sys

# insert from different path
sys.path.insert(1, '../')

# import libraries of package
from grid import *
from H2Cell import *
from windData import *
from SMR import *
from wind_turbine import *
from material import *
from sys_control import *
from prepost_process import *

# input for electrical grid 
dataMode = 0
inFile = 'UK_gridwatch_year2018_Jan.csv'
multiplier = 0.005

# wind data
v_max = 28.0
v_mean = 11.0
n_range = 40

# wind turbine data
d_wing = 90 # in m,  wind turbine diameter
J_turbine = 1.3E7 # in kg.m^2, moment of initia of turbine
h_hub = 50 # in m, the height of the hub
P_lim = 2E6 # in W, power limit of a turbine

cut_in = 4.0
cut_out = 25.0

# wind farm data
w_n_unit = 40

# SMR module data
P_nominal = 50 # nominal power, in MW
LF_lim = 0.05

# number of units in the npp
n_n_unit = 3

# hydrogen cell data
theta_m = 0.13     # the thickness of membrane, in mm
A = 16             # the area of the membrane, in cm^2
T = 50             # in C,
P_h2 = 1e5         # 
P_o2 = 1e5
P_h2o = 2e5

alpha_an = 0.5
alpha_cat = 0.5

i0_cat = 1e-3  # in A/cm^2
i0_an = 1e-7   # in A/cm^2

iter_max = 5000 # maximum number of iterations

# hydrogen cluster and storage data
h2_n_unit = 500        # total 300 units of pem cells
Pmax_unit = 0.3     # maximum power of a cell
Pmin_unit = 0.05    # minimum power of a cell

m_store = 0          # initial storage, in kg
###############################################
# generate grid demand
###############################################
uk_grid = grid(dataMode,inFile,multiplier)
uk_grid.gen()
uk_grid.demand_plot()
time = uk_grid.aquire_time()
P_demand = uk_grid.aquire_demand()

time = time[0:288]
P_demand = P_demand[0:288]

#time = time[0:48]
#P_demand = P_demand[0:48]

uk_grid.user_demand_plot(time,P_demand)

###############################################
# generate wind data during simulation time
###############################################
wind = wind_Rayleigh(v_max,v_mean,n_range,time)
time,v_wind = wind.genData()  # NOTE:the unit of time is in min #
print (time)
#print (v_wind)
wind.plt_v_dis()
wind.plt_windData()

###############################################
# create modules in the system
###############################################
w_turbine = wind_Turbine(d_wing,J_turbine,h_hub,P_lim,cut_in,cut_out)  # wind turbine
w_farm = wind_farm(w_n_unit)   # wind farm

# nuclear
module = SMR_module(P_nominal,LF_lim)   # SMR module
npp = SMR_NPP(n_n_unit)                   # SMR NPP

# energy storage and hybrid usage
h2_sys = h2_system(theta_m,A,alpha_an,alpha_cat,i0_an,i0_cat,T,P_h2,P_o2,P_h2o,iter_max,\
                    h2_n_unit,Pmax_unit,Pmin_unit,\
                    m_store)

###############################################
# modelling a windturbine
###############################################
# air property
airData = air()
airData.constant()
d_air = airData.density
# cp curve
cp_curve = cp_IEC()
cp_curve.curve_A()
cp_curve.cp_plot()
cp_array = cp_curve.cp_array(v_wind)

wP_out = w_turbine.P_output(d_air, time, v_wind, cp_array)
#print (wP_out)

###############################################
# modelling a wind farm 
###############################################
P_windfarm = w_farm.pArray(wP_out)
print ('wind farm output ',P_windfarm)
w_farm.wPower_plot(time,P_windfarm)


###############################################
# modelling a SMR NPP 
###############################################
p_unit = module.m_power()
P_nuclear = npp.npp_power(p_unit)

print ('nuclear power ',P_nuclear)


####################################################################
# calculate the power produced from coupled nuclear-renewable system
####################################################################
P_windfarm = np.asarray(P_windfarm)
P_coupled = P_nuclear + P_windfarm
print ('electricity produced by coupled system ',P_coupled)
print ('grid demand ', P_demand)


###################################################
# calculate the grid and hydrogen system balancing
###################################################
# aquire minimum demand of hydrogen production 
Pmin_cluster = h2_sys.Pmin_system()
print ('minimun power for h2 cluster ',Pmin_cluster)

balance_control = balancing()
P_to_h2sys = balance_control.cal_to_h2sys(P_coupled,P_demand,Pmin_cluster)
print ('power to h2 system ', P_to_h2sys)

###############################################
# modelling hydrogen cells 
###############################################
P_h2_produced,P_h2_consumed,P_abandon = h2_sys.cal(P_to_h2sys,time)

print ('h2 produces power ', P_h2_produced)
print ('h2 consumed power ', P_h2_consumed)
m_tot = h2_sys.aquire_m()
print ('\n')
print ('total storage',m_tot, ' kg')

m_stored_data = h2_sys.aquire_m_records()
###################################################
# calculate the powet to the grid 
###################################################
P_to_grid = balance_control.cal_to_grid(P_coupled,P_h2_produced,P_h2_consumed)

print ('wind-nuclear generated ',P_coupled)
print ('power to h2 system ', P_to_h2sys)
print ('power to grid ', P_to_grid)
print ('grid demand ', P_demand)
print ('abandoned power ',P_abandon)
print ('stored hydrogen ', m_stored_data)


###################################################
# post processing of data 
###################################################
post_process.plt_grid_balance(time,P_demand,P_to_grid)
post_process.plt_h2_stored(time,m_stored_data)
post_process.plt_power_abandon(time,P_abandon)
sys.exit()
