import os
import numpy as np
from scipy import stats
from matplotlib import pyplot as plt
from pickle_util import PickleUtil


n=5
arr = np.arange(n)


def reorder_min(arr):
    argmin = np.argmin(arr)
    arr = arr[argmin:] + arr[:argmin]

    return arr


def circle_distance(ind1, ind2, n):
    if ind2 < ind1:
        ind1, ind2 = [ind2, ind1].copy()
    return min(abs(ind2 - ind1), n-ind2+ind1)


def eval_closeness(arr):
    total_closeness = 0
    for index, element in enumerate(arr):
        if index == 0:
            neighbor_plus = 1
            neighbor_minus = 2
        else:
            neighbor_plus = index + 1
            neighbor_minus = index - 1
            if neighbor_plus >= len(arr):
                neighbor_plus = len(arr)-2

        total_closeness = circle_distance(arr.index(neighbor_plus), index, len(arr)) / (neighbor_plus+element)
        total_closeness += circle_distance(arr.index(neighbor_minus), index, len(arr)) / (neighbor_plus+element)
    return total_closeness


def recursive_search(n, prefix=[], highest_orders=set(), highest_num=0, seen_orders=set()):
    for cur_digit in set(range(n)).difference(set(prefix)):
        if cur_digit not in prefix:
            if len(prefix) < n-1:
                sub_highest_orders, sub_highest_num, sub_seen_orders = recursive_search(n, prefix+[cur_digit], highest_orders, highest_num)

                seen_orders.union(sub_seen_orders)

                if sub_highest_num == highest_num:
                    highest_orders.union(sub_highest_orders)

                elif sub_highest_num > highest_num:
                    highest_num = sub_highest_num
                    highest_orders = sub_highest_orders

            else:
                cur_order = tuple(reorder_min(prefix + [cur_digit]))
                if cur_order not in seen_orders:
                    seen_orders.add(cur_order)
                    cur_order_num = eval_closeness(cur_order)

                    if cur_order_num == highest_num:
                        highest_orders.add(cur_order)

                    elif cur_order_num > highest_num:
                        highest_num = cur_order_num
                        highest_orders = {cur_order}

    return highest_orders, highest_num, seen_orders

print(recursive_search(8)[:2])
