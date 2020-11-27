"""
The geometric parameters are written to vbs files for electromeganetic modelling

@author: Hao Yuan
"""

import os
import re
import numpy as np

def vbs_cmd_output(it, hh, Position, GeoFerrite, flag):
    
    # Read vbs file
    filename = "WPT_baseline.vbs"
    with open(filename) as f:
        VBS_cmd = f.readlines()
    VBS_cmd = [x.strip() for x in VBS_cmd] 
    
    # Update parameters of all keywords
    #--------------------------------------------------------------------------------
    kws = ["case", "NAME:L1", "NAME:gap", "NAME:width", "NAME:length", \
           "NAME:x_P1", "NAME:y_P1", "NAME:x_P2", "NAME:y_P2", \
           "NAME:x_P3", "NAME:y_P3", "NAME:x_P4", "NAME:y_P4", \
           "NAME:x_P1_s", "NAME:y_P1_s", "NAME:x_P2_s", "NAME:y_P2_s", \
           "NAME:x_P3_s", "NAME:y_P3_s", "NAME:x_P4_s", "NAME:y_P4_s", \
           "faceid3 = ", "faceid4 = "]
    # Rearrange Position to make keywords in the same order as 'kws'
    GeoCoil = np.array([Position[8], Position[9], Position[1], Position[0]])
    # Reshape GeoFerrite to [x_P1; y_P1 ;...; x_P1_s; y_P1_s; ...]
    GeoFerrite = np.reshape(GeoFerrite,(16,1))
    # L1 and gap will be used to locate faces where excitations apply    
    L1 = Position[8]
    gap = Position[9]
    
    loc = []
    for k in range(len(kws)):
        vbs_line = [j for j in VBS_cmd if kws[k] in j]
        loc.append(VBS_cmd.index(vbs_line[0]))
        if k == 0:               
            # update case number in the format of 'it_i'
            case_loc0 = VBS_cmd.index(vbs_line[0])
            case_loc1 = VBS_cmd.index(vbs_line[1])
            case_loc2 = VBS_cmd.index(vbs_line[2])
            if flag == 0:
                VBS_cmd[case_loc0] = VBS_cmd[case_loc0].replace('0_0', str(it)+'_'+str(hh))
                VBS_cmd[case_loc1] = VBS_cmd[case_loc1].replace('0_0', str(it)+'_'+str(hh))
                VBS_cmd[case_loc2] = VBS_cmd[case_loc2].replace('0_0', str(it)+'_'+str(hh))
            else:
                VBS_cmd[case_loc0] = VBS_cmd[case_loc0].replace('0_0', str(it)+'_'+str(hh)+'_MU')
                VBS_cmd[case_loc1] = VBS_cmd[case_loc1].replace('0_0', str(it)+'_'+str(hh)+'_MU')
                VBS_cmd[case_loc2] = VBS_cmd[case_loc2].replace('0_0', str(it)+'_'+str(hh)+'_MU')
        elif k>0 and k<5:
            # update geometric parameters
            single_cmd = VBS_cmd[VBS_cmd.index(vbs_line[0])+1]
            default_number = re.findall(r"[-+]?\d*\.\d+|\d+", single_cmd)
            single_temp = single_cmd.replace(default_number[0],str(GeoCoil[k-1]))
            VBS_cmd[VBS_cmd.index(vbs_line[0])+1] = single_temp
        elif k>4 and k<21:
            # update coordinates for making ferrites
            single_cmd = VBS_cmd[VBS_cmd.index(vbs_line[0])+1]
            default_number = re.findall(r"[-+]?\d*\.\d+|\d+", single_cmd)
            single_temp = single_cmd.replace(default_number[0],str(np.asscalar(GeoFerrite[k-5])))
            VBS_cmd[VBS_cmd.index(vbs_line[0])+1] = single_temp
        elif k == 21:
            # update coordinates for face selection (faceid3)
            single_cmd1 = VBS_cmd[VBS_cmd.index(vbs_line[0])+1]
            single_cmd2 = VBS_cmd[VBS_cmd.index(vbs_line[0])+2]
            if (L1/2-gap) > (L1/2*0.1):
                single_temp1 = single_cmd1.replace("-20",str(-L1/2+gap))
            else:
                single_temp1 = single_cmd1.replace("-20",str(-L1/2*0.1))
            single_temp2 = single_cmd2.replace("190",str(200-gap))
            VBS_cmd[VBS_cmd.index(vbs_line[0])+1] = single_temp1
            VBS_cmd[VBS_cmd.index(vbs_line[0])+2] = single_temp2
        else:
            # update coordinates for face selection (faceid4)
            single_cmd1 = VBS_cmd[VBS_cmd.index(vbs_line[0])+1]
            single_temp1 = single_cmd1.replace("-150",str(-L1/2-12*gap))
            VBS_cmd[VBS_cmd.index(vbs_line[0])+1] = single_temp1
            
    # ensure the the shortest coil length is not too short or even become negative
    if (L1/2-gap) < (L1/2*0.1):
        vbs_line = [j for j in VBS_cmd if '"L1/2-gap"' in j]
        res = [sub.replace('L1/2-gap', 'L1/2*0.1') for sub in vbs_line]
        for k in range(len(res)):
            VBS_cmd[VBS_cmd.index(vbs_line[k])] = res[k]        
       
    #--------------------------------------------------------------------------------    
        
    # Write the new vbs to specific folder
    if flag == 0:
        os.chdir(str(it)+'_'+str(hh))
        OutFileName = str(it)+'_'+str(hh)+'.vbs'
        with open(OutFileName, 'w') as f_out:
            for cmd in VBS_cmd:
                f_out.write("%s\n" % cmd)
    else:
        os.chdir(str(it)+'_'+str(hh)+'_MU')
        OutFileName = str(it)+'_'+str(hh)+'_MU'+'.vbs'
        with open(OutFileName, 'w') as f_out:
            for cmd in VBS_cmd:
                f_out.write("%s\n" % cmd)
    os.chdir("..")
        
            

    