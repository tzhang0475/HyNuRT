#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# File              : turbine_data.py
# Author            : tzhang
# Date              : 04.11.2019
# Last Modified Date: 06.11.2019
# Last Modified By  : tzhang

############################################################################
# wind turbine coefficients                                                #
# - user defined wind turbine coefficients                                 #
# - Haier wind turbine coefficients    (Haier[2009])                       #
# - Thongom wind turbine coefficients  (Thongam[2009])                     #
############################################################################

class data_Turbine:
    def __init__(self):
        self.coeffs = []  # coefficients to calculate efficiency cp of turbine
        self.poly = []    # polinominal coefficients to calculate optimum pitch angle


# pre-defined wind turbine with Herier (Herier [2009])
class data_Heier(data_Turbine):
    # generate data
    def gen(self):
        data_Heier.__c_Heier__(self)
        data_Heier.__p_Heier__(self)

    # pre-defined wind turbine coefficients with Herier (Herier [2009])
    def __c_Heier__(self):
        coeffs = []  
        c0 = None  # a dummy to eliminate misunderstanding
        # c1 to c6 are wind turbine coefficients
        c1 = 0.5
        c2 = 116.0
        c3 = 0.4
        c4 = 5.0
        c5 = 21.0
        c6 = 0.0

        coeffs.append(c0)
        coeffs.append(c1)
        coeffs.append(c2)
        coeffs.append(c3)
        coeffs.append(c4)
        coeffs.append(c5)
        coeffs.append(c6)

        self.coeffs = self.coeffs + coeffs

    # pre-defined optimized pitch angle coefficient with Herier (Herier [2009])
    def __p_Heier__(self):
        poly = []  
        p0 = None  # a dummy to eliminate misunderstanding
        # p1 to p4 are polinomial coefficients of beta 
        p1 =  0.00212298309850983
        p2 = -0.10552111636622796
        p3 =  1.79931615238508824
        p4 = -8.34638029169715701

        poly.append(p0)
        poly.append(p1)
        poly.append(p2)
        poly.append(p3)
        poly.append(p4)

        self.poly = self.poly + poly


# pre-defined wind turbine with Thongam el al (Thongam el al [2009])
class data_Thongam(data_Turbine):
    # generate data
    def gen(self):
        data_Thongam.__c_Thongam__(self)
        data_Thongam.__p_Thongam__(self)

    # pre-defined wind turbine coefficients with Thongam el al (Thongam el al [2009])
    def __c_Thongam__(self):
        coeffs = []  
        c0 = None  # a dummy to eliminate misunderstanding
        # c1 to c6 are wind turbine coefficients
        c1 = 0.5176
        c2 = 116.0
        c3 = 0.4
        c4 = 5.0
        c5 = 21.0
        c6 = 0.006795

        coeffs.append(c0)
        coeffs.append(c1)
        coeffs.append(c2)
        coeffs.append(c3)
        coeffs.append(c4)
        coeffs.append(c5)
        coeffs.append(c6)

        self.coeffs = self.coeffs + coeffs


    # pre-defined optimized pitch angle coefficient with Thongam (Thongam [2009])
    def __p_Thongam__(self):
        poly = []  
        p0 = None  # a dummy to eliminate misunderstanding
        # p1 to p4 are polinomial coefficients of beta 
        p1 =  0.00181568948139207
        p2 = -0.08293733085338961
        p3 =  1.28855124643962093
        p4 = -4.65888550563144754

        poly.append(p0)
        poly.append(p1)
        poly.append(p2)
        poly.append(p3)
        poly.append(p4)

        self.poly = self.poly + poly

# pre-defined wind turbine by user
class data_User(data_Turbine):
    # generate data
    def gen(self):
        data_User.__c_User__(self)
        data_User.__p_User__(self)

    def c_User(self,u1,u2,u3,u4,u5):
        coeffs = []  
        c0 = None  # a dummy to eliminate misunderstanding
        # c1 to c6 are wind turbine coefficients
        c1 = u1
        c2 = u2
        c3 = u3
        c4 = u4
        c5 = u5
        c6 = u6

        coeffs.append(c0)
        coeffs.append(c1)
        coeffs.append(c2)
        coeffs.append(c3)
        coeffs.append(c4)
        coeffs.append(c5)
        coeffs.append(c6)

        self.coeffs = self.coeffs + coeffs

    # pre-defined optimized pitch angle coefficient with Thongam (Thongam [2009])
    def __p_User__(self,u1,u2,u3,u4):
        poly = []  
        p0 = None  # a dummy to eliminate misunderstanding
        # p1 to p4 are polinomial coefficients of beta 
        p1 =  u1
        p2 =  u2
        p3 =  u3
        p4 =  u4

        poly.append(p0)
        poly.append(p1)
        poly.append(p2)
        poly.append(p3)
        poly.append(p4)

        self.poly = self.poly + poly

