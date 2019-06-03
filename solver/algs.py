#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Thu Feb  7 13:31:06 2019

@author: xj
"""


import numpy as np
from matplotlib import collections as mc
import pylab as pl
import matplotlib.pyplot as plt
from numpy import where

# =============================================================================
# General functions
# =============================================================================



# =============================================================================
# Tension functions
# =============================================================================

def FNC_Create_Map_Edge_to_Ten(ID_TJ_Edges,
                               Edges_Nodes, 
                               ID_TJ,
                               LIST_All_Nodes,
                               LIST_All_Edge_Nodes):
    """
    """
    MAP_Edge_to_Ten = []
    i_Ten = 0
    LIST_Unique_Edges_Nodes = np.array(Edges_Nodes)
    LIST_All_Nodes = np.array(LIST_All_Nodes)
    LIST_All_Edge_Nodes = np.array(LIST_All_Edge_Nodes)
    #blockPrint()
    prog = 1
    for edge_ind1 in ID_TJ_Edges:
        # Print progress
        if prog % int(len(ID_TJ_Edges)/5) == 0: print(math.ceil(100*prog/len(ID_TJ_Edges)),'% DONE')
        prog += 1
        
        tj1 = False
        tj2 = False
        # matched = False
        edge_ind2 = edge_ind1
        node1 = LIST_Unique_Edges_Nodes[where(edge_ind1 == LIST_Unique_Edges_Nodes[:,0])[0][0], 1]
        node2 = LIST_Unique_Edges_Nodes[where(edge_ind1 == LIST_Unique_Edges_Nodes[:,0])[0][0], 2]
        # check for existence in MAP_Edge_to_Ten to avoid double counting
        if edge_ind1 in [item[0] for item in MAP_Edge_to_Ten]: continue
        
        #while matched == False:
        for itr in range(10):
        
    #         print('---------')
    #         print('edge input: %d'%edge_ind1)
    #         print('potential edge pair:', edge_ind1, edge_ind2)
    #         print('nodes: %d %d'%(node1,node2))
            
            if node1 in ID_TJ:
                tj1 = True
                #print('node1 %d is a tj'%node1)
            else: # find the edge connects to the other tj
                #print('node1 %d is not a tj'%node1)
                newedge1 = LIST_All_Nodes[where(node1 == LIST_All_Nodes[:,0])[0][0], -2]
                newedge2 = LIST_All_Nodes[where(node1 == LIST_All_Nodes[:,0])[0][0], -1]
                #print('new edge options:', newedge1, newedge2)
                if newedge1 != edge_ind2:
                    edge_ind2 = newedge1
                    newnode1 = LIST_All_Edge_Nodes[where(edge_ind2 == LIST_All_Edge_Nodes[:,0])[0][0], 1]
                    newnode2 = LIST_All_Edge_Nodes[where(edge_ind2 == LIST_All_Edge_Nodes[:,0])[0][0], 2]
                    if newnode1 != node1:
                        node1 = newnode1
                    else:
                        node1 = newnode2
                else:
                    edge_ind2 = newedge2
                    newnode1 = LIST_All_Edge_Nodes[where(edge_ind2 == LIST_All_Edge_Nodes[:,0])[0][0], 1]
                    newnode2 = LIST_All_Edge_Nodes[where(edge_ind2 == LIST_All_Edge_Nodes[:,0])[0][0], 2]
                    if newnode1 != node1:
                        node1 = newnode1
                    else:
                        node1 = newnode2
    #             print('new edge chosen:', edge_ind2)
    #             print('new node options:', newnode1, newnode2)
    #             print('new node chosen:', node1)
            
            if node2 in ID_TJ:
                tj2 = True
                #print('node2 %d is a tj'%node2)
            else: # find the edge connects to the other tj
                #print('node2 %d is not a tj'%node2)
                newedge1 = LIST_All_Nodes[where(node2 == LIST_All_Nodes[:,0])[0][0], -2]
                newedge2 = LIST_All_Nodes[where(node2 == LIST_All_Nodes[:,0])[0][0], -1]
                #print('new edge options:', newedge1, newedge2)
                if newedge1 != edge_ind2:
                    edge_ind2 = newedge1
                    newnode1 = LIST_All_Edge_Nodes[where(edge_ind2 == LIST_All_Edge_Nodes[:,0])[0][0], 1]
                    newnode2 = LIST_All_Edge_Nodes[where(edge_ind2 == LIST_All_Edge_Nodes[:,0])[0][0], 2]
                    if newnode1 != node2:
                        node2 = newnode1
                    else:
                        node2 = newnode2
                else:
                    edge_ind2 = newedge2
                    newnode1 = LIST_All_Edge_Nodes[where(edge_ind2 == LIST_All_Edge_Nodes[:,0])[0][0], 1]
                    newnode2 = LIST_All_Edge_Nodes[where(edge_ind2 == LIST_All_Edge_Nodes[:,0])[0][0], 2]
                    if newnode1 != node2:
                        node2 = newnode1
                    else:
                        node2 = newnode2
    #             print('new edge chosen:', edge_ind2)
    #             print('new node options:', newnode1, newnode2)
    #             print('new node chosen:', node2)
            
            if tj1 and tj2:
                # record the two edge inds and map them to the same tension ind
                MAP_Edge_to_Ten.append([edge_ind1, i_Ten])
                MAP_Edge_to_Ten.append([edge_ind2, i_Ten])
    #             print('gottem')
    #             print('the associated edges are: %d and %d'%(edge_ind1, edge_ind2))
    #             print('the associated nodes are: %d and %d'%(node1, node2))
                break
                # matched = True
        else: # search is out of bounds - edge pointing away from region of interest
            MAP_Edge_to_Ten.append([edge_ind1, i_Ten])
            
        # count tensions
        i_Ten += 1
    
    MAP_Edge_to_Ten = np.array(MAP_Edge_to_Ten, dtype=int)
    print('DONE...')
    print('Number of tensions = ', i_Ten)
    print('Number of triple junctions =', len(ID_TJ))

# =============================================================================
# Pressure functions
# =============================================================================
def check_Gp_matrix(Gp, Ap):
    """
    Not sure why Ap or Gp is checked instead of the other...
    """
    # check for zero columns
    for i in range(Gp.shape[1]):
        sum = 0
        for j in range(Gp.shape[0]):
            sum += abs(Gp[j,i])
        #print(i, sum)
        if sum == 0:
            print('Zero column at', i)
            print(Gp[:,i])

    # check for identical rows
    for i in range(Ap.shape[0]):
        for j in range(i + 1, Ap.shape[0]):
            aa = Ap[:,i] - Ap[:,j]
            #print(aa)
            sum = 0
            for k in aa:
                sum += abs(k)
            if sum == 0:
                print('Identical column found at', i,j)
    print('Gp matrix checked.')
    
    
# =============================================================================
#     Visualization functions
# =============================================================================
def FNC_Vis_Mesh(GRAPH):
    """
    
    """
    c = np.array([(0, 1, 0, 1)]) #(1, 0, 0, 1), (0, 0, 1, 1)
    lc = mc.LineCollection(GRAPH, colors=c, linewidths=1)
    fig, ax = pl.subplots(figsize=(8,8))
    ax.add_collection(lc)
    plt.grid()
    ax.margins(0.1)

#    Depends on FNC_Map_Edge_to_Tension
#    for i in range(len(GRAPH)):
#        colorvalues.append(values[FNC_Map_Edge_to_Tension(MAP[i][0])])
#    colorvalues = np.array(colorvalues)
#    lc = mc.LineCollection(graph2, array=colorvalues, cmap=plt.cm.jet, linewidths=2)
#    fig, ax = pl.subplots(figsize=(10,8))
#    ax.add_collection(lc)
#    plt.title(dir)
#    plt.grid()
#    ax.margins(0.1)
#    
#    # 2. Append a color scale that is sensible and labelled
#    I = cm.ScalarMappable(norm=None, cmap='jet')
#    I.set_array(colorvalues)
#    axcb = fig.colorbar(I)
#    axcb.set_label('Tension')
    #plt.scatter(X, Y, s=15, marker='o', color='black')
    
    plt.show()
    #fig.savefig('../figs/mesh002_tension_colorbar.png')
    
    # 3. Perhaps also fill in intermediate edge segments with matching values