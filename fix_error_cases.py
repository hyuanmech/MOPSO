# -*- coding: utf-8 -*-
"""
Run problematic cases manually

@author: Hao Yuan
"""

import os
from run_maxwell_parallel import run_maxwell
from functools import partial
from multiprocessing import Pool

flag = 0 # no mutation: flag = 0; mutation: flag = 1

current_loop = '16'
nPop = 100

error_cases = []

# find indexes of problematic cases
for i in range(nPop):
    if flag == 0:
        os.chdir(current_loop+'_'+str(i))
        csvname = 'case'+current_loop+'_'+str(i)+'_coupling_coefficient.csv'
        if os.path.isfile(csvname) == False:
            error_cases.append(i)
    else:
        os.chdir(current_loop+'_'+str(i)+'_MU')
        csvname = 'case'+current_loop+'_'+str(i)+'_MU_coupling_coefficient.csv'
        if os.path.isfile(csvname) == False:
            error_cases.append(i)
    os.chdir('..')
    
# re-run the problematic cases
cwd = os.getcwd()
nProcessors = 8
#------------------------------------------------------
sim_round = len(error_cases)//nProcessors
sim_remain = len(error_cases)%nProcessors
for m in range(sim_round):
    pool = Pool(nProcessors)
    func = partial(run_maxwell, cwd, current_loop, flag)
    pool.map(func, error_cases[m*nProcessors:(m+1)*nProcessors])
    pool.close()
    pool.join()
    os.system('taskkill /IM "ansysedt.exe" /F')
if sim_remain>0:
    pool = Pool(sim_remain)
    func = partial(run_maxwell, cwd, current_loop, flag)
    pool.map(func, error_cases[sim_round*nProcessors:])
    pool.close()
    pool.join()
    os.system('taskkill /IM "ansysedt.exe" /F')    
#------------------------------------------------------