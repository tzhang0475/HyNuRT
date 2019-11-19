#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# File              : wind_turbine.py
# Author            : tzhang
# Date              : 28.10.2019
# Last Modified Date: 19.11.2019
# Last Modified By  : tzhang

import math
import numpy as np
import turbine_data
from matplotlib import pyplot as plt

"""
REFERENCES:
    - Heier, Siegfried, and Rachel Waddington. Grid Integration of Wind Energy Conversion Systems. Chichester, England: Wiley, 2014. Print.
    - Eberhart, Philip & Chung, Tek & Haumer, Anton & Kral, Christian. (2015). Open Source Library for the Simulation ofWind Power Plants. 929-936. 10.3384/ecp15118929. 
    - International Standard, IEC 61400-12-1:2017 Wind energy generation systems - Part 12-1: Power performance measurements of electricity producing wind turbines
"""

"""

a module simulate wind turbine                                           

"""

class wind_Turbine:
    # parameters describing a wind turbine
    def __init__(self, d_wing, J_turbine, h_hub, P_lim, cut_in, cut_out):
        self.d_wing = d_wing   # diameter of the turbine
        self.J_turbine = J_turbine  # moment of inertia of turbine
        self.h_hub = h_hub          # the height of the hub
       
        self.P_lim = P_lim         # power limit of the wind turbine, in W (usually the limit is about 2 MW, normaly between 0.5 to 3.6 MW
        self.cut_in = cut_in       # cut in velocity of wind turbine
        self.cut_out  = cut_out    # cut out energy of the wind turbine         

        self.energy = []           # total energy in wind
        self.p_out = []            # wind turbine output power

    # calculate energy in wind
    def _P_wind_(self, dens_air, time, v_wind): #  dens_air is the density of air, d_wing is the diameter of the turbine
        energy = []
        pi = 3.141592653 # pi constant
        for i in range(len(time)):
            Pw = 1./2. * dens_air * pi* self.d_wing**2/4. * v_wind[i]**3
            energy.append(Pw)

        self.energy = self.energy + energy

        return energy

    # calculate theoretical wind turbine output power
    def _P_harvest_(self,Pw,cp):        # calculate the harvest wind energy of a wind turbine
       # print (self.P_lim)
        P = Pw * cp           # harvest power is the product of wind power and wind turbine efficiency 
       # print (P)
        P = min(self.P_lim,P)
       # print (P)

#        self.P0 = self.P0 + Power
        return P

    # calculate wind turbine output power
    def P_output(self, dens_air, time, v_wind, cp):
        energy = wind_Turbine._P_wind_(self,dens_air,time,v_wind)

        power = []
        for i in range(len(time)):
            if v_wind[i] <=  self.cut_in:
                wPower = 0.0
            elif v_wind[i] >= self.cut_out:
                wPower = 0.0
            else:
              #  print (v_wind[i],cp[i])
                wPower = wind_Turbine._P_harvest_(self,energy[i],cp[i])
                wPower = wPower/1E6     # convert to MW
            power.append(wPower)

        self.p_out = self.p_out + power

        return power


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
    def _cp_value_(self,wind_velocity):
        wind = []
        for value in self.wind:
            wind.append(value)

        sort = wind
        if wind_velocity in wind:
            idx = wind.index(wind_velocity)
            cp = self.cp[idx]
        else:
            sort.append(wind_velocity)
            sort.sort()
            idx = sort.index(wind_velocity)
            cp = self.cp[idx-1]

        return cp

    # determine the array of cp
    def cp_array(self, v_wind):
        cp_array = []
        for i in range(len(v_wind)):
            cp = cp_IEC._cp_value_(self,v_wind[i])
            cp_array.append(cp)

        return cp_array

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
from windData import wind_Data, wind_Rayleigh
from material import air
from turbine_data import data_Turbine, data_Heier
from scipy import integrate
from sympy import *
# wind data
v_max = 20.0
v_mean = 10.0
n_range = 40

# time data
sTime = 0.0
eTime = 20.0
nData = 20

# air property
airData = air()
airData.constant()
d_air = airData.density

# wind turbine data
d_wing = 70 # in m,  wind turbine diameter
J_turbine = 1.3E7 # in kg.m^2, moment of initia of turbine
h_hub = 50 # in m, the height of the hub
P_lim = 2E6 # in W, power limit of a turbine

cut_in = 4.0
cut_out = 25.0



wind = wind_Rayleigh(v_max,v_mean,n_range,sTime,eTime,nData)
time,v_wind = wind.genData()
#print (time)
#print (v_wind)

cp_curve = cp_IEC()
cp_curve.curve_A()
#print (cp_curve.wind)
#print (cp_curve.cp)
cp_curve.cp_plot()
cp_array = cp_curve.cp_array(v_wind)
#print (cp_array)

w_turbine = wind_Turbine(d_wing,J_turbine,h_hub,P_lim,cut_in,cut_out)
wP_out = w_turbine.P_output(d_air, time, v_wind, cp_array)
print (wP_out)
"""    


"""

a module simulate wind farm                                 

"""
class wind_farm:
    def __init__(self,n_unit):
        self.n_unit = n_unit

    def p_out(self,p_unit):
        P_output = self.n_unit*p_unit

        return P_output
