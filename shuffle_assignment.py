from operator import mul
import itertools


class ShuffleAssignment(object):

    def __init__(self,
                 num_servers,
                 child_sizes,
                 hc_dim_sizes,
                 join_field_map):
        # validate
        if len(hc_dim_sizes) != len(join_field_map):
            raise Exception("hc_dim_sizes must match the \
                             length of join_field_map")
        # init variables
        self.num_servers = num_servers
        self.child_sizes = child_sizes
        self.hc_dim_sizes = hc_dim_sizes
        self.join_field_map = join_field_map
        self.num_vs = reduce(mul, self.hc_dim_sizes, 1)
        # r_index[i]: indexes of joined fields that is related to relation i
        self.r_index = [[] for i in range(0, len(child_sizes))]
        # compute voxel numbers
        self.voxel_numbers = []
        for i, jf_list in enumerate(join_field_map):
            for jf in jf_list:
                self.r_index[jf[0]].append(i)
        for i, size in enumerate(child_sizes):
            scale = 1
            for index in self.r_index[i]:
                scale = scale*hc_dim_sizes[index]
            self.voxel_numbers.append(scale)
        # compute voxel sizes
        self.normalized_voxel_sizes = []
        for i, num in enumerate(self.voxel_numbers):
            self.normalized_voxel_sizes.append(child_sizes[i]*self.num_vs/num)

    def variable(self, vs, rs):
        """ Return a variable indicating virtual server vs is assigned to
            real server rs.
        """
        return self.num_vs*(rs-1) + vs

    def coordinate_to_vs(self, coordinate):
        """ Return the virtual server id of the coordinate
        """
        if len(coordinate) != len(self.hc_dim_sizes):
            raise Exception(
                "coordinate has {} dims yet hc has {}".format(
                    len(coordinate), len(self.hc_dim_sizes)))
        vs = 0
        for i, s in enumerate(self.hc_dim_sizes):
            vs = vs * s + coordinate[i]
        return vs+1

    def voxel_to_vs(self, vox):
        """ Return an array of virtual servers which are mapped to a vox.
        """
        # helper function: combine two part of coordinates
        def full_coordinate(joined, unjoined):
            coordinates = sorted(joined+unjoined, key=lambda co: co[0])
            return tuple(map(lambda x: x[1], coordinates))

        # 1. coordinates of joined part, specified by the input
        joined = zip(self.r_index[vox["rel"]], vox["dims"])
        # 2. get the ranges for iterations of unjoined part
        unjoined_dims = [dim for dim in range(0, len(self.hc_dim_sizes))
                         if dim not in self.r_index[vox["rel"]]]
        unjoined_ranges = [range(0, self.hc_dim_sizes[dim]) for dim
                           in unjoined_dims]
        # 3. get the coordinates
        coordinates = [full_coordinate(joined, zip(unjoined_dims, subcube_co))
                       for subcube_co in itertools.product(*unjoined_ranges)]
        return [self.coordinate_to_vs(co) for co in coordinates]

    def get_wcnf(self):
        """ print problem model in WCNF (Weighted Conjunctive Normal Format)
        """
        max_size = reduce(mul, self.child_sizes, 1)
        wcnf = []
        # hard constraints: each virtual server must be assigned
        for vs in range(1, self.num_vs+1):
            l = [max_size]
            l.extend([self.variable(vs, rs)
                      for rs in range(1, self.num_servers+1)])
            l.append(0)
            wcnf.append(l)
        # soft constraints: penalty on work load on each server
        for i, size in enumerate(self.child_sizes):
            joined_ranges = [range(0, self.hc_dim_sizes[dim])
                             for dim in self.r_index[i]]
            for rs in range(1, self.num_servers+1):
                for subc_co in itertools.product(*joined_ranges):
                    l = [-self.normalized_voxel_sizes[i]]
                    vox = {
                        "rel": i,
                        "dims": subc_co
                    }
                    for vs in self.voxel_to_vs(vox):
                        l.append(vs)
                    l.append(0)
                    wcnf.append(l)
        return wcnf
