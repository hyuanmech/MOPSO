"""
Running ANSYS Maxwell in parallel

@author: Hao Yuan
"""

import os
import subprocess

def run_maxwell(cwd, it, flag, hh):
    if flag == 0:
        os.chdir(cwd+"\\"+str(it)+"_"+str(hh))
        vbs_name = str(it)+"_"+str(hh)+".vbs"
        subprocess.call(vbs_name,shell=True) 
        os.chdir("..")
    else:
        os.chdir(cwd+"\\"+str(it)+"_"+str(hh)+"_MU")
        vbs_name = str(it)+"_"+str(hh)+"_MU"+".vbs"
        subprocess.call(vbs_name,shell=True) 
        os.chdir("..")