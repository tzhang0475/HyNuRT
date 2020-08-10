#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# File              : H2Cell.py
# Author            : tzhang
# Date              : 13.11.2019
# Last Modified Date: 10.08.2020
# Last Modified By  : tzhang

"""
REFERENCES:
   - Marangio, F, Santarelli, M, and Cali, M. Theoretical model and experimental analysis of a high pressure PEM water electrolyser for hydrogen production. United Kingdom: N. p., 2009. Web. doi:10.1016/J.IJHYDENE.2008.11.083.
   - Alhassan Salami Tijani, M.F. Abdul Ghani, A.H. Abdol Rahim, Ibrahim Kolawole Muritala, Fatin Athirah Binti Mazlan, Electrochemical characteristics of (PEM) electrolyzer under influence of charge transfer coefficient,International Journal of Hydrogen Energy,Volume 44, Issue 50,2019,Pages 27177-27189,ISSN 0360-3199, doi:10.1016/j.ijhydene.2019.08.188.   
   -A. Awasthi, Keith Scott, S. Basu,Dynamic modeling and simulation of a proton exchange membrane electrolyzer for hydrogen production,International Journal of Hydrogen Energy,Volume 36, Issue 22,2011,Pages 14779-14786,ISSN 0360-3199,doi:10.1016/j.ijhydene.2011.03.045.
   -Gregor Taljan, Michael Fowler, Claudio Cañizares, Gregor Verbič,Hydrogen storage for mixed wind–nuclear power plants in the context of a Hydrogen Economy,International Journal of Hydrogen Energy,Volume 33, Issue 17,2008,Pages 4463-4475,ISSN 0360-3199,doi:10.1016/j.ijhydene.2008.06.040.
"""

import numpy as np
import math
from sympy import *
"""

a model to decribe hydrogen production

"""
class h2_module:
    def __init__(self,theta_m,A,alpha_an,alpha_cat,i0_an,i0_cat,\
            T,P_h2,P_o2,P_h2o,\
            iter_max):
        self.n = 2                  # electron number
        self.theta_m = theta_m      # the thickness of membrane
        self.A = A                  # the area of the membrane
        self.T = T                  # operating temperature
        self.P_h2 = P_h2
        self.P_o2 = P_o2
        self.P_h2o = P_h2o

        self.alpha_an = alpha_an
        self.alpha_cat = alpha_cat

        self.iter_max = iter_max

        # a typical exchange current density, Pt for cat, Pt-Ir an
        self.i0_cat = i0_cat # in A/cm^2
        self.i0_an = i0_an # in A/cm^2

        # the degree of humidification
        self.lambda_h = 25 # an assumed value

        # a symbol for current 
        self.I_sbl = 0 

    # modelling hydrogen production
    def cal(self,P):
        P = P*1e6      # convert MW to W
        I = h2_module.I_cal(self,P)
        n_rate = h2_module.h2_rate(I)

        return n_rate  # in mol/s

    # modelling (all) hydrogen consumed to produce power
    def cal_consume_all(self,n_unit_consume_rate):
        I_consumption = h2_module.I_consumption_cal(n_unit_consume_rate)
        P = h2_module.P_cal(self,I_consumption)

        P = P/1e6     # convert W to MW

        return P

    # calculate the power produced under current current
    def P_cal(self,I_consumption):
        # ideal gas constant
        R = 8.31446261815324 #in J⋅K−1⋅mol−1
        # Faraday constant
        F = 96485.3329      #s A / mol or C mol^-1
        
        self.I_sbl = I_consumption

        E0_rev = h2_module._E0_rev_(self)
        E_oc = h2_module._E_oc_(self,E0_rev)

        eta_act = h2_module._eta_act_(self)

        sigma_m = h2_module._sigma_m_(self)
        eta_ohm = h2_module._eta_ohm_(self,sigma_m)

        V_oc = h2_module.V_oc(E_oc,eta_act,eta_ohm)

        P = I_consumption * V_oc

        return P

    # calculate the current under power    
    def I_cal(self,P):
        # ideal gas constant
        R = 8.31446261815324 #in J⋅K−1⋅mol−1
        # Faraday constant
        F = 96485.3329      #s A / mol or C mol^-1
        E0_rev = h2_module._E0_rev_(self)
        E_oc = h2_module._E_oc_(self,E0_rev)
#        print (E_oc)
#        P = 15
        v_ini = E_oc
        I_ini = P/v_ini
        self.I_sbl = I_ini

        v_last = v_ini
        
        i_iter = 0

        # calculate pem current
        while i_iter <= self.iter_max:
            i_iter = i_iter + 1
            eta_act = h2_module._eta_act_(self)
#            print(eta_act)

            sigma_m = h2_module._sigma_m_(self)
            eta_ohm = h2_module._eta_ohm_(self,sigma_m)

            V_oc = h2_module.V_oc(E_oc,eta_act,eta_ohm)

#            print ('total voltage',V_oc)

            det_V = abs(V_oc - v_last)
#            print ('error is: ', det_V)

            v_last = V_oc

            if det_V < 1e-4:
                I = P/V_oc
                break

            I_curr = P/V_oc
            self.I_sbl = I_curr
        
        if i_iter > self.iter_max:
            print ('***************** WARNING !!*****************')
            print ('the pem current calculation does not converge')
            print ('*********************************************')

        return I

#        a validation of eta and i density
#
#        i_an = self.i0_an*math.exp(alpha_an*F/(R*(self.T+273.15))*eta_an)
#        i_cat = self.i0_cat*math.exp(-alpha_cat*F/(R*(self.T+273.15))*eta_cat)
#        i = i_an - i_cat
#        print(self.I_sbl/self.A,i)

    # calculate hydrogen production rate
    def h2_rate(I):
        # Faraday constant
        F = 96485.3329      #s A / mol or C mol^-1

        n_rate = I/(2*F)    # in mol/s

        return n_rate

    # calculate consumption current
    def I_consumption_cal(n_unit_consume_rate):
        # Faraday constant
        F = 96485.3329      #s A / mol or C mol^-1

        I_consumption = n_unit_consume_rate*2*F    # in mol/s

        return I_consumption


    # reverse energy 
    def _E0_rev_(self):
        E0_rev = 1.229 - 0.9*1e-3*(self.T-298)

        return E0_rev
    
    # open circuit energy
    def _E_oc_(self,E0_rev):
        # ideal gas constant
        R = 8.31446261815324 #in J⋅K−1⋅mol−1
        # Faraday constant
        F = 96485.3329      #s A / mol or C mol^-1

        # log term 
        t_log = R*self.T/(self.n*F) * np.log(self.P_h2*self.P_o2**(0.5)/self.P_h2o)

        E_oc = E0_rev + t_log

        return E_oc

    # the activation over potential
    def _eta_act_(self):
        # ideal gas constant
        R = 8.31446261815324 #in J⋅K−1⋅mol−1
        # Faraday constant
        F = 96485.3329      #s A / mol or C mol^-1

        # calculate the current density 
        i = self.I_sbl/self.A

     #   print ('current density', i)
        
        C_term = R*(self.T+273.15)/F

        eta_an = C_term/self.alpha_an * math.asinh(i/(2*self.i0_an))
        eta_cat = C_term/self.alpha_cat * math.asinh(i/(2*self.i0_cat))
        eta_act = eta_an + eta_cat

        return eta_act#, eta_an, eta_cat

    # the ohmic overvoltage potential
    def _eta_ohm_(self,sigma_m):
        j = self.I_sbl/self.A
        eta_ohm =self.theta_m * j/sigma_m

        return eta_ohm

    # the conductivity of the PEM
    def _sigma_m_(self):
        sigma_m = (0.005139*self.lambda_h - 0.00326)\
                *math.exp(1268*(1.0/303.0 - 1.0/(self.T+273.15)))

        return sigma_m
        
    # calculate the open circuit voltage 
    def V_oc(E_oc,eta_act,eta_ohm):
        V_oc = E_oc + eta_act + eta_ohm

        return V_oc
        


"""
class test

theta_m = 0.13 # the thickness of membrane, in mm
A = 16             # the area of the membrane, in cm^2
T = 50             # in C,
P_h2 = 1e5   # 
P_o2 = 1e5
P_h2o = 2e5

alpha_an = 0.5
alpha_cat = 0.5

i0_cat = 1e-3  # in A/cm^2
i0_an = 1e-7   # in A/cm^2

iter_max = 5000 # maximum number of iterations

P = 0.3         # in MW, the input power of the pem

pem = h2_module(theta_m,A,alpha_an,alpha_cat,i0_an,i0_cat,T,P_h2,P_o2,P_h2o,iter_max)
n_rate = pem.cal(P)

print ('production rate',n_rate)

"""

"""

a model for hydrogen cluster

"""
class h2_cluster:
    def __init__(self,n_unit,Pmax_unit,Pmin_unit):
        self.n_unit = n_unit # number of units 
        self.Pmax_unit = Pmax_unit  # maximum capacity of a module
        self.Pmin_unit = Pmin_unit  # minimum capacity od a module
        self.working_state = True   # default state of the cluster, true for production, false for consumption
        self.operation_state = True  # default state of production, true for full operation,false for partial operation

    # calculate the minimum energy to maintain the h2 cluster operation
    def P_min_operation(self):
        Pmin_cluster = self.n_unit * self.Pmin_unit

        return Pmin_cluster

    # calculate the total hydrogen prodcuction rate
    def h2_total_rate(self,n_rate,n_operate):
        n_rate_tot = n_rate * n_operate

        return n_rate_tot
    
    # calculate the totol amount of hydrogen produced or consumed
    def h2_calculation(self,n_rate_tot,t):
        n_tot = n_rate_tot*t

        return n_tot

    # calculate the totol rate of hydrogen consumed
    def h2_consumed_rate(self,n_consume,t):
        n_tot_consume_rate = n_consume/t

        return n_tot_consume_rate

    # calculate the rate per unit of hydrogen consumed
    def h2_unit_consume_rate(self,n_tot_consume_rate):
        n_unit_consume_rate = n_tot_consume_rate/self.n_unit

        return n_unit_consume_rate

    # calculate the number of working modules in partial electrolysis mode
    def n_unit_operation(self,P):
        n_operate = int(P/self.Pmin_unit)
        #print ('calculate result ', n_operate)
        P_residual = P - (self.Pmin_unit*n_operate)

        return n_operate, P_residual

    # calculate the input power to each unit at full operation and consumption 
    def p_unit_cal(self,P):
        P_unit = P/self.n_unit
        #P_unit = min(self.Pmax_unit,P_unit)

        if P_unit <= self.Pmax_unit and P_unit >= self.Pmin_unit:
            self.working_state = True      # change the state to production
            self.operation_state = True    # operation state change to full operation

            P_residual = 0.0
            n_operate = self.n_unit

        elif P_unit > self.Pmax_unit:
            self.working_state = True    # production with maximum power
            self.operation_state = True    # operation state change to full operation

            n_operate = self.n_unit
            P_residual = P - self.Pmax_unit*n_operate

        elif P_unit < self.Pmin_unit and P_unit >= 0:
            #print ('********************* WARNING !!*******************')
            #print ('  input power too low, pem partially functioning   ')
            #print ('***************************************************')
            self.working_state = True   # change the state to production, but no real production 
            self.operation_state = False    # operation state change to full operation

            n_operate,P_residual = h2_cluster.n_unit_operation(self,P) 
            P_unit = self.Pmin_unit

            #print ('partial operation: ', n_operate)

        else:
            self.working_state = False   # change the state to consumption
            self.operation_state = True    # operation state change to full operation

            P_unit = abs(P_unit)
            P_residual = 0
            n_operate = self.n_unit

        return P_unit, P_residual,n_operate

    # calculate the total resiudal power 
    def p_res_tot(self,P_residual):

        P_res_tot = P_residual*self.n_unit

        return P_res_tot


    # calculate the total residual energy
    def e_res_tot(P_res_tot,t):
        
        E_res_tot = P_res_tot*t

        return E_res_tot

    # calculate the total power produced by hydrogen
    def P_produced(self,p_unit):

        p_produced = p_unit * self.n_unit

        return p_produced

"""

a simple model for hydrogen storage 

"""

class h2_storage:
    def __init__(self,n_store = 0):
        self.n_store = n_store  # stored hydrogen, in mol

        self.output_max = 0

        self.v_store = 0
        self.m_store = 0

    def update(self,n_tot):
        h2_storage._store_update_(self,n_tot)
        h2_storage._mol_vol_converter_(self)
        h2_storage._mol_mass_converter_(self)

    # return current molar storage
    def aquire_n(self):
        return self.n_store

    # return current mass storage
    def aquire_m(self):
        return self.m_store

    # return the cunsumed hydrogen 
    def aquire_consume(self):
        return self.output_max

    # update stored hydrogen
    def _store_update_(self,n_tot):
        n_store_new = self.n_store + n_tot

        # define maximum output once the storage is not sufficient
        if n_store_new < 0.0:
            self.output_max = self.n_store
        else:
            self.output_max = 0.0   # no consumption during this period

        self.n_store = n_store_new
        self.n_store = max(0.0,self.n_store)

    # calculate hydrogen in mol to hydrogen in volume standard state
    def _mol_vol_converter_(self):
        v_f = 22.4          # volume per mole in standard condition
        self.v_store = self.n_store * v_f

    # calculate hydrogen in mol to hydrogen in mass, in kg
    def _mol_mass_converter_(self):
        m_f = 2e-3             # in kg/mol
        self.m_store = self.n_store * m_f





"""
class test
n_unit = 300        # total 300 units of pem cells
Pmax_unit = 0.3     # maximum power of a cell
Pmin_unit = 0.05    # minimum power of a cell

P_input = [50,-60,20,30,50,40,70] # 30 MW residual power from grid
t = [0,300,600,900,1200,1500,1800]     # in s

pem_cluster = h2_cluster(n_unit,Pmax_unit,Pmin_unit)
h2_store = h2_storage()

for i in range(len(P_input)-1):
    print ('\n')
    print ('new cycle')
    dt = t[i+1] - t[i]
    P_unit,P_residual = pem_cluster.p_unit_cal(P_input[i])
    
    print ('power to unit',P_unit)
    print (P_residual)
    n_rate = pem.cal(P_unit)
    print ('production rate',n_rate)

    if not pem_cluster.state:
        n_rate = -n_rate
    
    print (n_rate)    # mol/s
    
    n_rate_tot = pem_cluster.h2_total_rate(n_rate)
    print (n_rate_tot)
    
    n_tot = pem_cluster.h2_calculation(n_rate_tot,dt)
    
    print (n_tot)
    
    h2_store.update(n_tot)
    m_tot = h2_store.aquire_m()
    print (n_tot)
    print ('h2 mass stored',m_tot)

    n_consume = h2_store.aquire_consume()
    print ('consumed',n_consume)
    if n_consume > 0:
        print ('hydrogen fuel cell')
        n_tot_consume_rate = pem_cluster.h2_consumed_rate(n_consume,dt)
        n_unit_consume_rate = pem_cluster.h2_unit_consume_rate(n_tot_consume_rate)
        p_unit = pem.cal_consume_all(n_unit_consume_rate)
        P_h2 = pem_cluster.P_produced(p_unit)
        print ('power produced',P_h2)

print ('\n')
m_tot = h2_store.aquire_m()
print ('final h2 stored',m_tot)

"""


"""

a model for the hydrogen system 

"""

class h2_system(h2_module,h2_cluster,h2_storage):
    def __init__(self,theta_m,A,alpha_an,alpha_cat,i0_an,i0_cat,T,P_h2,P_o2,P_h2o,iter_max,\
                    n_unit,Pmax_unit,Pmin_unit,\
                    m_store):
        h2_module.__init__(self,theta_m,A,alpha_an,alpha_cat,i0_an,i0_cat,T,P_h2,P_o2,P_h2o,iter_max)
        h2_cluster.__init__(self,n_unit,Pmax_unit,Pmin_unit)
        # convert the initial storage from kg to mol
        m_f = 2e-3             # in kg/mol
        n_store = m_store/ m_f

        h2_storage.__init__(self,n_store)

        self.m_stored_data = [m_store]   # array of total stored hydrogen, in kg

    # calculate the power and hydrogen change 
    def cal(self,P_input,time):
        P_pro = []
        P_con = []
        P_res = []

        # convert unit of time array from min to s
        time = np.asarray(time,dtype = 'float')
        time = time * 60    
        time = list(time)
#        print ('convert time',time)

        for i in range(len(P_input)):
        #    print ('\n')
        #    print ('a new time step')
            
            if i != (len(time)-1):
                dt = time[i+1] - time[i]

            P_curr = P_input[i]
            # power production, consumption, and residual in current time step
            P_production, P_consumption, P_residual = h2_system.cal_curr(self,P_curr,dt)

            P_pro.append(P_production)
            P_con.append(P_consumption)
            P_res.append(P_residual)

        return P_pro, P_con, P_res

    # calculate total energy abondoned, in MWh
    def cal_e_abandon(self,P_res,time): 
        e_abandon = [0.0]
        e_acc_abandon = [0.0]
        for i in range(1,len(time)):
            e_ab = P_res[i-1] * (time[i]-time[i-1])  # please note the unit of time is min here
            e_ab = e_ab/60.0    # convert MWmin to MWh
            e_ab_acc = e_acc_abandon[i-1] + e_ab

            e_abandon.append(e_ab)
            e_acc_abandon.append(e_ab_acc)

        return e_abandon, e_acc_abandon
   
    # calculate the power and hydrogen change in current time step
    def cal_curr(self,P_curr,dt):
        P_unit,P_residual,n_operate = h2_cluster.p_unit_cal(self,P_curr)
        
#        print ('power to unit ',P_unit)
#        print ('residual power ',P_residual)
        
        # calculate the hydrogen production in current time step
        if self.working_state:        
            h2_system.production_process(self,P_unit,n_operate,dt)

            # power consumed to generate hydrogen
            P_consumption = P_curr

            # power produced by hydrogen fuel cell
            P_production = 0.0

        # calculate the hydrogen consumption in current time step
        else:                       
            h2_system.consumption_process(self,P_unit,n_operate,dt)

            # power consumed to generate hydrogen
            P_consumption = 0.0

            # power produced by hydrogen fuel cell or need to be produced
            P_production = abs(P_curr)  # as P_curr is a nagative value as input
           
            
            # check whether the storage of hydrogen is sufficient
            n_consume = h2_storage.aquire_consume(self)

            # if not sufficient, consume all the hydrogen in the storage
            if n_consume > 0:
                P_production = h2_system.consume_all(self,n_consume,dt)
        
        # update total stored hydrogen data
        h2_system.h2_stored(self)

        return P_production, P_consumption, P_residual
 
    # calculate the hydrogen production 
    def production_process(self,P_unit,n_operate,dt):
        n_rate = h2_module.cal(self,P_unit)
#        print ('production rate',n_rate)
    
        n_rate_tot = h2_cluster.h2_total_rate(self,n_rate,n_operate)
#        print ('cluster hydrogen generate rate ', n_rate_tot)
        
        n_tot = h2_cluster.h2_calculation(self,n_rate_tot,dt)
        
#        print ('total generated hydrogen (in mol) ',n_tot)
        
        h2_storage.update(self,n_tot)
     
    # calculate the hydrogen consumption 
    def consumption_process(self,P_unit,n_operate,dt):
        n_rate = h2_module.cal(self,P_unit)
        # convert to consume rate
        n_rate = -n_rate
        
        n_rate_tot = h2_cluster.h2_total_rate(self,n_rate,n_operate)
#       print ('cluster hydrogen comsuption rate ', n_rate_tot)
        
        n_tot = h2_cluster.h2_calculation(self,n_rate_tot,dt)
        
#        print ('total consumed hydrogen (in mol) ', n_tot)
        
        h2_storage.update(self,n_tot)

    # calculate the power generation by consume all the hydrogen in the storage
    def consume_all(self,n_consume,dt):
#        print ('hydrogen fuel cell')
        n_tot_consume_rate = h2_cluster.h2_consumed_rate(self,n_consume,dt)
        n_unit_consume_rate = h2_cluster.h2_unit_consume_rate(self,n_tot_consume_rate)
        p_unit = h2_module.cal_consume_all(self,n_unit_consume_rate)
        P_h2_gen = h2_cluster.P_produced(self,p_unit)
#        print ('power produced',P_h2)

        return P_h2_gen

    # return current mass storage
    def aquire_m(self):
        return self.m_store

    # return history of hydrogen mass storage data
    def aquire_m_records(self):
        return self.m_stored_data

    # record stored hydrogen data
    def h2_stored(self):
        m_store = h2_system.aquire_m(self)
        self.m_stored_data.append(m_store)
        

    # sysem minimum production power demand
    def Pmin_system(self):
        Pmin_cluster = h2_cluster.P_min_operation(self)
        
        return Pmin_cluster


"""
a class test

theta_m = 0.13 # the thickness of membrane, in mm
A = 16             # the area of the membrane, in cm^2
T = 50             # in C,
P_h2 = 1e5   # 
P_o2 = 1e5
P_h2o = 2e5

alpha_an = 0.5
alpha_cat = 0.5

i0_cat = 1e-3  # in A/cm^2
i0_an = 1e-7   # in A/cm^2

iter_max = 5000 # maximum number of iterations


n_unit = 300        # total 300 units of pem cells
Pmax_unit = 0.3     # maximum power of a cell
Pmin_unit = 0.05    # minimum power of a cell

m_store = 0          # initial storage, in kg

P_input = [50,-60,10,30,50,40,70] # 30 MW residual power from grid
time = [0,300,600,900,1200,1500,1800]     # in s

h2_sys = h2_system(theta_m,A,alpha_an,alpha_cat,i0_an,i0_cat,T,P_h2,P_o2,P_h2o,iter_max,\
                    n_unit,Pmax_unit,Pmin_unit,\
                    m_store)

h2_sys.cal(P_input,time)
m_tot = h2_sys.aquire_m()
print ('total storage',m_tot)
"""
