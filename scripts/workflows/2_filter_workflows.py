import pandas as pd
import os
import shutil

# Function to check if a file contains timelimit > 15000
def check_timelimit(file):
    try:
        df = pd.read_csv(file)
        if df['timelimit'].max() < 15000:
            return True
    except Exception as e:
        print(f"Error reading {file}: {e}")
    return False

source_directory = './workloads'
target_directory = './filtered_workloads'

# Create the target directory if it doesn't exist
if not os.path.exists(target_directory):
    os.makedirs(target_directory)

# Counter for renaming files sequentially
counter = 0

# Iterate over the range of filenames
for i in range(100000):
    file_name = f"{i}.csv"
    print(f"Checking {file_name}")
    source_file_path = os.path.join(source_directory, file_name)
    
    if os.path.exists(source_file_path) and check_timelimit(source_file_path):
        new_file_name = f"{counter}.csv"
        target_file_path = os.path.join(target_directory, new_file_name)
        shutil.copy2(source_file_path, target_file_path)
        print(f"Copied and renamed {file_name} to {new_file_name}")
        counter += 1

print("File copying and renaming process completed.")
