#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Sun Feb  3 16:21:42 2019

@author: xj

Please enter full directory of the mesh text file.
Example: python solver.py mesh_file_name
"""

# =============================================================================
# IMPORT LIBRARIES
# Try to reduce unused libraries for efficiency
# =============================================================================

#import numpy as np
import sys
#import os
#import math
#import pylab as pl
#import matplotlib.pyplot as plt
#import csv
#import scipy.stats as st
#from numpy import linalg
#from scipy.sparse.linalg import lsqr
#from matplotlib.pyplot import figure
#from matplotlib import cm
#from numpy import where
#from matplotlib.patches import Polygon
#from matplotlib.collections import PatchCollection

# =============================================================================
# IMPORT FUNCTIONS
# =============================================================================
#sys.path.append('../../PyCellFIT')
#print(sys.path)
from algs import *

# =============================================================================
# OBTAIN MESH DIRECTORY
# =============================================================================
#
#STR_dir_path = str(input("Please enter full directory \
#    of the mesh text file\n"))
#    print(type(STR_dir_path), STR_dir_path)
STR_mesh_dir = sys.argv[1]

# =============================================================================
# DECLARE GLOBAL MESH INFORMATION
# =============================================================================

# Counts of things
# integers
N_TJs = 0           # Number of triple junctions
N_Tens = 0          # Number of tensions
N_Edges = 0         # Number of edge segments
N_Edge_Groups = 0   # Number of edge groups (tensions)
N_Cells = 0         # Number of cells

# IDs of things
# ID is used to distinguish itself from index
# lists of integers
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
# Node_Edges
# Node_Cells
# Cell_Nodes
# Cell_Edges
# Edge_Cells

# Visualization information
GRAPH_All_Edges = []
GRAPH_TJ_Edges = []


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

