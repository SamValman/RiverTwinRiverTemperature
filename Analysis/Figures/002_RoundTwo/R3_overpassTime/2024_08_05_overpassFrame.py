# -*- coding: utf-8 -*-
"""
Created on Mon Aug  5 15:31:58 2024

@author: lgxsv2
"""

import matplotlib.pyplot as plt
import pandas as pd
import numpy as np

fp = r"C:\Users\lgxsv2\OneDrive - The University of Nottingham\PhD\yr_2\18_PaperThree\RT_temperaturePrivate\Analysis\Figures\laptopBased_overpassTime\GEEDates.csv"
fp = r"D:\RT_temperaturePrivate\Analysis\Figures\002_RoundTwo\R3_overpassTime\GEEDates.csv"
df = pd.read_csv(fp)


# organise df 
df['day'] = pd.to_datetime(df['date'], format='%d/%m/%Y').dt.day
df['time_hours'] = pd.to_timedelta(df['time']).dt.total_seconds() / 3600

## Plan some markers
markers = {
    'L9': 'o',     # Circle
    'L8': 's',     # Square
    'Aster': '^',        # Diamond
    'Ecostress': 'D'     # Triangle
}










fig, ax = plt.subplots()

# Set up the x-axis with dates from 1 to 30
ax.set_xlim(1, 31)
ax.set_xticks(np.arange(1, 31, 2))
ax.set_xlabel('Date in July')

# Set up the right y-axis with hours of the day in 3-hour increments
# ax = ax.twinx()
# ax.set_ylim(6, 21)
ax.set_yticks(np.arange(3, 22, 3))
ax.set_ylabel('Local time')
from matplotlib.ticker import FuncFormatter

def format_func(value, tick_number):
    return f'{int(value):02d}:00'

ax.yaxis.set_major_formatter(FuncFormatter(format_func))
# Title for the plot
# plt.title('Dates and Hours of the Day')

# Show grid for better readability
# for i, row in df.iterrows():
#     ax.plot()
#     ax.annotate(row['sat'], (row['day'], row['time_hours']), textcoords="offset points", xytext=(0,5), ha='center')
for sat, marker in markers.items():
    subset = df[df['sat'] == sat]
    ax.scatter(subset['day'], subset['time_hours'], label=sat, marker=marker, s=100, zorder=5)  # s=100 sets marker size
ax.grid(True)

plt.legend(title='Satellite System', loc='lower left')

# Display the plot
plt.show()
