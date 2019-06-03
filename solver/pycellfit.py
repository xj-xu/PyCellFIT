#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Mon Apr 29 10:27:23 2019

@author: xj

Please enter full directory of the mesh text file.
Example: python solver.py mesh_file_name
"""

# =============================================================================
# IMPORT LIBRARIES
# =============================================================================
import sys
import numpy as np
from matplotlib import collections as mc
import pylab as pl
import matplotlib.pyplot as plt
from numpy import where


# =============================================================================
# GLOBAL VARIABLES
# =============================================================================

STR_mesh_dir = sys.argv[1] # directory path of FEM file

N_TJs = 0           # Number of triple junctions
N_Tens = 0          # Number of tensions
N_Edges = 0         # Number of edge segments
N_Edge_Groups = 0   # Number of edge groups (tensions)
N_Cells = 0         # Number of cells

ID_Nodes = []       # List of node IDs
ID_TJs = []         # List of triple junction IDs
ID_TJ_Edges = []    # List of edges associated with TJs
ID_Cells = []       # List of Cell IDs

# Spatial information
S_All_Nodes = []    # [x, y, edge1, edge2]
S_TJ_Edge_Vecs = [] # 6 by N_TJ list of direction vectors 
                    # [[vec1x, vec1y, vec2x, vec2y, vec3x, vec3y], [], ...]

# Maps of things
MAP_Edge_Nodes = []     # [[edge ID, node1 ID, node2 ID], [], ...] for all nodes
MAP_TJ_Edge_Nodes = []  # for TJ nodes

# Visualization information
GRAPH_All_Edges = []
GRAPH_TJ_Edges = []

# =============================================================================
# FUNCTIONS
# =============================================================================

def FNC_Read_Mesh():
    """
    Parse the mesh .txt file (STR_mesh_dir) and populate 
    the global variables with information.
    02/07/19:
    solver.ipynb uses the 'with open()' statement 5 times.
    Trying to optimize parsing.
    02/16/19:
    Reduced it to ___ 'with open()' statements
    """
    global STR_mesh_dir
    global ID_Nodes
    global ID_TJs
    global ID_TJ_Edges
    global S_TJ_Edge_Vecs
    global S_All_Nodes
    global MAP_Edge_Nodes
    
    with open(STR_mesh_dir, 'r') as df:
        flag_nodes = False
        for line in df:
            # Read node info between BEGIN_NODES -> BEGIN_ALLEDGES
            if 'BEGIN_NODES' in line:
                flag_nodes = True
                continue
            if 'BEGIN_ALLEDGES' in line:
                flag_nodes = False
            if flag_nodes == True:
                elements = line.split('\t')
                try:
                    ID_Nodes.append(int(elements[0]))
                    S_All_Nodes.append([
                            float(elements[1]),
                            float(elements[2]),
                            int(elements[-4]),
                            int(elements[-3])])
                except:
                    continue
            if 'Vec1' in line:  # Select TJs by using 'Vec1' as a filter  
                elements = line.split('\t')
                ID_TJs.append(int(elements[0])) # node ID
                try:
                    S_TJ_Edge_Vecs.append([ # Vec(r*cos(theta), r*sin(theta))
                            float(elements[5].split(' ')[1]),
                            float(elements[5].split(' ')[2]),
                            float(elements[6].split(' ')[1]),
                            float(elements[6].split(' ')[2]),
                            float(elements[7].split(' ')[1]),
                            float(elements[7].split(' ')[2])])
                except:
                    print('ERROR: MISSING DIRECTION VECTORS \
                          AT NODE %d'%int(elements[0]))
                    S_TJ_Edge_Vecs.append([
                            float(elements[5].split(' ')[1]),
                            float(elements[5].split(' ')[2]),
                            float(elements[6].split(' ')[1]),
                            float(elements[6].split(' ')[2]),
                            0,
                            0]) 
                ID_TJ_Edges.append(int(elements[9]))
                ID_TJ_Edges.append(int(elements[10]))
                ID_TJ_Edges.append(int(elements[11]))
            # Read edge info between BEGIN_ALLEDGES -> BEGIN_EDGEGROUPS
            if 'Edge2D' in line:
                elements = line.split('\t')
                MAP_Edge_Nodes.append([
                        int(elements[0]),
                        int(elements[2]),
                        int(elements[3])])

    
def FNC_Fill_Mesh_Info():
    """
    Calculate or formulate other mesh information.
    Repeated TJ edges are due to short edge groups.
    # LIST_Unique_TJ_Edges was needed but I've chosen to simply update
    # ID_TJ_Edges and encapsulating the crap
    """
    global N_TJs
    global ID_TJ_Edges
    global MAP_TJ_Edge_Nodes
    global GRAPH_All_Edges
    global GRAPH_TJ_Edges

    ID_TJ_Edges = list(set(ID_TJ_Edges)) # Removes repeated TJ edge IDs
    
    for edge in MAP_Edge_Nodes:
        if edge[0] in ID_TJ_Edges:
            MAP_TJ_Edge_Nodes.append(edge)
            
    N_TJs = len(ID_TJs) # number of TJs = number of TJ IDs
    
    for i in range(len(MAP_Edge_Nodes)): 
        ind0 = ID_Nodes.index(MAP_Edge_Nodes[i][1])
        ind1 = ID_Nodes.index(MAP_Edge_Nodes[i][2])        
        GRAPH_All_Edges.append([
                (S_All_Nodes[ind0][0], S_All_Nodes[ind0][1]),
                (S_All_Nodes[ind1][0], S_All_Nodes[ind1][1])])
    
    for i in range(len(MAP_TJ_Edge_Nodes)): 
        ind0 = ID_Nodes.index(MAP_TJ_Edge_Nodes[i][1])
        ind1 = ID_Nodes.index(MAP_TJ_Edge_Nodes[i][2])
        GRAPH_TJ_Edges.append([
                (S_All_Nodes[ind0][0], S_All_Nodes[ind0][1]),
                (S_All_Nodes[ind1][0], S_All_Nodes[ind1][1])])

def FNC_Vis_Mesh(GRAPH):
    """
    Plots the FEM file to visualize the image in vector form.
    """
    c = np.array([(0, 1, 0, 1)]) #(1, 0, 0, 1), (0, 0, 1, 1)
    lc = mc.LineCollection(GRAPH, colors=c, linewidths=1)
    fig, ax = pl.subplots(figsize=(8,8))
    ax.add_collection(lc)
    plt.grid()
    ax.margins(0.1)
    plt.show()
    
    
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
# MAIN FUNCTIONS
# =============================================================================
    
def FNC_Mesh():
    """
    """
    FNC_Read_Mesh()
    FNC_Fill_Mesh_Info()
    print('SYSTEM: %s IS READ AND LOADED.'%STR_mesh_dir)
    FNC_Vis_Mesh(GRAPH_All_Edges)
    
def FNC_Cal_Tension():
    """
    """
    FNC_Create_Map_Edge_to_Ten(ID_TJ_Edges, MAP_Edge_Nodes, 
                               ID_TJs, S_All_Nodes, MAP_Edge_Nodes)

def FNC_Cal_Pressure():
    """
    """
    pass


def main():
    """
    
    """
    FNC_Mesh()
    print(N_TJs)
    FNC_Cal_Tension()
    FNC_Cal_Pressure()


if __name__ == "__main__":
    main()
