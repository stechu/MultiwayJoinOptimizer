#!/usr/bin/env python
import optimizer
import unittest
import numpy as np

''' unit test of optimizer
'''


class TestOpimizerFunctions(unittest.TestCase):

    def testWorkLoad1(self):
        joinFieldMap = [[[0, 1], [1, 0]], [[1, 1], [2, 0]], [[0, 0], [2, 1]]]
        dimSizes = [3, 3, 3]
        childSizes = [27, 9, 9]
        self.assertEqual(
            optimizer.workLoad(dimSizes, childSizes, joinFieldMap), 5)

    def testWorkLoad2(self):
        joinFieldMap = [[[0, 1], [1, 0]], [[1, 1], [2, 0]]]
        dimSizes = [4, 6]
        childSizes = [24, 36, 48]
        self.assertEqual(
            optimizer.workLoad(dimSizes, childSizes, joinFieldMap),
            24.0 / 4.0 + 36.0 / 24.0 + 48.0 / 6.0)

    def testOpimizer(self):
        ''' Result(x,y,z,u,v) :- R(x,y), S(y,z), T(z,u), P(u,v)
        '''
        joinFieldMap = [[[0, 1], [1, 0]], [[1, 1], [2, 0]],
                        [[2, 1], [3, 0]]]
        childSizes = [36, 72, 64, 36]
        self.assertEqual(
            optimizer.getDimSizesBFS(64, childSizes, joinFieldMap),
            optimizer.getDimSizesDFS(64, childSizes, joinFieldMap)
        )

    '''
    def testOptFracDimSize(self):
        joinFieldMap = [[[0, 1], [1, 0]], [[1, 1], [2, 0]],
                        [[2, 1], [3, 0]]]
        childSizes = [36, 72, 64, 36]
        optimizer.optDimFracSize(64, childSizes, joinFieldMap)
    '''

    def testOptFracDimSize2(self):
        joinFieldMap = [[[0, 1], [1, 0]], [[1, 1], [2, 0]], [[0, 0], [2, 1]]]
        childSizes = [500, 500, 500]
        (obj, shares) = optimizer.optDimFracSize(64, childSizes, joinFieldMap)
        np.testing.assert_almost_equal(obj, 0.82763333)
        np.testing.assert_almost_equal(
            shares, [0.33333333, 0.33333333, 0.33333333])


if __name__ == '__main__':
    unittest.main()
