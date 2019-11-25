#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# File              : prepost_process.py
# Author            : tzhang
# Date              : 25.11.2019
# Last Modified Date: 25.11.2019
# Last Modified By  : tzhang

from matplotlib import pyplot as plt

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


    # data writer
#    def data_writer(time,P_demand,P_to_grid,P_abandon,P_nuclear,P_windfarm)
