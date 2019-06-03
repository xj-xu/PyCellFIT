#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Tue Mar 26 17:34:57 2019

@author: xj
"""

import matplotlib.pyplot as plt
import numpy as np
from osgeo import gdal

ImArray = []
EdgeDensity = 4 # number of intermediate nodes
LIST_TJs, LIST_EJs = [], []
TJ_pos_tuple = []
LIST_EdgeGroups = []
eX, eY = [], [] # x and y positions of edge nodes already parsed
N_TJs = 0

def ReadImage(ImPath):
    """
    ImPath[str]: directory path of the image to be read in
    returns: 2d numpy array of the pixel values
    """
    global ImArray
    ds = gdal.Open(ImPath)
    ImArray = np.array(ds.GetRasterBand(1).ReadAsArray())
    
def DisplayRaster():
    """
    ImArray: 2d numpy array
    Plots the watershed image as a colormap390k
    """
    global ImArray, LIST_TJs, LIST_EJs
    X, Y = np.meshgrid([i for i in range(ImArray.shape[1])], [i for i in range(ImArray.shape[0])])
    plt.figure(figsize=(10,10))
    plt.pcolormesh(X, Y, ImArray, cmap=plt.cm.Greys)
    plt.scatter(LIST_EJs[:, 1], LIST_EJs[:, 0], c='red', s=5)
    plt.scatter(LIST_TJs[:, 1], LIST_TJs[:, 0], c='yellow', s=10)
    plt.xlabel('x %d'%ImArray.shape[1])
    plt.ylabel('y %d'%ImArray.shape[0])
    plt.show()
    
def FilterDanglingPixels():
    """
    """
    global ImArray
    PixelsRemoved = 0
    for i in range(ImArray.shape[0] - 1):
        for j in range(ImArray.shape[1] - 1):
            p0 = ImArray[i, j]
            p1 = ImArray[i - 1, j]
            p2 = ImArray[i + 1, j]
            p3 = ImArray[i, j - 1]
            p4 = ImArray[i, j + 1]
            if p0 != p1 and p0 != p2 and p0 != p3 and p0 != p4:
                PixelsRemoved += 1
                if p1 == p2 or p1 == p3 or p1 == p4:
                    ImArray[i, j] = p1
                elif p2 == p3 or p2 == p4:
                    ImArray[i, j] = p2
                else:
                    ImArray[i, j] = p3
    print('Dangling Pixels Removed = %d'%PixelsRemoved)
    return ImArray
    
def GetNeiPix(x, y):
    """
    ImArray[numpy.ndarray]: 2d array of watershed image
    x and y[int]: x and y position of node (the dual lattice of the pixel lattice)
    Returns length of an unique list of the 4 neighboring pixel values
    """
    global ImArray
    return len(np.unique([ImArray[x - 1, y - 1],
            ImArray[x - 1, y],
            ImArray[x, y - 1],
            ImArray[x, y]]))
    
def CreateNodeLists():
    """
    ImArray[numpy.ndarray]: 2d array of watershed image
    1) Form a x_len by y_len dual square lattice grid to the pixel lattice grid.
    2) Find triple junctions and edge junctions by looking at
       the 4 immediate neighbors to each complement node.
    3) Store info that can be directly used for tension calculations
    Also updates N_TJs.
    """
    global ImArray, N_TJs
    x_len = ImArray.shape[0] - 1
    y_len = ImArray.shape[1] - 1
    Info_TJs = [] # triple junction info [x, y]
    Info_EJs = [] # edge junction info [x, y]
    for x in range(1, x_len):
        for y in range(1, y_len):
            N = GetNeiPix(x, y)
            if N <= 1:
                continue
            elif N == 2:
                Info_EJs.append([x, y])
            elif N == 3:
                Info_TJs.append([x, y])
                TJ_pos_tuple.append((x, y))
            else:
                print('ERROR: QUAD JUNCTION FOUND AT (%d, %d)'%(x, y))
    N_TJs = len(Info_TJs)
    return np.array(Info_TJs), np.array(Info_EJs)

def FindPath(x0, y0):
    """
    ImArray[numpy.ndarray]: 2d array of watershed image
    x and y[int]: initial position x and y position of node (the dual lattice of the pixel lattice)
    Recursively traces from the starting TJ to the ending TJ.
    """
    global ImArray, eX, eY, TJ_pos_tuple
    indx, indy = [-1, 0, 1, 0], [0, 1, 0, -1]
    while(True):
        # break condition: reach other TJ
        if GetNeiPix(x0, y0) == 3:
            return TJ_pos_tuple.index((x0, y0))
        for n in range(4): # nodes left, up, right, down
            xn, yn = (x0 + indx[n]), (y0 + indy[n])
            if GetNeiPix(xn, yn) == 2:
                eX.append(xn)
                eY.append(yn)
                FindPath(xn, yn)
    
    
def BuildEdgeMaps():
    """
    ImArray[numpy.ndarray]: 2d array of watershed image
    1) Go through each triple junction
    2) Each TJ have 4 neighbor pixels, 3 of which will lead to an edge (by definition of TJ)
    3) Skip edge if it is already identified, since there are many overlaps
    4) Record edgegroup by an ID, start and end TJs, and intermediate edge nodes
    """
    global ImArray, N_TJs, LIST_TJs, LIST_EdgeGroups, eX, eY
    indx, indy = [-1, 0, 1, 0], [0, 1, 0, -1]
    EdgeGroup_ID = 1
    for i in range(N_TJs):
        x, y = LIST_TJs[i][0], LIST_TJs[i][1]
        for n in range(4): # nodes left, up, right, down
            xn, yn = (x + indx[n]), (y + indy[n]) # NOTE! x and y may be reversed, causing bugs
            if xn in eX and yn in eY:
                continue
            if GetNeiPix(xn, yn) == 2:
                LIST_EdgeGroups.append([EdgeGroup_ID, i, FindPath(xn, yn)])
                EdgeGroup_ID += 1
        
    
def GetMedianCellRadius(watershedIm):
    """
    """
    pass

def GenerateMesh():
    """
    """
    pass
    
def CreateAndSaveMesh(watershedIm, imName, setRadius):
    """
    
    """
    if setRadius:
        AvgCellRadius = GetMedianCellRadius(watershedIm)
        print('Average cell radius = %d (pixels)'%AvgCellRadius)
    
    maxSegLen = AvgCellRadius / (EdgeDensity - 1.0)
    GenerateMesh(watershedIm, maxSegLen)
    
def main(path):
    """
    """
    global LIST_TJs, LIST_EJs
    ReadImage(path)
    # FilteredImArray = FilterDanglingPixels()
    LIST_TJs, LIST_EJs = CreateNodeLists()
    DisplayRaster()
    BuildEdgeMaps()
    

if __name__ == "__main__":
    main("../meshes/tension_test_meshes/CellFIT_MeshOfHexagonalCells120.tif")
# "../meshes/Mesh002/Map0.png"
# "../meshes/Mesh002/Outline_0_000.tif"