#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# File              : wind_turbine.py
# Author            : tzhang
# Date              : 28.10.2019
# Last Modified Date: 05.11.2019
# Last Modified By  : tzhang
import math
import numpy as np
import turbine_data

"
a module simulate wind turbine                                           
the model is based on modelica windPowerPlant (Eberhart [2015])          

"

class wind_Turbine:
    # parameters describing a wind turbine
    def __init__(self,d_wing,P_lim,J_turbine):
        self.d_wing = d_wing   # diameter of the turbine
        self.P_lim  = P_lim    # output power limit of the wind turbine, in W (usually the limit is about 2 MW, normaly between 0.5 to 3.6 MW)
        self.J_turbine = J_turbine  # moment of inertia of turbine
        self.coeffs = []        # coefficients for wind turbine
        self.P0 = 0.0          # the harvest power of wind turbine    


    # wind energy at current moment
    def P_wind(self, v_wind, dens_air): # v_wind is the velocity of the wind at the moment, dens_air is the density of air
        pi = 3.141592653 # pi constant
        
        Pw = 1./2. * dens_air * pi*self.d_wing**2/4. * v_wind**3

        return Pw

    def P_harvest(self,Pw):        # calculate the harvest wind energy of a wind turbine
        P = Pw * self.cp           # harvest power is the product of wind power and wind turbine efficiency 
        Power = max(0.0,P)         # eleminate negative  power, minimal power to 0

        self.P0 = self.P0 + Power
    
    # calculate wind turbine efficiency, 
    def cp_cal(self,beta,lambda_1):
        # pass wind turbine coefficients to variables
        c1 = self.coeffs[1]
        c2 = self.coeffs[2]
        c3 = self.coeffs[3]
        c4 = self.coeffs[4]
        c5 = self.coeffs[5]
        c6 = self.coeffs[6]

        cp = c1 * (c2/lambda_1-c3*beta-c4)*math.exp(-c5/lambda_1) + c6*lambda_1

        return cp

    # calculate lambda1 
    def lambda_1_cal(beta,lambda_tsr):
        c1 = 1/(lambda_tsr+0.089)  
        c2 = 0.035/(beta**3+1)

        c = c1 - c2

        lambda_1 = 1/c

        return lambda_1

    # calcualte the tip speed ratio
    def tsr_cal(self,omega,v_wind):  # omega is the angular velocity, v_wind is the wind velocity at the moment 
        lambda_tsr = omegea * self.d_wing/(2*v_wind)

        return lambda_tsr

    # calculate pitch angle beta (in deg)
    def beta_cal(self, lambda_str):

        # polinominal terms 
        t1 = p1 * lambda_tsr**3
        t2 = p2 * lambda_tsr**2
        t3 = p3 * lambda_tsr
        t4 = p4

        beta = t1 + t2 + t3 + t4

        return beta

    
