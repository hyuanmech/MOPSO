# -*- coding: utf-8 -*-
"""
Created on Tue Dec 17 20:53:38 2019

@author: yuanh
"""
import numpy as np
import os
import matplotlib.pyplot as plt

def GeoConstrain(Position, nVar, it, hh, flag):
    
    LowerLimit = np.zeros((nVar,1))
    UpperLimit = np.zeros((nVar,1))
    
    Position_cons = np.zeros((nVar,1))
	
    LowerLimit[0] = 300
    UpperLimit[0] = 600	
    length = np.maximum(Position[0], LowerLimit[0])
    length = np.minimum(length, UpperLimit[0])
    Position_cons[0] = length    
    	
    LowerLimit[1] = 30
    UpperLimit[1] = 60	
    width = np.maximum(Position[1], LowerLimit[1])
    width = np.minimum(width, UpperLimit[1])
    Position_cons[1] = width
    
    diag_length = (length-width)/2/np.sin(np.deg2rad(45))
    r1 = 0.1
    r2 = 0.4
    LowerLimit[2] = np.floor(diag_length*r1)
    UpperLimit[2] = np.ceil(diag_length*r2)
    d1_diag = np.maximum(Position[2], LowerLimit[2])
    d1_diag = np.minimum(d1_diag, UpperLimit[2])
    Position_cons[2] = d1_diag
    
    r_ref = d1_diag/diag_length # ensure the long edge is longer than the short one
    r3 = 0.5
    LowerLimit[3] = np.floor(diag_length*r3)
    UpperLimit[3] = np.floor(diag_length*(1-r_ref))
    d2_diag = np.maximum(Position[3], LowerLimit[3])
    d2_diag = np.minimum(d2_diag, UpperLimit[3])
    Position_cons[3] = d2_diag
    
    # range of the length of short edge
    L_short_max = 2*d1_diag*0.98
    r5 = 0.5
    r6 = 1
    LowerLimit[4] = np.floor(L_short_max*r5)
    UpperLimit[4] = np.ceil(L_short_max*r6)
    L_short = np.maximum(Position[4], LowerLimit[4])
    L_short = np.minimum(L_short, UpperLimit[4]*0.9)
    Position_cons[4] = L_short
    
    # range of the angle of trapezoid
    # theta_min constrains the ferrite within the boundary
    L_long_max = (diag_length-d2_diag)*2*0.9
    theta_min = np.degrees(np.arctan((d2_diag-d1_diag)/((L_long_max-L_short)/2)))
    LowerLimit[5] = theta_min
    UpperLimit[5] = 89.9
    theta = np.maximum(Position[5], LowerLimit[5])
    theta = np.minimum(theta, UpperLimit[5])
    Position_cons[5] = theta
    
    # range of the gap on the short edge
    r7 = 0.5
    LowerLimit[6] = 1
    UpperLimit[6] = np.floor(L_short*r7)
    g1 = np.maximum(Position[6], LowerLimit[6])
    g1 = np.minimum(g1, UpperLimit[6])
    Position_cons[6] = g1
    
    # range of the gap on the long edge
    L_long = L_short+(d2_diag-d1_diag)/\
    np.tan(np.deg2rad(theta))*2 # length of the short edege of trapezoid
    LowerLimit[7] = 1
    UpperLimit[7] = np.floor(L_long-(L_short-g1))
    g2 = np.maximum(Position[7], LowerLimit[7])
    g2 = np.minimum(g2, UpperLimit[7])
    Position_cons[7] = g2
    
    LowerLimit[8] = 10
    UpperLimit[8] = np.floor((length/2-12*5)*2)
    L1 = np.maximum(Position[8], LowerLimit[8])
    L1 = np.minimum(L1, UpperLimit[8])
    Position_cons[8] = L1
    
    LowerLimit[9] = 5
    UpperLimit[9] = np.floor((length-L1)/2/12)
    gap = np.maximum(Position[9], LowerLimit[9])
    gap = np.minimum(gap, UpperLimit[9])
    Position_cons[9] = gap
    
    # Calculate coordinates of corners of ferrite
    x_M1 = d1_diag*np.sin(np.deg2rad(45)) # x of the middle point on the short edge
    y_M1 = d1_diag*np.cos(np.deg2rad(45)) # y of the middle point on the short edge
    L_M1P1 = g1/2 # distance between M1 and P1 (northwest point of the ferrite)
    x_P1 = x_M1+L_M1P1*np.sin(np.deg2rad(45)) # x of P1
    y_P1 = y_M1-L_M1P1*np.cos(np.deg2rad(45)) # y of P1
    L_M1P2 = L_short/2 # distance between M1 and P2 (southwest point of the ferrite)
    x_P2 = x_M1+L_M1P2*np.sin(np.deg2rad(45)) # x of P2
    y_P2 = y_M1-L_M1P2*np.cos(np.deg2rad(45)) # y of P2
    
    x_M2 = d2_diag*np.sin(np.deg2rad(45)) # x of the middle point on the long edge
    y_M2 = d2_diag*np.cos(np.deg2rad(45)) # y of the middle point on the long edge
    L_M2P3 = g2/2 # distance between M2 and P3 (northeast point of the ferrite)
    x_P3 = x_M2+L_M2P3*np.sin(np.deg2rad(45)) # x of P3
    y_P3 = y_M2-L_M2P3*np.cos(np.deg2rad(45)) # y of P3
    L_long = L_short+(d2_diag-d1_diag)/\
    np.tan(np.deg2rad(theta))*2 # length of the short edege of trapezoid
    L_M2P4 = L_long/2 # # distance between M2 and P4 (southeast point of the ferrite)
    x_P4 = x_M2+L_M2P4*np.sin(np.deg2rad(45)) # x of P4
    y_P4 = y_M2-L_M2P4*np.cos(np.deg2rad(45)) # y of P4
    
    x_P1_s = x_P1-g1*np.sin(np.deg2rad(45)) # x of P1_s which the symmetric point of P1
    y_P1_s = y_P1+g1*np.cos(np.deg2rad(45)) # y of P1_s which the symmetric point of P1
    x_P2_s = x_P2-L_short*np.sin(np.deg2rad(45)) # x of P2_s which the symmetric point of P2
    y_P2_s = y_P2+L_short*np.cos(np.deg2rad(45)) # y of P2_s which the symmetric point of P2
    x_P3_s = x_P3-g2*np.sin(np.deg2rad(45)) # x of P3_s which the symmetric point of P3
    y_P3_s = y_P3+g2*np.cos(np.deg2rad(45)) # y of P3_s which the symmetric point of P3
    x_P4_s = x_P4-L_long*np.sin(np.deg2rad(45)) # x of P4_s which the symmetric point of P4
    y_P4_s = y_P4+L_long*np.cos(np.deg2rad(45)) # y of P4_s which the symmetric point of P4
    
    x_P1 = np.asscalar(np.array(x_P1))
    y_P1 = np.asscalar(np.array(y_P1))
    x_P2 = np.asscalar(np.array(x_P2))
    y_P2 = np.asscalar(np.array(y_P2))
    x_P3 = np.asscalar(np.array(x_P3))
    y_P3 = np.asscalar(np.array(y_P3))
    x_P4 = np.asscalar(np.array(x_P4))
    y_P4 = np.asscalar(np.array(y_P4))
    x_P1_s = np.asscalar(np.array(x_P1_s))
    y_P1_s = np.asscalar(np.array(y_P1_s))
    x_P2_s = np.asscalar(np.array(x_P2_s))
    y_P2_s = np.asscalar(np.array(y_P2_s))
    x_P3_s = np.asscalar(np.array(x_P3_s))
    y_P3_s = np.asscalar(np.array(y_P3_s))
    x_P4_s = np.asscalar(np.array(x_P4_s))
    y_P4_s = np.asscalar(np.array(y_P4_s))
    
    GeoFerrite = np.array([[x_P1, y_P1],[x_P2, y_P2],[x_P3, y_P3],[x_P4, y_P4],\
                       [x_P1_s, y_P1_s],[x_P2_s, y_P2_s],[x_P3_s, y_P3_s],[x_P4_s, y_P4_s]])
    
    output_coil = np.zeros((13*4+1, 2)) 
    output_coil[0,0] = np.maximum(L1/2-gap, L1/2*0.1)
    output_coil[0,1] = -L1/2
    output_coil[1,0] = -L1/2
    output_coil[1,1] = output_coil[0,1] 
    output_coil[2,0] = output_coil[1,0]
    output_coil[2,1] = output_coil[1,1]+L1
    output_coil[3,0] = output_coil[2,0]+L1
    output_coil[3,1] = output_coil[2,1]
    
    for i in range(1,13):
        output_coil[4*i,0] = output_coil[4*i-1,0]
        output_coil[4*i,1] = output_coil[4*i-1,0]-(L1+gap*(i-1)*2+gap)
        output_coil[4*i+1,0] = output_coil[4*i,0]-(L1+gap*i*2-gap)
        output_coil[4*i+1,1] = output_coil[4*i,1] 
        output_coil[4*i+2,0] = output_coil[4*i+1,0]
        output_coil[4*i+2,1] = output_coil[4*i+1,1]+(L1+gap*i*2)
        output_coil[4*i+3,0] = output_coil[4*i+2,0]+(L1+gap*i*2)
        output_coil[4*i+3,1] = output_coil[4*i+2,1]
        if i == 12:
            output_coil[4*i+4,0] = output_coil[4*i+3,0]
            output_coil[4*i+4,1] = output_coil[4*i+3,0]-(L1+gap*i*2+gap)
    
    height = (length-width)/2
    line_width = 0.25
    plt.plot(output_coil[:,0],output_coil[:,1],linewidth=line_width)
    
    plt.plot(np.array([x_P1,x_P2,x_P4,x_P3,x_P1])+width/2,\
             np.array([y_P1,y_P2,y_P4,y_P3,y_P1])+width/2,linewidth=line_width)
    plt.plot(np.array([x_P1_s,x_P2_s,x_P4_s,x_P3_s,x_P1_s])+width/2,\
             np.array([y_P1_s,y_P2_s,y_P4_s,y_P3_s,y_P1_s])+width/2,linewidth=line_width)
    plt.plot(np.array([x_P1,x_P2,x_P4,x_P3,x_P1])+width/2,\
             -np.array([y_P1,y_P2,y_P4,y_P3,y_P1])-width/2,linewidth=line_width)
    plt.plot(np.array([x_P1_s,x_P2_s,x_P4_s,x_P3_s,x_P1_s])+width/2,\
             -np.array([y_P1_s,y_P2_s,y_P4_s,y_P3_s,y_P1_s])-width/2,linewidth=line_width)
    plt.plot(-np.array([x_P1,x_P2,x_P4,x_P3,x_P1])-width/2,\
             -np.array([y_P1,y_P2,y_P4,y_P3,y_P1])-width/2,linewidth=line_width)
    plt.plot(-np.array([x_P1_s,x_P2_s,x_P4_s,x_P3_s,x_P1_s])-width/2,\
             -np.array([y_P1_s,y_P2_s,y_P4_s,y_P3_s,y_P1_s])-width/2,linewidth=line_width)
    plt.plot(-np.array([x_P1,x_P2,x_P4,x_P3,x_P1])-width/2,\
             np.array([y_P1,y_P2,y_P4,y_P3,y_P1])+width/2,linewidth=line_width)
    plt.plot(-np.array([x_P1_s,x_P2_s,x_P4_s,x_P3_s,x_P1_s])-width/2,\
             np.array([y_P1_s,y_P2_s,y_P4_s,y_P3_s,y_P1_s])+width/2,linewidth=line_width)
    plt.plot([-width/2, width/2, width/2, -width/2, -width/2],\
            [width/2, width/2, width/2+height, width/2+height, width/2],linewidth=line_width)
    plt.plot([width/2, -width/2, -width/2, width/2, width/2],\
            [-width/2, -width/2, -width/2-height, -width/2-height, -width/2],linewidth=line_width)
    plt.plot([width/2, width/2+height, width/2+height, width/2, width/2],\
             [-width/2, -width/2, width/2, width/2, -width/2],linewidth=line_width)
    plt.plot([-width/2, -width/2-height, -width/2-height, -width/2, -width/2],\
             [width/2, width/2, -width/2, -width/2, width/2],linewidth=line_width)
    
    plt.xlim(-400, 400)
    plt.ylim(-400, 400)
    
    plt.gca().set_aspect('equal', adjustable='box')
        
    CurrentDirectory = os.getcwd()
    if flag == 0:    
        os.mkdir(str(it)+'_'+str(hh))
        os.chdir(str(it)+'_'+str(hh))
        plt.savefig(str(it)+'_'+str(hh)+'_geo.pdf', dpi=300)
        plt.close()
    else:
        os.mkdir(str(it)+'_'+str(hh)+'_MU')
        os.chdir(str(it)+'_'+str(hh)+'_MU')
        plt.savefig(str(it)+'_'+str(hh)+'_MU_geo.pdf', dpi=300)
        plt.close()
    os.chdir(CurrentDirectory)
        
    return Position_cons.transpose(), GeoFerrite, LowerLimit.transpose(), UpperLimit.transpose()    