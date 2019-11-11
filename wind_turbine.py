#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# File              : wind_turbine.py
# Author            : tzhang
# Date              : 28.10.2019
# Last Modified Date: 10.11.2019
# Last Modified By  : tzhang

import math
import numpy as np
import turbine_data
from matplotlib import pyplot as plt

"""

a module simulate wind turbine                                           

"""

class wind_Turbine:
    # parameters describing a wind turbine
    def __init__(self,d_wing,J_turbine, cut_in, cut_out):
        self.d_wing = d_wing   # diameter of the turbine
        self.J_turbine = J_turbine  # moment of inertia of turbine
        
        self.cut_in = cut_in       # cut in energy of wind turbine
        self.cut_out  = cut_out    # cut out energy of the wind turbine, in W (usually the limit is about 2 MW, normaly between 0.5 to 3.6 MW)
        
    def P_harvest(self,Pw,cp):        # calculate the harvest wind energy of a wind turbine
        P = Pw * cp           # harvest power is the product of wind power and wind turbine efficiency 
        Power = max(0.0,P)         # eleminate negative  power, minimal power to 0

#        self.P0 = self.P0 + Power
        return Power

class cp_IEC:
    def __init__(self):
        self.wind = []
        self.cp = []

    # a reference curve taken from IEC standard
    def curve_A(self):
        wind = [2.1, 2.5, 3.0, 3.5, 4.0, 4.5, 5.0, 5.5, 6.0, 6.5, 7.0, 7.5, 8.0, 8.5, 9.0, 9.5, 10.0, 10.5, 11.0, 11.5, 12.0, 12.5, 13.0, 13.5, 14.0, 14.5, 15.0, 15.5, 16.0, 16.5, 17.0, 17.5, 18.0, 18.5, 19.0, 19.4, 20.0, 20.5, 20.9, 21.5, 22.0, 22.6, 24.6, 25.0]
        cp = [-0.26, -0.16, -0.10, -0.03, 0.00, 0.05, 0.15, 0.28, 0.36, 0.40, 0.42, 0.43, 0.44, 0.44, 0.44, 0.45, 0.43, 0.42, 0.41, 0.38, 0.36, 0.33, 0.30, 0.27, 0.25, 0.22, 0.20, 0.18, 0.17, 0.15, 0.14, 0.13, 0.12, 0.11, 0.09, 0.08, 0.07,0.04, 0.05, 0.03, 0.00, 0.03, 0.00, 0.00]

        self.wind = self.wind + wind 
        self.cp = self.cp + cp
    # anohter reference curve taken from IEC standard
    def curve_B(self):
        wind = [2.1, 2.5, 3.0, 3.5, 4.0, 4.5, 5.0, 5.5, 6.0, 6.5, 7.0, 7.5, 8.0, 8.5, 9.0, 9.5, 10.0, 10.5, 11.0, 11.5, 12.0, 12.5, 13.0, 13.5, 14.0, 14.5, 15.0, 15.5, 16.0, 16.5, 17.0, 17.5, 18.0, 18.5, 19.0, 19.4, 20.0, 20.5, 20.9]
        cp = [-0.26, -0.16, -0.10, -0.03, 0.00, 0.05, 0.15, 0.28, 0.36, 0.40, 0.42, 0.43, 0.44, 0.44, 0.44, 0.45, 0.43, 0.42, 0.41, 0.38, 0.36, 0.33, 0.30, 0.27, 0.25, 0.22, 0.20, 0.18, 0.17, 0.15, 0.14, 0.13, 0.12, 0.11, 0.10, 0.09, 0.09,0.08, 0.08]

        self.wind = self.wind + wind 
        self.cp = self.cp + cp

    # determine the cp value according to wind velocity
    def cp_value(self,v_wind):
        wind = []
        for value in self.wind:
            wind.append(value)

        sort = wind
        sort.append(v_wind)
        sort.sort()
        idx = sort.index(v_wind)
        cp = self.cp[idx-1]

        return cp

    def cp_plot(self):
        plt.figure(figsize = (12,8))
        plt.plot(self.wind,self.cp, color = 'r',linestyle = '-',marker = '^',markersize = '5')
        plt.xlabel('wind velocity (m/s)',fontsize = '16')
        plt.xlim(left = 0.0)
        plt.ylabel('cp', fontsize = '16')
        plt.grid(linestyle='--',linewidth = '1')

        pltName = 'cp_curve.png'
#        plt.show()
#        plt.close()
        plt.savefig(pltName,dpi = 100)






"""
class test 
"""    
from windData import wind_Data, wind_Rayleigh
from material import air
from turbine_data import data_Turbine, data_Heier
from scipy import integrate
from sympy import *
# wind data
v_max = 20.0
v_mean = 10.0
n_range = 20

# time data
sTime = 0.0
eTime = 20.0
nData = 20

# air property
airData = air()
airData.constant()
d_air = airData.density

# wind turbine data
d_wing = 90 # in m,  wind turbine diameter
P_lim = 2E6 # in W, power limit of a turbine
J_turbine = 1.3E7 # in kg.m^2, moment of initia of turbine

beta = 7.87


wind = wind_Rayleigh(v_max,v_mean,n_range,sTime,eTime,nData)
windData = wind.genData()


print (windData)

cp_curve = cp_IEC()
cp_curve.curve_A()
cp_curve.cp_plot()

cp = cp_curve.cp_value(windData[1][1])
print (cp)

"""
windTurbine = wind_Turbine(d_wing,P_lim,J_turbine)

#P_wind = windTurbine.P_wind(windData[1][1],d_air)
P_wind = windTurbine.P_wind(20.0,d_air)

print ('%.6e'%P_wind)


turbineData = data_Heier()
turbineData.gen()
print (turbineData.coeffs)

#lambda_tsr =windTurbine.tsr_cal(omega,windData[1][1])
#lambda_1 = windTurbine.lambda_1_cal(beta,lambda_tsr)
#cp = windTurbine.cp_cal(beta, lambda_1,turbineData.coeffs)
#cp = 0.59
#Power = windTurbine.P_harvest(P_wind,cp)
#print (Power)
# odes
omega = der(phi)
P = tau * omega
tau = J*der(omega)
P = P_wind * cp

der(omega) = P_wind * cp/(J*omega)


t = [0.0, 0.5, 1.0]
v_wind = windData[1][1]
coeffs = turbineData.coeffs

C = P_wind/J_turbine

omega = symbols('omega')
def eq(omega,t,v_wind,beta,coeffs,C):
    lambda_tsr =windTurbine.tsr_cal(omega,v_wind)
    lambda_1 = wind_Turbine.lambda_1_cal(beta,lambda_tsr)
    cp = windTurbine.cp_cal(beta, lambda_1,coeffs)

    domegadt = C*cp/omega

    return domegadt

eq = eq(omega,t,v_wind,beta,coeffs,C)
print (eq)
omega0 = 0.0

omega = integrate.odeint(eq,omega0,t)
 
"""
