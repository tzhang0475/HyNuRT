#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# File              : nu_opti.py
# Author            : tzhang
# Date              : 08.08.2020
# Last Modified Date: 03.09.2020
# Last Modified By  : tzhang
"""

a test module of GA


"""
import sys
import os
import numpy as np

# insert from different path
sys.path.insert(1, '../../../')
# import libraries of package
from opti import *
from prepost_process import mod_control as mc

class game:
    # run the model and get scores
    def play_game(population,keyword,inputfile,modelname):

        if os.path.isfile('cal_data.txt'):
            os.remove('cal_data.txt')
 
        for mortal in population:
            input_data = []
            for data in mortal:
                input_data.append(data)
            input_data.append(1)

            mc.mod_input(inputfile,keyword,input_data)
            mc.mod_run(modelname,inputfile)

    # get scores
    def evaluate():
        para1_array = []
        para2_array = []

        with open('cal_data.txt','r') as f:
            for line in f:
                if 'RFG' in line:
                    para1 = float(line.split(':')[-1].lstrip().rstrip())
                    para1_array.append(para1)
                elif 'IRR' in line:
                    para2 = float(line.split(':')[-1].lstrip().rstrip())
                    para2_array.append(para2)
        f.close()
        scores = game._cal_score_(para1_array,para2_array)
        print ('system score is:', max(scores))
        return scores

    # calculator of score 
    def _cal_score_(para1_array,para2_array):
        scores = []

        weight = 0.75

        for i in range(len(para1_array)):
            score = weight * 10.0 * (para1_array[i]-0.95) + (1.0-weight) * 10.0 * (para2_array[i]-0.06)
            print ('RFG: ', para1_array[i], 'IRR: ', para2_array[i],'score: ',score)
            scores.append(score)

        return scores

    # calculate initial survival rate
    def r_suv_ini(ref_argu,keyword,inputfile,modelname):
        if os.path.isfile('cal_data.txt'):
            os.remove('cal_data.txt')
 
        input_data = []
        for data in ref_argu:
            input_data.append(data)
        input_data.append(1)

        mc.mod_input(inputfile,keyword,input_data)
        mc.mod_run(modelname,inputfile)

        r_suv = game.evaluate()[0]

        return r_suv



if __name__ == '__main__':

    model = 'NuReModel.py'
    infile = 'input'
    keyword = 'n_units'
    
    n_units_ref = [4,50,220]
    n_sigma = [2,30,30]
    pop_size = 10
    max_gen = 20
    r_mutation = 0.03
    glasshour = 5

    r_suv = game.r_suv_ini(n_units_ref,keyword,infile,model)
    
    if os.path.isfile('eco_data.txt'):
        os.remove('eco_data.txt')
    
    op = opti_ga(n_units_ref,n_sigma,pop_size,max_gen,r_mutation,r_suv,glasshour)
    op.run_ga(keyword,infile,model,game)
    
    
