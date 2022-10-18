# import pytest
import numpy as np

from tusz_data_processing.feature_functions import number_zero_crossings


def test_number_zero_crossings():
    list1 = np.array([[0, 1, 3, 4, -1, -2, 8, 10, -1, 0]]).T
    list2 = np.array([[-3, 2, -1, 0, -1, 1, 0, 1, 2, 0]]).T
    list3 = [0, 1, 3, 4, -1, -2, 8, 10, -1, 0]
    list4 = np.array(list3)
    list5 = np.zeros(4)
    mat1 = np.hstack((list1, list2))
    assert number_zero_crossings(list1) == 3
    assert number_zero_crossings(list2) == 3
    assert number_zero_crossings(list3) == 3
    assert number_zero_crossings(list4) == 3
    assert number_zero_crossings(list5) == 0
    assert all(number_zero_crossings(mat1) == np.array([3, 3]))


# def test_sort_features():


if __name__ == "__main__":
    exit(0)
