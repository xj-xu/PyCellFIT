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
#from matplotlib import collections as mc
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
# DECLARE GLOBAL VARIABLES
# =============================================================================

N_TJ = 0    # Number of triple junctions
N_Ten = 0   # Number of tensions
N_Cell = 0  # Number of cells

LIST_TJ_IDs = []    # List of triple junction IDs
LIST_Cell_IDs = []  # List of Cell IDs

LIST_All_Nodes = []     # [Node ID, x coordinate, y coordinate, edge1, edge2]
LIST_Edge_Vectors = []  # 6 by N_TJ list of direction vectors 
                        # LIST_Edge_Vectors indexing:
                        # (0,1) -> Vec1 (x,y) 
                        # (2,3) -> Vec2 (x,y)
                        # (4,5) -> Vec3 (x,y)
                        

def FNC_Read_Mesh():
    """
    Parse the mesh .txt file (STR_mesh_dir) and populate 
    the global variables with information.
    02/07/19:
    solver.ipynb opens the same file 5 times.
    Try to optimize parsing.
    """
    global LIST_TJ_IDs
    global STR_mesh_dir
    with open(STR_mesh_dir, 'r') as df:
        for line in df:
            # Select triple junctions by using 'Vec1' as filter
            if 'Vec1' in line:
                
                # Break each line into elements
                elements = line.split('\t')
                
                # elements[0]: node number
                ID_TJ.append(int(elements[0]))
                
                # elements[1:2]: x, y coordinates of the triple junction
                X.append(int(elements[1]))
                Y.append(int(elements[2]))
                
                # elements[3:4] are repeats of elements[1:2]
                
                # elements[5:7]: vectors representing the 3 edges
                # e.g. (Vec1 r*cos(theta) r*sin(theta))
                vect_lst.append([float(elements[5].split(' ')[1]),
                                 float(elements[5].split(' ')[2]),
                                float(elements[6].split(' ')[1]),
                                float(elements[6].split(' ')[2]),
                                float(elements[7].split(' ')[1]),
                                float(elements[7].split(' ')[2])]) 
                
                # elements[8]: 'Edge'
                
                # elements[9:11]: edge numbers of the 3 associated edges
                ID_TJ_Edges.append(int(elements[9]))
                ID_TJ_Edges.append(int(elements[10]))
                ID_TJ_Edges.append(int(elements[11]))
                
                # count the triple junction
                N_TJ +=1
    

def FNC_Cal_Tension():
    """
    """
    trial_fnc()

def FNC_Cal_Pressure():
    """
    """
    pass


def main():
    """
    
    """
    FNC_Read_Mesh()
    FNC_Cal_Tension()
    FNC_Cal_Pressure()


if __name__ == "__main__":
    main()

