#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# File              : windData.py
# Author            : tzhang
# Date              : 26.10.2019
# Last Modified Date: 13.11.2019
# Last Modified By  : tzhang

# module to read or generate Rayleigh Distribution winddata
import math
import random
import numpy as np
import matplotlib.pyplot as plt

class wind_Data:
    def __init__(self):
        self.time = []
        self.wind = []

# generate Rayleigh distribution wind data
class wind_Rayleigh(wind_Data):
    def __init__(self,v_max,v_m,n,sTime,eTime,nData):
        wind_Data.__init__(self)
        self.v_max = v_max # max wind velocity
        self.v_m = v_m # mean wind velocity
        self.n = n # number of intervals
        
        # generate the time array for wind data
        step = (eTime - sTime)/nData
        eTime = eTime + step
        time = np.arange(sTime,eTime,step)

        self.time = self.time + list(time) # time array

        self.pdf = [] # probability distribution funciton
        self.cdf = [] # cumulated probablity distribution
        self.v_data = [] # velocity distribution



    # Rayleigh probablity distribution function
    def _Rayleigh_(self):
        pi = 3.141592653
        dv = self.v_max/self.n
        const = pi/2*dv**2/self.v_m**2 # constant in the distribution
        pdf = []
        for k in range(self.n):
            idx = k+1 # k starts from 0, the first interval
            v_exp = -pi/4 * idx**2 * dv**2/self.v_m**2
            v_const = idx * const
            pdf_k = v_const*math.exp(v_exp)

            pdf.append(pdf_k)
        self.pdf = self.pdf + pdf
#        return pdf

    # calculate the velocity distribution
    def _v_dis_(self):
        dv = self.v_max/self.n
        v_data = []
        v_data.append(0.001) # set a minimal velocity of wind
        for k in range(self.n):
            idx = k+1
            vk = idx*dv
            v_data.append(vk)

        self.v_data = self.v_data + v_data
#        return v_data

    # calcualte cumulated probability distribution
    def _cdf_cal_(self):
        cdf = []
        cdf.append(0.0)
        for i in range(len(self.pdf)):
           cdf_curr =  cdf[-1] + self. pdf[i]
           cdf.append(cdf_curr)
        cdf.append(1.0)

        self.cdf = self.cdf + cdf

    # generate a random wind velocity according to cdf
    def _v_wind_(self):
        seed = random.random()
        cdf = []
        for value in self.cdf:
            cdf.append(value)
        if seed <= self.cdf[1]:
            v_wind = self.v_data[0] # set a minimal value for wind velocity
        elif seed >= self.cdf[-2]:
            v_wind = self.v_data[-1] # cover the range cannot be nomalized due to n number
        else:                   # generate a wind volicity accoring to cdf
            sort = cdf
            sort.append(seed)
            sort.sort()
            idx = sort.index(seed)
            if idx >= (len(self.v_data)):
                print (idx)
                print (seed)
                print (sort)
                print (len(sort))
            v_wind = self.v_data[idx-1]

        return v_wind

    # generate time dependent wind velocity curve
    def _windCurve_(self):
        wind = []
        for i in range(len(self.time)):
     #       print ('length cdf: ',len(self.cdf))
            v_wind = wind_Rayleigh._v_wind_(self)
            wind.append(v_wind)

        self.wind = self.wind + wind

    # merge time into one array
#    def _windData_(self):
#        windData = []
#        for i in range(len(self.time)):
#            data = []
#            data.append(self.time[i])
#            data.append(self.wind[i])
#            self.windData.append(data)
#
    # main function to generate wind data
    def genData(self):
        wind_Rayleigh._Rayleigh_(self)
        wind_Rayleigh._v_dis_(self)
        wind_Rayleigh._cdf_cal_(self)
        wind_Rayleigh._windCurve_(self)
#        wind_Rayleigh._windData_(self)

#        windData = self.windData
        time = self.time
        v_wind = self.wind
    
        return time,v_wind

    # plot wind velocity distribution probability
    def plt_v_dis(self):
        v_data = self.v_data[1:]
        plt.figure(figsize = (12,8))
        plt.bar(v_data,self.pdf, color = 'c')
        plt.xlabel('wind velocity (m/s)',fontsize = '16')
        plt.xlim(left = 0.0)
        step = 0.0+max(self.v_data)/self.n
        plt.xticks(np.arange(0.0,(max(self.v_data)+step),step))
        plt.ylabel('probability', fontsize = '16')
        plt.grid(linestyle='--',linewidth = '1')

        pltName = 'wind_v_Rayleigh.png'
        plt.show()
        plt.close()
        plt.savefig(pltName,dpi = 100)

    def plt_windData(self): 
        plt.figure(figsize = (12,8))
        plt.plot(self.time,self.wind, color = 'r')
        plt.xlabel('time',fontsize = '16')
        plt.xlim(left = 0.0)
        plt.ylabel('wind velocity (m/s)', fontsize = '16')
        plt.grid(linestyle='--',linewidth = '1')

        pltName = 'windData_Rayleigh.png'
        plt.show()
        plt.close()
        plt.savefig(pltName,dpi = 100)

""" 
#a test case for wind source class (Rayleigh distribution)

wind = wind_Rayleigh(20,7,20,0,60,60)
time,v_wind = wind.genData()
wind.plt_v_dis()
wind.plt_windData()
print (time)
print (v_wind)
"""


# class to read wind data
class wind_readData(wind_Data):

    def _readFile_(self,inFile):
        time = []
        wind = []
        windData = []
        with open (inFile,'r') as f:
            content = f.readlines()
        f.close()

        for line in content:
            try:
                float(line.split()[0])
                data = []
                time.append(line.split()[0])
                wind.append(line.split()[1])
                data.append(line.split()[0])
                data.append(line.split()[1])
                windData.append(data)
            except ValueError:
                pass
        
        self.time = self.time + time
        self.wind = self.wind + wind
#        self.windData = self.windData + windData

#        return windData

    # plot time dependent wind velocity
    def plt_windData(self): 
        plt.figure(figsize = (12,8))
        plt.plot(self.time,self.wind, color = 'r')
        plt.xlabel('time',fontsize = '16')
        plt.xlim(left = 0.0)
        plt.ylabel('wind velocity (m/s)', fontsize = '16')
        plt.grid(linestyle='--',linewidth = '1')

        pltName = 'windData_Source.png'
        plt.show()
        plt.close()
        plt.savefig(pltName,dpi = 100)


