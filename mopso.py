"""
Multi-Objective Particle Swarm Optimization [Coello Coello et al., 2004] 

Main program for mopso

@author: Hao Yuan
"""

import os
import numpy as np
import matplotlib.pyplot as plt
from mopso_functions import Domination, CreateGrid, FindGridIndex, SelectLeader, Mutation, DeleteOneRepMemebr, ZDT    
from ferrite_geo_variation import geometry_parameters
from geo_parameters_update import vbs_cmd_output
from run_maxwell_parallel import run_maxwell
from functools import partial
from multiprocessing import Pool

if __name__ == "__main__":
    
    # MOPSO parameters
    #==========================================================================
    nVar = 10     # number of decision variables

    MaxIt = 10      # maximum number of iterations
    nPop = 8       # population size 
    nRep = 100      # repository size
    
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
    cwd = os.getcwd()
    it = -1
    nProcessors = 4
    nRuns = nPop//nProcessors
    remain = nPop%nProcessors
    Position = np.zeros((nPop, nVar))
    GeoFerriteAll = []
    for hh in range(nRuns):
        for i in range(nProcessors):
            [P_single, GeoFerrite, LowerLimit, UpperLimit] = \
            geometry_parameters(it,nRuns*nProcessors+i,nVar)
            Position[nRuns*nProcessors+i,:] = P_single
            VarMin[nRuns*nProcessors+i,:] = LowerLimit
            VarMax[nRuns*nProcessors+i,:] = UpperLimit
            GeoFerriteAll.append(GeoFerrite)
            vbs_cmd_output(it, nRuns*nProcessors+i, Position, GeoFerrite)
            
        # initial costs
        pool = Pool(nProcessors)
        func = partial(run_maxwell, cwd, it)
        pool.map(func, list(range(nRuns*nProcessors, (nRuns+1)*nProcessors)))
        pool.close()
        pool.join()
        os.system('taskkill /IM "ansysedt.exe" /F')

        
    # initial velocities are all zeros
    Velocity = np.zeros((nPop, nVar))
    
    
    
    
    
    
    
    
    
    
    

    
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
            Position[i] = np.maximum(Position[i],VarMin)
            Position[i] = np.minimum(Position[i],VarMax)
            
            # apply mutation
            #------------------------------------------------------------------
            MutatedPosition = Mutation(Position, it, MaxIt, mu, VarMin, VarMax)
                            
        # compute cost
        # cost must be outside of the inner loop for parallel computation
        #---------------------------
        Cost = ZDT(Position)
        #---------------------------
        
        # compute cost_mu if MutatedPosition is not empty
        if MutatedPosition:
            index_mu = MutatedPosition[0]
            Position_mu = MutatedPosition[1]
            # compute cost
            #---------------------------
            Cost_mu = ZDT(Position_mu)
            #---------------------------
            # determine the domination between mutated and original costs
            # if neither dominates, randomly choose one
            for j in range(index_mu.shape[0]):
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

  