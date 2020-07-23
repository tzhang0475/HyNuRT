#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# File              : prepost_process.py
# Author            : tzhang
# Date              : 25.11.2019
# Last Modified Date: 24.07.2020
# Last Modified By  : tzhang

from matplotlib import pyplot as plt
import numpy as np

"""

a tool for pre-process

"""
class pre_process:
    def __init__(self):
        pass



"""

a tool for post-process

"""
class post_process:

    # plot the grid demand and the system generatrion
    def plt_grid_balance(time,P_demand,P_to_grid):
        plt.figure(figsize = (12,8))
        plt.plot(time,P_demand, color = 'g',label = 'grid demand')
        plt.plot(time,P_to_grid, color = 'b', label = 'system deliver')
        plt.legend()
        plt.xlabel('Time (min)',fontsize = '16')
        plt.xlim(left = 0.0)
        plt.ylabel('Power (MW)', fontsize = '16')
        plt.grid(linestyle='--',linewidth = '1')

        pltName = 'grid_blance.png'
        plt.savefig(pltName,dpi = 100)

    # plot the stored mass of hydrogen
    def plt_h2_stored(time,m_stored_data):
        plt.figure(figsize = (12,8))
        plt.plot(time,m_stored_data[0:-1], color = 'k')
        plt.xlabel('Time (min)',fontsize = '16')
        plt.xlim(left = 0.0)
        plt.ylabel('Hydrogen Storage (kg)', fontsize = '16')
        plt.grid(linestyle='--',linewidth = '1')

        pltName = 'hydrogen_storage.png'
        plt.savefig(pltName,dpi = 100)


    # plot the abandoned power 
    def plt_power_abandon(time,P_abandon):
        plt.figure(figsize = (12,8))
        plt.plot(time,P_abandon, color = 'c')
        plt.xlabel('Time (min)',fontsize = '16')
        plt.xlim(left = 0.0)
        plt.ylabel('Power (MW)', fontsize = '16')
        plt.grid(linestyle='--',linewidth = '1')

        pltName = 'power_abondoned.png'
        plt.savefig(pltName,dpi = 100)

    # plot cash flow of a unit n years
    def plt_cashflow(n_year,cashflow,system):
        
        year = np.arange(0,n_year,1) 

        plt.figure(figsize = (14,8))
        plt.plot(year,cashflow, color = 'firebrick',linewidth = '3',marker = 'o', markersize = '5')
        plt.xlabel('year',fontsize = '16')
        plt.xlim(left = 0.0)
        plt.ylabel('Cash Flow ($ in Million)', fontsize = '16')
        plt.grid(linestyle='--',linewidth = '1')

        pltName = system+'_'+'cashflow.png'
        plt.savefig(pltName,dpi = 100)

    # plot cash flow of a system with n units and cash flow of each unit in the system
    def plt_sys_cashflow(n_year,cashflow,cashdic):

        year = np.arange(0,n-year,1)
        
        plt.figure(figsize = (14,8))

        # plot overall system cash flow
        plt.plot(year,cashflow, color = 'firebrick',linewidth = '3',marker = 'o', markersize = '5', label = 'system')

        # plot cash flow of each component
        for key in cashdic.keys():
            plt.plot(year,cashflow[key],linewidth = '2', lable = key)

        plt.xlabel('year',fontsize = '16')
        plt.xlim(left = 0.0)
        plt.ylabel('Cash Flow ($ in Million)', fontsize = '16')
        plt.grid(linestyle='--',linewidth = '1')


    # cash flow data writer
    def data_cashflow(cashflow, cashdic):
        
        datafile = 'data_cashflow.txt'

        with open(datafile,"w+") as f:
            f.write('year'+'    '+'system'+'    ')
            for key in cashdic.keys():
                f.write(key+'   ')
            f.write('\n')

            for i in range(len(cashflow)):
                f.write(str(i)+'    ')
                f.write(str(cashflow[i])+'      ')
                for key in cashdic.keys():
                    f.write(cashdic[key][i]+'       ')
                f.write('\n')
