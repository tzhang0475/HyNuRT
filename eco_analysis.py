#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# File              : eco_analysis.py
# Author            : tzhang
# Date              : 26.11.2019
# Last Modified Date: 05.12.2019
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
from prepost_process import *




"""

economical analysis of SMR

REFERENCES:
    - Geoffrey A. Black, Fatih Aydogan, Cassandra L. Koerner,Economic viability of light water small modular nuclear reactors: General methodology and vendor data,Renewable and Sustainable Energy Reviews,Volume 103,2019,Pages 248-258,ISSN 1364-0321, doi:10.1016/j.rser.2018.12.041.
    - NEA/OEC, Current Status, Technical Feasibility and Economics of Small Nuclear Reactors, NEA/OECD, 2011.
    - Boldon, Lauren M., and Sabharwall, Piyush. Small modular reactor: First-of-a-Kind (FOAK) and Nth-of-a-Kind (NOAK) Economic Analysis. United States: N. p., 2014. Web. doi:10.2172/1167545
    - Locatelli, G , Pecoraro, M, Meroni, G et al. (1 more author) (2017) Appraisal of small modular nuclear reactors with ‘real options’ valuation. Proceedings of the Institution of Civil Engineers - Energy, 170 (2). 1600004. pp. 51-66. ISSN 1751-4223
    - Piyush Sabharwall, Shannon Bragg-Sitton, Lauren Boldon, Seth Blumsack, Nuclear Renewable Energy Integration: An Economic Case Study, The Electricity Journal, Volume 28, Issue 8, 2015, Pages 85-95, ISSN 1040-6190, doi:10.1016/j.tej.2015.09.003.
"""

class SMR_eco:

    def __init__(self,P_unit,n_unit,year,lifetime,FOAK = True):
        self.P_unit = P_unit        # power of one SMR module
        self.n_unit = n_unit        # number of units in one nuclear power plant
        self.year = year            # use currency in which year
        self.lifetime = lifetime    # life time of a unit

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
        self.idc = 0.0
        # O&M cost per unit per year
        self.om_unit_year = 0.0
        # fuel cost per unit per year
        self.fuel_unit_year = 0.0
        # decommissioning cost per unit per year
        self.dcms_unit_year = 0.0

        # smr cash flow
        self.cashflow = []
        # smr LCOE
        self.LCOE = 0.0
        # smr NPV
        self.NPV = 0.0
        # smr IRR
        self.IRR = 0.0

    # calculate the net cash flow of from 0 to nth year
    def cal_NCF(self,y_unit_construct,price_e,f_utilization):

        cashflow = []

        # calculate duration for construction
        y_construction = y_unit_construct * self.n_unit

        # calculate investment per year
        occ_year = self.occ/y_construction

        # calculate averaged interest per year
        idc_year = self.idc/y_construction

        # calculate hours per year, ignore leap year
        hours = 365*24

        for i in range(self.lifetime+int(y_construction/2)):
            # the very beginning of the project
            if i == 0:
                cashflow.append(0.0)
            elif i > 0 and i <= y_construction:
                unit_done = int((i-1)/y_unit_construct)

                cost_year = occ_year + (self.om_unit_year+self.fuel_unit_year+self.dcms_unit_year)*unit_done + idc_year
                production_year = ((self.P_unit*unit_done*hours*f_utilization) * price_e)

                cashflow_year = (cashflow[-1]*1e6 + production_year - cost_year)/1e6        # convert to million dollar 

                cashflow.append(cashflow_year)

            else:
                cost_year = ((self.om_unit_year+self.fuel_unit_year+self.dcms_unit_year)*self.n_unit)#*(1+r_discount)**i 
                production_year = ((self.P_unit*self.n_unit*hours*f_utilization) * price_e)#*(1+r_discount)**i

                cashflow_year = (cashflow[-1]*1e6 + production_year - cost_year)/1e6        # convert to million dollar 

                cashflow.append(cashflow_year)


        self.cashflow = self.cashflow + cashflow

    # calculate the levelized cost of electricity used
    def cal_LCOE(self,r_discount,y_unit_construct,price_e,f_utilization):

        # calculate duration for construction
        y_construction = y_unit_construct * self.n_unit

        # calculate investment per year
        occ_year = self.occ/y_construction

        # calculate hours per year, ignore leap year
        hours = 365*24

        for i in range(self.lifetime + int(y_construction/2)):
            # the very beginning of the project
            if i == 0:
                cost = 0.0
                production = 0.0

            elif i > 0 and i <= y_construction:
                unit_done = int((i-1)/y_unit_construct)

                cost_year = (occ_year + (self.om_unit_year+self.fuel_unit_year+self.dcms_unit_year)*unit_done)/(1+r_discount)**i 
                production_year = (self.P_unit*unit_done*hours*f_utilization)/(1+r_discount)**i

                cost = cost + cost_year
                production = production + production_year


            else:
                cost_year = ((self.om_unit_year+self.fuel_unit_year+self.dcms_unit_year)*self.n_unit)/(1+r_discount)**i 
                production_year = (self.P_unit*self.n_unit*hours*f_utilization)/(1+r_discount)**i

                cost = cost + cost_year
                production = production + production_year

        LCOE = cost/production  # unit in $/MWh


        print ('smr levelized cost of electricity: ',LCOE, ' $/MWh')

        self.LCOE = self.LCOE + LCOE

    # calculate Net Present Value (NPV)
    def cal_NPV(self,r_discount,r_inflation):

        # calculate the real rate of interest
        r_interest = r_discount + r_inflation

        # calculate duration for construction
        y_construction = y_unit_construct * self.n_unit

        NPV = 0

        for i in range(self.lifetime+int(y_construction/2)):
            NPV_curr = self.cashflow[i]/(1+r_interest)**i

            NPV = NPV + NPV_curr

        self.NPV = self.NPV + NPV
    
    # calculate Internal Rate of Return (IRR)
    def cal_IRR(self,r_discount,r_inflation):

        # calculate duration for construction
        y_construction = y_unit_construct * self.n_unit

        # initial guess of IRR
        IRR = r_discount + r_inflation

        NPV = self.NPV

        epsi = 1e-6

        step_size = 0.01

        n_iter = 0

        iter_max = 100

        while abs(NPV) > epsi:

            if NPV > 0:

                IRR = IRR + step_size
            else:
                IRR = IRR - step_size

            NPV_new = 0.0

            for i in range(self.lifetime+int(y_construction/2)):

                NPV_curr = self.cashflow[i]/(1+IRR)**i

                NPV_new = NPV_new + NPV_curr

            if NPV_new * NPV < 0:
                step_size = step_size/2

            NPV = NPV_new

            n_iter = n_iter + 1

            if n_iter > iter_max:
                print ('not converge')
                break

        self.IRR = self.IRR + IRR

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
    def cal_IDC(self,r_discount,y_unit_construct):
        idc = []
        
        # calculate total construction time
        y_construct = y_unit_construct * self.n_unit
        
        idc = y_construct/2 * (self.occ/y_construct * (1+r_discount)**(y_construct-1) - self.occ/y_construct)

        self.idc = self.idc + idc

    # calculate operation and maintainence cost per unit per year
    def cal_OM_unit(self,om_cost_MWh,f_utilization):
        # calculate hours per year, ignore leap year
        hours = 365*24
        # elecectricity produced per unit per year
        P_MWh = self.P_unit * hours * f_utilization 

        # calculate O&M cost per unit per year
        om_unit_year = om_cost_MWh * P_MWh

        self.om_unit_year = self.om_unit_year + om_unit_year

    # calculate fuel cost per unit per year
    def cal_fuel_unit(self,fuel_cost_MWh,f_utilization):
        # calculate hours per year, ignore leap year
        hours = 365*24
        # elecectricity produced per unit per year
        P_MWh = self.P_unit * hours * f_utilization

        # calculate O&M cost per unit per year
        fuel_unit_year = fuel_cost_MWh * P_MWh

        self.fuel_unit_year = self.fuel_unit_year + fuel_unit_year

    # calculate the decommissioning cost per unit per year
    def cal_decommissioning_unit(self,dcms_cost_MWh,f_utilization):
        # calculate hours per year, ignore leap year
        hours = 365*24
        # elecectricity produced per unit per year
        P_MWh = self.P_unit * hours * f_utilization 

        # calculate O&M cost per unit per year
        dcms_unit_year = dcms_cost_MWh * P_MWh

        self.dcms_unit_year = self.dcms_unit_year + dcms_unit_year


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
sub_sys1 = 'smr'
P_unit = 50             #electrical power in MW
n_unit = 4
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

# config learning factors
x = 0.15
y = 0.74
z = 0.82
k = 0.02

# technology learning rate
r_learning = 0.04



smr = SMR_eco(P_unit,n_unit,year,lifetime,FOAK)

ME_2_curr,ME_9_curr = smr.import_coa()

coa = coa_pwr12()
cost_kW_pwr12 = coa.aquire_cost_kW(ME_2_curr,ME_9_curr)
print ('PWR12 cost per kW: ', cost_kW_pwr12)

smr.cal_OCC(ME_2_curr,ME_9_curr,eta_direct,eta_indirect,x,y,z,k,r_learning)
print ('total cost of the NPP: ', '%.9e'%smr.occ)
print ('total cost of the NPP per kW: ', smr.occ_kW)
smr.cal_IDC(r_discount,y_unit_construct)
print ('total interest to pay: ', smr.idc)
smr.cal_OM_unit(om_cost_MWh,f_uti)
print ('O&M cost per unit per year: ',smr.om_unit_year)
smr.cal_fuel_unit(fuel_cost_MWh,f_uti)
print ('fuel cost per unit per year: ',smr.fuel_unit_year)
smr.cal_decommissioning_unit(dcms_cost_MWh,f_uti)
print ('decommissioning cost per unit per year: ',smr.dcms_unit_year)

smr.cal_NCF(y_unit_construct,price_e,f_uti)
cashflow = smr.cashflow

smr.cal_LCOE(r_discount,y_unit_construct,price_e,f_uti)
print ('smr levelized cost of electricity: ',smr.LCOE, ' $/MWh')

y_tot = lifetime+int((y_unit_construct*n_unit)/2)
post_process.plt_cashflow(y_tot,cashflow,sub_sys1)

smr.cal_NPV(r_discount,r_inflation)
print ('SMR net present value: ', smr.NPV, 'million $')
smr.cal_IRR(r_discount,r_inflation)
print ('SMR internal rate of return: ', smr.IRR)

print ('\n')


"""

economical analysis of the wind farm

"""

class wind_eco:
    def __init__(self,P_lim,n_unit,lifetime):
        self.P_lim = P_lim
        self.n_unit = n_unit
        self.lifetime = lifetime

        # overnight capital cost of the wind farm
        self.occ = 0.0

        # O&M cost per unit per year
        self.om_unit_year = 0.0

        # decommissioning cost per unit per year
        self.dcms_unit_year = 0.0

        # wind farm cash flow
        self.cashflow = []
        # wind farm LCOE
        self.LCOE = 0.0
        # wind farm NPV
        self.NPV = 0.0
        # wind farm IRR
        self.IRR = 0.0


    # calculate the net cash flow of from 0 to nth year
    def cal_NCF(self,price_e,f_inter):

        cashflow = []

        # calculate hours per year, ignore leap year
        hours = 365*24

        for i in range(self.lifetime+1):
            # the very beginning of the project
            if i == 0:
                cashflow.append(0.0)
            elif i == 1:
                cost_year = self.occ
                production_year = 0.0

                cashflow_year = (cashflow[-1]*1e6 + production_year - cost_year)/1e6        # convert to million dollar 

                cashflow.append(cashflow_year)

            else:
                cost_year = ((self.om_unit_year+self.dcms_unit_year)*self.n_unit)
                production_year = ((self.P_lim*self.n_unit*hours*f_inter) * price_e)

                cashflow_year = (cashflow[-1]*1e6 + production_year - cost_year)/1e6        # convert to million dollar 

                cashflow.append(cashflow_year)


        self.cashflow = self.cashflow + cashflow
    
    # calculate the levelized cost of electricity used
    def cal_LCOE(self,r_discount,price_e,f_inter):

        # calculate hours per year, ignore leap year
        hours = 365*24

        for i in range(self.lifetime+1):
            # the very beginning of the project
            if i == 0:
                cost = 0.0
                production = 0.0

            elif i == 1:

                cost_year = self.occ/(1+r_discount)**i 
                production_year = 0.0

                cost = cost + cost_year
                production = production + production_year


            else:
                cost_year = ((self.om_unit_year+self.dcms_unit_year)*self.n_unit)/(1+r_discount)**i 
                production_year = (self.P_lim*self.n_unit*hours*f_inter)/(1+r_discount)**i

                cost = cost + cost_year
                production = production + production_year

        LCOE = cost/production  # unit in $/MWh
        
        self.LCOE = self.LCOE + LCOE

    # calculate Net Present Value (NPV)
    def cal_NPV(self,r_discount,r_inflation):

        # calculate the real rate of interest
        r_interest = r_discount + r_inflation

        NPV = 0

        for i in range(self.lifetime+1):
            NPV_curr = self.cashflow[i]/(1+r_interest)**i

            NPV = NPV + NPV_curr

        self.NPV = self.NPV + NPV
    
    # calculate Internal Rate of Return (IRR)
    def cal_IRR(self,r_discount,r_inflation):

        # initial guess of IRR
        IRR = r_discount + r_inflation

        NPV = self.NPV

        epsi = 1e-6

        step_size = 0.01

        n_iter = 0

        iter_max = 100

        while abs(NPV) > epsi:

            if NPV > 0:

                IRR = IRR + step_size
            else:
                IRR = IRR - step_size

            NPV_new = 0.0

            for i in range(self.lifetime+1):

                NPV_curr = self.cashflow[i]/(1+IRR)**i

                NPV_new = NPV_new + NPV_curr

            if NPV_new * NPV < 0:
                step_size = step_size/2

            NPV = NPV_new

            n_iter = n_iter + 1

            if n_iter > iter_max:
                print ('not converge')
                break

        self.IRR = self.IRR + IRR



    # calculate the overnight capital cost of the wind farm
    def cal_OCC(self,cost_kW):
        
        # capital cost of a wind turbine
        cost_unit = cost_kW * self.P_lim * 1000
        # capical cost of the wind farm
        occ = cost_unit * self.n_unit

        self.occ = self.occ + occ

    # calculate the o&m cost per year
    def cal_OM_unit(self,om_cost_MWh,f_inter):
        # calculate hours per year, ignore leap year
        hours = 365*24
        # elecectricity produced per unit per year
        P_MWh = self.P_lim * hours * f_inter 

        # calculate O&M cost per unit per year
        om_unit_year = om_cost_MWh * P_MWh

        self.om_unit_year = self.om_unit_year + om_unit_year

    # calculate the decommissioning cost per unit per year
    def cal_decommissioning_unit(self,dcms_cost_MWh,f_inter):
        # calculate hours per year, ignore leap year
        hours = 365*24
        # elecectricity produced per unit per year
        P_MWh = self.P_lim * hours * f_inter

        # calculate O&M cost per unit per year
        dcms_unit_year = dcms_cost_MWh * P_MWh

        self.dcms_unit_year = self.dcms_unit_year + dcms_unit_year




"""

a test class for wind_eco

"""
sub_sys2 = 'windfarm'
P_lim = 2           # in MW
w_n_unit = 40   
w_lifetime = 30     # 30 years life time
loc_type = 1        # 1 for land wind farm, 0 for off-shore wind farm

# discount rate 
r_discount = 0.05
# inflation rate
r_inflation = 0.03

# electricty price per MWh
price_e = 130

# captical cost of a wind turbine per kW
cost_kW = 1590      # $ per kW 

# om cost of a wind turbine per MWh
w_om_cost_MWh = 14.4

# decommissioning cost of a wind turbine per MWh
w_dcms_cost_MWh = 4.0

# wind farm intermittence factor
f_inter = 0.3


wfarm = wind_eco(P_lim,w_n_unit,w_lifetime)
wfarm.cal_OCC(cost_kW)
print ('total wind farm capital cost: ', wfarm.occ)
wfarm.cal_OM_unit(w_om_cost_MWh,f_inter)
print ('om cost of per turbine per year: ', wfarm.om_unit_year)
wfarm.cal_decommissioning_unit(dcms_cost_MWh,f_inter)
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

economical analysis of the hydrogen cluster

"""

