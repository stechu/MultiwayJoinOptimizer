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
def coordinate_to_worker_id(coordinate, dim_sizes):
    result = 0
    for k, v in enumerate(coordinate):
        result = result+v
        if k != (len(dim_sizes)-1):
            result = result * dim_sizes[k]
    return result


# recursively get coordinates
def get_coordinates(coordinates, dim_sizes, coordinate, current_idx):
    if(current_idx == len(dim_sizes)):
        coordinates.append(coordinate)
    else:
        for i in range(0, dim_sizes[current_idx]):
            cp_coordinates = coordinate[:]
            cp_coordinates.append(i)
            get_coordinates(coordinates, dim_sizes,
                            cp_coordinates, current_idx+1)


# compute hyper cube partition given
def hyper_cube_partition(dim_sizes, hashed_dims):
    coordinates = []
    get_coordinates(coordinates, dim_sizes, [], 0)
    cell_partition = dict()
    for coordinate in coordinates:
        cell_number = 0
        count = 1
        for dim in hashed_dims:
            cell_number += coordinate[dim]
            if count != len(dim_sizes):
                cell_number *= dim_sizes[dim]
            count += 1
        if cell_number in cell_partition:
            cell_partition[cell_number].append(
                coordinate_to_worker_id(coordinate, dim_sizes))
        else:
            cell_partition[cell_number] = [
                coordinate_to_worker_id(coordinate, dim_sizes)]
            #raise Exception("Error!")

    return [v[1] for v in sorted(cell_partition.items())]


# return false if the product is greater than k
def product_not_greater(dims, k):
    r = 1
    for i in dims:
        r *= i
        if r > k:
            return False
    return True


# compute work load give a hyper cube size assignment
def workLoad(dim_sizes, child_sizes, join_field_map):
    if len(dim_sizes) != len(join_field_map):
        raise Exception("dim_sizes must match the length of join_field_map")
    # build reverse index: relation->joinField
    rIndex = [[] for i in range(0, len(child_sizes))]
    for i, jf_list in enumerate(join_field_map):
        for jf in jf_list:
            rIndex[jf[0]].append(i)
    load = float(0)
    for i, size in enumerate(child_sizes):
        scale = 1
        for index in rIndex[i]:
            scale = scale*dim_sizes[index]
        load = load + float(child_sizes[i])/float(scale)
        #print i, child_sizes[i], scale, load
    return load


# using recursive call: will expode the stack
def enum_dim_sizes(visited, dim_sizes, num_server,
                   child_sizes, join_field_map):
    visited.add(dim_sizes)
    yield (workLoad(dim_sizes, child_sizes, join_field_map), dim_sizes)
    for i, d in enumerate(dim_sizes):
        new_dim_sizes = dim_sizes[0:i]
        + tuple([dim_sizes[i]+1]) + dim_sizes[i+1:]
        if product_not_greater(new_dim_sizes, num_server)\
           and new_dim_sizes not in visited:
            for x in enum_dim_sizes(visited, new_dim_sizes, num_server,
                                    child_sizes, join_field_map):
                yield x


def get_dim_size_dfs(num_server, child_sizes, join_field_map):
    firstDims = tuple([1 for x in join_field_map])
    return min(enum_dim_sizes(set(), firstDims, num_server,
                              child_sizes, join_field_map))


# using standard bfs
def getDimSizesBFS(num_server, child_sizes, join_field_map):
    visited = set()
    toVisit = collections.deque()
    toVisit.append(tuple([1 for i in join_field_map]))
    minWorkLoad = sum(child_sizes)
    while len(toVisit) > 0:
        dim_sizes = toVisit.pop()
        if workLoad(dim_sizes, child_sizes, join_field_map) < minWorkLoad:
            minWorkLoad = workLoad(dim_sizes, child_sizes, join_field_map)
            optimalDimSizes = dim_sizes
        visited.add(dim_sizes)
        for i, d in enumerate(dim_sizes):
            new_dim_sizes = dim_sizes[0:i] +\
                tuple([dim_sizes[i]+1]) + dim_sizes[i+1:]
            if product_not_greater(new_dim_sizes, num_server)\
               and new_dim_sizes not in visited:
                toVisit.append(new_dim_sizes)
    return (minWorkLoad, optimalDimSizes)


# get optimal fracitonal dim size, see P9 in http://arxiv.org/abs/1401.1872
def frac_dim_sizes(num_server, child_sizes, join_field_map):
    # get relation -> variable mapping
    rel_var_amp = dict()
    for idx, flist in enumerate(join_field_map):
        for (r, v) in flist:
            if r in rel_var_amp:
                rel_var_amp[r].append(idx)
            else:
                rel_var_amp[r] = [idx]
    # LP problem formulation
    prob = LpProblem("Hyper Cube Size", LpMinimize)
    # transform relations sizes to log scale
    log_rel_size = [math.log(s, num_server) for s in child_sizes]
    # define share size exponents
    share_ex_vars = LpVariable.dicts("e", range(0, len(join_field_map)), 0, 1)
    # objective function
    obj = LpVariable("obj", 0, None)
    prob += lpSum(obj)
    # constraint: sum of share exponents is at most 1
    prob += lpSum(share_ex_vars) <= 1
    # constraints: work load on each relation is smaller than obj
    for idx, val in enumerate(log_rel_size):
        prob += lpSum([share_ex_vars[var] for var
                       in rel_var_amp[idx]]) + obj >= log_rel_size[idx]
    prob.solve()
    answer = dict()
    for v in prob.variables():
        answer[v.name] = v.value()
    #print answer
    return (answer["obj"], [answer["e_{}".format(i)]
                            for i in range(0, len(join_field_map))])
