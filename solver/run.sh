#!/usr/bin/env bash

MESH_DIR_PATH="../meshes/Mesh002/Outline_0_000.txt"
echo "Mesh directory inputted: $MESH_DIR_PATH"
python solver.py $MESH_DIR_PATH
