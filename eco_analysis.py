#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# File              : eco_analysis.py
# Author            : tzhang
# Date              : 26.11.2019
# Last Modified Date: 02.12.2019
# Last Modified By  : tzhang

import sys
import numpy as np
import math

# use a tool to calculation inflation, written by 'Los Angeles Times Data and Graphics Department', the project is on GitHub, details see: https://github.com/datadesk/cpi
# but this module is quite slow
# later a new model can be developed
import cpi

"""

economical analysis of the system

"""





"""

economical analysis of SMR

REFERENCES:
    - Geoffrey A. Black, Fatih Aydogan, Cassandra L. Koerner,Economic viability of light water small modular nuclear reactors: General methodology and vendor data,Renewable and Sustainable Energy Reviews,Volume 103,2019,Pages 248-258,ISSN 1364-0321, doi:10.1016/j.rser.2018.12.041.
    - NEA/OEC, Current Status, Technical Feasibility and Economics of Small Nuclear Reactors, NEA/OECD, 2011.
    - Boldon, Lauren M., and Sabharwall, Piyush. Small modular reactor: First-of-a-Kind (FOAK) and Nth-of-a-Kind (NOAK) Economic Analysis. United States: N. p., 2014. Web. doi:10.2172/1167545

"""
class SMR_eco:
    def __init__(self,P_unit,n_unit,year,lifetime,FOAK = True):
        self.P_unit = P_unit        # power of one SMR module
        self.n_unit = n_unit        # number of units in one nuclear power plant
        self.year = year            # use currency in which year

        self.P_pwr12 = 1147         #in MW, the electrical power output of PWR12

        # whether the site include first of a kind (FOAK), default FALSE
        if FOAK == 1:
            self.FOAK = True
        else:
            self.FOAK = False

        # unit cost data
        self.unit_direct_cost = []
        self.unit_direct_cost_tot  = 0.0

        self.unit_indirect_cost = []
        self.unit_indirect_cost_tot  = 0.0

        self.unit_cost_tot = 0.0
        self.unit_cost_kW = 0.0

        # npp cost data
        self.occ = 0.0
        self.occ_kW = 0.0

        # interest during construction
        self.idc = []
        # O&M cost per unit per year
        self.om_unit_year = 0

    # calculate the overnight calpatical cost
    def cal_OCC(self,ME_2_curr,ME_9_curr,eta_direct,eta_indirect,x,y,z,k,r_learning): 

        SMR_eco.unit_direct_cost_coa(self,ME_2_curr,eta_direct)
        SMR_eco.unit_indirect_cost_coa(self,ME_9_curr,eta_indirect)
        SMR_eco.cal_unit_cost_tot(self)
#        print ('total cost of a unit: ', self.unit_cost_tot)
        SMR_eco.cal_unit_cost_kW(self)
#        cost_ratio = SMR_eco.cost_kW/cost_kW_pwr12
#        print ('original cost ratio: ',cost_ratio)
        f_cosite = SMR_eco.cosite_factor(self)
#        print ('co_site factor is: ', f_cosite)
        f_modular = SMR_eco.iPWR_factor(self)
#        print ('modular factor: ', f_modular)
        f_config_learning = SMR_eco.config_learning_factor(self,x,y,z,k)
#        print ('config learning rate: ', f_config_learning)
        f_tech_learning = SMR_eco.tech_learning_factor(self,x,r_learning)
#        print ('technology learning rate: ', f_tech_learning)

        occ = self.unit_cost_tot*self.n_unit * f_cosite * f_modular * f_config_learning * f_tech_learning
#        print ('total cost of the NPP: ', occ)
        occ_kW = occ/(self.P_unit*self.n_unit*1000)
#        print ('SMR cost of the NPP per kW: ', occ_kW)

        self.occ = self.occ + occ
        self.occ_kW = self.occ_kW + occ_kW

    # calculate interest during construction (IDC)
    def cal_IDC(self,r_interest,y_construct):
        idc = []

        for i in range(y_construct):
            n = i + 1
            idc_curr = n/2 * (self.occ/n * (1+r_interest)**(n-1) - self.occ/n)
            idc.append(idc_curr)
        
        self.idc = self.idc + idc

    # calculate operation and maintainence cost per unit per year
    def cal_OM_unit(self,om_cost_kWh):
        # calculate hours per year, ignore leap year
        hours = 365*24
        # elecectricity produced per unit per year
        P_kWh = self.P_unit * hours

        # calculate O&M cost per unit per year
        om_unit_year = om_cost_kWh * P_kWh

        self.om_unit_year = self.om_unit_year + om_unit_year

    # calculate co-site factor 
    def cosite_factor(self):
        # calculat the ratio of direct cost and indirect cost in tot cost
        f_ind = self.unit_indirect_cost_tot/self.unit_cost_tot
        f_dir = self.unit_direct_cost_tot/self.unit_cost_tot

        n_unit = float(self.n_unit)

        f_cosite = (1 + (self.n_unit-1)*(1-f_ind))/self.n_unit

        return f_cosite

    # cacluate learning reduction factor by plant configuration
    # - x: FOAK extra cost parameter, range 15%-55%
    # - y: parameter related to the gain in building a pair of units, range 74%-85%
    # - z: parameter related to the gain in building two pairs of units on the same site, 82%-95%
    # - k: industrial productivity coefficient, 0%-2%
    def config_learning_factor(self,x,y,z,k):

        # the cost of 1st unit according to whether it is FOAK
        if self.FOAK:
            f_ini = 1.+x
        else:
            f_ini = 1.0
        
        # total cost of the 1st unit 
        if self.n_unit == 1:
            f_curr = f_ini

        # total cost of more than one unit
        elif self.n_unit > 1:
            f_curr = f_ini
            for i in range(2,self.n_unit+1):
                if i%2 == 0:
                    f_curr = f_curr + y/(1+k)**(i-2)
                else:
                    f_curr = f_curr + z/(1+k)**(i-2)
    
        f_config_learning = f_curr/self.n_unit

        return f_config_learning

    # calculate the learning rate by technology improvement
    # the learning rate is nomally a value between 1% to 6%
    # according to historical data, between 3% to 4.5%
    def tech_learning_factor(self,x,rate):
        # calculate FOAK extra cost fact
        f_cost_FOAK = (1+x)#*self.unit_cost_tot

        # calculate the NPP power output
        P_npp = self.P_unit * self.n_unit

        # calculate the exponential term
        b = -math.log10(1-rate)/math.log10(2)
   
        f_tech_learning = f_cost_FOAK * P_npp**(-b)

        return f_tech_learning



    # define iPWR design simplification factor
    def iPWR_factor(self):
        if self.P_unit <= 35.:
            f_modular = 0.6
        elif self.P_unit > 35. and self.P_unit < 600.:
            f_modular = 4e-10*(self.P_unit)**3 - 1e-6*(self.P_unit)**2 + 0.0012*self.P_unit + 0.581
        else:
            f_modular = 1.0

        return f_modular


    # estimate the direct cost by the method of coa with existing PWR-12 data, use two digits value to evaluate
    def unit_direct_cost_coa(self,ME_2_curr,eta_direct):
        unit_direct_cost = []

        # total direct cost
        unit_direct_cost_tot = 0

        # calculate scale factor
        f_scale = (self.P_unit/self.P_pwr12)**eta_direct
        
        # calculate tow digits new cost
        for i in range(len(ME_2_curr)):
            data = []
            data.append(ME_2_curr[i][0])

            cost_new = float(ME_2_curr[i][1]) * f_scale

            data.append('%.0f'%cost_new)
            unit_direct_cost.append(data)
            unit_direct_cost_tot = unit_direct_cost_tot + cost_new
       
#        print (unit_direct_cost)
#        print ('%.0f'%unit_direct_cost_tot)
        
        self.unit_direct_cost = self.unit_direct_cost + unit_direct_cost
        self.unit_direct_cost_tot = self.unit_direct_cost_tot + unit_direct_cost_tot

    # estimate the indirect cost by the method of coa with existing PWR-12 data, use two digits value to evaluate
    def unit_indirect_cost_coa(self,ME_9_curr,eta_indirect):
        unit_indirect_cost = []

        # total direct cost
        unit_indirect_cost_tot = 0

        # calculate scale factor
        f_scale = (self.P_unit/self.P_pwr12)**eta_indirect
        
        # calculate tow digits new cost
        for i in range(len(ME_9_curr)):
            data = []
            data.append(ME_9_curr[i][0])

            cost_new = float(ME_9_curr[i][1]) * f_scale

            data.append('%.0f'%cost_new)
            unit_indirect_cost.append(data)
            unit_indirect_cost_tot = unit_indirect_cost_tot + cost_new
       
#        print (unit_indirect_cost)
#        print ('%.0f'%unit_indirect_cost_tot)
        
        self.unit_indirect_cost = self.unit_indirect_cost + unit_indirect_cost
        self.unit_indirect_cost_tot = self.unit_indirect_cost_tot + unit_indirect_cost_tot

    # calculate SMR total cost         
    def cal_unit_cost_tot(self):

        unit_cost_tot = self.unit_direct_cost_tot + self.unit_indirect_cost_tot
#        print ('total cost',unit_cost_tot)
    
        self.unit_cost_tot = self.unit_cost_tot + unit_cost_tot

    # calculate SMR total cost per kW        
    def cal_unit_cost_kW(self):

        self.unit_cost_kW = self.unit_cost_kW +  self.unit_cost_tot/(self.P_unit*1000)

    # import the coa data for PWR12
    def import_coa(self):
        coa = coa_pwr12()
        direct_cost_dd = coa.aquire_2_dd()
        direct_cost_dd_curr = coa.inflation(direct_cost_dd,self.year)
        indirect_cost_dd = coa.aquire_9_dd()
        indirect_cost_dd_curr = coa.inflation(indirect_cost_dd,self.year)

        # convert direct and indirect cost madien experiences to current current currency
        ME_2_curr = coa.aquire_code_ME(direct_cost_dd_curr)
        ME_9_curr = coa.aquire_code_ME(indirect_cost_dd_curr)

        return ME_2_curr,ME_9_curr



"""

the Code of Account (COA) of DOE Energy Economic Data Base (EEDB), the data of PWR 12, for Capitalized Direct Costs (2*), and Indirect Cost (9*)

REFERENCES:
    - Generation IV International Forum, Economic Modeling Working Group; 2007. Holcomb D, Peretz F, Qualls A. Advanced High Temperature Reactor Systems and Economic Analysis, Rev 0.ORNL/TM-2011/364 September 2011. Oak Ridge National Laboratory; 2011.


"""
class coa_pwr12:
    def __init__(self):
        self.pwr12_data = [
                ['21','Structures and improvements subtotal',200744098,303499834,198110031],
                ['211','Yardwork',24992519,32518044,25641072],
                ['212','Reactor containment building',64836041,100710559,62341201],
                ['213','Turbine room and heater bay',23152330,37872452,24016964],
                ['214','Security building',1361955,1914689,1312224],
                ['215','Primary auxiliary building and tunnels',18472145,27163800,19114786],
                ['216','Waste processing building',14367318,22378826,13883581],
                ['217','Fuel storage building',9879103,13030890,9603975],
                ['218','Other structures',43682687,67910574,42196228],
                ['22','Reactor plant equipment',303048181,370640594,290413681],
                ['220A','Nuclear steam supply (NSSS)',179340000,179340000,173959800],
                ['221','Reactor equipment',10516879,11191741,10304492],
                ['222','Main heat transfer transport system',9898419,20509935,9526332],
                ['223','Safeguards system',12416260,24389226,11541651],
                ['224','Radwaste processing',20942407,30865919,19885175],
                ['225','Fuel handling and storage',3167160,4248375,3103137],
                ['226','Other reactor plant equipment',37759511,67363994,33544955],
                ['227','Reactor instrumentation and control',21555270,23607427,21329518],
                ['228','Reactor plant miscellaneous items',7452275,9123977,7218621],
                ['23','Turbine plant equipment',223778366,266443824,209610905],
                ['231','Turbine generator',133984273,137755009,131357864],
                ['233','Condensing systems',28981986,38244984,25749941],
                ['234','Feedwater heating system',23588801,32713168,19800879],
                ['235','Other turbine plant equipment',22323194,40286456,18690726],
                ['236','Instrumentation and control',6854212,7980222,6216009],
                ['237','Turbine plant miscellaneous items',8045900,9463985,7795486],
                ['24','Electric plant equipment',81322724,119236515,62241755],
                ['241','Switchgear',11946283,11946368,11225531],
                ['242','Station service equipment',20163388,20318526,19039791],
                ['243','Switchboards',2048898,2091797,1858720],
                ['244','Protective equipment',4261386,4975308,4308153],
                ['245','Electric structure and wiring contnr.',22301683,46674779,12419117],
                ['246','Power and control wiring',20601086,33229737,13390443],
                ['25','Miscellaneous plant equipment subtotal',46701898,70656254,44618307],
                ['251','Transportation and lifting equipment',5993830,6360616,6607780],
                ['252','Air, water and steam service systems',28725654,51096666,26656904],
                ['253','Communications equipment',6415046,7272235,6139079],
                ['254','Furnishings and fixtures',2735984,2901892,2637261],
                ['255','Waste water treatment equipment',2831384,3024845,2577283],
                ['26','Main condenser heat rejection system',48980965,56612488,47841279],
                ['261','Structures',4332720,5726470,4197560],
                ['262','Mechanical equipment',44648245,50886018,43643719],
                ['91','Construction services',226915000,411147000,185639000],
                ['92','Engineering and home office services',212742000,487254000,90716000],
                ['93','Field supervision and field office services',111400000,443845000,79262000],
                ]
        self.data_year = 1987


    # aquire two digits capitialize direct cost
    def aquire_2_dd(self):
        direct_cost_dd = []

        for data in self.pwr12_data:
            if len(data[0]) == 2 and data[0][0] == '2':
                direct_cost_dd.append(data)
                

        return direct_cost_dd


    # aquire two digits capitialize indirect cost
    def aquire_9_dd(self):
        indirect_cost_dd = []

        for data in self.pwr12_data:
            if len(data[0]) == 2 and data[0][0] == '2':
                indirect_cost_dd.append(data)

        return indirect_cost_dd

    # aquire three digits capitialize direct cost
    def aquire_2_ddd(self):
        direct_cost_ddd = []

        for data in self.pwr12_data:
            if len(data[0]) >= 3 and data[0][0] == '2':
                direct_cost_ddd.append(data)

        return direct_cost_ddd

    # aquire three digits capitialize Structures and improvements subtotal (code 21)
    def aquire_ddd_21(self):
        ddd_21 = []

        for data in self.pwr12_data:
            if len(data[0]) == 3 and data[0][0] == '2' and data[0][1] == '1':
                ddd_21.append(data)
                
        return ddd_21

    # aquire three digits capitialize Reactor plant equipment (code 22)
    def aquire_ddd_22(self):
        ddd_22 = []

        for data in self.pwr12_data:
            if len(data[0]) >= 3 and data[0][0] == '2' and data[0][1] == '2':
                ddd_22.append(data)
                
        return ddd_22

    # aquire three digits capitialize Turbine plant equipment (code 23)
    def aquire_ddd_23(self):
        ddd_23 = []

        for data in self.pwr12_data:
            if len(data[0]) == 3 and data[0][0] == '2' and data[0][1] == '3':
                ddd_23.append(data)
                
        return ddd_23

    # aquire three digits capitialize Electric plant equipment (code 24)
    def aquire_ddd_24(self):
        ddd_24 = []

        for data in self.pwr12_data:
            if len(data[0]) == 3 and data[0][0] == '2' and data[0][1] == '4':
                ddd_24.append(data)
                
        return ddd_24

    # aquire three digits capitialize Miscellaneous plant equipment subtotal (code 25)
    def aquire_ddd_25(self):
        ddd_25 = []

        for data in self.pwr12_data:
            if len(data[0]) == 3 and data[0][0] == '2' and data[0][1] == '5':
                ddd_25.append(data)
                

        return ddd_25

    # aquire three digits capitialize Main condenser heat rejection system (code 26)
    def aquire_ddd_26(self):
        ddd_26 = []

        for data in self.pwr12_data:
            if len(data[0]) == 3 and data[0][0] == '2' and data[0][1] == '6':
                ddd_26.append(data)
                

        return ddd_26

    # aquire account code and account description
    def aquire_code_description(self,array):

        array = np.asarray(array)
        code_and_description = array[:,:2]


        return code_and_description

    # aquire account code and account median experience (ME)
    def aquire_code_ME(self,array):

        array = np.asarray(array)
        code_ME = array[:,[0,3]]


        return code_ME

    # aquire account code and account better experience (BE)
    def aquire_code_BE(self,array):

        array = np.asarray(array)
        code_BE = array[:,[0,2]]


        return code_BE

    # aquire account code and account improved total cost
    def aquire_code_improved(self,array):

        array = np.asarray(array)
        code_improved = array[:,[0,4]]


        return code_improved

    # update the inflation according to year, use the cpi module (one can use other methods to convert dollars)
    def inflation(self,array,year):       # year is the target year to convert to
        array_new = []
        for data in array:
            data_new = []
            data_new.append(data[0])
            data_new.append(data[1])
            BE_new = cpi.inflate(data[2],self.data_year,to = year)
            ME_new = cpi.inflate(data[3],self.data_year,to = year)
            improved_new = cpi.inflate(data[4],self.data_year,to = year)

            data_new.append(BE_new)
            data_new.append(ME_new)
            data_new.append(improved_new)

            array_new.append(data_new)


        return array_new

    # calculate PWR 12 cost per MW
    def aquire_cost_kW(self,data_direct,data_indirect):
        P_pwr12 = 1147          # electrical power of pwr 12, in MW

        data_direct = np.asarray(data_direct)
        data_indirect = np.asarray(data_indirect)
        
        data_direct = data_direct[:,1]
        data_indirect = data_indirect[:,1]

        data_direct = np.asarray(data_direct,dtype = float)
        data_indirect = np.asarray(data_indirect,dtype = float)

        cost_direct_tot = sum(data_direct)
        cost_indirect_tot = sum(data_indirect)

        cost_tot = cost_direct_tot + cost_indirect_tot

        cost_kW = cost_tot/(P_pwr12*1000)       # dollar per kW

        return cost_kW

"""

a test class for coa_pwr12

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

"""

a test class for SMR_eco

"""
P_unit = 50             #electrical power in MW
n_unit = 3
year = 2018
FOAK = 1
lifetime = 60           # life time the npp

eta_direct = 0.51              # oecd nea value, large uncentainty
eta_indirect = 0.51              # oecd nea value, large uncentainty

# config learning factors
x = 0.15
y = 0.74
z = 0.82
k = 0.02

# technology learning rate
r_learning = 0.03

# interest rate 
r_interest = 0.05

# construction time, in year
y_construct = 6

# operation and maintainess cost, dollar per kWh 
om_cost_kWh = 33.5  

smr = SMR_eco(P_unit,n_unit,year,lifetime,FOAK)

ME_2_curr,ME_9_curr = smr.import_coa()

coa = coa_pwr12()
cost_kW_pwr12 = coa.aquire_cost_kW(ME_2_curr,ME_9_curr)
print ('PWR12 cost per kW: ', cost_kW_pwr12)

smr.cal_OCC(ME_2_curr,ME_9_curr,eta_direct,eta_indirect,x,y,z,k,r_learning)
print ('total cost of the NPP: ', '%.9e'%smr.occ)
#smr.cal_IDC(r_interest,y_construct)
#print (smr.idc)
smr.cal_OM_unit(om_cost_kWh)
print ('O&M cost per unit per year: ',smr.om_unit_year)
