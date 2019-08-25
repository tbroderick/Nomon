import pandas as pd
from pandas import ExcelWriter
from pandas import ExcelFile
from matplotlib import pyplot as plt
import seaborn as sns
from scipy import stats
import numpy as np
import math


df = pd.read_excel('resources/koester_data.xlsx', sheetname='Sheet1')

print("Column headings:", list(df.columns))

fig, ax = plt.subplots()
fig.set_size_inches(10, 8)

def plot_data(data, color):
    kernel = stats.gaussian_kde(data)
    x = np.arange(0, 2000, 1)
    plt.plot(x, kernel(x), lw=3, label="Response Time", c=color)

    prob_values = np.array(kernel(x))

    cdf = np.zeros(x.shape)
    for i in range(len(cdf)):
        cdf[i] = np.sum(prob_values[np.where(x < x[i])])

    percentile_95 = np.min(np.where(cdf >= 0.95))
    plt.axvline(percentile_95, color="black", label="95th percentile")

    avg_mean = np.average(data)

    avg_std = np.std(data)

    plt.axvline(avg_mean, color=color, linestyle="--", alpha=0.8)
    for i in [-1, 1]:
        plt.axvline(avg_mean + i*avg_std, color=color, linestyle=":", alpha=0.6)

    plt.legend()
    plt.xlabel("Time (ms)")


response_time_data = df['avgResponseTime'].values[np.where(np.isnan(df['avgResponseTime'].values) == False)]
plot_data(response_time_data, "rosybrown")

row_time_data = df['rowResponseTime'].values[np.where(np.isnan(df['rowResponseTime'].values) == False)]
col_time_data = df['colResponseTime'].values[np.where(np.isnan(df['colResponseTime'].values) == False)]
row_col_data = np.append(row_time_data, col_time_data)
plot_data(row_col_data, "steelblue")

plt.show()
