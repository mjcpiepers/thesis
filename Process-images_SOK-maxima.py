#This code was written with the help of chatGPT
import tifffile as tiff
import numpy as np
import pandas as pd
import os

# Define file path (update this to the correct path)
file_path = "/Users/maizellab06/Quantifications/maximaVSorganShape/python_scripts/stacks/SOK5/SOK5_2023-02-24_pt2.tif"

# Define output directory and CSV name
output_dir = "/Users/maizellab06/Quantifications/maximaVSorganShape/python_scripts/outputs_csv"
output_csv_path = os.path.join(output_dir, "SOK5_2023-02-24_pt2.csv")

# Ensure the output directory exists
os.makedirs(output_dir, exist_ok=True)

# Define width per pixel (µm) (Update this value based on your microscope calibration)
width_per_pixel = 1.083  # Example value in micrometers

# Check if file exists before proceeding
if not os.path.exists(file_path):
    print(f"Error: The file {file_path} does not exist.")
    exit()

# Load the TIFF file
tif_stack = tiff.imread(file_path)

# Define parameters
radius = 50  # Radius for circular maxima search
results = []
max_width_so_far = 0  # Track max width so far
max_columns_so_far = 0  # Track max Columns with Max > 0 so far

# Function to create a circular mask
def create_circular_mask(shape, center, radius):
    Y, X = np.ogrid[:shape[0], :shape[1]]
    dist_from_center = np.sqrt((X - center[1])**2 + (Y - center[0])**2)
    return dist_from_center <= radius

# Process each time frame in the stack
for time_idx, frame in enumerate(tif_stack):
    maxima_coords = []

    # Determine the image height for each frame
    image_height = frame.shape[0]  # Get number of rows in the frame

    # Count the number of columns where max intensity > 0, this measures the width
    column_max_values = np.max(frame, axis=0)  # Get max intensity per y-column
    num_columns_greater_than_zero = np.sum(column_max_values > 0)

    # Ensure Columns with Max > 0 does not decrease / ensures it so that the LR cannot decrease in length (because that would be unrealistic.
    num_columns_greater_than_zero = max(num_columns_greater_than_zero, max_columns_so_far)
    max_columns_so_far = num_columns_greater_than_zero  # Update running max

    # Compute width in micrometers. This calculation is off by a factor 10, but is corrected in the subsequent script.
    width_um = num_columns_greater_than_zero * width_per_pixel

    # Ensure Width (µm) does not decrease. / ensures it so that the LR cannot decrease in length (because that would be unrealistic. Same functionallity, as before but now for µm. This is redundant but doesn't hurt.
    width_um = max(width_um, max_width_so_far)
    max_width_so_far = width_um  # Update running max

    # Work on a copy of the frame to suppress found regions.
    frame_copy = frame.copy()

    for _ in range(3):  # Find 3 maxima
        if np.all(frame_copy == 0):  # If no signal left, break
            maxima_coords.append((None, None))  # Append none if no more maxima can be found
            continue

        # Find the highest intensity pixel
        max_y, max_x = np.unravel_index(np.argmax(frame_copy), frame_copy.shape)

        # Create a circular mask centered on the found max
        mask = create_circular_mask(frame.shape, (max_y, max_x), radius)

        # Store the detected maximum
        maxima_coords.append((max_x, max_y))  # Store (X, Y) coordinates

        # Suppress the detected region by setting it to zero to avoid duplicate maxima
        frame_copy[mask] = 0

    # Compute derived columns
    derived_data = {}
    for i in range(3):
        max_x, max_y = maxima_coords[i]
        if max_x is not None and max_y is not None:
            derived_data[f"Max {i+1} X / Columns with Max > 0"] = max_x / num_columns_greater_than_zero if num_columns_greater_than_zero > 0 else None
            derived_data[f"Max {i+1} Y / Image height"] = max_y / image_height
            # Compute deviation from 0.5 using Max X Y / Image height, which is a measure for the position relative to the center.
            derived_data[f"Deviation from 0.5 (Max {i+1})"] = abs(derived_data[f"Max {i+1} Y / Image height"] - 0.5) if derived_data[f"Max {i+1} Y / Image height"] is not None else None
        else:
            derived_data[f"Max {i+1} X / Columns with Max > 0"] = None
            derived_data[f"Max {i+1} Y / Image height"] = None
            derived_data[f"Deviation from 0.5 (Max {i+1})"] = None

    # Store results
    results.append({
        "Timepoint": time_idx,
        "Columns with Max > 0": num_columns_greater_than_zero,
        "Width per pixel (µm)": width_per_pixel,
        "Width (µm)": width_um,
        "Image height (px)": image_height,  # Dynamically set for each frame
        "Max 1 X": maxima_coords[0][0], "Max 1 Y": maxima_coords[0][1],
        "Max 2 X": maxima_coords[1][0], "Max 2 Y": maxima_coords[1][1],
        "Max 3 X": maxima_coords[2][0], "Max 3 Y": maxima_coords[2][1],
        **derived_data  # Append all computed columns dynamically
    })

# Convert to DataFrame
df_results = pd.DataFrame(results)

# Save the results as a CSV file
df_results.to_csv(output_csv_path, index=False)

# Print a preview of the results
print(df_results.head())

print(f"Analysis complete! Results saved to {output_csv_path}")