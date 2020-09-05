#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# File              : NuReModel.py
# Author            : tzhang
# Date              : 20.11.2019
# Last Modified Date: 04.09.2020
# Last Modified By  : tzhang

"""

a model of coupled nuclear-renewable system for a mircogrid

Nuclear: nuclear power plant with n Small Modular Reactor (SMR) module, each has a maximum capacity of n MW
Renewable: wind farm with n wind turbine, each wind turbine has maximum capacity of 2 MW, and the total capacity of the wind farm is n MW
Hydrogen Production and Comsumption: a cluster consisted of n cells, each cell has a maximum capacity of 0.3 MW and a minimum capacity of 0.05 MW

Grid Demand: the demand data is the acutal grid data of UK in Jan, 2018. The data is scaled to 1% to simulate the grid demand of a microgrid

"""
import sys
import os

# insert from different path
sys.path.insert(1, '../../../')

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

inData = dataReader(str(sys.argv[1]))
inData.read()

###############################################
# run infomation
###############################################
title = inData.title
label = inData.label

###############################################
# configration of the hybrid system
###############################################
# input for electrical grid 
dataMode = inData.dataMode
inFile_Array = inData.inFile_Array
multiplier = inData.multiplier

###############################################
# hybrid system config
components = inData.components
num_chars = inData.num_chars
unit_power = inData.unit_power
n_units = inData.n_units
lifetimes = inData.lifetimes
con_time = inData.con_time
sys_lifetime = inData.sys_lifetime

# hybrid system control parameter
# data selection time scale
time_interval = inData.time_interval
# auto construction scheme
auto_con = inData.auto_con
# length of the time array
len_time = inData.len_time
###############################################


###############################################
# economic data of the hybrid system
###############################################
dollar_year = inData.dollar_year

# discount rate 
r_discount = inData.r_discount

# energy inflation rate
# e_inflation = 0.05

price_e_base = inData.price_e_base                      # electricty price per MWh
price_ePEM_base = inData.price_ePEM_base                    # electricty price per MWh
price_h2_base = inData.price_h2_base                     # price of h2 per kg

###############################################
# wind data
v_max = inData.v_max
v_mean = inData.v_mean
n_range = inData.n_range

# wind turbine data
d_wing = inData.d_wing # in m,  wind turbine diameter
J_turbine = inData.J_turbine # in kg.m^2, moment of initia of turbine
h_hub = inData.h_hub # in m, the height of the hub

cut_in = inData.cut_in
cut_out = inData.cut_out

loc_type = inData.loc_type        # 1 for land wind farm, 0 for off-shore wind farm

# captical cost of a wind turbine per kW
w_cost_kW = inData.w_cost_kW      # $ per kW 
# om cost of a wind turbine per MWh
w_om_cost_MWh = inData.w_om_cost_MWh
# decommissioning cost of a wind turbine per MWh
w_dcms_cost_MWh = inData.w_dcms_cost_MWh


###############################################



###############################################
# SMR module data
#P_nominal = 50 # nominal power, in MW
LF_lim = inData.LF_lim


# whether first of a kind, 1 for yes, 0 for no
FOAK = inData.FOAK

eta_direct = inData.eta_direct              # oecd nea value, large uncentainty
eta_indirect = inData.eta_indirect              # oecd nea value, large uncentainty

# operation and maintainess cost, dollar per MWh 
nu_om_cost_MWh = inData.nu_om_cost_MWh
# fuel cost, dollar per MWh 
nu_fuel_cost_MWh = inData.nu_fuel_cost_MWh
# decommisioning cost per MWh
nu_dcms_cost_MWh = inData.nu_dcms_cost_MWh

# config learning factors
x_learn = inData.x_learn 
y_learn = inData.y_learn
z_learn = inData.z_learn
k_learn = inData.k_learn

# technology learning rate
r_learning = inData.r_learning

###############################################



###############################################
# hydrogen cell data
theta_m = inData.theta_m     # the thickness of membrane, in mm
A_m = inData.A_m             # the area of the membrane, in cm^2

T_op = inData.T_op             # in C

P_h2 = inData.P_h2         # pressure of the system in pa 
P_o2 = inData.P_o2
P_h2o = inData.P_h2o

alpha_an = inData.alpha_an
alpha_cat = inData.alpha_cat

i0_cat = inData.i0_cat  # in A/cm^2
i0_an = inData.i0_an   # in A/cm^2

iter_max = inData.iter_max # maximum number of iterations

###############################################



###############################################
# hydrogen cluster and storage data
Pmin_unit = inData.Pmin_unit    # minimum power of a cell

m_store = inData.m_store          # initial storage, in kg

capex_kW = inData.capex_kW     # capital cost per kW
cap_op_ratio = inData.cap_op_ratio # capital cost operational cost ratio

###############################################
print ('system units configuration: ',n_units)
print ('initial h2 loading: ',str(m_store))


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
        #print ("H2 storage  model under development")
        pass

###############################################


###############################################
# electricity production part
case_dict = {}
for inFile in inFile_Array:

    idx = inFile_Array.index(inFile)

    key_dataset = 'dataset_'+str(idx)

    
    ###############################################
    # generate grid demand
    ###############################################
    data_grid = grid(dataMode,inFile,multiplier)
    data_grid.gen()
    #data_grid.demand_plot()
    time = data_grid.aquire_time()
    P_demand = data_grid.aquire_demand()
    
    if len_time != 0:
        time = time[0:len_time]
    
    t_scale = cp.time_scale_trans(time)
    
    #################################################
    # calculate system performance during time period
    #################################################
    case_data = []
    for case in cases[1:]:
    
        num = len(case_data)+1
    
        case_label = 'case'+str(num)
            
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
                #print ("H2 storage  model under development")
                pass
    
        # scale demand according to capacity ratio
        P_demand = data_grid.aquire_demand_array()
        P_demand = list(P_demand * capa_ratio)
       
        if len_time != 0:
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
        # balance controller 
        balance_control = balancing()

        w_turbine = wind_Turbine(d_wing,J_turbine,h_hub,w_P_unit,cut_in,cut_out)  # wind turbine
        w_farm = wind_farm(n_unit_wind_op)   # wind farm
        
        # nuclear
        module = SMR_module(nu_P_unit,LF_lim)   # SMR module
        npp = SMR_NPP(n_unit_npp_op)                   # SMR NPP
        
        # energy storage and hybrid usage
        h2_sys = h2_system(theta_m,A_m,alpha_an,alpha_cat,i0_an,i0_cat,T_op,P_h2,P_o2,P_h2o,iter_max,\
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
        #cp_curve.cp_plot()
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
        #print ('electricity demanded by system ',P_demand)
        
        
         
        ###################################################
        # calculate the grid and hydrogen system balancing
        ###################################################
        # aquire minimum demand of hydrogen production 
        Pmin_cluster = h2_sys.Pmin_system()
        #print ('minimun power for h2 cluster ',Pmin_cluster)
        
        P_to_h2sys_virtual = balance_control.cal_to_h2sys_virtual(P_coupled,P_demand,Pmin_cluster)
        #print ('power to h2 system virtual', P_to_h2sys_virtual)
        
        
        ###############################################
        # modelling hydrogen cells 
        ###############################################
        P_h2_produced,P_h2_consumed,P_abandon = h2_sys.cal(P_to_h2sys_virtual,time)
       
        #print ('virtual power to h2 system', P_to_h2sys_virtual)
        #print ('h2 produces power ', P_h2_produced)
        #print ('h2 consumed power ', P_h2_consumed)
        #sys.exit()
        m_tot = h2_sys.aquire_m()
        #print ('\n')
        #print ('total storage',m_tot, ' kg')
        
        m_stored_data = h2_sys.aquire_m_records()
        
        P_to_h2sys = balance_control.cal_to_h2sys(P_h2_produced,P_h2_consumed,P_abandon)

        # calculate accumulated erengy to and from h2 system, and net value
        e_acc_to_h2sys,e_acc_from_h2sys,e_acc_net_h2sys =\
                balance_control.cal_e_acc_h2sys(P_to_h2sys,time)
        # calculate total ernegy abondaned and accumulated abandoned energy
        e_abandon,e_acc_abandon = balance_control.cal_e_abandon(P_abandon,time)
        ###################################################
        # calculate the powet to the grid 
        ###################################################
        P_to_grid = balance_control.cal_to_grid(P_demand,P_coupled,P_h2_produced,P_h2_consumed)
        #print ('power to grid ', P_to_grid)

        # calculate to ratio fit to the grid demand 
        ratio_gridfit = balance_control.ratio_fit(P_demand,P_to_grid)
        
        # calculate total ernegy send to grid
        e_acc_to_grid = balance_control.cal_e_acc_grid(P_to_grid,time)
        
        #print ('wind-nuclear generated ',P_coupled)
        #print ('power to h2 system ', P_to_h2sys)
        #print ('power to grid ', P_to_grid)
        #print ('grid demand ', P_demand)
        #print ('abandoned power ',P_abandon)
        #print ('stored hydrogen ', m_stored_data)
        #print ('\n')
        
        ###################################################
        # post processing of data 
        ###################################################
        #post_process.plt_grid_balance(case_label,time,P_demand,P_to_grid)
        #post_process.plt_h2_stored(case_label,time,m_stored_data)
        #post_process.plt_power_abandon(case_label,time,P_abandon)
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
    
        dataflow = cp.model_cp_data(e_acc_to_grid,e_acc_net_h2sys,e_abandon,m_stored_data)
        dataflow = cp.data_scale(dataflow,t_scale)
    
        # add windfarm intermittence factor
        dataflow.append(ratio_gridfit)

        # add windfarm intermittence factor
        dataflow.append(f_inter)
    
        case_data.append(dataflow)
        
        # end of data set production modelling
        ###################################################
    case_dict[key_dataset] = case_data

# end of electricity produciton part modeling
###################################################

###############################################
# merge data of different inFiles to get average
case_data_ave = cp.case_data_ave(case_dict)

# hybrid coupling
case_lifetime = cp.case_lifetime_convert(sys_con.lifetime_scale,cases,case_data_ave)
y_tot = len(case_lifetime)
price_e,price_ePEM,price_h2 = cp.cal_price_array(sys_con.lifetime_scale,price_e_base,price_ePEM_base,price_h2_base)
e_to_grid,e_to_h2,e_ab,m_h2 = cp.cal_energy_array(case_lifetime)
f_uti = cp.cal_f_uti(sys_con.lifetime_scale,e_to_grid,e_to_h2)
r_gridfit_array = cp.cal_r_fit_array(case_lifetime)
ratio_gridfit_ave = cp.cal_r_fit_ave(r_gridfit_array)

print ('to grid ratio array: ', r_gridfit_array)
print ('to grid ratio: ', ratio_gridfit_ave)
#post_process.excel_lifetime(sys_con.lifetime_scale,e_to_grid,e_to_h2,e_ab,m_h2)
#post_process.data_lifetime('case',sys_con.lifetime_scale,e_to_grid,e_to_h2,e_ab,m_h2)
###############################################

###############################################
# economic analysis part

eco_pack = []
for key in system.config.keys():
    if system.config[key][0] == '00':
        smr_eco = nuclear_eco(system.config[key][1],system.config[key][2],dollar_year,system.config[key][3],system.config[key][4],FOAK)
        ME_2_curr,ME_9_curr = smr_eco.import_coa()
        smr_eco.cal_OCC(ME_2_curr,ME_9_curr,eta_direct,eta_indirect,x_learn,y_learn,z_learn,k_learn,r_learning)
        smr_eco.cal_IDC(r_discount)
        smr_eco.cal_OM_unit(nu_om_cost_MWh,f_uti)
        smr_eco.cal_fuel_unit(nu_fuel_cost_MWh,f_uti)
        smr_eco.cal_decommissioning_unit(nu_dcms_cost_MWh,f_uti)
    
        data = {'00':smr_eco}
        eco_pack.append(data)
    elif system.config[key][0] == '01':
        f_inter_array = wind_farm.cal_f_inter_array(sys_con.lifetime_scale,cases,case_data_ave)
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
        PEM_eco.cal_CAPEX(capex_kW)
        PEM_eco.cal_OPEX(capex_kW,cap_op_ratio)

        data = {'10':PEM_eco}
        eco_pack.append(data)
    elif system.config[key][0] == '20':
        #print ("H2 storage  model under development")
        pass

sys_eco = system_eco()

sys_eco.cal_hybrid_cashflow(system.config,sys_con.lifetime_scale,eco_pack,price_e,price_ePEM,price_h2,e_to_grid,e_to_h2,m_h2)
sys_eco.cal_LCOE(e_to_grid,m_h2)
print ('system levelized cost of electricity: ',sys_eco.LCOE,'$/MWh')
#print(sys_eco.profit)
#print(sys_eco.cost)

sys_eco.cal_NPV(r_discount)
print ('system net present value: ', sys_eco.NPV, 'million $')
sys_eco.cal_IRR(r_discount)
print ('system internal rate of return: ', sys_eco.IRR)

post_process.plt_cashflow(y_tot,sys_eco.cashflow,label)
post_process.writer_cashflow(sys_eco.cashflow,label)

with open('cal_data.txt','a') as f:
    f.write('\n')
    f.write ('system configuarion: ')
    for num in n_units:
        f.write(str(num)+' ')
    f.write('\n')
    f.write ('total energy abandoned in lifetime (MWh) - EAB: '+str('%.2f'%sum(e_ab))+'\n')
    f.write ('ratio system fit the grid demands - RFG: '+str('%.4f'%ratio_gridfit_ave)+'\n')
    f.write ('system net present value (in million $) - NPV: '+str(sys_eco.NPV)+'\n')
    f.write ('system internal rate of return - IRR: '+str(sys_eco.IRR)+'\n')
    f.write('\n')
f.close()
sys.exit()
