#!/usr/bin/env python

import json
import argparse
import collections
from pulp import *
import math

#parse args
parser = argparse.ArgumentParser(
    description='collect running time of workers of a query')
parser.add_argument("-query", type=str, help="query json file")
parser.add_argument("-worker_number", type=int, help="number of workers")
parser.add_argument("-e", type=float, help="relax parameter")
args = parser.parse_args()


def pretty_json(obj):
    return json.dumps(obj, sort_keys=True, indent=4, separators=(',', ':'))


# convert a coordinate to work id
def coordinate_to_worker_id(coordinate, dimSizes):
    result = 0
    for k, v in enumerate(coordinate):
        result = result+v
        if k != (len(dimSizes)-1):
            result = result * dimSizes[k]
    return result


# recursively get coordinates
def get_coordinates(coordinates, dimSizes, coordinate, currentIndex):
    if(currentIndex == len(dimSizes)):
        coordinates.append(coordinate)
    else:
        for i in range(0, dimSizes[currentIndex]):
            cp_coordinates = coordinate[:]
            cp_coordinates.append(i)
            get_coordinates(coordinates, dimSizes,
                            cp_coordinates, currentIndex+1)


# compute hyper cube partition given
def hyper_cube_partition(dimSizes, hashedDims):
    coordinates = []
    get_coordinates(coordinates, dimSizes, [], 0)
    cell_partition = dict()
    for coordinate in coordinates:
        cell_number = 0
        count = 1
        for dim in hashedDims:
            cell_number += coordinate[dim]
            if count != len(dimSizes):
                cell_number *= dimSizes[dim]
            count += 1
        if cell_number in cell_partition:
            cell_partition[cell_number].append(
                coordinate_to_worker_id(coordinate, dimSizes))
        else:
            cell_partition[cell_number] = [
                coordinate_to_worker_id(coordinate, dimSizes)]
            #raise Exception("Error!")

    return [v[1] for v in sorted(cell_partition.items())]


# return false if the product is greater than k
def productNotGreater(dims, k):
    r = 1
    for i in dims:
        r *= i
        if r > k:
            return False
    return True


# compute work load give a hyper cube size assignment
def workLoad(dimSizes, childSizes, joinFieldMap):
    if len(dimSizes) != len(joinFieldMap):
        raise Exception("dimSizes must match the length of joinFieldMap")
    # build reverse index: relation->joinField
    rIndex = [[] for i in range(0, len(childSizes))]
    for i, jfList in enumerate(joinFieldMap):
        for jf in jfList:
            rIndex[jf[0]].append(i)
    load = float(0)
    for i, size in enumerate(childSizes):
        scale = 1
        for index in rIndex[i]:
            scale = scale*dimSizes[index]
        load = load + float(childSizes[i])/float(scale)
        #print i, childSizes[i], scale, load
    return load


# using recursive call: will expode the stack
def enumerateDimSizes(visited, dimSizes, numberOfServers,
                      childSizes, joinFieldMap):
    visited.add(dimSizes)
    yield (workLoad(dimSizes, childSizes, joinFieldMap), dimSizes)
    for i, d in enumerate(dimSizes):
        newDimSizes = dimSizes[0:i] + tuple([dimSizes[i]+1]) + dimSizes[i+1:]
        if productNotGreater(newDimSizes, numberOfServers)\
           and newDimSizes not in visited:
            for x in enumerateDimSizes(visited, newDimSizes, numberOfServers,
                                       childSizes, joinFieldMap):
                yield x


def getDimSizesDFS(numberOfServers, childSizes, joinFieldMap):
    firstDims = tuple([1 for x in joinFieldMap])
    return min(enumerateDimSizes(set(), firstDims, numberOfServers,
                                 childSizes, joinFieldMap))


# using standard bfs
def getDimSizesBFS(numberOfServers, childSizes, joinFieldMap):
    visited = set()
    toVisit = collections.deque()
    toVisit.append(tuple([1 for i in joinFieldMap]))
    minWorkLoad = sum(childSizes)
    while len(toVisit) > 0:
        dimSizes = toVisit.pop()
        if workLoad(dimSizes, childSizes, joinFieldMap) < minWorkLoad:
            minWorkLoad = workLoad(dimSizes, childSizes, joinFieldMap)
            optimalDimSizes = dimSizes
        visited.add(dimSizes)
        for i, d in enumerate(dimSizes):
            newDimSizes = dimSizes[0:i] +\
                tuple([dimSizes[i]+1]) + dimSizes[i+1:]
            if productNotGreater(newDimSizes, numberOfServers)\
               and newDimSizes not in visited:
                toVisit.append(newDimSizes)
    return (minWorkLoad, optimalDimSizes)


# get optimal fracitonal dimension size
def optDimFracSize(numberOfServers, childSizes, joinFieldMap):
    # get relation -> variable mapping
    relVarMap = dict()
    for flist in joinFieldMap:
        for (r, v) in flist:
            if r in relVarMap:
                relVarMap[r].append(v)
            else:
                relVarMap[r] = [v]
    # LP problem formulation
    shareExIndices = range(0, len(childSizes))
    logRelSize = [math.log(s, numberOfServers) for s in childSizes]
    prob = LpProblem("Hyper Cube Size", LpMinimize)
    # define share size exponents
    shareExVars = LpVariable.dicts("e", shareExIndices, 0, 1)
    # objective function
    obj = LpVariable("obj", 0, None)
    prob += lpSum(obj)
    # constraint: sum of share exponents is at most 1
    prob += lpSum(shareExVars) <= 1
    # constraints: work load on each relation is smaller than obj
    for idx, val in enumerate(logRelSize):
        prob += lpSum([shareExVars[var] for var in relVarMap[idx]]) + obj >=\
            logRelSize[idx]
    print prob
    return 0
