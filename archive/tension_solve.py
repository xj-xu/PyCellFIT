
##########################################
#
# File created 12/07/18 by XJ
# Switched to .py file since tensions
# solution have been found
#
##########################################


import numpy as np
import os, sys
import math
import pylab as pl
import matplotlib.pyplot as plt
import csv
import scipy.stats as st

from numpy import linalg
from scipy.sparse.linalg import lsqr
from matplotlib import collections as mc
from matplotlib.pyplot import figure
from numpy import where

def blockPrint():
    sys.stdout = open(os.devnull, 'w')
    
def enablePrint():
    sys.stdout = sys.__stdout__

# Enter directory of the .txt file containing FEM data
#dir = '/Users/xj/Desktop/PHYS_4998/Mesh002/Outline_0_000.txt'
dir = '/Users/xj/PyCellFIT/meshes/011719_wound/outline/outline.txt'

N_TJ = 0    # Number of triple junctions
N_Ten = 0 # Number of tensions
ID_TJ = [] # Indices of nodes that are triple junctions
ID_TJ_Edges = [] # Indices of edges that are associated with triple junctions
X,Y = [],[] # list of x, y position coordinates
MAP_Edge_to_Ten = [] # edges and their associated tension (two edges have the same tension)
#LIST_rho = [] # list of the radius of curvatures
Unique = []   # number of unique edges involved in the calculation
vect_lst = [] # 6 by N_TJ list of direction vectors 
                # vect_lst indexing:
                # (0,1) -> Vec1 (x,y) 
                # (2,3) -> Vec2 (x,y)
                # (4,5) -> Vec3 (x,y)
edge_nodes = [] # [edge ind, node1, node2] Indices of nodes associated with each edge, for all edges
all_nodes = []  # [Node index, x coordinate, y coordinate, edge1, edge2] for all nodes
graph = []      # for plotting with line collection e.g. [[(0, 0), (1, 1)], [(2, 3), (3, 3)]]
unique_edges_nodes = [] # [edge ind, node1, node2] Indices of nodes associated with each edge, for edges of concern


##########################################
#
# PARSE INFORMATION
#
##########################################


print('PARSING FILE %s...'%dir)

# Parse .txt file and fill above lists
with open(dir, 'r') as df:
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
            
            # elements[5:7]: vectors representing the 3 edges e.g. (Vec1 r*cos(theta) r*sin(theta))
            vect_lst.append([float(elements[5].split(' ')[1]), float(elements[5].split(' ')[2]),
                            float(elements[6].split(' ')[1]), float(elements[6].split(' ')[2]),
                            float(elements[7].split(' ')[1]), float(elements[7].split(' ')[2])]) 
            
            # elements[8]: 'Edge'
            
            # elements[9:11]: edge numbers of the 3 associated edges
            ID_TJ_Edges.append(int(elements[9]))
            ID_TJ_Edges.append(int(elements[10]))
            ID_TJ_Edges.append(int(elements[11]))
            
            # count the triple junction
            N_TJ +=1

print('---Shared edges---')
for j in ID_TJ_Edges:
    if j not in Unique:
        Unique.append(j)
    else:
        print(j)

with open(dir, 'r') as df:
    for line in df:
        if 'Edge2D' in line:
            elements = line.split('\t')
            edge_nodes.append([int(elements[0]), int(elements[2]), int(elements[3])])
            if int(elements[0]) in Unique:
                unique_edges_nodes.append([int(elements[0]), int(elements[2]), int(elements[3])])
        # Read in radius of curvatures
#         if 'Circle' in line:
#             elements = line.split('\t')
#             LIST_rho.append()

with open(dir, 'r') as df:
    flag = False
    for line in df:
        if 'BEGIN_NODES' in line:
            flag = True
            continue
        if 'BEGIN_ALLEDGES' in line:
            break
        if flag == True:
            elements = line.split('\t')
            try:
                all_nodes.append([int(elements[0]),
                                  float(elements[1]),
                                  float(elements[2]),
                                  int(elements[-4]),
                                  int(elements[-3])
                                 ])
            except:
                continue


ind_node = np.array(all_nodes)[:,0]
# change unique_edges_nodes to edge_nodes TO VISUALIZE ALL EDGES
for i in range(len(unique_edges_nodes)): 
    ind0 = where(ind_node == unique_edges_nodes[i][1])[0][0]
    ind1 = where(ind_node == unique_edges_nodes[i][2])[0][0]
    graph.append([(all_nodes[ind0][1], all_nodes[ind0][2]),
                  (all_nodes[ind1][1], all_nodes[ind1][2])])
    # if i == 4: print(all_nodes[ind0][0], all_nodes[ind1][0])

# Convert to numpy array for easy handling
unique_edges_nodes = np.array(unique_edges_nodes)
edge_nodes = np.array(edge_nodes)
all_nodes = np.array(all_nodes)

print('DONE...')

##########################################
#
# Creating a map of 
# edge numbers -> tension number
#
##########################################

print('CREATING MAP OF EDGE# -> TENSION# ...')
# Infinite while loop occurs when an input edge points out of bounds
# Can be solved in 3 ways
# 1) set a max iteration of while loop (depending on number of intermediate nodes created);
#    switching to a for loop induces the same effect
# 2) add in information about the 3rd edge for all_nodes, if a third edge is found then
#    we've exited the boundary and we should break the loop
MAP_Edge_to_Ten = []
N_Ten = 0

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
    node1 = unique_edges_nodes[where(edge_ind1 == unique_edges_nodes[:,0])[0][0], 1]
    node2 = unique_edges_nodes[where(edge_ind1 == unique_edges_nodes[:,0])[0][0], 2]
    
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
            newedge1 = all_nodes[where(node1 == all_nodes[:,0])[0][0], -2]
            newedge2 = all_nodes[where(node1 == all_nodes[:,0])[0][0], -1]
            #print('new edge options:', newedge1, newedge2)
            if newedge1 != edge_ind2:
                edge_ind2 = newedge1
                newnode1 = edge_nodes[where(edge_ind2 == edge_nodes[:,0])[0][0], 1]
                newnode2 = edge_nodes[where(edge_ind2 == edge_nodes[:,0])[0][0], 2]
                if newnode1 != node1:
                    node1 = newnode1
                else:
                    node1 = newnode2
            else:
                edge_ind2 = newedge2
                newnode1 = edge_nodes[where(edge_ind2 == edge_nodes[:,0])[0][0], 1]
                newnode2 = edge_nodes[where(edge_ind2 == edge_nodes[:,0])[0][0], 2]
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
            newedge1 = all_nodes[where(node2 == all_nodes[:,0])[0][0], -2]
            newedge2 = all_nodes[where(node2 == all_nodes[:,0])[0][0], -1]
            #print('new edge options:', newedge1, newedge2)
            if newedge1 != edge_ind2:
                edge_ind2 = newedge1
                newnode1 = edge_nodes[where(edge_ind2 == edge_nodes[:,0])[0][0], 1]
                newnode2 = edge_nodes[where(edge_ind2 == edge_nodes[:,0])[0][0], 2]
                if newnode1 != node2:
                    node2 = newnode1
                else:
                    node2 = newnode2
            else:
                edge_ind2 = newedge2
                newnode1 = edge_nodes[where(edge_ind2 == edge_nodes[:,0])[0][0], 1]
                newnode2 = edge_nodes[where(edge_ind2 == edge_nodes[:,0])[0][0], 2]
                if newnode1 != node2:
                    node2 = newnode1
                else:
                    node2 = newnode2
#             print('new edge chosen:', edge_ind2)
#             print('new node options:', newnode1, newnode2)
#             print('new node chosen:', node2)
        
        if tj1 and tj2:
            # record the two edge inds and map them to the same tension ind
            MAP_Edge_to_Ten.append([edge_ind1, N_Ten])
            MAP_Edge_to_Ten.append([edge_ind2, N_Ten])
#             print('gottem')
#             print('the associated edges are: %d and %d'%(edge_ind1, edge_ind2))
#             print('the associated nodes are: %d and %d'%(node1, node2))
            break
            # matched = True
    else: # search is out of bounds - edge pointing away from region of interest
        MAP_Edge_to_Ten.append([edge_ind1, N_Ten])
        
    # count tensions
    N_Ten += 1

MAP_Edge_to_Ten = np.array(MAP_Edge_to_Ten, dtype=int)
print('DONE...')
print('Number of tensions = ', N_Ten)
print('Number of triple junctions =', N_TJ)

##########################################
#
# VISUALIZATION OF SETUP
#
##########################################

c = np.array([(1, 0, 0, 1), (0, 1, 0, 1), (0, 0, 1, 1)])
lc = mc.LineCollection(graph, colors=c, linewidths=2)
fig, ax = pl.subplots(figsize=(10,10))
ax.add_collection(lc)
plt.title(dir)
plt.grid()
ax.margins(0.1)
#plt.scatter(X, Y, marker='o', color='black')
plt.show()
# plt.savefig('mesh002_tj_only_visualization')


##########################################
#
# Matrix construction and solve system of equations
#
##########################################

def writetofile(filename, results):
    """
    filename: string
    results: array
    Prints results to txt file with the given name.
    Dependencies: global variable MAP_Edge_to_Ten
    """
    f = open(filename, 'w')
    f.write('Tension                 Associated edges\n')
    for i in range(len(results)):
        ass_edges = where(i == MAP_Edge_to_Ten[:,1])[0]
        f.write(str(results[i])+'\t'+str(ass_edges)+'\n')
    f.close()

def MAP_Edge_to_Tension(Edge_ID):
    """
    Takes in an edge ID and returns the tension ID
    """
    global MAP_Edge_to_Ten
    ind = where(Edge_ID == MAP_Edge_to_Ten[:,0])[0][0]
    return MAP_Edge_to_Ten[ind, 1]
    
G = np.mat(np.zeros((N_Ten, 2*N_TJ)))
A = np.zeros((N_Ten+1, N_Ten+1))
b = np.zeros(N_Ten+1)
A[:-1,-1] = 1
A[-1,:-1] = 1
b[-1] = N_Ten

# go through all triple junctions
for i in range(N_TJ):
    # go through the 3 edges of each triple junction
    for vec in range(3):
        
        # norm of the vector representing an edge
        norm = np.sqrt(vect_lst[i][2*vec]**2 + vect_lst[i][2*vec + 1]**2)
        
        # column number that correspond to the particular tension
        col = MAP_Edge_to_Tension(ID_TJ_Edges[3*i + vec])
    
        # assign values to matrix
        #if i == 0: print(vec, vect_lst[i][2*vec + 1] / norm)
        G[col, 2*i] = vect_lst[i][2*vec] / norm
        G[col, 2*i + 1] = vect_lst[i][2*vec + 1] / norm

# Due to confusing numpy indices, the row and columns have been
# swapped - thus G.T * G in the formalism is computed as G * G.T
C = np.matmul(G, G.T)
C = 2.0*C # interestingly, having this factor of 2 does not change the results
A[:-1,:-1] = C
# print('---G matrix---')
# print(G.shape, G)
# print('---G.T matrix---')
# print(G.T.shape, G.T)
# print('---G.T * G matrix---')
# print(C.shape, C)
# print('---A matrix---')
# print(A.shape, A)

print('---Gamma---')
# print('linalg.lstsq')
# gamma = linalg.lstsq(A, b, rcond=None)
# print(gamma[0])
print('linalg.solve')
gamma2 = linalg.solve(A, b)
print('Max tension = %f\nMin tension = %f'%(max(gamma2), min(gamma2)))
#writetofile('mesh002_tensions.txt', gamma2)
# print(gamma2)
# print('sparse.linalg.lsqr')
# gamma3 = lsqr(A, b)
# print(gamma3[0])



##########################################
#
# VISUALIZATION OF TENSIONS
#
##########################################


lc = mc.LineCollection(graph, array=gamma2[:-1], cmap=plt.cm.jet, linewidths=3)
fig, ax = pl.subplots(figsize=(10,10))
ax.add_collection(lc)
plt.title(dir)
plt.grid()
ax.margins(0.1)
plt.scatter(X, Y, s=15, marker='o', color='black')
#plt.show()
#plt.savefig('mesh002_tension_solved.png')

jetc = np.zeros((100,1))
for i in range(100):
    jetc[i,0] = i
fig = plt.figure(figsize=(25/3, 6.25))
# show color bar
# ax = fig.add_subplot(111)
# ax.set_axis_off()
# im = ax.imshow(jetc, cmap=plt.cm.jet)

##########################################
#
# Read in CellFIT tension results
#
##########################################

#dir_cellfit = '/Users/xj/Desktop/PHYS_4998/Mesh002/Outline_0_000_Output_exclude_outside_edges.csv'
#dir_cellfit2 = '/Users/xj/Desktop/PHYS_4998/Mesh002/Outline_0_000_Output_include_outside_edges.csv'
dir_cellfit = '/Users/xj/PyCellFIT/meshes/hex_test_images/nearseg_hex90/CellFIT_MeshOfHexagonalCells090_Output.csv'
gamma_c = np.zeros(N_Ten)
gamma_c_inc = np.zeros(N_Ten+50)
CellFIT_results_EdgeID = np.zeros(N_Ten, dtype=int)
with open(dir_cellfit, mode='r') as csvf:
    allresults = csv.reader(csvf, delimiter=' ')
    i = -1
    for row in allresults:
        row = row[0].split(',')
        if i >= 0:
            CellFIT_results_EdgeID[i] = int(row[0])
            gamma_c[i] = float(row[1])
        i += 1  
# with open('/Users/xj/Desktop/PHYS_4998/Mesh002/Outline_0_000_Output_include_outside_edges.csv', mode='r') as csvf:
#     allresults = csv.reader(csvf, delimiter=' ')
#     i = -1
#     for row in allresults:
#         row = row[0].split(',')
#         if i >= 0:
#             gamma_c_inc[i] = float(row[1])
#         i += 1
# print(CellFIT_results_EdgeID)

##########################################
#
# COMPARE RESULTS
#
##########################################
### Compare python results to CellFIT results

gamma_p = gamma2.copy()[:-1]
print(len(gamma_p))
print('----------CellFIT results excl edges------------')
#mean, var, std = st.mvsdist(gamma_c)
print('Mean =', gamma_c.mean())
print('Interval: [%f, %f]'%(gamma_c.min(),gamma_c.max()))
print('Std =', gamma_c.std())
figure(2)
plt.hist(gamma_c, bins=30, density=True)
plt.title('CellFIT results')

# print('----------CellFIT results incl edges------------')
# mean, var, std = st.mvsdist(gamma_c_inc)
# print('Mean =',mean.mean())
# print('Interval: [%f, %f]'%(gamma_c_inc.min(),gamma_c_inc.max()))
# print('Std =', gamma_c_inc.std())
# figure(2)
# plt.hist(gamma_c_inc, bins=30, density=True)
# plt.title('CellFIT results')

print('----------Python results------------')

print('Mean =', gamma_p.mean())
print('Interval: [%f, %f]'%(gamma_p.min(),gamma_p.max()))
print('Std =', gamma_p.std())
figure(3)
plt.hist(gamma_p, bins=30, density=True)
plt.title('Python results')
plt.show()
