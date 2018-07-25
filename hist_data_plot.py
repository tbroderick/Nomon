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
        sq_sum+=((index-mean)**2)*data_set[index]
    return math.sqrt(sq_sum/(sum(data_set)-1))


data = pickle.load(open("C:/Users/nickb/PycharmProjects/Nomon/keyboard/barsdump.p",'rb'))
print(len(data))

act_avg = data[0][1]
pred_avg = data[0][0]
length = len(data[0][0])
for set in data[1:]:
    act_avg=[act_avg[i]+set[1][i] for i in range(length)]
    pred_avg = [pred_avg[i] + set[0][i] for i in range(length)]

# act_avg = [i/len(data) for i in act_avg]
# pred_avg = [i/len(data) for i in pred_avg]
data=[[pred_avg, act_avg]]

for set in data:

    pretrain = set[0][30:60]
    actual = set[1][30:60]

    pretrain = [i * 100 / sum(pretrain) for i in pretrain]
    actual = [i * 100 / sum(actual) for i in actual]

    length = len(pretrain)

    modes = [0 for i in range(length)]
    modes[calc_mode(pretrain)] = max(pretrain + actual) * 1.1
    modes[calc_mode(actual)] = max(pretrain + actual) * 1.1

    mp = calc_mode(pretrain)
    ma = calc_mode(actual)
    sp = std_dev(pretrain)
    sa = std_dev(actual)

    stddevp=[[mp+sp]*3+[mp-sp]*3,[0,max(pretrain + actual) * 1.1, 0]*2]
    stddeva = [[ma + sa] * 3 + [ma - sa] * 3, [0, max(pretrain + actual) * 1.1, 0] * 2]

    plt4 = plt.plot(stddeva[0], stddeva[1], '--', alpha=1)
    plt3 = plt.plot(stddevp[0], stddevp[1], '--', alpha=1)
    plt1=plt.bar(range(length), actual, width=1, alpha = 0.5)
    plt2=plt.bar(range(length), pretrain,width=1, alpha = 0.5)


    plt.legend((plt1[0], plt2[0], plt3[0], plt4[0]), ('act', 'pre'))
    plt.show()