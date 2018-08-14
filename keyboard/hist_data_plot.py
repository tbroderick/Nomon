from __future__ import print_function
import pickle
import math


import matplotlib.pyplot as plt

def calc_mode(data_set):
    return data_set.index(max(data_set))

def std_dev(data_set):
    mean = sum([data_set[i]*i for i in range(len(data_set))])/sum(data_set)
    print(mean)
    sq_sum=0
    for index in range(length):
        sq_sum += ((index-mean)**2)*data_set[index]
    return math.sqrt(sq_sum/(sum(data_set)-1))


datas = [pickle.load(open("C:/Users/nickb/PycharmProjects/Nomon/keyboard/barsdump_default.p", 'rb'))+
         pickle.load(open("C:/Users/nickb/PycharmProjects/Nomon/keyboard/barsdump.p", 'rb')),
         pickle.load(open("C:/Users/nickb/PycharmProjects/Nomon/keyboard/barsdump_old.p", 'rb'))]
for data in datas:
    data_size=len(data)
    act_avg = data[0][1]
    pred_avg = data[0][0]
    length = len(data[0][0])
    for set in data[1:]:
        act_avg=[act_avg[i]+set[1][i] for i in range(length)]
        pred_avg = [pred_avg[i] + set[0][i] for i in range(length)]

    data = [[pred_avg, act_avg]]

    for set in data:

        pretrain = set[0][35:55]
        actual = set[1][35:55]

        pretrain = [i * 100 / sum(pretrain) for i in pretrain]
        actual = [i * 100 / sum(actual) for i in actual]

        length = len(pretrain)
        height = max(pretrain + actual) * 1.1

        modes = [0 for i in range(length)]
        modes[calc_mode(pretrain)] = height
        modes[calc_mode(actual)] = height

        mp = calc_mode(pretrain)-10
        ma = calc_mode(actual)-10
        sp = std_dev(pretrain)
        sa = std_dev(actual)

        # plot histgrams
        plt1 = plt.bar(range(-length/2, length/2), actual, color='b', width=1, alpha=0.5)
        plt2 = plt.bar(range(-length/2,length/2), pretrain, color='r', width=1, alpha=0.5)

        # plot modes
        plt.plot([mp] * 2, [0, height*1.15], linewidth=2, color='r')
        plt.plot([ma] * 2, [0, height*1.15], linewidth=2, color='b')

        # plot std devs
        plt.plot([mp + sp] * 2, [0, height], '--', color='r', alpha=0.75)
        plt.plot([mp - sp] * 2, [0, height], '--', color='r', alpha=0.55)

        plt.plot([ma + sa] * 2, [0, height], '--', color='b', alpha=0.75)
        plt.plot([ma - sa] * 2, [0, height], '--', color='b', alpha=0.75)

        plt.text(max(ma+sa, mp+sp) + 0.5, height * 0.8, "act " + u'\u03C3' + ' = ' + str(round(sa, 3)), color='b', fontsize=12)
        plt.text(max(ma+sa, mp+sp) + 0.5, height * 0.75, "pre " + u'\u03C3' + ' = ' + str(round(sp, 3)), color='r', fontsize=12)

        plt.text(max(ma, mp) + 0.5, height * 1.12, 'act mode = ' + str(ma), color='b', fontsize=12)
        plt.text(max(ma, mp) + 0.5, height * 1.07, 'pre mode = ' + str(mp), color='r', fontsize=12)

        plt.ylabel("Percentage (%)")
        plt.xlabel("Time Difference from Noon (22.125 ms)")


        plt.legend((plt1[0], plt2[0]), ('act', 'pre'))
        if data_size > 10:
            plt.title("New Pretraining--20 Trials", loc='left')
        else:
            plt.title("Old Pretraining--10 Trials", loc='left')

        plt.show()