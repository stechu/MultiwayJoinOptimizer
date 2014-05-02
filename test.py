#!/usr/bin/env python
import optimizer
import unittest
import numpy as np
from shuffle_assignment import ShuffleAssignment

''' unit test of optimizer
'''


class TestOpimizerFunctions(unittest.TestCase):

    def test_workload_1(self):
        join_field_map = [[[0, 1], [1, 0]], [[1, 1], [2, 0]], [[0, 0], [2, 1]]]
        dim_sizes = [3, 3, 3]
        child_sizes = [27, 9, 9]
        self.assertEqual(
            optimizer.workload(dim_sizes, child_sizes, join_field_map), 5)

    def test_workload_2(self):
        join_field_map = [[[0, 1], [1, 0]], [[1, 1], [2, 0]]]
        dimSizes = [4, 6]
        child_sizes = [24, 36, 48]
        self.assertEqual(
            optimizer.workload(dimSizes, child_sizes, join_field_map),
            24.0 / 4.0 + 36.0 / 24.0 + 48.0 / 6.0)

    def test_optimizer(self):
        ''' Result(x,y,z,u,v) :- R(x,y), S(y,z), T(z,u), P(u,v)
        '''
        join_field_map = [[[0, 1], [1, 0]],
                          [[1, 1], [2, 0]],
                          [[2, 1], [3, 0]]]
        child_sizes = [36, 72, 64, 36]
        self.assertEqual(
            optimizer.get_dim_sizes_bfs(64, child_sizes, join_field_map),
            optimizer.get_dim_size_dfs(64, child_sizes, join_field_map)
        )

    def test_frac_dim_size(self):
        join_field_map = [[[0, 1], [1, 0]], [[1, 1], [2, 0]],
                          [[2, 1], [3, 0]]]
        child_sizes = [36, 72, 64, 36]
        optimizer.frac_dim_sizes(64, child_sizes, join_field_map)

    def test_frac_dim_size_2(self):
        join_field_map = [[[0, 1], [1, 0]], [[1, 1], [2, 0]], [[0, 0], [2, 1]]]
        child_sizes = [500, 500, 500]
        (obj, shares) = optimizer.frac_dim_sizes(64, child_sizes,
                                                 join_field_map)
        np.testing.assert_almost_equal(obj, 0.82763333)
        np.testing.assert_almost_equal(
            shares, [0.33333333, 0.33333333, 0.33333333])

    def test_shuffle_assignment(self):
        def assert_list_of_set(a, b):
            self.assertEqual(map(set, a), map(set, b))
        join_field_map = [[[0, 1], [1, 0]],
                          [[2, 0], [1, 1]],
                          [[0, 0], [2, 1]]]
        child_sizes = [500, 500, 500]
        model = ShuffleAssignment(64, child_sizes,
                                  [10, 20, 10], join_field_map)
        # test r_index
        assert_list_of_set(model.r_index, [[2, 0], [0, 1], [1, 2]])
        self.assertEqual(model.voxel_numbers, [100, 200, 200])
        self.assertEqual(model.coordinate_to_vs((9, 19, 9)), 2000)
        self.assertEqual(model.normalized_voxel_sizes, [10000, 5000, 5000])
        print len(model.get_wcnf())


if __name__ == '__main__':
    unittest.main()
