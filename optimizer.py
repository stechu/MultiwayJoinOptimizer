#!/usr/bin/env python

import json


def pretty_json(obj):
    return json.dumps(obj, sort_keys=True, indent=4, separators=(',', ':'))


def coordinate_to_worker_id(coordinate, dimSizes):
    result = 0
    for k, v in enumerate(coordinate):
        result = result+v
        if k != (len(dimSizes)-1):
            result = result * dimSizes[k]
    return result


def get_coordinates(coordinates, dimSizes, coordinate, currentIndex):
    if(currentIndex == len(dimSizes)):
        coordinates.append(coordinate)
    else:
        for i in range(0, dimSizes[currentIndex]):
            cp_coordinates = coordinate[:]
            cp_coordinates.append(i)
            get_coordinates(coordinates, dimSizes,
                            cp_coordinates, currentIndex+1)


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


def main():
    print "hello world"


if __name__ == "__main__":
    main()
