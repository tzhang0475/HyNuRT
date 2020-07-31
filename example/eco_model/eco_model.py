#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# File              : eco_model.py
# Author            : tzhang
# Date              : 29.07.2020
# Last Modified Date: 01.08.2020
# Last Modified By  : tzhang

import sys

# insert from different path
sys.path.insert(1, '../../')

from eco_analysis import *
"""

a test class for coa_pwr12

"""
year_curr = 2018

coa = coa_pwr12()

direct_cost_dd = coa.aquire_2_dd()
ddd_21 = coa.aquire_ddd_21()

des_21 = coa.aquire_code_description(ddd_21)

print (des_21)


ME_21 = coa.aquire_code_ME(ddd_21)

ME_2 = coa.aquire_code_ME(direct_cost_dd)
print (ME_21)
print (ME_2)

indirect_cost_dd = coa.aquire_9_dd()

direct_cost_dd_2018 = coa.inflation(direct_cost_dd,year_curr)
indirect_cost_dd_2018 = coa.inflation(indirect_cost_dd,year_curr)
print (direct_cost_dd_2018)

ME_2_2018 = coa.aquire_code_ME(direct_cost_dd_2018)

print (ME_2_2018)

ME_9_2018 = coa.aquire_code_ME(indirect_cost_dd_2018)

cost_kW_pwr12 = coa.aquire_cost_kW(ME_2_2018,ME_9_2018)

print ('PWR12 cost per kW', cost_kW_pwr12)



"""

a test class for SMR_eco

"""
sub_sys1 = 'smr'
P_unit = 60             #electrical power in MW
n_unit = 6
year = 2018
FOAK = 1
lifetime = 60           # life time the npp

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

# electricty price per MWh
price_e = 130

# the utilization factor
f_uti = 0.85

# discount rate 
r_discount = 0.05
# inflation rate
r_inflation = 0.03

# energy inflation rate
e_inflation = 0.05

# config learning factors
x = 0.15
y = 0.74
z = 0.82
k = 0.02

# technology learning rate
r_learning = 0.04



smr = nuclear_eco(P_unit,n_unit,year,lifetime,y_unit_construct,FOAK)
classmap={'smr_eco':smr,'smr_eco2':smr}
ME_2_curr,ME_9_curr = smr.import_coa()

coa = coa_pwr12()
cost_kW_pwr12 = coa.aquire_cost_kW(ME_2_curr,ME_9_curr)
print ('PWR12 cost per kW: ', cost_kW_pwr12)

smr.cal_OCC(ME_2_curr,ME_9_curr,eta_direct,eta_indirect,x,y,z,k,r_learning)
print ('total cost of the NPP: ', '%.9e'%smr.occ)
print ('total cost of the NPP per kW: ', smr.occ_kW)
smr.cal_IDC(r_discount)
print ('total interest to pay: ', smr.idc)
smr.cal_OM_unit(om_cost_MWh,f_uti)
print ('O&M cost per unit per year: ',smr.om_unit_year)
smr.cal_fuel_unit(fuel_cost_MWh,f_uti)
print ('fuel cost per unit per year: ',smr.fuel_unit_year)
smr.cal_decommissioning_unit(dcms_cost_MWh,f_uti)
print ('decommissioning cost per unit per year: ',smr.dcms_unit_year)

smr.cal_NCF(price_e,f_uti)
cashflow = smr.cashflow
print ('net cass flow of smr',cashflow)

smr.cal_LCOE(r_discount,price_e,f_uti)
print ('smr levelized cost of electricity: ',smr.LCOE, ' $/MWh')

y_tot = lifetime+int((y_unit_construct*n_unit)/2)
post_process.plt_cashflow(y_tot,cashflow,sub_sys1)

smr.cal_NPV(r_discount,r_inflation)
print ('SMR net present value: ', smr.NPV, 'million $')
smr.cal_IRR(r_discount,r_inflation)
print ('SMR internal rate of return: ', smr.IRR)

print ('\n')

"""

a test class for wind_eco

"""
sub_sys2 = 'windfarm'
P_lim = 2           # in MW
w_n_unit = 40   
w_lifetime = 30     # 30 years life time
loc_type = 1        # 1 for land wind farm, 0 for off-shore wind farm
w_con_time = 1
# discount rate 
r_discount = 0.05
# inflation rate
r_inflation = 0.025

# energy inflation rate
e_inflation = 0.05

# electricty price per MWh
price_e = 130

# captical cost of a wind turbine per kW
cost_kW = 1590      # $ per kW 

# om cost of a wind turbine per MWh
w_om_cost_MWh = 14.4

# decommissioning cost of a wind turbine per MWh
w_dcms_cost_MWh = 4.0

# wind farm intermittence factor
f_inter = [0.5] * (w_lifetime + 1)
f_inter_ave = 0.5


wfarm = wind_eco(P_lim,w_n_unit,w_lifetime,w_con_time)
wfarm.cal_OCC(cost_kW)
print ('total wind farm capital cost: ', wfarm.occ)
wfarm.cal_OM_unit(w_om_cost_MWh,f_inter_ave)
print ('om cost of per turbine per year: ', wfarm.om_unit_year)
wfarm.cal_decommissioning_unit(dcms_cost_MWh,f_inter_ave)
print ('decommissioning cost per turbine per year: ',smr.dcms_unit_year)

wfarm.cal_NCF(price_e,f_inter)
cashflow = wfarm.cashflow


wfarm.cal_LCOE(r_discount,price_e,f_inter)
print ('wind farm levelized cost of electricity: ',wfarm.LCOE, ' $/MWh')

y_tot = w_lifetime+1
post_process.plt_cashflow(y_tot,cashflow,sub_sys2)

wfarm.cal_NPV(r_discount,r_inflation)
print ('wind farm net present value: ', wfarm.NPV, 'million $')
wfarm.cal_IRR(r_discount,r_inflation)
print ('wind farm internal rate of return: ', wfarm.IRR)

print ('\n')

"""

a test class for h2sys_eco

"""
Pmax_unit = 0.5     # maximum power of a unit
n_unit = 10         # number of units

h2_con_time = 1

capex_kw = 1400     # capital cost per kW

cap_op_ratio = 0.02 # capital cost operational cost ratio

price_e = [0,130,130,130,130,130]       # electricty price per MWh

energy = [0, 100,100,100,100,100]

price_h2 = [0,14,14,14,14,14]     # price of h2 per kg
production_h2 = [0,6000,6000,6000,6000,6000]    # production in kg of each year (or other unit time, year is for cash flow analysis)

lifetime = 5

# calculate PEM cost and profit
PEM_eco = h2_cost_simple(Pmax_unit,n_unit,lifetime,h2_con_time)

cost_CAPEX = PEM_eco.cal_CAPEX(capex_kw)
cost_OPEX = PEM_eco.cal_OPEX(capex_kw,cap_op_ratio)

PEM_eco.cal_NCF(lifetime,energy,price_e, price_h2, production_h2)

print (PEM_eco.cashflow)


