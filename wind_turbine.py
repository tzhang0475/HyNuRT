import math
import numpy as np

# a module simulate wind turbine
# the model is based on modelica windPowerPlant (Eberhart [2015])
class wind_Turbine:
    # parameters describing a wind turbine
    def __init__(self,d_wing,P_lim):
        self.d_wing = d_wing   # diameter of the turbine
        self.P_lim  = P_lim    # output power limit of the wind turbine, in W (usually the limit is about 2 MW, normaly between 0.5 to 3.6 MW)
        self.coeffs = []        # coefficients for wind turbine
        self.P0 = 0.0          # the harvest power of wind turbine    


    # wind energy at current moment
    def P_wind(self, v_wind, dens_air): # v_wind is the velocity of the wind at the moment, dens_air is the density of air
        pi = 3.141592653 # pi constant
        
        Pw = 1./2. * dens_air * pi*self.d_wing**2/4. * v_wind**3

        return Pw

    def P_harvest(self,Pw):        # calculate the harvest wind energy of a wind turbine
        P = Pw * self.cp           # harvest power is the product of wind power and wind turbine efficiency 

        self.P0 = self.P0 + P
    
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
        
    # pre-defined wind turbine coefficients with Herier (Herier [2009])
    def c_Herier(self):
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

    # pre-defined wind turbine coefficients with Thongam el al (Thongam el al [2009])
    def c_Thongam(self):
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

    # user definedwind turbine coefficients
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
