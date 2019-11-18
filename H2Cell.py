#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# File              : H2Cell.py
# Author            : tzhang
# Date              : 13.11.2019
# Last Modified Date: 18.11.2019
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
        self.n = 2 # electron number
        self.theta_m = theta_m # the thickness of membrane
        self.A = A             # the area of the membrane
        self.T = T
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
        I = h2_module.I_cal(self,P)
        n_rate = h2_module.h2_rate(I)

        return n_rate  # in mol/s

    
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
        while i_iter <= iter_max:
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
        
        if i_iter > iter_max:
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
        t_log = R*self.T/(self.n*F) * np.log(P_h2*P_o2**(0.5)/P_h2o)

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
        eta_ohm = theta_m * j/sigma_m

        return eta_ohm

    # the conductivity of the PEM
    def _sigma_m_(self):
        sigma_m = (0.005139*self.lambda_h - 0.00326)\
                *math.exp(1268*(1.0/303.0 - 1.0/(self.T+273.15)))

        return sigma_m
        
    # calculate the 
    def V_oc(E_oc,eta_act,eta_ohm):
        V_oc = E_oc + eta_act + eta_ohm

        return V_oc
        
    def I_eq(self,V_oc):
        E_expr = V_oc*self.I_sbl

        return E_expr

    def eq_solver(E_expr,E,E_oc,eta_ohm):
        v_ini = E_oc + eta_ohm
        I_ini = E/v_ini

        E_expr_new = E_expr.subs(I,I_ini)
        print (E_expr_new)
        
#        print (I)

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

P = 0         # in W, the input power of the pem

pem = h2_module(theta_m,A,alpha_an,alpha_cat,i0_an,i0_cat,T,P_h2,P_o2,P_h2o,iter_max)
n_rate = pem.cal(P)

print ('production rate',n_rate)

"""

"""

a model for hydrogen cluster

"""
class h2_cluster:
    def __init__(self, n_unit,Pmax_unit,Pmin_unit):
        self.n_unit = n_unit # number of units 
        self.Pmax_unit = Pmax_unit  # maximum capacity of a module
        self.Pmin_unit = Pmin_unit  # minimum capacity od a module

    # calculate the total hydrogen prodcuction rate
    def h2_total_rate(self,n_rate):
        n_rate_tot = n_rate * self.n_unit

        return n_rate_tot
    
    # calculate the totol amount of hydrogen produced
    def h2_production(n_rate_tot,t):
        n_tot = n_rate_tot*t

        return n_tot

    # calculate the input power to each unit 
    def p_unit(self,P):
        P = P/self.n_unit
        P_unit = min(self.Pmax_unit,P)

        if P_unit < P:
            P_residual = P - self.Pmax_unit

        elif P_unit < Pmin_unit:
            print ('***************** WARNING !!*****************')
            print ('  input power too low, pem not functioning   ')
            print ('*********************************************')

            P_unit = 0
            P_residual = P
        else:
            P_residual = 0


        return P_unit, P_residual

    # calculate the total resiudal power 
    def p_res_tot(self,P_residual):

        P_res_tot = P_residual*self.n

        return P_res_tot


    # calculate the total residual energy
    def e_res_tot(P_res_tot,t):
        
        E_res_tot = P_res_tot*t

        return E_res_tot
