#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# File              : grid.py
# Author            : tzhang
# Date              : 18.11.2019
# Last Modified Date: 21.11.2019
# Last Modified By  : tzhang
import csv
from datetime import datetime as dtCal
import numpy as np
from matplotlib import pyplot as plt
"""

a module to read grid demand data (in csv format)
    - to be done: generate a nomalized daily grid data

"""

class grid:
    def __init__(self,dataMode,inFile=None,multiplier=1.0):
        self.dataMode = dataMode  # mode for grid data, 0 for read from input file,
        self.multiplier = float(multiplier)
        self.inFile = inFile

        # grid data
        self.date = []
        self.time = []
        self.demand = []
    
    # read grid data from csv file
    def _readData_(self):
        date = []
        demand = []
        with open(self.inFile) as csv_file:
            csv_data = csv.reader(csv_file,delimiter=',')
            for row in csv_data:
                date.append(row[1])
                demand.append(row[2])
        del date[0]
        del demand[0]
#        print (date[-1])
#        print (demand[-1])

        return date, demand

    # convert date file into time array, in minute
    def _date_time_converter_(self,date):
        time = []
        date0 = date[0].split()[0]
        clock0 = date[0].split()[1]

        year0 = int(date0.split('-')[0])
        month0 = int(date0.split('-')[1])
        day0 = int(date0.split('-')[2])
        hour0 = int(clock0.split(':')[0])
        minute0 = int(clock0.split(':')[1])
        second0 = 0

        date_ini = dtCal(year0,month0,day0,hour0,minute0,second0) 

        for data in date:
            date_curr = data.split()[0]
            clock_curr = data.split()[1]

            year = int(date_curr.split('-')[0])
            month = int(date_curr.split('-')[1])
            day = int(date_curr.split('-')[2])
            hour = int(clock_curr.split(':')[0])
            minute = int(clock_curr.split(':')[1])
            second = 0
            
            date_curr = dtCal(year,month,day,hour,minute,second)
            dTime = date_curr - date_ini
            
            # calculate current time in unit minute
            t_curr = dTime.days*1440 + dTime.seconds/60
            time.append(t_curr)

        return time

    # scale the demand 
    def _demand_scale_(self,demand):
        demand = np.asarray(demand,dtype = float)
        demand = demand*self.multiplier

        demand = list(demand)

        return demand


    # generate grid data
    def gen(self):
        if self.dataMode == 0:
            date,demand = grid._readData_(self)
            time = grid._date_time_converter_(self,date)
            if self.multiplier != 1.0:
                demand = grid._demand_scale_(self,demand)
        else:
            # to be imporved
            pass

        self.date = self.date + date
        self.time = self.time + time
        self.demand = self.demand + demand

    # plot grid demand data
    def demand_plot(self):
        plt.figure(figsize = (12,8))
        plt.plot(self.time,self.demand, color = 'g')
        plt.xlabel('Time (min)',fontsize = '16')
        plt.xlim(left = 0.0)
        plt.ylabel('Grid Demand (MW)', fontsize = '16')
        plt.grid(linestyle='--',linewidth = '1')

        pltName = 'grid_demand.png'
#        plt.show()
#        plt.close()
        plt.savefig(pltName,dpi = 100)

    # aquire time data
    def aquire_time(self):
        return self.time

    # aquire demand data
    def aquire_demand(self):
        return self.demand

    # plot user defined grid demand data
    def user_demand_plot(self,time,demand):
        plt.figure(figsize = (12,8))
        plt.plot(time,demand, color = 'g')
        plt.xlabel('Time (min)',fontsize = '16')
        plt.xlim(left = 0.0)
        plt.ylabel('Grid Demand (MW)', fontsize = '16')
        plt.grid(linestyle='--',linewidth = '1')

        pltName = 'user_grid_demand.png'
#        plt.show()
#        plt.close()
        plt.savefig(pltName,dpi = 100)



"""
a class test

the test data comes from: G.B. National Grid Status, https://www.gridwatch.templar.co.uk/

dataMode = 0
inFile = 'UK_gridwatch_year2018_Jan.csv'
multiplier = 0.005

uk_grid = grid(dataMode,inFile,multiplier)
uk_grid.gen()
uk_grid.demand_plot()

print (uk_grid.date)
print (uk_grid.time)
print (uk_grid.demand)
"""
