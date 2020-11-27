# -*- coding: utf-8 -*-
"""
The geometry of ferrite is varied for optimisation. The ferrite has a shape similar to
the trapezoid, but may be separated into two sections, which emulates the arrangement
of ferrite in practical applications. 

@author: Hao Yuan
"""

import numpy as np
import os
import matplotlib.pyplot as plt

def geometry_parameters(it,hh,nVar):
    
    LowerLimit = np.zeros((nVar,1))
    UpperLimit = np.zeros((nVar,1))
    Position = np.zeros((nVar,1))
    
    # Parameters depicting the geometry of trapezoid
    length = 600 # length of the edge
    width = 50  # width of the longest ferrite strip
    d1_diag = 80 # distance between the square origin and the short edge of trapezoid
    d2_diag = 240 # distance between the square origin and the long edge of trapezoid
    L_short = 80 # length of the short edge of trapezoid
    theta = 80 # angle of the trapezoid, which should be constrained by L
    g1 = 1 # gap on the short edge of trapezoid
    g2 = 5 # gap on the long edge of trapezoid
    L1 = 20 # length of the first coil from the centre
    gap = 10 # gap between coil

    #=================================================================================
    # Generate random numbers for the above parameters with constraints
    #=================================================================================
    # global geometry of the coupler
    length = np.random.uniform(low=300, high=600, size=(1,))
    LowerLimit[0] = 300
    UpperLimit[0] = 600
    Position[0] = length
    
    width = np.random.uniform(low=30, high=60, size=(1,))
    LowerLimit[1] = 30
    UpperLimit[1] = 60
    Position[1] = width
    
    # range of the distances of the short and long edges from the origin
    diag_length = (length-width)/2/np.sin(np.deg2rad(45))
    r1 = 0.1
    r2 = 0.4
    d1_diag = np.random.uniform(low=np.floor(diag_length*r1), \
                                high=np.ceil(diag_length*r2), size=(1,))
    LowerLimit[2] = np.floor(diag_length*r1)
    UpperLimit[2] = np.ceil(diag_length*r2)
    Position[2] = d1_diag
    
    r_ref = d1_diag/diag_length # ensure the long edge is longer than the short one
    r3 = 0.5
    d2_diag = np.random.uniform(low=np.floor(diag_length*r3), \
                                high=np.floor(diag_length*(1-r_ref)), size=(1,))
    LowerLimit[3] = np.floor(diag_length*r3)
    UpperLimit[3] = np.floor(diag_length*(1-r_ref))
    Position[3] = d2_diag
    
    # range of the length of short edge
    L_short_max = 2*d1_diag*0.98
    r5 = 0.5
    r6 = 1
    L_short = np.random.uniform(low=np.floor(L_short_max*r5), \
                                high=np.ceil(L_short_max*r6), size=(1,))
    LowerLimit[4] = np.floor(L_short_max*r5)
    UpperLimit[4] = np.ceil(L_short_max*r6)
    Position[4] = L_short
    
    # range of the angle of trapezoid
    # theta_min constrains the ferrite within the boundary
    L_long_max = (diag_length-d2_diag)*2
    theta_min = np.degrees(np.arctan((d2_diag-d1_diag)/((L_long_max-L_short)/2)))
    theta = np.random.uniform(low=theta_min, high=89.9, size=(1,))
    LowerLimit[5] = np.ceil(theta_min)
    UpperLimit[5] = 89.9
    Position[5] = theta
    
    # range of the gap on the short edge
    r7 = 0.5
    g1 = np.random.uniform(low=0.1, high=np.floor(L_short*r7), size=(1,))
    LowerLimit[6] = 1
    UpperLimit[6] = np.floor(L_short*r7)
    Position[6] = g1
    
    # range of the gap on the long edge
    L_long = L_short+(d2_diag-d1_diag)/\
    np.tan(np.deg2rad(theta))*2 # length of the short edege of trapezoid
    g2 = np.random.uniform(low=1, high=np.floor(L_long-(L_short-g1)), size=(1,))
    LowerLimit[7] = 1
    UpperLimit[7] = np.floor(L_long-(L_short-g1))
    Position[7] = g2
        
    L1 = np.random.uniform(low=10, high=np.floor((length/2-12*5)*2), size=(1,))
    LowerLimit[8] = 10
    UpperLimit[8] = np.floor((length/2-12*5)*2)
    Position[8] = L1
    
    gap = np.random.uniform(low=4, high=np.floor((length-L1)/2/12), size=(1,))
    LowerLimit[9] = 4
    UpperLimit[9] = np.floor((length-L1)/2/12)
    Position[9] = gap
    #=================================================================================
    

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
    output_coil[0,0] = L1/2-gap
    output_coil[0,1] = -L1/2
    output_coil[1,0] = output_coil[0,0]-L1+gap
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
    plt.plot(output_coil[:,0],output_coil[:,1])
    
    plt.plot(np.array([x_P1,x_P2,x_P4,x_P3,x_P1])+width/2,\
             np.array([y_P1,y_P2,y_P4,y_P3,y_P1])+width/2)
    plt.plot(np.array([x_P1_s,x_P2_s,x_P4_s,x_P3_s,x_P1_s])+width/2,\
             np.array([y_P1_s,y_P2_s,y_P4_s,y_P3_s,y_P1_s])+width/2)
    plt.plot(np.array([x_P1,x_P2,x_P4,x_P3,x_P1])+width/2,\
             -np.array([y_P1,y_P2,y_P4,y_P3,y_P1])-width/2)
    plt.plot(np.array([x_P1_s,x_P2_s,x_P4_s,x_P3_s,x_P1_s])+width/2,\
             -np.array([y_P1_s,y_P2_s,y_P4_s,y_P3_s,y_P1_s])-width/2)
    plt.plot(-np.array([x_P1,x_P2,x_P4,x_P3,x_P1])-width/2,\
             -np.array([y_P1,y_P2,y_P4,y_P3,y_P1])-width/2)
    plt.plot(-np.array([x_P1_s,x_P2_s,x_P4_s,x_P3_s,x_P1_s])-width/2,\
             -np.array([y_P1_s,y_P2_s,y_P4_s,y_P3_s,y_P1_s])-width/2)
    plt.plot(-np.array([x_P1,x_P2,x_P4,x_P3,x_P1])-width/2,\
             np.array([y_P1,y_P2,y_P4,y_P3,y_P1])+width/2)
    plt.plot(-np.array([x_P1_s,x_P2_s,x_P4_s,x_P3_s,x_P1_s])-width/2,\
             np.array([y_P1_s,y_P2_s,y_P4_s,y_P3_s,y_P1_s])+width/2)
    plt.plot([-width/2, width/2, width/2, -width/2, -width/2],\
            [width/2, width/2, width/2+height, width/2+height, width/2])
    plt.plot([width/2, -width/2, -width/2, width/2, width/2],\
            [-width/2, -width/2, -width/2-height, -width/2-height, -width/2])
    plt.plot([width/2, width/2+height, width/2+height, width/2, width/2],\
             [-width/2, -width/2, width/2, width/2, -width/2])
    plt.plot([-width/2, -width/2-height, -width/2-height, -width/2, -width/2],\
             [width/2, width/2, -width/2, -width/2, width/2])
    
    plt.xlim(-400, 400)
    plt.ylim(-400, 400)
    
    plt.gca().set_aspect('equal', adjustable='box')
        
    CurrentDirectory = os.getcwd()    
    os.mkdir(str(it)+'_'+str(hh))
    os.chdir(str(it)+'_'+str(hh))
    plt.savefig(str(it)+'_'+str(hh)+'_geo.pdf', dpi=300)
    plt.close()
    os.chdir(CurrentDirectory)
        
    return Position.transpose(), GeoFerrite, LowerLimit.transpose(), UpperLimit.transpose()
