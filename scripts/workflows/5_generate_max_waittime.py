import os
import pandas as pd
import random

# Input and output directories
input_dir = "./filtered_workloads_1s_stats"
output_dir = "./filtered_workloads_1s_stats_max_waittime"

# Create output directory if it doesn't exist
os.makedirs(output_dir, exist_ok=True)

# List all CSV files in the input directory
csv_files = [f for f in os.listdir(input_dir) if f.endswith(".csv")]

# Calculate 30% of files for setting `max_waittime` to 0
num_files = len(csv_files)
zero_waittime_files = set(random.sample(csv_files, int(0.0 * num_files)))

# Define a function to calculate a random max_waittime
def calculate_random_max_waittime(value, min_val, max_val):
    # Scale max_waittime between 60 seconds and 12 hours (43200 seconds)
    min_wait = 60
    max_wait = 43200
    normalized_value = (value - min_val) / (max_val - min_val) if max_val > min_val else 0
    # Random factor to introduce variability
    random_factor = random.uniform(0.8, 1.2)
    print((normalized_value * (max_wait - min_wait) + min_wait) * random_factor)
    return (normalized_value * (max_wait - min_wait) + min_wait) * random_factor

# Process each CSV file
for csv_file in csv_files:
    # Read the CSV file
    input_path = os.path.join(input_dir, csv_file)
    df = pd.read_csv(input_path)
    
    if csv_file in zero_waittime_files:
        # Set max_waittime to 0 for selected files
        df["max_waittime"] = 0
    else:
        # Get the min and max of total_length_seconds
        min_val = df["total_length_seconds"].min()
        max_val = df["total_length_seconds"].max()
        
        # Calculate random max_waittime for other files
        df["max_waittime"] = df["total_length_seconds"].apply(
            lambda x: calculate_random_max_waittime(x, min_val, max_val)
        )
   
        print(df["max_waittime"])

    # Save the updated DataFrame to the output directory
    output_path = os.path.join(output_dir, csv_file)
    df.to_csv(output_path, index=False)

print(f"Processed {num_files} files. Updated files are saved in {output_dir}.")

