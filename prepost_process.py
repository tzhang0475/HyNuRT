#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# File              : prepost_process.py
# Author            : tzhang
# Date              : 25.11.2019
# Last Modified Date: 31.07.2020
# Last Modified By  : tzhang

from matplotlib import pyplot as plt
import numpy as np
import pandas as pd
import os

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
        f.close()

    # write system performance data to text file
    def data_performance(label,time,P_demand,P_coupled,P_to_grid,P_to_h2sys,P_abandon,M_stored_data):
        datafile = 'data_performance_'+label+'.txt'

        with open(datafile, 'w+') as f:
            f.write('time'+'    ')
            f.write('grid demand'+'      ')
            f.write('wind-nuclear generated'+'      ')
            f.write('power to grid'+'      ')
            f.write('power to h2 system'+'      ')
            f.write('abandoned power'+'      ')
            f.write('stored hydrogen'+'      ')
            f.write('\n')

            for i in range(len(time)):
                f.write(str('%.2f'%time[i])+'    ')
                f.write(str('%.2f'%P_demand[i])+'    ')
                f.write(str('%.2f'%P_coupled[i])+'    ')
                f.write(str('%.2f'%P_to_grid[i])+'    ')
                f.write(str('%.2f'%P_to_h2sys[i])+'    ')
                f.write(str('%.2f'%P_abandon[i])+'    ')
                f.write(str('%.3f'%M_stored_data[i])+'    ')
                f.write('\n')

        f.close()

    # write system performance data to excel file
    def excel_performance(label,time,P_demand,P_coupled,P_to_grid,P_to_h2sys,P_abandon,e_acc_to_grid,e_acc_to_h2sys,e_acc_from_h2sys,e_acc_net_h2sys,e_acc_abandon,m_stored_data):
        datafile = 'data_performance_'+label+'.xlsx'
        sheetname1 = 'power_'+label
        sheetname2 = 'energy_'+label

        # remove exists file 
        if os.path.isfile(datafile):
            os.remove(datafile)

        # write data to xlsx file
        df1 = pd.DataFrame({'time':time,\
                        'grid demand (MW)':P_demand,\
                        'wind-nuclear generated (MW)': P_coupled,\
                        'power to grid (MW)':P_to_grid,\
                        'power to h2 system (MW)':P_to_h2sys,\
                        'abandoned power (MW)':P_abandon})
        df2 = pd.DataFrame({'time':time,\
                        'accumulated energy to grid (MWh)':e_acc_to_grid,\
                        'accumulated energy to h2 system (MWh)':e_acc_to_h2sys,\
                        'accumulated energy from h2 system (MWh)': e_acc_from_h2sys,\
                        'accumulated net energy to h2 system (MWh)':e_acc_net_h2sys,\
                        'accumulated abondoned energy (MWh)':e_acc_abandon,\
                        'stored hydrogen (kg)':m_stored_data})

        writer = pd.ExcelWriter(datafile, engine='xlsxwriter')

        df1.to_excel(writer,sheet_name = sheetname1)
        df2.to_excel(writer,sheet_name = sheetname2)

        workbook = writer.book
        worksheet1 = writer.sheets[sheetname1]
        worksheet2 = writer.sheets[sheetname2]

        # set format of data
        form1 = workbook.add_format({'num_format':'0.0'})
        form2 = workbook.add_format({'num_format':'0.00'})
        form3 = workbook.add_format({'num_format':'0.000'})

        # add format
        worksheet1.set_column('B:B',15,form1)
        worksheet1.set_column('C:G',30,form2)

        worksheet2.set_column('B:B',15,form1)
        worksheet2.set_column('C:G',40,form2)
        worksheet2.set_column('H:H',30,form3)

        writer.save()



    # select data according to time interval, time_interval in unit of minute 
    def data_opti(time,time_interval,\
            P_demand,P_coupled,P_to_grid,P_to_h2sys,P_abandon,\
            e_acc_to_grid,e_acc_to_h2sys,e_acc_from_h2sys,e_acc_net_h2sys,e_acc_abandon,\
            m_stored_data):

        # select index of requested data
        idx_array = [0]
        for i in range(1,len(time)-1):
            if time[i]%time_interval == 0:
                idx_array.append(i)
            elif time[i-1]%time_interval > time[i]%time_interval and time[i]%time_interval < time[i+1]:
                idx_array.append(i)
        idx_array.append(len(time)-1)
        # new array for selected data
        time_slct = []
        P_demand_slct = []
        P_coupled_slct = []
        P_to_grid_slct = []
        P_to_h2sys_slct = []
        P_abandon_slct = []
        m_stored_data_slct = []

        e_acc_to_grid_slct = []
        e_acc_to_h2sys_slct = []
        e_acc_from_h2sys_slct = []
        e_acc_net_h2sys_slct = []
        e_acc_abandon_slct = []

        for idx in idx_array:
            time_slct.append(time[idx])

            P_demand_slct.append(P_demand[idx])
            P_coupled_slct.append(P_coupled[idx])
            P_to_grid_slct.append(P_to_grid[idx])
            P_to_h2sys_slct.append(P_to_h2sys[idx])
            P_abandon_slct.append(P_abandon[idx])
            m_stored_data_slct.append(m_stored_data[idx])

            e_acc_to_grid_slct.append(e_acc_to_grid[idx])
            e_acc_to_h2sys_slct.append(e_acc_to_h2sys[idx])
            e_acc_from_h2sys_slct.append(e_acc_from_h2sys[idx])
            e_acc_net_h2sys_slct.append(e_acc_net_h2sys[idx])
            e_acc_abandon_slct.append(e_acc_abandon[idx])

        return time_slct,\
                P_demand_slct,P_coupled_slct,P_to_grid_slct,P_to_h2sys_slct,P_abandon_slct,\
                e_acc_to_grid_slct,e_acc_to_h2sys_slct,e_acc_from_h2sys_slct,e_acc_net_h2sys_slct,e_acc_abandon_slct,\
                m_stored_data_slct




