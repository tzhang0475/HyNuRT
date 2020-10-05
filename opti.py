#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# File              : opti.py
# Author            : tzhang
# Date              : 03.08.2020
# Last Modified Date: 05.10.2020
# Last Modified By  : tzhang

"""

modules to optimize number of units in the system 

"""


"""

optimize number of units in the system by genetic algorithms

- S.Singh, K.S. Vermab Optimal Power Flow using Genetic Algorithm andParticle Swarm
Optimization IOSR Journal of Engineering (IOSRJEN) Vol. 2 Issue 1, Jan.2012, pp. 046-049

"""
import os
import random
import numpy as np
import matplotlib as plt
from prepost_process import mod_control as mc
from prepost_process import post_process as postp

import sys

class opti_ga:
    def __init__(self,n_units_ref,n_sigma,pop_size,max_gen,r_mutation,r_suv,hourglass):
         # set general parameters
        self.chromosome_start = n_units_ref
        self.n_sigma = n_sigma
        self.pop_size = pop_size
        self.max_gen = max_gen
        self.r_mutation = r_mutation
        self.r_suv = r_suv

        self.hourglass = hourglass
        self.best_score_progress = [] # track progress

    # create some starting random population
    def creation(self):
        # set up an initial array of all zeros
        ancestors = []
        # loop through each row (individual)
        for i in range(self.pop_size):
            ancestor = []

            # Choose a random number of units to create
            for j in range(len(self.n_sigma)):
                var = random.randint(-self.n_sigma[j], self.n_sigma[j])
                # change the number of units accordingly
                mortal = self.chromosome_start[j] + var
                ancestor.append(mortal)

            ancestors.append(ancestor) 
    
        return ancestors


    # run the model and get scores
    def play_game(self,population,keyword,inputfile,modelname):

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
    def evaluate(self):
        scores = []
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
        print ('system score is:', max(scores))
        return scores

    # a function to select qualified population 
    def killer(self,population,scores,seed = None):
        
        suvivals = []
        suv_score = [] 

        d = 5

        # add former best score if exists
        if seed != None:
            suvivals.append(seed)
            suv_score.append(seed[1])

        for i in range(len(scores)):

            suv_data = []

            if scores[i] >= self.r_suv:
                suv_data.append(population[i])
                suv_data.append(scores[i])
                suv_score.append(scores[i])
                suvivals.append(suv_data)
            else:
                # suvival with russian roulette
                rad = random.random()
                if rad <= (1/d):
                    suv_data.append(population[i])
                    suv_data.append(scores[i])
                    suv_score.append(scores[i])
                    suvivals.append(suv_data)
        
        if len(suv_score) != 0.0:
            r_suv_new = sum(suv_score)/len(suv_score)
            if r_suv_new > self.r_suv:
                self.r_suv = r_suv_new

        return suvivals

    # record seed data
    def seed_selector(self,suvivals):

        suv_score = []
        
        for doc in suvivals:
            suv_score.append(doc[1]) 

        seed_idx = suv_score.index(max(suv_score))

        seed = suvivals[seed_idx]

        return seed
            
    
    # a mechanism to select next generation
    def select_individual_by_tournament(self,suvivals):
    
        # pick individuals for tournament
        fighter_1 = random.randint(0,len(suvivals)-1)
        fighter_2 = random.randint(0,len(suvivals)-1)
    
        # get fitness score for each
        fighter_1_fitness = suvivals[fighter_1][1]
        fighter_2_fitness = suvivals[fighter_2][1]
    
        # identify undividual with highest fitness
        # fighter 1 will win if score are equal
        if fighter_1_fitness >= fighter_2_fitness:
            winner = fighter_1
        else:
            winner = fighter_2
    
        # return the chromosome of the winner
        return suvivals[winner][0]

    # crossover
    def breed_by_crossover(self,parent_1,parent_2):
        child = []

        for i in range(len(parent_1)):
            eta = random.random()
            n_new = int(eta*parent_1[i] + (1-eta)*parent_2[i])

            child.append(n_new)

        return child

    
    # random mutation
    def randomly_mutate(self,child):

        child_new = []

        for gene in child:

            # convert to binary
            gene_bin = '{0:b}'.format(gene)    

            # apply random mutation
            random_mutation_array = np.random.random(size = (len(gene_bin)))
            random_mutation_boolean = random_mutation_array <= self.r_mutation

            # a boolean function see if random_mutation_array <= mutation_probablity true or false, return true/false
            gene_bin_new = []
            for i in range(len(random_mutation_boolean)):
                if random_mutation_boolean[i]:
                    gene_bin_new.append(str(abs(int(gene_bin[i])-1)))
                else:
                    gene_bin_new.append(gene_bin[i])

            gene_bin_new = ''.join(gene_bin_new)

            # convert to demical
            gene_new = int(str(gene_bin_new),2)

            if gene_new == 0:
                gene_new = gene
            
            child_new.append(gene_new)

        # return mutation population
        return child_new

    def run_ga(self,keyword,inputfile,modelname,game):
    #def run_ga(self):
    
        # create ancestors
        ancestors = self.creation()
        
        # to be come mature and being evaluated
        game.play_game(ancestors,keyword,inputfile,modelname)
        scores = game.evaluate()
        best_score = np.max(scores)
        # Add starting best score to progress tracker
        self.best_score_progress.append(best_score)
         
        # selection
        suvivals = self.killer(ancestors,scores)
        print (suvivals)
        if len(suvivals) == 0:
            print ('*** MASSACRE! ***')
            sys.exit()

        # select seed
        seed = self.seed_selector(suvivals)

        best_score = seed[1]
        print ('Starting best score, percent target: %.3f' %best_score)
        # set reset value of hourglass
        timer_reset = self.hourglass

        #print (seed)
        with open('ga.log','w+') as f:
            f.write('begin recording'+'\n')
            for data in suvivals:
                f.write(str(data))
                f.write('\n')

            f.write('batch-done\n')
            f.close()

    
        # go through the generations of genetic algorithm
        for generation in range(self.max_gen):

            print ('\n')
            print ('current population generation',generation)
            print ('\n')
                
            # create an empty list for new population
            children = []
    
            # create new population generating a child at a time
            for i in range(self.pop_size):
                parent_1 = self.select_individual_by_tournament(suvivals)
                parent_2 = self.select_individual_by_tournament(suvivals)
                #print (parent_1,parent_2)
                # cross over
                child = self.breed_by_crossover(parent_1,parent_2)
                #print (child)
                # apply mutation
                child = self.randomly_mutate(child)
                if child not in children:
                    children.append(child)
                #print (child)

             # to be come mature and being evaluated
            game.play_game(children,keyword,inputfile,modelname)
            scores = game.evaluate()
   
            # selection
            suvivals = self.killer(children,scores,seed)
            print ('suvivals',suvivals)

            # select seed
            seed_new = self.seed_selector(suvivals)

            best_score = seed_new[1]
            print ('Best score in current round: %.3f' %best_score)
            print ('Best data in current round: ',seed_new[0])
            # Add starting best score to progress tracker
            self.best_score_progress.append(best_score)
           # print (seed_new)

            # data counter
            if seed_new == seed:
                self.hourglass = self.hourglass - 1
                print ('tik')
                if self.hourglass == 0:
                    print ('time is up!')
                    # plot progress
                    postp.plt_GA(self.best_score_progress)
                    sys.exit()
            else:
                seed = seed_new
                # reset hourglass
                self.hourglass = timer_reset

                print ('reset')
            with open('ga.log','a') as f:
                for data in suvivals:
                    f.write(str(data))
                    f.write('\n')

                f.write('batch-done\n')
            f.close()


        # GA has completed required generation
        print('End best score: %.3f' %best_score)
        print ('End best data: ',seed_new[0])
        
        # plot progress
        postp.plt_GA(self.best_score_progress)

        with open ('ga_data.txt','w+') as f:
            for i in range(len(self.best_score_progress):
                    f.write(str(i+1)+'  ')
                    f.write(str(self.best_score_progress[i])+'\n')


"""

a test module of GA


n_units_ref = [6,60,200]
n_sigma = [4,40,100]
pop_size = 20
max_gen = 20
r_mutation = 0.2
r_suv = 0.2
hourglass = 5

op = opti_ga(n_units_ref,n_sigma,pop_size,max_gen,r_mutation,r_suv,hourglass)
op.run_ga()


"""
