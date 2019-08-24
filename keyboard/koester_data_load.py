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

# for phase_num in list(range(1, 3)):
#     phase_data = df[df['phase'] == phase_num][['avgTrialTime', 'sdTrialTime']]
#
#     x = np.arange(0, 3000, 1)
#     pdf_values = np.zeros(x.shape)
#     for point in phase_data.values:
#         mean, std = point
#         pdf_values += stats.norm(mean, std).pdf(x)
#
#     pdf_values /= np.sum(pdf_values)
#
#
#     color = ["darkslategrey", "cadetblue"][phase_num-1]
#     ax.plot(x, pdf_values, lw=3, label="Trial Time: "+str(phase_num) + " press", c=color)
#
#     avg_mean = np.average(phase_data.values.T[0])
#
#     avg_std = np.sqrt(np.average(np.square(phase_data.values.T[1])))
#
#     plt.axvline(avg_mean, color=color, linestyle="--", alpha=0.8)
#     for i in [-1,1]:
#         plt.axvline(avg_mean + i*avg_std, color=color, linestyle=":", alpha=0.6)
# # plt.show()

response_time_data = df['avgResponseTime'].values[np.where(np.isnan(df['avgResponseTime'].values) == False)]
kernel = stats.gaussian_kde(response_time_data)
x = np.arange(0, 2500, 1)
plt.plot(x, kernel(x), lw=3, label="Response Time", c="rosybrown")

prob_values = np.array(kernel(x))

cdf = np.zeros(x.shape)
for i in range(len(cdf)):
    cdf[i] = np.sum(prob_values[np.where(x < x[i])])

percentile_95 = np.min(np.where(cdf >= 0.95))
plt.axvline(percentile_95, color="black", label="95th percentile")

avg_mean = np.average(response_time_data)

avg_std = np.std(response_time_data)

plt.axvline(avg_mean, color="rosybrown", linestyle="--", alpha=0.8)
for i in [-1,1]:
    plt.axvline(avg_mean + i*avg_std, color="rosybrown", linestyle=":", alpha=0.6)

plt.legend()
plt.xlabel("Time (ms)")
plt.ylabel("probability")
plt.show()
