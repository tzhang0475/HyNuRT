#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# File              : eco_analysis.py
# Author            : tzhang
# Date              : 26.11.2019
# Last Modified Date: 28.09.2020
# Last Modified By  : tzhang

import sys
import numpy as np
import math
import importlib.util


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

class nuclear_eco:

    def __init__(self,P_unit,n_unit,year,lifetime,y_unit_construct,FOAK = True):
        self.P_unit = P_unit        # power of one SMR module
        self.n_unit = n_unit        # number of units in one nuclear power plant
        self.year = year            # use currency in which year
        self.lifetime = lifetime    # life time of a unit
        self.y_unit_construct = y_unit_construct    # years needed to construct a unit
       
        y_construction = y_unit_construct * n_unit
        self.y_construction = y_construction    # years needed to construct a unit

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

    # calculate the net cost of from 0 to nth year
    def cal_cost(self):

        cost = []

        # calculate investment per year
        occ_year = self.occ/self.y_construction

        # calculate averaged interest per year
        idc_year = self.idc/self.y_construction

        # calculate hours per year, ignore leap year
        hours = 365*24

        for i in range(self.lifetime+int(self.y_construction/2)):
            # the very beginning of the project
            if i == 0:
                cost.append(0.0)
            elif i > 0 and i <= self.y_construction:
                unit_done = int((i-1)/self.y_unit_construct)

                cost_year = occ_year + (self.om_unit_year+self.fuel_unit_year+self.dcms_unit_year)*unit_done + idc_year

                cost_year = cost_year/1e6        # convert to million dollar 

                cost.append(cost_year)

            else:
                cost_year = ((self.om_unit_year+self.fuel_unit_year+self.dcms_unit_year)*self.n_unit)#*(1+r_discount)**i 

                cost_year = cost_year/1e6        # convert to million dollar 

                cost.append(cost_year)

        return cost

    def cal_cost_year(self,unit_done,year):

        # calculate investment per year
        occ_year = self.occ/self.y_construction

        # calculate averaged interest per year
        idc_year = self.idc/self.y_construction

        # calculate hours per year, ignore leap year
        hours = 365*24

        # the very beginning of the project
        if year == 0:
            cost_year = 0.0
        elif year > 0 and year <= self.y_construction:
    
            cost_year = occ_year + (self.om_unit_year+self.fuel_unit_year+self.dcms_unit_year)*unit_done + idc_year
    
            cost_year = cost_year/1e6        # convert to million dollar 
    
        else:
            cost_year = ((self.om_unit_year+self.fuel_unit_year+self.dcms_unit_year)*self.n_unit)#*(1+r_discount)**i 
    
            cost_year = cost_year/1e6        # convert to million dollar 

        return cost_year

    # calculate the net cash flow of from 0 to nth year
    def cal_NCF(self,price_e,f_utilization):

        cashflow = []

        # calculate investment per year
        occ_year = self.occ/self.y_construction

        # calculate averaged interest per year
        idc_year = self.idc/self.y_construction

        # calculate hours per year, ignore leap year
        hours = 365*24

        for i in range(self.lifetime+int(self.y_construction/2)):
            # the very beginning of the project
            if i == 0:
                cashflow.append(0.0)
            elif i > 0 and i <= self.y_construction:
                unit_done = int((i-1)/self.y_unit_construct)

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
    def cal_LCOE(self,r_discount,price_e,f_utilization):

        # calculate investment per year
        occ_year = self.occ/self.y_construction

        # calculate hours per year, ignore leap year
        hours = 365*24

        for i in range(self.lifetime + int(self.y_construction/2)):
            # the very beginning of the project
            if i == 0:
                cost = 0.0
                production = 0.0

            elif i > 0 and i <= self.y_construction:
                unit_done = int((i-1)/self.y_unit_construct)

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


        #print ('smr levelized cost of electricity: ',LCOE, ' $/MWh')

        self.LCOE = self.LCOE + LCOE

    # calculate Net Present Value (NPV)
    def cal_NPV(self,r_discount):

        # calculate the real rate of interest
        r_interest = r_discount


        NPV = 0

        for i in range(self.lifetime+int(self.y_construction/2)):
            NPV_curr = self.cashflow[i]/(1+r_interest)**i

            NPV = NPV + NPV_curr

        self.NPV = self.NPV + NPV
    
    # calculate Internal Rate of Return (IRR)
    def cal_IRR(self,r_discount):


        # initial guess of IRR
        IRR = r_discount

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

            for i in range(self.lifetime+int(self.y_construction/2)):

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

        self.unit_direct_cost_coa(ME_2_curr,eta_direct)
        self.unit_indirect_cost_coa(ME_9_curr,eta_indirect)
        self.cal_unit_cost_tot()
#        print ('total cost of a unit: ', self.unit_cost_tot)
        self.cal_unit_cost_kW()
#        cost_ratio = SMR_eco.cost_kW/cost_kW_pwr12
#        print ('original cost ratio: ',cost_ratio)
        f_cosite = self.cosite_factor()
#        print ('co_site factor is: ', f_cosite)
        f_modular = self.iPWR_factor()
#        print ('modular factor: ', f_modular)
        f_config_learning = self.config_learning_factor(x,y,z,k)
#        print ('config learning rate: ', f_config_learning)

        if self.FOAK and self.n_unit > 1: 
            f_tech_learning = 1.0
        elif not self.FOAK and self.n_unit>1:
            f_tech_learning = self.tech_learning_factor(x,r_learning)
        else:
            f_tech_learning = 1.0
#        print ('technology learning rate: ', f_tech_learning)

        occ = self.unit_cost_tot*self.n_unit * f_cosite * f_modular * f_config_learning * f_tech_learning
#        print ('total cost of the NPP: ', occ)
        occ_kW = occ/(self.P_unit*self.n_unit*1000)
#        print ('SMR cost of the NPP per kW: ', occ_kW)

        self.occ = self.occ + occ
        self.occ_kW = self.occ_kW + occ_kW

    # calculate interest during construction (IDC)
    def cal_IDC(self,r_discount):
        idc = []
        
        idc = self.y_construction/2 * (self.occ/self.y_construction * (1+r_discount)**(self.y_construction-1) - self.occ/self.y_construction)

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
#r_inflation = 0.03

# energy inflation rate
e_inflation = 0.05

# config learning factors
x = 0.15
y = 0.74
z = 0.82
k = 0.02

# technology learning rate
r_learning = 0.04



smr = nuclear_eco(P_unit,n_unit,year,lifetime,FOAK)

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

smr.cal_NCF(price_e,f_uti)
cashflow = smr.cashflow

smr.cal_LCOE(r_discount,price_e,f_uti)
print ('smr levelized cost of electricity: ',smr.LCOE, ' $/MWh')

y_tot = lifetime+int((y_unit_construct*n_unit)/2)
post_process.plt_cashflow(y_tot,cashflow,sub_sys1)

smr.cal_NPV(r_discount)
print ('SMR net present value: ', smr.NPV, 'million $')
smr.cal_IRR(r_discount)
print ('SMR internal rate of return: ', smr.IRR)

print ('\n')

"""

"""

economical analysis of the wind farm

REFERENCES:
    - Stehly, Tyler J., Heimiller, Donna M., and Scott, George N. 2016 Cost of Wind Energy Review. United States: N. p., 2017. Web. doi:10.2172/1415731.
    - Magdi Ragheb, Chapter 25 - Economics of Wind Power Generation, Editor(s): Trevor M. Letcher, Wind Energy Engineering, Academic Press,2017,Pages 537-555,ISBN 9780128094518,doi:10.1016/B978-0-12-809451-8.00025-4.
    - María Isabel Blanco,The economics of wind energy,Renewable and Sustainable Energy Reviews,Volume 13, Issues 6–7,2009,Pages 1372-1382,ISSN 1364-0321,doi:10.1016/j.rser.2008.09.004.

"""

class wind_eco:
    def __init__(self,P_lim,n_unit,lifetime,con_time):
        self.P_lim = P_lim
        self.n_unit = n_unit
        self.lifetime = lifetime
        self.con_time = con_time    # construction time, in year

        # overnight capital cost of the wind farm
        self.occ = 0.0
        self.occ_unit = 0.0

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

    # calculate year cost under different conditions
    def cal_cost_year(self,unit_op,unit_con,unit_replace):

        # calculate construction occ of this year
        cost_con = self.occ_unit * unit_con

        # calculate construction occ of this year
        cost_replace = self.occ_unit * unit_replace

        # calculate operation cost of this year
        cost_op = (self.om_unit_year+self.dcms_unit_year) * unit_op

        cost_year = (cost_con + cost_op + cost_replace)/1e6    # convert to million dollar

        return cost_year

    # calculate the cost of from 0 to nth year
    def cal_cost(self):

        cost = []

        for i in range(self.lifetime+1):
            # the very beginning of the project
            if i == 0:
                cost.append(0.0)
            elif i == 1:
                cost_year = self.occ/1e6        # convert to million dollar 
                cost.append(cost_year)
            else:
                cost_year = ((self.om_unit_year+self.dcms_unit_year)*self.n_unit)/1e6   # convert to million dollar
                cost.append(cost_year)

        return cost


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
                production_year = ((self.P_lim*self.n_unit*hours*f_inter[i]) * price_e)

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
                production_year = (self.P_lim*self.n_unit*hours*f_inter[i])/(1+r_discount)**i

                cost = cost + cost_year
                production = production + production_year

        LCOE = cost/production  # unit in $/MWh
        
        self.LCOE = self.LCOE + LCOE

    # calculate Net Present Value (NPV)
    def cal_NPV(self,r_discount):

        # calculate the real rate of interest
        r_interest = r_discount 

        NPV = 0

        for i in range(self.lifetime+1):
            NPV_curr = self.cashflow[i]/(1+r_interest)**i

            NPV = NPV + NPV_curr

        self.NPV = self.NPV + NPV
    
    # calculate Internal Rate of Return (IRR)
    def cal_IRR(self,r_discount):

        # initial guess of IRR
        IRR = r_discount

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

    # calculate the overnight capital cost of the wind turbine
    def _cal_OCC_unit_(self,cost_kW):
        
        # capital cost of a wind turbine
        occ_unit = cost_kW * self.P_lim * 1000

        return occ_unit


    # calculate the overnight capital cost of the wind farm
    def cal_OCC(self,cost_kW):
        
        # capital cost of a wind turbine
        cost_unit = cost_kW * self.P_lim * 1000
        # capical cost of the wind farm
        occ = cost_unit * self.n_unit
        
        self.occ_unit = cost_unit
        self.occ = self.occ + occ

    # calculate the o&m cost per year
    def cal_OM_unit(self,om_cost_MWh,f_inter_ave):
        # calculate hours per year, ignore leap year
        hours = 365*24
        # elecectricity produced per unit per year
        P_MWh = self.P_lim * hours * f_inter_ave 

        # calculate O&M cost per unit per year
        om_unit_year = om_cost_MWh * P_MWh

        self.om_unit_year = self.om_unit_year + om_unit_year

    # calculate the decommissioning cost per unit per year
    def cal_decommissioning_unit(self,dcms_cost_MWh,f_inter_ave):
        # calculate hours per year, ignore leap year
        hours = 365*24
        # elecectricity produced per unit per year
        P_MWh = self.P_lim * hours * f_inter_ave

        # calculate O&M cost per unit per year
        dcms_unit_year = dcms_cost_MWh * P_MWh

        self.dcms_unit_year = self.dcms_unit_year + dcms_unit_year


"""

a test class for wind_eco

sub_sys2 = 'windfarm'
P_lim = 2           # in MW
w_n_unit = 40   
w_lifetime = 30     # 30 years life time
loc_type = 1        # 1 for land wind farm, 0 for off-shore wind farm

# discount rate 
r_discount = 0.05
# inflation rate
#r_inflation = 0.025

# energy inflation rate
e_inflation = 0.05

# electricty price per MWh
price_e = 130

# captical cost of a wind turbine per kW
cost_kW = 1590      # $ per kW 

# om cost of a wind turbine per MWh
w_om_cost_MWh = 14.4

# decommissioning cost of a wind turbine per MWh
w_dcms_cost_MWh = 4.0

# wind farm intermittence factor
f_inter_ave = 0.3


wfarm = wind_eco(P_lim,w_n_unit,w_lifetime)
wfarm.cal_OCC(cost_kW)
print ('total wind farm capital cost: ', wfarm.occ)
wfarm.cal_OM_unit(w_om_cost_MWh,f_inter_ave)
print ('om cost of per turbine per year: ', wfarm.om_unit_year)
wfarm.cal_decommissioning_unit(dcms_cost_MWh,f_inter_ave)
print ('decommissioning cost per turbine per year: ',smr.dcms_unit_year)

wfarm.cal_NCF(price_e,f_inter)
cashflow = wfarm.cashflow


wfarm.cal_LCOE(r_discount,price_e,f_inter)
print ('wind farm levelized cost of electricity: ',wfarm.LCOE, ' $/MWh')

y_tot = w_lifetime+1
post_process.plt_cashflow(y_tot,cashflow,sub_sys2)

wfarm.cal_NPV(r_discount)
print ('wind farm net present value: ', wfarm.NPV, 'million $')
wfarm.cal_IRR(r_discount)
print ('wind farm internal rate of return: ', wfarm.IRR)

print ('\n')

"""

"""

economical analysis of the PEM cluster

REFERENCE:
    - University of California, Berkeley, Wei, Max, Lipman, Timothy, Mayyas, Ahmad, Chien, Joshua, Chan, Shuk Han, Gosselin, David, Breunig, Hanna, Stadler, Michael, McKone, Thomas, Beattie, Paul, Chong, Patricia, Colella, Whitney, and James, Brian. A Total Cost of Ownership Model for Low Temperature PEM Fuel Cells in Combined Heat and Power and Backup Power Applications. United States: N. p., 2014. Web. doi:10.2172/1163271.
    - Saur, G. Wind-To-Hydrogen Project: Electrolyzer Capital Cost Study. United States: N. p., 2008. Web. doi:10.2172/944892.
    - Schoots K, Ferioli F, Kramer GJ, Zwaan, van der BCC. Learning curves for hydrogen production technology: An assessment of observed cost reductions. International Journal of Hydrogen Energy. 2008;33(11):2630-2645. doi: 10.1016/j.ijjhydene.2008.03.011

"""
# an cost model with brakdown of PEM 
class h2_cost_breakdown:
    def __init__(self,Pmax_unit,n_unit):
        self.Pmax_unit = Pmax_unit*1000 # convert MW to kW
        self.n_unit = n_unit

        self.cost_layer = 0.0

    
    # capital cost breakdown: stack cost (membrane electrode assembly (MEA) cost, and flow plates cost, and assembly), balance of plant (BoP), Power electrionics cost, gas conditioning cost

    # stack cost in $/kw 
    # catalyst cost (related to pladium price)
    def cata_cost():
        pass

    # gas diffusion layer cost
    def layer_cost(self,cost_layer_kW):
        cost_layer = self.n_unit * self.Pmax_unit * cost_layer_kW
        
        self.cost_layer = cost_layer

    # membrane cost
    def mem_cost():
        pass

    # electrode cost
    def elec_cost():
        pass

    # flow plate cost
    def plate_cost():
        pass

    # stack assembly cost (MEA+cost)
    def assembly_cost():
        pass


    # Blance of Plant (BoP) cost 
    # hydrogen management cost
    def h2manage_cost():
        pass

    # air management cost
    def airmanage_cost():
        pass

    # temperature management cost
    def tempmanage_cost():
        pass

    # other cost
    def other_cost():
        pass


# an cost model of PEM with simple cost estimate 
class h2_cost_simple:
    def __init__(self,Pmax_unit,n_unit,lifetime,con_time):
        self.Pmax_unit = Pmax_unit*1000 # convert MW to kW
        self.n_unit = n_unit
        self.lifetime = lifetime
        self.con_time = con_time    # construction time, in year

        self.cost_CAPEX = 0
        self.cost_OPEX = 0
#        self.cost_elec = 0
        self.cost = 0
        self.profit = 0

        # PEM cashflow 
        self.cashflow = []

    # CAPEX of a PEM unit, capex_kw in $/kW
    def cal_CAPEX(self,capex_kw):
        cost_CAPEX = capex_kw * self.Pmax_unit 

        self.cost_CAPEX = cost_CAPEX

        #return cost_CAPEX

    # OPEX of a PEM unit
    def cal_OPEX(self,capex_kw,cap_op_ratio):
        opex_kw = capex_kw * cap_op_ratio

        cost_OPEX = opex_kw * self.Pmax_unit 

        self.cost_OPEX = cost_OPEX

        #return cost_OPEX

    # electricity cost of a PEM unit with input power during time peroid (electricity price in $/MWh, time in s, enery in MWh)
    def cal_cost_elec(self,price_e,energy):
       
        # calculate total cost over period of time
        cost_elec = price_e * energy

        return cost_elec


    # profits from hydrogen production (H2_price in $/kg of each year, H2 production mass in kg of each year)
    def profits_H2(self, price_h2, production_h2):
        # calculate the profits from H2
        profit = price_h2 * production_h2 

        self.profit = profit

        return profit

    # calculate year cost under different conditions
    def cal_cost_year(self,unit_op,unit_con,unit_replace,price_ePEM,e_to_h2):

        # calculate construction occ of this year
        cost_con = self.cost_CAPEX * unit_con

        # calculate operation cost of this year
        cost_op = self.cost_OPEX * unit_op

        # calculate construction occ of this year
        cost_replace = self.cost_CAPEX * unit_replace

        # calculate electricity cost
        cost_elec = price_ePEM * e_to_h2


        cost_year = (cost_con + cost_op + cost_elec + cost_replace)/1e6    # convert to million dollar

        return cost_year

    # net cost of the PEM from 0 to nth year, year 0 are construction year, no electricy are consumed, cost are accounted in year 1
    def cal_cost(self, lifetime, energy, price_e):
        cost = []

        # calculate seconds per year, ignore leap year
        # seconds = 365*24*60*60

        for i in range(self.lifetime+1):
            # the very beginning of the project
            if i == 0:
                cost.append(0.0)
            elif i == 1:
                cost_elec_year = self.cal_cost_elec(price_e[i],energy[i])
                cost_year = (self.cost_CAPEX + self.cost_OPEX) * self.n_unit + cost_elec_year

                cost_year = cost_year/1e6        # convert to million dollar 

                cost.append(cost_year)

            else:
                cost_elec_year = self.cal_cost_elec(price_e[i],energy[i])
                cost_year = self.cost_OPEX * self.n_unit + cost_elec_year

                cost_year = cost_year/1e6        # convert to million dollar 

                cost.append(cost_year)

        return cost

    # net cash flow of the PEM from 0 to nth year, year 0 are construction year, no electricy are consumed, cost are accounted in year 1
    def cal_NCF(self, lifetime, energy, price_e, price_h2, production_h2):
        cashflow = []

        # calculate seconds per year, ignore leap year
        # seconds = 365*24*60*60

        for i in range(self.lifetime+1):
            # the very beginning of the project
            if i == 0:
                cashflow.append(0.0)
            elif i == 1:
                cost_elec_year = self.cal_cost_elec(price_e[i],energy[i])
                cost_year = (self.cost_CAPEX + self.cost_OPEX) * self.n_unit + cost_elec_year
                profit_year = self.profits_H2(price_h2[i],production_h2[i]) 

                cashflow_year = (cashflow[-1] + profit_year - cost_year)/1e6        # convert to million dollar 

                cashflow.append(cashflow_year)

            else:
                cost_elec_year = self.cal_cost_elec(price_e[i],energy[i])
                cost_year = self.cost_OPEX * self.n_unit + cost_elec_year
                profit_year = self.profits_H2(price_h2[i],production_h2[i]) 

                cashflow_year = (cashflow[-1] + profit_year - cost_year)/1e6        # convert to million dollar 

                cashflow.append(cashflow_year)


        self.cashflow = self.cashflow + cashflow



"""

a test class for h2sys_eco

Pmax_unit = 0.5     # maximum power of a unit
n_unit = 10         # number of units

capex_kw = 1400     # capital cost per kW

cap_op_ratio = 0.02 # capital cost operational cost ratio

price_e = [0,130,130,130,130,130]       # electricty price per MWh

energy = [0, 100,100,100,100,100]

price_h2 = [0,14,14,14,14,14]     # price of h2 per kg
production_h2 = [0,6000,6000,6000,6000,6000]    # production in kg of each year (or other unit time, year is for cash flow analysis)

lifetime = 5

# calculate PEM cost and profit
PEM_eco = h2_cost_simple(Pmax_unit,n_unit,lifetime)

cost_CAPEX = PEM_eco.cal_CAPEX(capex_kw)
cost_OPEX = PEM_eco.cal_OPEX(capex_kw,cap_op_ratio)

PEM_eco.cal_NCF(lifetime,energy,price_e, price_h2, production_h2)

print (PEM_eco.cashflow)

"""

"""

an economic model for a hybrid system

"""
#from sys_control import *

class system_eco:
    def __init__(self):
        #super().__init__(components,num_chars,unit_power,n_units,lifetimes,con_time,sys_lifetime)
        # economic parameters

        # system annually cost
        self.cost = []
        # system annually profits
        self.profit = []
        # system cash flow
        self.cashflow = []
        # cashflow of each component
        self.cashflow_comp = {}
        # system LCOE
        self.LCOE = 0.0
        # system NPV
        self.NPV = 0.0
        # system IRR
        self.IRR = 0.0
    
    # adjust cashflow according to real construction plan
    def _flow_adjust_(self,cashdic):
        for i in range(len(cashdic.keys())):
            cashflow = [1.0]*(self.sys_lifetime+1)
            key = list(cashdic)[i]
#            cashflow[(self.year_start[i]-1):(self.year_start[i]+len(cashdic[key]))] = cashdic[key]
            for n in range(len(cashdic[key])):
                cashflow[self.year_start[i]-1+n] = cashdic[key][n]

            self.cashflow_comp[key] = cashflow


    # sum up system cash flow
    def cal_cashflow(self,cashdic):
        self._flow_adjust_(cashdic)

        cashflow = np.zeros(self.sys_lifetime+1)
        for key in self.cashflow_comp.keys():
            cashflow = cashflow + np.asarray(self.cashflow_comp[key],dtype=float)

        self.cashflow = cashflow

    # calculate hybrid profit
    def _cal_hybrid_profit_(self,lifetime_scale,price_e,price_h2,e_to_grid,m_h2_production):

        profit = []

        for i in range(len(lifetime_scale)-1):

            # selling electricity profits, e_price $/MWh, e_to_grid MWh
            e_profit = price_e[i] * e_to_grid[i]
            # selling hydrogen profits, h2_price $/kg, m_h2_production kg
            h2_profit = price_h2[i] * m_h2_production[i]

            # total profits of a year 
            profit_year = (e_profit + h2_profit)/1e6    # convert to million dollar

            profit.append(profit_year)

        self.profit = profit

    
    # calculate hybrid cost
    def _cal_hybrid_cost_(self,sys_config,lifetime_scale,eco_pack,price_ePEM,e_to_h2):

        cost = []

        for char in lifetime_scale[0]:
            if char == '00':
                col_npp = lifetime_scale[0].index(char)
            elif char == '01':
                col_wind = lifetime_scale[0].index(char)
            elif char == '02':
                print ('model under development')
            elif char == '10':
                col_pem = lifetime_scale[0].index(char)

        for key in sys_config.keys():
            if sys_config[key][0] == '00':
                npp_lifetime = sys_config[key][3]
                npp_batch = sys_config[key][-1]
            elif sys_config[key][0] == '01':
                wind_lifetime = sys_config[key][3]
                wind_batch = sys_config[key][-1]
            elif sys_config[key][0] == '02':
                print ('model under development')
            elif sys_config[key][0] == '10':
                pem_lifetime = sys_config[key][3]
                pem_batch = sys_config[key][-1]
            elif sys_config[key][0] == '20':
                store_lifetime = sys_config[key][3]
                store_batch = sys_config[key][-1]
                
       
        for i in range(1,len(lifetime_scale)):
            year = lifetime_scale[i][0]

            cost_npp = 0.0
            cost_wfarm = 0.0
            cost_PV = 0.0
            cost_pem = 0.0

            for data in eco_pack:
                
                if data.get('00'):
                    npp_unit_done = lifetime_scale[i][col_npp]
                    cost_npp = data['00'].cal_cost_year(npp_unit_done,year)
                elif data.get ('01'):
                    wfarm_unit_op = int(lifetime_scale[i][col_wind])

                    if year == 0:
                        wfarm_unit_con = 0
                        wfarm_unit_replace = 0
                    else:
                        cycle = int(year/wind_lifetime)

                        if year < lifetime_scale[-1][0]:
                            wfarm_unit_con = int(lifetime_scale[i+1][col_wind]) - int(lifetime_scale[i][col_wind])
                        else:
                            wfarm_unit_con = 0

                        if cycle > 0 and cycle < wind_batch:
                            idx = i - cycle*wind_lifetime
                            wfarm_unit_replace = max(0,int(lifetime_scale[idx][col_wind]) - int(lifetime_scale[idx-1][col_wind]))
                        else:
                            wfarm_unit_replace = 0
                        
                        #print ('wind',year,wfarm_unit_op,wfarm_unit_con,wfarm_unit_replace)

                    cost_wfarm = data['01'].cal_cost_year(wfarm_unit_op,wfarm_unit_con,wfarm_unit_replace)

                elif data == 'PV_eco':
                    print ('model under development')
                elif data.get('10'):
                    pem_unit_op = int(lifetime_scale[i][col_pem])
                    if year == 0:
                        pem_unit_con = 0
                        pem_unit_replace = 0
                    else:
                        cycle = int(year/pem_lifetime)

                        if year < lifetime_scale[-1][0]:
                            pem_unit_con = int(lifetime_scale[i+1][col_pem]) - int(lifetime_scale[i][col_pem])
                        else:
                            pem_unit_con = 0

                        if cycle > 0 and cycle < pem_batch:
                            idx = i - cycle*pem_lifetime
                            pem_unit_replace = max(0,int(lifetime_scale[idx][col_pem]) - int(lifetime_scale[idx-1][col_pem]))
                        else:
                            pem_unit_replace = 0
                        #print ('pem',year,pem_unit_op,pem_unit_con,pem_unit_replace)

                    cost_pem = data['10'].cal_cost_year(pem_unit_op,pem_unit_con,pem_unit_replace,price_ePEM[i-1],e_to_h2[i-1])

            cost_year = -(cost_npp + cost_wfarm + cost_PV +cost_pem)

            cost.append(cost_year)

        self.cost = cost

    # calculate hybrid systme cashflow
    def cal_hybrid_cashflow(self,sys_config,lifetime_scale,eco_pack,price_e,price_ePEM,price_h2,e_to_grid,e_to_h2,m_h2):

        cashflow = []

        self._cal_hybrid_profit_(lifetime_scale,price_e,price_h2,e_to_grid,m_h2)
        self._cal_hybrid_cost_(sys_config,lifetime_scale,eco_pack,price_ePEM,e_to_h2)

        for i in range(len(lifetime_scale)-1):
            if i == 0:
                cashflow_year = 0.0
            else:
                cashflow_year = cashflow[i-1]+ self.profit[i] + self.cost[i]
            cashflow.append(cashflow_year)
        
        self.cashflow = cashflow

    # calculate system LCOE
    def cal_LCOE(self,e_to_grid,m_h2):

        # total electricity produced to grid
        e_tot_to_grid = sum(e_to_grid)

        # total cost of the system
        cost_tot = -sum(self.cost) * 1e6    # in million dollar

        LCOE = cost_tot/e_tot_to_grid

        self.LCOE = LCOE
    # calculate NPV
    def cal_NPV(self,r_discount):
        # calculate the real rate of interest
        r_interest = r_discount 

        NPV = 0

        for i in range(len(self.cashflow)):
            NPV_curr = self.cashflow[i]/(1+r_interest)**i

            NPV = NPV + NPV_curr

        self.NPV = NPV



    # calculate Internal Rate of Return (IRR)
    def cal_IRR(self,r_discount):

        # initial guess of IRR
        IRR = r_discount

        NPV = self.NPV

        epsi = 1e-6

        step_size = 0.01

        n_iter = 0

        iter_max = 200

        while abs(NPV) > epsi:

            if NPV > 0:
                IRR = IRR + step_size
            else:
                IRR = IRR - step_size

            NPV_new = 0.0

            for i in range(len(self.cashflow)):
                NPV_curr = self.cashflow[i]/(1+IRR)**i
                NPV_new = NPV_new + NPV_curr

            if NPV_new * NPV < 0:
                step_size = step_size/2.

            NPV = NPV_new

            n_iter = n_iter + 1

            if n_iter > iter_max:
                print ('***************')
                print ('*NOT CONVERGE!*')
                print ('***************')
                break
            elif IRR > 1.0:
                print ('***************')
                print ('*IRR over 1.0!*')
                print ('***************')
                IRR = 1.0
                break

        self.IRR = IRR


"""

a test class for a hybrid system

from coupling import *

components = ['SMR','wind','PEM','storage']
num_chars = ['00','01','10','20']
unit_power = [60.0,2.0,0.6,0.0]
n_units = [6,80,500,1]
lifetimes = [60,30,20,60]
con_time = [2,1,1,1]

sys_lifetime = 60

# discount rate 
r_discount = 0.05
# inflation rate
#r_inflation = 0.03
# electricty price per MWh
price_e = 130

# energy inflation rate
e_inflation = 0.05

price_e_h2 = [0,0,0,0,0,0]       # electricty price per MWh
price_h2 = [0,14,14,14,14,14]     # price of h2 per kg

# smr unit data
year = 2018
FOAK = 1

eta_direct = 0.51              # oecd nea value, large uncentainty
eta_indirect = 0.51              # oecd nea value, large uncentainty

# operation and maintainess cost, dollar per MWh 
nu_om_cost_MWh = 25.8  
# fuel cost, dollar per MWh 
nu_fuel_cost_MWh = 8.26
# decommisioning cost per MWh
nu_dcms_cost_MWh = 0.16 

# construction time of a unit, in year
#y_unit_construct = 2


# the utilization factor
f_uti = 0.85

# config learning factors
x = 0.15
y = 0.74
z = 0.82
k = 0.02

# technology learning rate
r_learning = 0.04

# wind turbine data
loc_type = 1        # 1 for land wind farm, 0 for off-shore wind farm

# captical cost of a wind turbine per kW
w_cost_kW = 1590      # $ per kW 

# om cost of a wind turbine per MWh
w_om_cost_MWh = 14.4

# decommissioning cost of a wind turbine per MWh
w_dcms_cost_MWh = 4.0

# wind farm intermittence factor
f_inter = 0.3

# PEM data
capex_kw = 1400     # capital cost per kW

cap_op_ratio = 0.02 # capital cost operational cost ratio


energy = [0, 100,100,100,100,100]

production_h2 = [0,6000,6000,6000,6000,6000]    # production in kg of each year (or other unit time, year is for cash flow analysis)

lifetime = 5

# build systems structure
system = sys_config(components,num_chars,unit_power,n_units,lifetimes,con_time,sys_lifetime)
sys_con = con_plan(system,con_time)

sys_con.cal_scale(auto_con)
sys_con.con_schedule(auto_con)

# build module structure
eco_pack = []
for key in system.config.keys():
    if system.config[key][0] == '00':
        smr_eco = nuclear_eco(system.config[key][1],system.config[key][2],year,system.config[key][3],system.config[key][4],FOAK)
        ME_2_curr,ME_9_curr = smr_eco.import_coa()
        smr_eco.cal_OCC(ME_2_curr,ME_9_curr,eta_direct,eta_indirect,x,y,z,k,r_learning)
        smr_eco.cal_IDC(r_discount)
        smr_eco.cal_OM_unit(nu_om_cost_MWh,f_uti)
        smr_eco.cal_fuel_unit(nu_fuel_cost_MWh,f_uti)
        smr_eco.cal_decommissioning_unit(nu_dcms_cost_MWh,f_uti)

        eco_pack.append(smr_eco)
    elif system.config[key][0] == '01':
        wfarm_eco = wind_eco(system.config[key][1],system.config[key][2],system.config[key][3],system.config[key][4])
        wfarm_eco.cal_OCC(w_cost_kW)
        wfarm_eco.cal_OM_unit(w_om_cost_MWh,f_inter)
        wfarm_eco.cal_decommissioning_unit(w_dcms_cost_MWh,f_inter)

        eco_pack.append(wfarm_eco)
    elif system.config[key][0] == '02':
        print ("PV model under development")
    elif system.config[key][0] == '10':
        PEM_eco = h2_cost_simple(system.config[key][1],system.config[key][2],system.config[key][3],system.config[key][4])
        PEM_eco.cal_CAPEX(capex_kw)
        PEM_eco.cal_OPEX(capex_kw,cap_op_ratio)

        eco_pack.append(PEM_eco)
    elif system.config[key][0] == '20':
        print ("H2 storage  model under development")

print (eco_pack)
eco_map = cp().mapping_eco(system.config,smr_eco,wfarm_eco,PEM_eco)
#print (eco_map[1][0])

sys_eco = system_eco(system)

sys_eco._cal_hybrid_cost_(sys_con.lifetime_scale,eco_map)

"""


"""
# non-hybrid model
sys_cashdic = {}
comp_1_cashflow = []
comp_2_cashflow = [] 
comp_3_cashflow = []


for i in range(6):
    comp_1_cashflow.append(float(i))

for i in range(3):
    comp_2_cashflow.append(float(i))

for i in range(3):
    comp_3_cashflow.append(float(i))

n_comp = len(sys_cashdic.keys())
print (n_comp)
year_start = [1,5,3]
year_dec = [20,20,20]

sys_cashdic['comp1'] = comp_1_cashflow
sys_cashdic['comp2'] = comp_2_cashflow
sys_cashdic['comp3'] = comp_3_cashflow

sys = sys_eco(sys_lifetime, year_start, year_dec)

sys.cal_cashflow(sys_cashdic)

sys.cal_NPV(r_discount)
sys.cal_IRR(r_discount)

print (sys.NPV,sys.IRR)
"""
