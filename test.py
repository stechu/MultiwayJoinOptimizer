#!/usr/bin/env python
import optimizer
import unittest

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
            24.0/4.0+36.0/24.0+48.0/6.0)

    def testOpimizer(self):
        joinFieldMap = [[[0, 1], [1, 0]], [[1, 1], [2, 0]],
                        [[2, 1], [3, 0]]]
        childSizes = [36, 72, 64, 36]
        self.assertEqual(
            optimizer.getDimSizesBFS(64, childSizes, joinFieldMap),
            optimizer.getDimSizesDFS(64, childSizes, joinFieldMap)
        )

if __name__ == '__main__':
    unittest.main()
