#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# File              : NuReModel.py
# Author            : tzhang
# Date              : 20.11.2019
# Last Modified Date: 31.07.2020
# Last Modified By  : tzhang

"""

a model of coupled nuclear-renewable system for a mircogrid

Nuclear: nuclear power plant with n Small Modular Reactor (SMR) module, each has a maximum capacity of n MW
Renewable: wind farm with n wind turbine, each wind turbine has maximum capacity of 2 MW, and the total capacity of the wind farm is n MW
Hydrogen Production and Comsumption: a cluster consisted of n cells, each cell has a maximum capacity of 0.3 MW and a minimum capacity of 0.05 MW

Grid Demand: the demand data is the acutal grid data of UK in Jan, 2018. The data is scaled to 0.5% to simulate the grid demand of a microgrid

"""
import sys
import os

# insert from different path
sys.path.insert(1, '../../')
path_re = os.path.realpath(__file__)

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
from coupling import *


###############################################
# configration of the hybrid system
###############################################
# input for electrical grid 
dataMode = 0
inFile = 'UK_gridwatch_year2018_Jan.csv'
multiplier = 0.01

###############################################
# hybrid system config
components = ['SMR','wind','PEM','storage']
num_chars = ['00','01','10','20']
unit_power = [60.0,2.0,0.6,0.0]
n_units = [6,80,500,1]
lifetimes = [60,30,20,60]
con_time = [2,1,1,1]

sys_lifetime = 60

# hybrid system control parameter
# data selection time scale
time_interval = 60.0
# auto construction scheme
auto_con = 1
# length of the time array
len_time = 289
###############################################


###############################################
# economic data of the hybrid system
###############################################
dollar_year = 2018

# discount rate 
r_discount = 0.05
# inflation rate
r_inflation = 0.03

# energy inflation rate
# e_inflation = 0.05

price_e_base = 130                      # electricty price per MWh
price_ePEM_base = 0.0                    # electricty price per MWh
price_h2_base = 14.0                     # price of h2 per kg

###############################################
# wind data
v_max = 28.0
v_mean = 11.0
n_range = 40

# wind turbine data
d_wing = 90 # in m,  wind turbine diameter
J_turbine = 1.3E7 # in kg.m^2, moment of initia of turbine
h_hub = 50 # in m, the height of the hub
#P_lim = 2  # in MW, power limit of a turbine

cut_in = 4.0
cut_out = 25.0

# wind farm data
#w_n_unit = 80

#w_lifetime = 30     # 30 years life time
loc_type = 1        # 1 for land wind farm, 0 for off-shore wind farm

# captical cost of a wind turbine per kW
w_cost_kW = 1590      # $ per kW 

# om cost of a wind turbine per MWh
w_om_cost_MWh = 14.4

# decommissioning cost of a wind turbine per MWh
w_dcms_cost_MWh = 4.0


###############################################



###############################################
# SMR module data
#P_nominal = 50 # nominal power, in MW
LF_lim = 0.05

# number of units in the npp
#n_n_unit = 6

# whether first of a kind, 1 for yes, 0 for no
FOAK = 1

# life time expection of the NPP
#npp_lifetime = 60

eta_direct = 0.51              # oecd nea value, large uncentainty
eta_indirect = 0.51              # oecd nea value, large uncentainty

# operation and maintainess cost, dollar per MWh 
nu_om_cost_MWh = 25.8  
# fuel cost, dollar per MWh 
nu_fuel_cost_MWh = 8.26
# decommisioning cost per MWh
nu_dcms_cost_MWh = 0.16 

# construction time of a unit, in year
#y_unit_construct = 2

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
#h2_n_unit = 500        # total 300 units of pem cells
#Pmax_unit = 0.6     # maximum power of a cell
Pmin_unit = 0.05    # minimum power of a cell

m_store = 0          # initial storage, in kg

capex_kw = 1400     # capital cost per kW
cap_op_ratio = 0.02 # capital cost operational cost ratio

#pem_lifetime = 20   # lifetime of pem fuel cell

###############################################


###############################################
# generate grid demand
###############################################
data_grid = grid(dataMode,inFile,multiplier)
data_grid.gen()
data_grid.demand_plot()
time = data_grid.aquire_time()
P_demand = data_grid.aquire_demand()

time = time[0:len_time]

t_scale = cp.time_scale_trans(time)

###############################################
# build systems structure
system = sys_config(components,num_chars,unit_power,n_units,lifetimes,con_time,sys_lifetime)
sys_con = con_plan(components,num_chars,unit_power,n_units,lifetimes,con_time,sys_lifetime)
#sys_con = con_plan(system,con_time)
#sys_con = con_plan(con_time)

sys_con.cal_scale(auto_con)
sys_con.con_schedule(auto_con)

cases = cp.case_to_cal(sys_con.lifetime_scale)
for char in cases[0]:
    if char == '00':
        col_npp = cases[0].index(char)
    elif char == '01':
        col_wind = cases[0].index(char)
    elif char == '02':
        print ("PV model under development")
    elif char == '10':
        col_pem = cases[0].index(char)
    elif char == '20':
        print ("H2 storage  model under development")

for key in system.config.keys():
    if system.config[key][0] == '00':
        nu_P_unit = system.config[key][1]
    elif system.config[key][0] == '01':
        w_P_unit = system.config[key][1]
    elif system.config[key][0] == '02':
        print ("PV model under development")
    elif system.config[key][0] == '10':
        pem_P_unit = system.config[key][1]
    elif system.config[key][0] == '20':
        print ("H2 storage  model under development")

###############################################



###############################################
# electricity production part
case_data = []

for case in cases[1:]:
        
    capa_ratio = float(case[-1])

    # read operation unit data
    for char in cases[0]:
        if char == '00':
            n_unit_npp_op = int(case[col_npp])
        elif char == '01':
            n_unit_wind_op = int(case[col_wind])
        elif char == '02':
            print ("PV model under development")
        elif char == '10':
            n_unit_pem_op = int(case[col_pem])
        elif system.config[key][0] == '20':
            print ("H2 storage  model under development")

    # scale demand according to capacity ratio
    P_demand = data_grid.aquire_demand_array()
    P_demand = list(P_demand * capa_ratio)
    
    P_demand = P_demand[0:len_time]

    
    ###############################################
    # generate wind data during simulation time
    ###############################################
    wind = wind_Rayleigh(v_max,v_mean,n_range,time)
    time,v_wind = wind.genData()  # NOTE:the unit of time is in min #
    #print (v_wind)
    #wind.plt_v_dis()
    #wind.plt_windData()
    
    ###############################################
    # create modules in the system
    ###############################################
    w_turbine = wind_Turbine(d_wing,J_turbine,h_hub,w_P_unit,cut_in,cut_out)  # wind turbine
    w_farm = wind_farm(n_unit_wind_op)   # wind farm
    
    # nuclear
    module = SMR_module(nu_P_unit,LF_lim)   # SMR module
    npp = SMR_NPP(n_unit_npp_op)                   # SMR NPP
    
    # energy storage and hybrid usage
    h2_sys = h2_system(theta_m,A,alpha_an,alpha_cat,i0_an,i0_cat,T,P_h2,P_o2,P_h2o,iter_max,\
                        n_unit_pem_op,pem_P_unit,Pmin_unit,\
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
    #w_farm.wPower_plot(time,P_windfarm)
    
    # calculate windfarm intermittence factor
    f_inter = w_farm.cal_f_inter(P_windfarm,time,w_P_unit)
    
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
    #print ('minimun power for h2 cluster ',Pmin_cluster)
    
    balance_control = balancing()
    P_to_h2sys = balance_control.cal_to_h2sys(P_coupled,P_demand,Pmin_cluster)
    #print ('power to h2 system ', P_to_h2sys)
    
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
    #print ('\n')
    #print ('total storage',m_tot, ' kg')
    
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
    #post_process.plt_grid_balance(time,P_demand,P_to_grid)
    #post_process.plt_h2_stored(time,m_stored_data)
    #post_process.plt_power_abandon(time,P_abandon)
    #post_process.data_performance('full',time,P_demand,P_coupled,P_to_grid,P_to_h2sys,P_abandon,m_stored_data)
    
    
    time_slct, P_demand_slct, P_coupled_slct, \
            P_to_grid_slct, P_to_h2sys_slct, P_abandon_slct,\
            e_acc_to_grid_slct,e_acc_to_h2sys_slct, e_acc_from_h2sys_slct, e_acc_net_h2sys_slct, e_acc_abandon_slct,\
            m_stored_data_slct = \
             post_process.data_opti(time,time_interval,P_demand,P_coupled,\
             P_to_grid,P_to_h2sys,P_abandon,\
             e_acc_to_grid,e_acc_to_h2sys,e_acc_from_h2sys,e_acc_net_h2sys,e_acc_abandon,\
             m_stored_data)
    #post_process.data_performance('hour_data',time_slct,P_demand_slct,\
    #        P_coupled_slct,P_to_grid_slct,P_to_h2sys_slct,P_abandon_slct,m_stored_data_slct)
    #post_process.excel_performance('hour_data',time_slct,\
    #        P_demand_slct,P_coupled_slct,P_to_grid_slct,P_to_h2sys_slct,P_abandon_slct,\
    #        e_acc_to_grid_slct,e_acc_to_h2sys_slct,e_acc_from_h2sys_slct,e_acc_net_h2sys_slct,e_acc_abandon_slct,\
    #        m_stored_data_slct)

    dataflow = cp.model_cp_data(e_acc_to_grid,e_acc_net_h2sys,m_stored_data)
    dataflow = cp.data_scale(dataflow,t_scale)

    # add windfarm intermittence factor
    dataflow.append(f_inter)

    case_data.append(dataflow)
    
    # end of electricity produciton part modeling
    ###################################################


###############################################
# hybrid coupling
case_lifetime = cp.case_lifetime_convert(sys_con.lifetime_scale,cases,case_data)
y_tot = len(case_lifetime)
price_e,price_ePEM,price_h2 = cp.cal_price_array(sys_con.lifetime_scale,price_e_base,price_ePEM_base,price_h2_base)
e_to_grid,e_to_h2,m_h2 = cp.cal_energy_array(case_lifetime)
###############################################

###############################################
# economic analysis part

eco_pack = []
for key in system.config.keys():
    if system.config[key][0] == '00':
        smr_eco = nuclear_eco(system.config[key][1],system.config[key][2],dollar_year,system.config[key][3],system.config[key][4],FOAK)
        ME_2_curr,ME_9_curr = smr_eco.import_coa()
        smr_eco.cal_OCC(ME_2_curr,ME_9_curr,eta_direct,eta_indirect,x,y,z,k,r_learning)
        smr_eco.cal_IDC(r_discount)
        smr_eco.cal_OM_unit(nu_om_cost_MWh,f_uti)
        smr_eco.cal_fuel_unit(nu_fuel_cost_MWh,f_uti)
        smr_eco.cal_decommissioning_unit(nu_dcms_cost_MWh,f_uti)
    
        data = {'00':smr_eco}
        eco_pack.append(data)
    elif system.config[key][0] == '01':
        f_inter_array = wind_farm.cal_f_inter_array(sys_con.lifetime_scale,cases,case_data)
        f_inter_ave = wind_farm.cal_f_inter_ave(f_inter_array)
        wfarm_eco = wind_eco(system.config[key][1],system.config[key][2],system.config[key][3],system.config[key][4])
        wfarm_eco.cal_OCC(w_cost_kW)
        wfarm_eco.cal_OM_unit(w_om_cost_MWh,f_inter_ave)
        wfarm_eco.cal_decommissioning_unit(w_dcms_cost_MWh,f_inter_ave)

        data = {'01':wfarm_eco}
        eco_pack.append(data)

    elif system.config[key][0] == '02':
        print ("PV model under development")
    elif system.config[key][0] == '10':
        PEM_eco = h2_cost_simple(system.config[key][1],system.config[key][2],system.config[key][3],system.config[key][4])
        PEM_eco.cal_CAPEX(capex_kw)
        PEM_eco.cal_OPEX(capex_kw,cap_op_ratio)

        data = {'10':PEM_eco}
        eco_pack.append(data)
    elif system.config[key][0] == '20':
        print ("H2 storage  model under development")

sys_eco = system_eco()

sys_eco._cal_hybrid_cost_(sys_con.lifetime_scale,eco_pack,price_ePEM,e_to_h2)
sys_eco._cal_hybrid_profit_(sys_con.lifetime_scale,price_e,price_h2,e_to_grid,m_h2)

sys_eco.cal_hybrid_cashflow(sys_con.lifetime_scale,eco_pack,price_e,price_ePEM,price_h2,e_to_grid,e_to_h2,m_h2)
#print(sys_eco.profit)
#print(sys_eco.cost)
#print(sys_eco.cashflow)
post_process.plt_cashflow(y_tot,sys_eco.cashflow,'system')
