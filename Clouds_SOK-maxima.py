#Make cloudplots. This code was written with the help of chatGPT
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
from scipy.stats import gaussian_kde
from matplotlib.colors import LinearSegmentedColormap

# Import paths (in same folder)
file_paths = {
    "SOK1": "SOK1_2021-05-06.csv",
    "SOK1_2": "SOK1_2021-05-03.csv",
    "SOK1_3": "SOK1_2024-01-17.csv",
    "SOK1_manual": "SOK1_manual_measurements.csv",
    "SOK2": "SOK2_2021-07-27.csv",
    "SOK2_2": "SOK2_2021-07-28.csv",
    "SOK2_manual": "SOK2_manual_measurements.csv",
    "SOK5": "SOK5_2021-05-19.csv",
    "SOK5_2": "SOK5_2021-05-26.csv",
    "SOK5_3pt1": "SOK5_2023-02-24_pt1.csv",
    "SOK5_3pt2": "SOK5_2023-02-24_pt2.csv",
    "SOK5_manual": "SOK5_manual_measurements.csv",
    "SOK5_abl": "SOK5abl_2023-11-05_stack0.csv",
    "SOK5_abl_1": "SOK5abl_2023-11-05_stack1.csv"
}

# Define Matplotlib colormaps for each SOK group
group_colormaps = {
    "SOK1": LinearSegmentedColormap.from_list("custom_red", [(1,1,1,0), "red"], N=3),
    "SOK2": LinearSegmentedColormap.from_list("custom_orange", [(1,1,1,0), "orange"], N=3),
    "SOK5": LinearSegmentedColormap.from_list("custom_blue", [(1,1,1,0), "blue"], N=3),
    "SOK5abl": LinearSegmentedColormap.from_list("custom_purple", [(1,1,1,0), "purple"], N=3)
}

# Load datasets
dfs = {}
for key, path in file_paths.items():
    try:
        dfs[key] = pd.read_csv(path, sep=',', decimal='.')
    except FileNotFoundError:
        print(f"Warning: {path} not found. Skipping.")

# Define figure size in pixels, standard width is overriden to have each developmental stage a different width. For each stage, specify the width of LRP in µm. Remove the # for the stage you want to see. Add # for all other stages.
#width_px = 300  # width in pixels
height_px = 600  # height in pixels
dpi = 100  # dots per inch

#Founder
Xmin = 11
Xmax = 15
width_px = 150

#stage I
#Xmin = 8
#Xmax = 15
#width_px = 150

#stage II
#Xmin = 15
#Xmax = 23
#width_px = 200

#stage III
#Xmin = 23
#Xmax = 30
#width_px = 300

#stage IV
#Xmin = 30
#Xmax = 38
#width_px = 380

#stage V
#Xmin = 38
#Xmax = 45
#width_px = 450

#stage VI
#Xmin = 45
#Xmax = 50
#width_px = 500

#stage VII
#Xmin = 50
#Xmax = 60
#width_px = 600

#stage eLR
#Xmin = 60
#Xmax = 130
#width_px = 1000

#All
#Xmin = 0
#Xmax = 150
#width_px = 1000

# Convert pixels to inches
fig_width = width_px / dpi
fig_height = height_px / dpi

# Create plot
fig, ax = plt.subplots(figsize=(fig_width, fig_height))
fig.patch.set_facecolor("white")
ax.set_facecolor("white")

# Define grid for KDE (cloud) contouring
xmin, xmax = 0, 1
ymin, ymax = 0, 0.5
xgrid, ygrid = np.meshgrid(np.linspace(xmin, xmax, 100), np.linspace(ymin, ymax, 200))

# Track z-order to make sure first plots are not hidden
z_order = 1

# To store number of valid data points per SOK group
group_counts = {}

# Iterate through each SOK group separately
for sok_group, cmap in group_colormaps.items():
    all_x = []
    all_y = []
    total_filtered_rows = 0  # Track how many rows are used after width filter
    
    for key, df in dfs.items():
        if key.startswith(sok_group):
            required_columns = [
                "Width (µm)",
                "Max 1 X / Columns with Max > 0", "Deviation from 0.5 (Max 1)",
                "Max 2 X / Columns with Max > 0", "Deviation from 0.5 (Max 2)",
                "Max 3 X / Columns with Max > 0", "Deviation from 0.5 (Max 3)"
            ]
            #grabs the columns for the three maxima from csv file
            if not all(col in df.columns for col in required_columns):
                continue
            
            X = df["Width (µm)"] / 10
            #width was off by a factor 10 in the columns, correcting it here
            df_filtered = df[(X >= Xmin) & (X <= Xmax)].copy()
            total_filtered_rows += len(df_filtered)
            if df_filtered.empty:
                continue

            all_x.extend(df_filtered["Max 1 X / Columns with Max > 0"])
            all_y.extend(df_filtered["Deviation from 0.5 (Max 1)"])
            
            all_x.extend(df_filtered["Max 2 X / Columns with Max > 0"])
            all_y.extend(df_filtered["Deviation from 0.5 (Max 2)"])
            
            all_x.extend(df_filtered["Max 3 X / Columns with Max > 0"])
            all_y.extend(df_filtered["Deviation from 0.5 (Max 3)"])
    
     #Only proceed if data exists
    if len(all_x) > 0 and len(all_y) > 0:
        #convert to array
        all_x = np.array(all_x)
        all_y = np.array(all_y)
        
        #Log data
        print(f"{sok_group}: {total_filtered_rows} rows after width filter")
        print(f"{sok_group}: {len(all_x)} raw (x, y) points before NaN/Inf filtering")

        #Clean data: remove NaN and Infinite values
        valid_mask = (~np.isnan(all_x)) & (~np.isnan(all_y)) & (~np.isinf(all_x)) & (~np.isinf(all_y))
        all_x, all_y = all_x[valid_mask], all_y[valid_mask]
        
        #store and report the cleaned data points
        print(f"{sok_group}: {len(all_x)} valid (x, y) points after NaN/Inf filtering\n")
        group_counts[sok_group] = len(all_x)

        #Continue if there are at least two data points
        if len(all_x) > 1:
            #estimate point density
            xy = np.vstack([all_x, all_y])
            kde = gaussian_kde(xy)

            #Evaluate cloud on a grid
            grid_positions = np.vstack([xgrid.ravel(), ygrid.ravel()])
            density_values = kde(grid_positions).reshape(xgrid.shape)

            #Mask the lowest density points
            density_mask = density_values > np.percentile(density_values, 0)
            masked_density = np.where(density_mask, density_values, np.nan)

            #Make the cloud
            contour = ax.contourf(
                xgrid, ygrid, masked_density, levels=2, cmap=cmap, alpha=0.33, zorder=z_order
            )
            contour.set_cmap(cmap)
            #Make an outline
            ax.contour(
                xgrid, ygrid, masked_density, levels=2, colors="black", linewidths=0.3, zorder=z_order + 15
            )
            #Adjust order to make the clouds overlap
            z_order += 2

# Set axis limits and remove ticks
ax.set_xlim(0, 1)
ax.set_ylim(0, 0.5)
ax.set_xticks([])
ax.set_yticks([])

# Show plot
plt.show()

# Print data point counts per SOK group
print("Final number of valid (x, y) data points per SOK group:")
for group, count in group_counts.items():
    print(f"{group}: {count}")