from optimizer import *
import unittest
import numpy as np
from shuffle_assignment import ShuffleAssignment

''' unit test of optimizer
'''


class TestOpimizerFunctions(unittest.TestCase):

    def workload_1(self):
        """A(x,y,z) :- R(x,y),S(y,z),T(z,x)"""
        join_conditions = [
            [[0, 1], [1, 0]], [[1, 1], [2, 0]], [[0, 0], [2, 1]]]
        child_num_cols = [2, 2, 2]
        r_index = reversed_index(child_num_cols, join_conditions)
        dim_sizes = [3, 3, 3]
        child_sizes = [27, 9, 9]
        self.assertEqual(
            workload(dim_sizes, child_sizes, r_index), 5)

    def workload_2(self):
        """A(x,y,z) :- R(x,y),S(y,z), T(z,p)"""
        join_conditions = [[[0, 1], [1, 0]], [[1, 1], [2, 0]]]
        dim_sizes = [4, 6]
        child_num_cols = [2, 2, 2]
        r_index = reversed_index(child_num_cols, join_conditions)
        child_sizes = [24, 36, 48]
        self.assertEqual(
            workload(dim_sizes, child_sizes, r_index),
            24.0 / 4.0 + 36.0 / 24.0 + 48.0 / 6.0)

    def optimizer(self):
        # 1. symmetric case: A(x,y,z) :- R(x,y), S(y,z), T(z,x)
        join_conditions = [
            [[0, 1], [1, 0]], [[1, 1], [2, 0]], [[0, 0], [2, 1]]]
        dim_sizes = [4, 4, 4]
        child_num_cols = [2, 2, 2]
        r_index = reversed_index(child_num_cols, join_conditions)
        child_sizes = [50, 50, 50]
        wl_by_opt, _ = get_dim_sizes_bfs(
            64, child_sizes, child_num_cols,  join_conditions)
        self.assertEqual(wl_by_opt, workload(dim_sizes, child_sizes, r_index))

        # 2. Result(x,y,z,u,v) :- R(x,y), S(y,z), T(z,u), P(u,v)
        join_conditions = [[[0, 1], [1, 0]],
                          [[1, 1], [2, 0]],
                          [[2, 1], [3, 0]]]
        child_num_cols = [2, 2, 2, 2]
        child_sizes = [36, 72, 64, 36]
        self.assertEqual(
            get_dim_sizes_bfs(
                64, child_sizes, child_num_cols,  join_conditions),
            get_dim_size_dfs(
                64, child_sizes, child_num_cols, join_conditions)
        )

    def test_frac_dim_size(self):
        join_conditions = [
            [[0, 1], [1, 0]], [[1, 1], [2, 0]], [[0, 0], [2, 1]]]
        child_sizes = [20, 20, 20]
        print frac_dim_sizes(64, child_sizes, join_conditions)

        join_conditions = [[[0, 1], [1, 0]], [[1, 1], [2, 0]],
                          [[2, 1], [3, 0]]]
        child_sizes = [36, 72, 64, 36]
        print frac_dim_sizes(64, child_sizes, join_conditions)

    def frac_dim_size_2(self):
        join_conditions = [
            [[0, 1], [1, 0]], [[1, 1], [2, 0]], [[0, 0], [2, 1]]]
        child_sizes = [500, 500, 500]
        (obj, shares) = frac_dim_sizes(64, child_sizes, join_conditions)
        np.testing.assert_almost_equal(obj, 0.82763333)
        np.testing.assert_almost_equal(
            shares, [0.33333333, 0.33333333, 0.33333333])

    def shuffle_assignment(self):
        def assert_list_of_set(a, b):
            self.assertEqual(map(set, a), map(set, b))
        join_conditions = [[[0, 1], [1, 0]],
                          [[2, 0], [1, 1]],
                          [[0, 0], [2, 1]]]
        child_sizes = [500, 500, 500]
        model = ShuffleAssignment(64, child_sizes,
                                  [10, 20, 10], join_conditions)
        # test r_index
        assert_list_of_set(model.r_index, [[2, 0], [0, 1], [1, 2]])
        self.assertEqual(model.voxel_numbers, [100, 200, 200])
        self.assertEqual(model.coordinate_to_vs((9, 19, 9)), 2000)
        self.assertEqual(model.normalized_voxel_sizes, [10000, 5000, 5000])

    def shuffle_workload(self):
        join_conditions = [[[0, 1], [1, 0]],
                          [[2, 0], [1, 1]],
                          [[0, 0], [2, 1]]]
        child_sizes = [20, 20, 20]
        model = ShuffleAssignment(2, child_sizes,
                                  [2, 1, 1], join_conditions)
        print model.get_wcnf()


if __name__ == '__main__':
    unittest.main()
