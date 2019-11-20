#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# File              : SMR.py
# Author            : tzhang
# Date              : 06.11.2019
# Last Modified Date: 20.11.2019
# Last Modified By  : tzhang

"""

a simple SMR model

"""

class SMR_module:
    def __init__(self,P_nominal,LF_lim):
        self.P_nominal = P_nominal
        self.LF_lim = LF_lim        # percentage/min, i.g. 0.05 5%/min

    # module output 
    def m_power(self):
        return self.P_nominal

class SMR_NPP:
    def __init__(self,n_unit):
        self.n_unit = n_unit

    # npp power ouput
    def npp_power(self,p_unit):
        npp_power = p_unit * self.n_unit

        return npp_power



"""
a test class
"""
P_nominal = 50 # nominal power, in MW
LF_lim = 0.05

n_unit = 3

module = SMR_module(P_nominal,LF_lim)
p_unit = module.m_power()

npp = SMR_NPP(n_unit)
n_power = npp.npp_power(p_unit)

print (p_unit)
print (n_power)
