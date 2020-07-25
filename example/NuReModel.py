#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# File              : NuReModel.py
# Author            : tzhang
# Date              : 20.11.2019
# Last Modified Date: 26.07.2020
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
from eco_analysis import *


###############################################
# configration of the hybrid system
###############################################
# input for electrical grid 
dataMode = 0
inFile = 'UK_gridwatch_year2018_Jan.csv'
multiplier = 0.005


###############################################
# wind data
v_max = 28.0
v_mean = 11.0
n_range = 40

# wind turbine data
d_wing = 90 # in m,  wind turbine diameter
J_turbine = 1.3E7 # in kg.m^2, moment of initia of turbine
h_hub = 50 # in m, the height of the hub
P_lim = 2  # in MW, power limit of a turbine

cut_in = 4.0
cut_out = 25.0

# wind farm data
w_n_unit = 40

w_lifetime = 30     # 30 years life time
loc_type = 1        # 1 for land wind farm, 0 for off-shore wind farm

# captical cost of a wind turbine per kW
cost_kW = 1590      # $ per kW 

# om cost of a wind turbine per MWh
w_om_cost_MWh = 14.4

# decommissioning cost of a wind turbine per MWh
w_dcms_cost_MWh = 4.0

# wind farm intermittence factor
# f_inter = 0.3

###############################################



###############################################
# SMR module data
P_nominal = 50 # nominal power, in MW
LF_lim = 0.05

# number of units in the npp
n_n_unit = 3

# whether first of a kind, 1 for yes, 0 for no
FOAK = 1

# life time expection of the NPP
npp_lifetime = 60

eta_direct = 0.51              # oecd nea value, large uncentainty
eta_indirect = 0.51              # oecd nea value, large uncentainty

# operation and maintainess cost, dollar per MWh 
om_cost_MWh = 25.8  
# fuel cost, dollar per MWh 
fuel_cost_MWh = 8.26
# decommisioning cost per MWh
dcms_cost_MWh = 0.16 

# construction time of a unit, in year
y_unit_construct = 2

# the utilization factor
f_uti = 0.85

# config learning factors
x = 0.15
y = 0.74
z = 0.82
k = 0.02

# technology learning rate
r_learning = 0.04

###############################################



###############################################
# hydrogen cell data
theta_m = 0.13     # the thickness of membrane, in mm
A = 16             # the area of the membrane, in cm^2
T = 80             # in C,
P_h2 = 1e5         # 
P_o2 = 1e5
P_h2o = 2e5

alpha_an = 0.5
alpha_cat = 0.5

i0_cat = 1e-3  # in A/cm^2
i0_an = 1e-7   # in A/cm^2

iter_max = 5000 # maximum number of iterations

###############################################



###############################################
# hydrogen cluster and storage data
h2_n_unit = 500        # total 300 units of pem cells
Pmax_unit = 0.3     # maximum power of a cell
Pmin_unit = 0.05    # minimum power of a cell

m_store = 0          # initial storage, in kg

capex_kw = 1400     # capital cost per kW
cap_op_ratio = 0.02 # capital cost operational cost ratio

pem_lifetime = 20   # lifetime of pem fuel cell

# yearly electricity price for PEM (for hybrid system it equals to 0)
price_ePEM = [0.0] * pem_lifetime 
###############################################



###############################################
# generate grid demand
###############################################
uk_grid = grid(dataMode,inFile,multiplier)
uk_grid.gen()
uk_grid.demand_plot()
time = uk_grid.aquire_time()
P_demand = uk_grid.aquire_demand()

time = time[0:289]
P_demand = P_demand[0:289]

#time = time[0:48]
#P_demand = P_demand[0:48]

uk_grid.user_demand_plot(time,P_demand)

###############################################
# economic data of the hybrid system
###############################################
dollar_equal = 2018

# life time of the hybrid system
sys_lifetime = 60

# electricty price per MWh
price_e = 130


# discount rate 
r_discount = 0.05
# inflation rate
r_inflation = 0.03

# hydrogen price per kg, use constant value in current example
price_h2 = [14] * pem_lifetime



###############################################
# electricity production part

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
#print ('wind farm output ',P_windfarm)
w_farm.wPower_plot(time,P_windfarm)

# calculate windfarm intermittence factor
f_inter = w_farm.cal_f_inter(P_windfarm,time,P_lim)

###############################################
# modelling a SMR NPP 
###############################################
p_unit = module.m_power()
P_nuclear = npp.npp_power(p_unit)

#print ('nuclear power ',P_nuclear)


####################################################################
# calculate the power produced from coupled nuclear-renewable system
####################################################################
P_windfarm = np.asarray(P_windfarm)
P_coupled = P_nuclear + P_windfarm
#print ('electricity produced by coupled system ',P_coupled)
#print ('grid demand ', P_demand)



###################################################
# calculate the grid and hydrogen system balancing
###################################################
# aquire minimum demand of hydrogen production 
Pmin_cluster = h2_sys.Pmin_system()
print ('minimun power for h2 cluster ',Pmin_cluster)

balance_control = balancing()
P_to_h2sys = balance_control.cal_to_h2sys(P_coupled,P_demand,Pmin_cluster)
print ('power to h2 system ', P_to_h2sys)

# calculate accumulated erengy to and from h2 system, and net value
e_acc_to_h2sys,e_acc_from_h2sys,e_acc_net_h2sys =\
        balance_control.cal_e_acc_h2sys(P_to_h2sys,time)

###############################################
# modelling hydrogen cells 
###############################################
P_h2_produced,P_h2_consumed,P_abandon = h2_sys.cal(P_to_h2sys,time)

#print ('h2 produces power ', P_h2_produced)
#print ('h2 consumed power ', P_h2_consumed)
m_tot = h2_sys.aquire_m()
print ('\n')
print ('total storage',m_tot, ' kg')

m_stored_data = h2_sys.aquire_m_records()

# calculate total ernegy abondaned and accumulated abandoned energy
e_abandon,e_acc_abandon = h2_sys.cal_e_abandon(P_abandon,time)
###################################################
# calculate the powet to the grid 
###################################################
P_to_grid = balance_control.cal_to_grid(P_coupled,P_h2_produced,P_h2_consumed)

# calculate total ernegy send to grid
e_acc_to_grid = balance_control.cal_e_acc_grid(P_to_grid,time)

#print ('wind-nuclear generated ',P_coupled)
#print ('power to h2 system ', P_to_h2sys)
#print ('power to grid ', P_to_grid)
#print ('grid demand ', P_demand)
#print ('abandoned power ',P_abandon)
#print ('stored hydrogen ', m_stored_data)


###################################################
# post processing of data 
###################################################
post_process.plt_grid_balance(time,P_demand,P_to_grid)
post_process.plt_h2_stored(time,m_stored_data)
post_process.plt_power_abandon(time,P_abandon)
post_process.data_performance('full',time,P_demand,P_coupled,P_to_grid,P_to_h2sys,P_abandon,m_stored_data)

time_interval = 60.0

time_slct, P_demand_slct, P_coupled_slct, \
        P_to_grid_slct, P_to_h2sys_slct, P_abandon_slct,\
        e_acc_to_grid_slct,e_acc_to_h2sys_slct, e_acc_from_h2sys_slct, e_acc_net_h2sys_slct, e_acc_abandon_slct,\
        m_stored_data_slct = \
         post_process.data_opti(time,time_interval,P_demand,P_coupled,\
         P_to_grid,P_to_h2sys,P_abandon,\
         e_acc_to_grid,e_acc_to_h2sys,e_acc_from_h2sys,e_acc_net_h2sys,e_acc_abandon,\
         m_stored_data)
post_process.data_performance('hour_data',time_slct,P_demand_slct,\
        P_coupled_slct,P_to_grid_slct,P_to_h2sys_slct,P_abandon_slct,m_stored_data_slct)
post_process.excel_performance('hour_data',time_slct,\
        P_demand_slct,P_coupled_slct,P_to_grid_slct,P_to_h2sys_slct,P_abandon_slct,\
        e_acc_to_grid_slct,e_acc_to_h2sys_slct,e_acc_from_h2sys_slct,e_acc_net_h2sys_slct,e_acc_abandon_slct,\
        m_stored_data_slct)
sys.exit()

# end of electricity produciton part modeling
###################################################
