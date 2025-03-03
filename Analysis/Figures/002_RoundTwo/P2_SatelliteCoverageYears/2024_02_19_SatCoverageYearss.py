# -*- coding: utf-8 -*-
"""
Created on Mon Feb 19 00:29:53 2024

@author: lgxsv2
"""

import matplotlib.pyplot as plt 
import pandas as pd 
#%%
fn = r"C:\Users\lgxsv2\OneDrive - The University of Nottingham\PhD\yr_2\18_PaperThree\RT_temperaturePrivate\Analysis\GenericFigures\SatelliteCoverageYears\SatelliteDates.csv"

df = pd.read_csv(fn)

#%% grey plain full length
plt.close('all')

# Prepare data for plotting
lines = []

for index, row in df.iterrows():
    sat = row['Sat']
    start_year = row['date_start']
    end_year = min(row['date_end'], 2024)  # Cap end year at 2024
    lines.append([(start_year, sat), (end_year, sat)])

# Create the plot
plt.figure(figsize=(10, 6))
lines.reverse()

# Plot each line separately
s = 1
for line in lines:
    if s!=9:
        plt.plot(*zip(*line), linestyle='-', linewidth=8, c='grey')#, alpha=0)
        s+=1
    else:
        plt.plot(*zip(*line), linestyle='-', linewidth=8,c='Blue')#, alpha=0)

# Customize plot
plt.xlabel('Period of data capture')
plt.ylabel('Thermal satellite')
# plt.title('Satellite Data Capture Timeline')
plt.yticks(df['Sat'])
plt.grid(False)
plt.xlim(2010, 2024)
plt.gca().spines['top'].set_visible(False)
plt.gca().spines['right'].set_visible(False)
# Show plot
plt.tight_layout()
plt.show()


#%% top figure
plt.close('all')
plt.figure()
plt.gca().spines['top'].set_visible(False)
plt.gca().spines['right'].set_visible(False)
plt.gca().spines['bottom'].set_visible(False)

x = list(range(2010,2025))
y = [3,3,3,3, 4,4,4,4, 4,5,5,5,5,5,5]
plt.plot(x,y, c='red', linestyle='-')
plt.ylabel('Concurrent thermal \n image capture')
plt.yticks([])
plt.xticks([])
plt.xlim(2010, 2024)



#%% with avg line - didnt work





# # Prepare data for plotting
# lines = []
# year_counts = {year: 0 for year in range(1984, 2025)}

# for index, row in df.iterrows():
#     sat = row['Sat']
#     start_year = row['date_start']
#     end_year = min(row['date_end'], 2024)  # Cap end year at 2024
#     for year in range(start_year, end_year + 1):
#         lines.append([(year, sat), (year + 1, sat)])  # Each satellite line spans one year
#         year_counts[year] += 1

# # Create the plot
# plt.figure(figsize=(10, 6))

# # Plot each line separately
# for line in lines:
#     plt.plot(*zip(*line), linestyle='-', c='Grey')

# # Plot the additional line at the bottom with color coding based on counts
# bottom_line = [(year, year_counts[year]) for year in range(1984, 2025)]
# plt.plot(*zip(*bottom_line), linestyle='-', color='red')  # Adjust color as needed

# # Customize plot
# plt.xlabel('Year')
# plt.ylabel('Satellite')
# # plt.title('Satellite Data Capture Timeline')
# plt.yticks(df['Sat'])
# plt.grid(False)

# Show plot
# plt.tight_layout()
# plt.show()

#%%
