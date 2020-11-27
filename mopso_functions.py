"""
Multi-Objective Particle Swarm Optimization [Coello Coello et al., 2004] 

Functions needed to implement mopso 

@author: Hao Yuan
"""

import numpy as np

# Determine the dominations of all particles    
def Domination(Position, Cost):
    # if a position is dominated, the corresponding value is set to 1
    IsDominated = np.zeros(Position.shape[0])
    # loop cost value of each particle and determines domination
    for i in range(Position.shape[0]-1):
        for j in range(i+1,Position.shape[0]):
            compare_0p = np.where((Cost[i]-Cost[j])>0)
            compare_0m = np.where((Cost[i]-Cost[j])<0)
            if compare_0p[0].size == 0:
                IsDominated[j] = 1
            elif compare_0m[0].size == 0:
                IsDominated[i] = 1
            else:
                IsDominated = IsDominated
    return IsDominated

# Create grid based on the cost                    
def CreateGrid(Cost, nGrid, alpha):
    # get the range of Cost values
    cmin = np.amin(Cost, axis=0)
    cmax = np.amax(Cost, axis=0)
    # inflate the range by factor alpha
    dc = cmax-cmin
    cmin=cmin-alpha*dc
    cmax=cmax+alpha*dc
    # build Grid to store lB and UB of each objective function
    nObj = Cost.shape[1]
    Grid = []
    for i in range(nObj):
        ci = np.linspace(cmin[i], cmax[i], num=nGrid+1)
        Grid.append(np.append(-np.inf, ci))   # stores LB for ith objective function
        Grid.append(np.append(ci, np.inf))    # stores UB for ith objective function
    return Grid

# Get arbitrarily determined GridIndex for each particle
def FindGridIndex(Grid, Cost):
    nParticle = Cost.shape[0]
    nObj = Cost.shape[1]
    Grid_num = Grid[0].shape[0]
    # GridSubIndex stores indexes of results of all objective functions
    GridSubIndex = np.zeros((nParticle,nObj))
    # GridIndex stores arbitrarily determined overall index of each particle
    GridIndex = np.zeros(nParticle)
    # get indexes of results of all objective functions
    for i in range(nParticle):
        for j in range(nObj):
            Cost_diff = Grid[2*j+1]-Cost[i][j]
            GridSubIndex[i][j] = np.where(Cost_diff > 0, Cost_diff, np.inf).argmin()
    # calculate the overall indexes using the equation a = (a-1)*Grid_num+b, where a and b 
    # represent indexes of results of neighboring objective functions [..., a, b, ...]
    for i in range(nParticle):
        GridIndex[i] = GridSubIndex[i][0]
        for j in range(1,nObj):
            GridIndex[i] = (GridIndex[i]-1)*Grid_num + GridSubIndex[i][j]
    return GridIndex

# Select the global best position
# This function first gets all GridIndexes and groups them based on the values.
# Then, probablities are assigned to all these groups, which are inversely
# proportional to the number of particles contained. Finally, Roulette
# Wheel selection is performed to select a group, and the 'leader' is
# randomly selected from the group.
def SelectLeader(Position, GridIndex, beta):
    leader = np.zeros((1,Position.shape[1]))
    # group identical indexes and get their counts
    [OC, N] = np.unique(GridIndex, return_counts=True)
    # assign possibility to each group
    # group with more particles has a smaller possibility to be chosen
    P = np.exp(-beta*N)
    P = P/np.sum(P)
    # Roulette Wheel selection to get selected cell index (sci)
    r = np.random.rand(1)
    Pcum = np.cumsum(P)
    sci = np.where((Pcum-r) > 0, (Pcum-r), np.inf).argmin()
    # select the cell 
    sc = OC[sci]
    # select cell member with the index of sc
    scm = np.where(GridIndex == sc)
    # randomly choose a member from the group with the index of sc
    smi = np.random.randint(scm[0].shape[0], size=1)
    # sm is the index of the leader
    sm = scm[0][int(smi)]
    leader = Position[sm]
    return leader        

# Apply mutation to randomly selected positions
# Note that original and mutated positions should be stored separately in matrix format 
# to implement parallel modelling at each iteration
def Mutation(Position, it, MaxIt, mu, VarMin, VarMax):
    # pm=[0 1] drops rapidly from 1 with the increase of it
    MutatedPosition = []
    pm = (1-it/MaxIt)**(1/mu)
    # generate an array r of random values between 0 and 1
    r = np.random.rand(Position.shape[0])
    # mutate the position if r<pm
    index_mu = np.where(r-pm < 0)
    Position_mu = np.zeros((index_mu[0].shape[0], Position.shape[1]))
    for i in range(index_mu[0].shape[0]):
        Position_mu[i,:] = Position[index_mu[0][i],:]
        # randomly select a dimension k of the position
        k = np.random.randint(Position.shape[1], size=1)
        # add mutation to the range of the selected dimension but limit it to [VarMin VarMax]
        dx = pm*(VarMax[i][k]-VarMin[i][k])
        LB = np.maximum(Position_mu[i][k]-dx, VarMin[i][k])
        UB = np.minimum(Position_mu[i][k]+dx, VarMax[i][k])
        # mutate the selected dimension given the range [LB UB]
        Position_mu[i][k] = np.random.uniform(LB, UB, size=1)
        # export index_mu for further comparsion
        MutatedPosition = [index_mu[0], Position_mu]
    return MutatedPosition

# Delete extra particles from repository
# This function works similar to SelectLeader, but assigns possibilities in 
# proportional to the number of positions in each group
def DeleteOneRepMemebr(Position_rep, Cost_rep, GridIndex, gamma):
    # group identical indexes and get their counts
    [OC, N] = np.unique(GridIndex, return_counts=True)
    # assign possibility to each group
    # group with more particles has a larger possibility to be chosen
    P = np.exp(gamma*N);
    P = P/np.sum(P);
    # Roulette Wheel selection to get selected cell index (sci)
    r = np.random.rand(1)
    Pcum = np.cumsum(P)
    sci = np.where((Pcum-r) > 0, (Pcum-r), np.inf).argmin()
    # select the cell 
    sc = OC[sci]
    # select cell member with the index of sc
    scm = np.where(GridIndex == sc)
    # randomly choose a member from the group with the index of sc
    smi = np.random.randint(scm[0].shape[0], size=1)
    # sm is the index of the position to be deleted
    sm = scm[0][int(smi)]
    # delete the selected position
    Position_rep = np.delete(Position_rep,sm,0)
    Cost_rep = np.delete(Cost_rep,sm,0)
    GridIndex = np.delete(GridIndex,sm,0)
    Remain_rep = [Position_rep, Cost_rep, GridIndex]
    return Remain_rep

# Test only!!! ZDT gives all costs for all positions
def ZDT(Position):
    nParticle = Position.shape[0]
    nDim = Position.shape[1]
    Cost = np.zeros((nParticle, 2))
    for i in range(nParticle):
        f1 = Position[i][0]
        g = 1+9/(nDim-1)*np.sum(Position[i][1:])
        h = 1-np.sqrt(f1/g)
        f2 = g*h
        Cost[i][0] = f1
        Cost[i][1] = f2
    return Cost    