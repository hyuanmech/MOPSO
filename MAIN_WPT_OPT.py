"""
Multi-Objective Particle Swarm Optimization [Coello Coello et al., 2004] 

Main program for mopso

@author: Hao Yuan
"""

import os
import dill
import numpy as np
import matplotlib.pyplot as plt
from mopso_functions import Domination, CreateGrid, FindGridIndex, SelectLeader, Mutation, DeleteOneRepMemebr   
from ferrite_geo_variation import geometry_parameters
from geo_parameters_update import vbs_cmd_output
from run_maxwell_parallel import run_maxwell
from functools import partial
from multiprocessing import Pool
from GeoConstrain import GeoConstrain
import csv

if __name__ == "__main__":
    
    # MOPSO parameters
    #==========================================================================
    nVar = 10     # number of decision variables

    MaxIt = 10      # maximum number of iterations
    nPop = 100      # population size 
    nRep = 50      # repository size
    
    VarMin = np.zeros((nPop, nVar))     # lower bound of variables 
    VarMax = np.zeros((nPop, nVar))     # upper bound of variables
    
    w = 0.5         # inertia weight
    wdamp = 0.99    # innertia weight damping rate
    c1 = 1          # personal learning coefficient
    c2 = 2          # global learning coefficient
    
    nGrid = 10      # number of grids per dimension
    alpha = 0.1     # inflation rate
    beta = 2        # leader selection pressure
    gamma = 2       # deletion selection pressure
    mu = 0.1        # mutation rate
    
    # Initialization
    #==========================================================================
    # initialize positions randomly and build vbs file for each position
    it = -1
    Position = np.zeros((nPop, nVar))
    for i in range(nPop):
        [P_single, GeoFerrite, LowerLimit, UpperLimit] = geometry_parameters(it,i,nVar)
        Position[i,:] = P_single
        VarMin[i,:] = LowerLimit
        VarMax[i,:] = UpperLimit
        flag = 0
        vbs_cmd_output(it, i, Position[i], GeoFerrite, flag)
        
    # initial velocities are all zeros
    Velocity = np.zeros((nPop, nVar))
    
    # eletromagenetic modelling with Maxwell
    cwd = os.getcwd()
    nProcessors = 8
    
    dill.dump_session('All_variables.db')
    dill.load_session('All_variables.db')
    #------------------------------------------------------
    flag = 0
    sim_round = nPop//nProcessors
    sim_remain = nPop%nProcessors
    for m in range(sim_round):
        pool = Pool(nProcessors)
        func = partial(run_maxwell, cwd, it, flag)
        pool.map(func, list(range(nPop))[m*nProcessors:(m+1)*nProcessors])
        pool.close()
        pool.join()
        os.system('taskkill /IM "ansysedt.exe" /F')
    if sim_remain>0:
        pool = Pool(sim_remain)
        func = partial(run_maxwell, cwd, it, flag)
        pool.map(func, list(range(nPop))[sim_round*nProcessors:])
        pool.close()
        pool.join()
        os.system('taskkill /IM "ansysedt.exe" /F')    
    #------------------------------------------------------
    
    # extract cost
    Cost = np.zeros((nPop, 2))
    for i in range(nPop):
        Cost[i,0] = Position[i,0]**2*1e-6
        os.chdir(cwd+"\\"+str(it)+"_"+str(i))
        with open('case'+str(it)+'_'+str(i)+'_coupling_coefficient.csv') as csv_file:
            csv_reader = csv.reader(csv_file, delimiter=',')
            k = 0
            for row in csv_reader:
                if k == 1:
                    Cost[i,1] = 1/float(row[1])
                k = k+1                
    os.chdir(cwd)
                
    # initial positions and costs are assumed to be 'best'
    Position_best = Position
    Cost_best = Cost
    
    # determine domination for the initialized positions
    IsDominated = Domination(Position, Cost)
    # store non-dominated positions in repository
    Position_rep = Position[np.where(IsDominated==0)]
    Cost_rep = Cost[np.where(IsDominated==0)]
    # create grid for positions in repository
    Grid = CreateGrid(Cost_rep, nGrid, alpha)
    # get GridIndex for each position in repository
    GridIndex = FindGridIndex(Grid, Cost_rep)
    
    # MOPSO main loop
    #==========================================================================
    for it in range(MaxIt):
        dill.dump_session('All_variables.db')
        dill.load_session('All_variables.db')
        for i in range(nPop):
            # select the global best position
            #------------------------------------------------------------------
            leader = SelectLeader(Position_rep, GridIndex, beta)
            # update velocities
            Velocity[i,:]=w*Velocity[i,:]+c1*np.random.uniform(0,1,size=nVar)\
            *(Position_best[i]-Position[i])+c2*np.random.uniform(0,1,size=nVar)\
            *(leader-Position[i])
            # update positions
            Position[i] = Position[i]+Velocity[i]
            # limit dimensions of positions within the range
            flag = 0 # no mutation: flag = 0; mutation: flag = 1
            [Position[i], GeoFerrite, LowerLimit, UpperLimit] = \
            GeoConstrain(Position[i], nVar, it, i, flag)
            VarMin[i,:] = LowerLimit
            VarMax[i,:] = UpperLimit
            vbs_cmd_output(it, i, Position[i], GeoFerrite, flag)
            
        del csv_reader
        dill.dump_session('All_variables.db')
        dill.load_session('All_variables.db')
        # eletromagenetic modelling with Maxwell
        #------------------------------------------------------
        flag = 0
        sim_round = nPop//nProcessors
        sim_remain = nPop%nProcessors
        for m in range(sim_round):
            pool = Pool(nProcessors)
            func = partial(run_maxwell, cwd, it, flag)
            pool.map(func, list(range(nPop))[m*nProcessors:(m+1)*nProcessors])
            pool.close()
            pool.join()
            os.system('taskkill /IM "ansysedt.exe" /F')
        if sim_remain>0:
            pool = Pool(sim_remain)
            func = partial(run_maxwell, cwd, it, flag)
            pool.map(func, list(range(nPop))[sim_round*nProcessors:])
            pool.close()
            pool.join()
            os.system('taskkill /IM "ansysedt.exe" /F')    
        #------------------------------------------------------
        
        # extract cost
        Cost = np.zeros((nPop, 2))
        for i in range(nPop):
            Cost[i,0] = Position[i,0]**2*1e-6
            os.chdir(cwd+"\\"+str(it)+"_"+str(i))
            with open('case'+str(it)+'_'+str(i)+'_coupling_coefficient.csv') as csv_file:
                csv_reader = csv.reader(csv_file, delimiter=',')
                k = 0
                for row in csv_reader:
                    if k == 1 and row[1]:
                        Cost[i,1] = 1/float(row[1])
                    k = k+1
        os.chdir(cwd)
           
        # apply mutation
        #------------------------------------------------------------------
        MutatedPosition = Mutation(Position, it, MaxIt, mu, VarMin, VarMax)
        
        # compute cost_mu if MutatedPosition is not empty
        if MutatedPosition:
            index_mu = list(MutatedPosition[0])
            Position_mu = MutatedPosition[1]
            flag = 1 # no mutation: flag = 0; mutation: flag = 1
            VarMin_mu = np.zeros((len(index_mu), nVar))
            VarMax_mu = np.zeros((len(index_mu), nVar))
            for i in range(len(index_mu)):
                [Position_mu[i], GeoFerrite, LowerLimit, UpperLimit] = \
                GeoConstrain(Position_mu[i], nVar, it, index_mu[i], flag)
                VarMin_mu[i,:] = LowerLimit
                VarMax_mu[i,:] = UpperLimit
                vbs_cmd_output(it, index_mu[i], Position_mu[i], GeoFerrite, flag)
        
        del csv_reader
        del pool
        del wb
        del sheet
        dill.dump_session('All_variables.db')
        dill.load_session('All_variables.db')
        # eletromagenetic modelling with Maxwell
        #------------------------------------------------------
        flag = 1
        sim_round = nPop//nProcessors
        sim_remain = nPop%nProcessors
        for m in range(sim_round):
            pool = Pool(nProcessors)
            func = partial(run_maxwell, cwd, it, flag)
            pool.map(func, index_mu[m*nProcessors:(m+1)*nProcessors])
            pool.close()
            pool.join()
            os.system('taskkill /IM "ansysedt.exe" /F')
        if sim_remain>0:
            pool = Pool(sim_remain)
            func = partial(run_maxwell, cwd, it, flag)
            pool.map(func, index_mu[sim_round*nProcessors:])
            pool.close()
            pool.join()
            os.system('taskkill /IM "ansysedt.exe" /F')    
        #------------------------------------------------------
            
        # extract cost of mutated position
        Cost_mu = np.zeros((len(index_mu), 2))
        for i in range(len(index_mu)):
            Cost_mu[i,0] = Position_mu[i,0]**2*1e-6
            os.chdir(cwd+"\\"+str(it)+"_"+str(index_mu[i])+"_MU")
            with open('case'+str(it)+'_'+str(index_mu[i])+'_MU'+'_coupling_coefficient.csv') as csv_file:
                csv_reader = csv.reader(csv_file, delimiter=',')
                k = 0
                for row in csv_reader:
                    if k == 1 and row[1]:
                        Cost_mu[i,1] = 1/float(row[1])
                    k = k+1
                  
        # determine the domination between mutated and original costs
        # if neither dominates, randomly choose one
#        index_mu = index_mu.astype(int)[:,0].tolist()
        for j in range(len(index_mu)):
            compare_mu_0p = np.where((Cost[index_mu[j]]-Cost_mu[j])>0)
            compare_mu_0m = np.where((Cost[index_mu[j]]-Cost_mu[j])<0)
            if compare_mu_0p[0].size == 0:
                Position[index_mu[j]] = Position[index_mu[j]]
                Cost[index_mu[j]] = Cost[index_mu[j]]
            elif compare_mu_0m[0].size == 0:
                Position[index_mu[j]] = Position_mu[j]
                Cost[index_mu[j]] = Cost_mu[j]
            else:
                if np.random.rand(1)<0.5:
                    Position[index_mu[j]] = Position_mu[j]
                    Cost[index_mu[j]] = Cost_mu[j]
                            
        # update personal best
        #------------------------------------------------------------------
        for k in range(nPop):
            compare_best_0p = np.where((Cost[k]-Cost_best[k])>0)
            compare_best_0m = np.where((Cost[k]-Cost_best[k])<0)
            if compare_best_0p[0].size == 0:
                Position_best[k] = Position[k]
                Cost_best[k] = Cost[k]
            elif compare_best_0m[0].size == 0:
                Position_best[k] = Position_best[k]
                Cost_best[k] = Cost_best[k]
            else:
                if np.random.rand(1)<0.5:
                    Position_best[k] = Position[k]
                    Cost_best[k] = Cost[k]
                
        # add current positions to repository and go through selection process
        #---------------------------------------------------------------------
        # concatenate Position_rep and Position
        Position_all = np.concatenate((Position_rep, Position), axis=0)
        Cost_all = np.concatenate((Cost_rep, Cost), axis=0)
        
        # determine domination for combined positions
        IsDominated_all = Domination(Position_all, Cost_all)
        # store non-dominated positions in repository
        Position_rep = Position_all[np.where(IsDominated_all==0)]
        Cost_rep = Cost_all[np.where(IsDominated_all==0)]
        # create grid for positions in repository
        Grid = CreateGrid(Cost_rep, nGrid, alpha)
        # get GridIndex for each position in repository
        GridIndex = FindGridIndex(Grid, Cost_rep)
        
        # remove random positions if repository is overloaded
        #---------------------------------------------------------------------
        if Position_rep.shape[0]>nRep:
            extra = Position_rep.shape[0]-nRep
            for e in range(extra):
                Remain_rep = DeleteOneRepMemebr(Position_rep, Cost_rep, GridIndex, gamma)
                Position_rep = Remain_rep[0]
                Cost_rep = Remain_rep[1]
                GridIndex = Remain_rep[2]
                
        # damp inertia weight
        w = w*wdamp
                
        # plot costs (assuming two objective functions)
        #----------------------------------------------------------------------
        print(it)
        if it % 1 == 0:
            fig = plt.figure()
            plt.plot(Cost[:,0], Cost[:,1], marker = 'o', color = 'r', \
                     markerfacecolor = 'none', linestyle = 'none')
            plt.plot(Cost_rep[:,0], Cost_rep[:,1], marker = 'o', color = 'k', \
                     markerfacecolor = 'none', linestyle = 'none')
            



  