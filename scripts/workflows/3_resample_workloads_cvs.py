import pandas as pd
import os

# Source and target directories
source_directory = "./filtered_workloads"
target_directory = "./filtered_workloads_1s"

# Ensure the target directory exists
os.makedirs(target_directory, exist_ok=True)

# Function to fix timestamps, resample, and keep counter timestamps
def fix_and_resample_csv(file_path, output_path):
    # Read the CSV file
    df = pd.read_csv(file_path)

    # Fix the timestamp (convert from 100ms to seconds)
    df['timestamp'] = df['timestamp'] / 10

    # Convert the timestamp to datetime and set as index
    df['timestamp'] = pd.to_datetime(df['timestamp'], unit='s')
    df.set_index('timestamp', inplace=True)

    # Separate numeric and non-numeric columns
    numeric_df = df.select_dtypes(include=['number'])
    non_numeric_df = df.select_dtypes(exclude=['number'])

    # Resample numeric columns to 1-second intervals using mean
    resampled_numeric = numeric_df.resample('1S').mean()

    # Fill missing values in numeric columns
    resampled_numeric = resampled_numeric.fillna(0)

    # Forward-fill non-numeric columns
    resampled_non_numeric = non_numeric_df.resample('1S').ffill()

    # Combine numeric and non-numeric columns
    resampled_df = pd.concat([resampled_numeric, resampled_non_numeric], axis=1)

    # Drop rows where all columns are missing
    resampled_df.dropna(how='all', inplace=True)

    # Reset the index
    resampled_df.reset_index(inplace=True)

    # Replace the timestamp column with a counter starting from 0
    resampled_df['timestamp'] = range(len(resampled_df))

    # Validate DataFrame before saving
    if not resampled_df.empty:
        # Save the resampled DataFrame to the target directory
        resampled_df.to_csv(output_path, index=False)
    else:
        print(f"Warning: {file_path} resulted in an empty DataFrame and was skipped.")

# Process each file in the source directory
for file_name in os.listdir(source_directory):
    if file_name.endswith('.csv'):
        # Full path to the source file
        source_file_path = os.path.join(source_directory, file_name)
        
        # Full path to the target file
        target_file_path = os.path.join(target_directory, file_name)
        
        # Fix timestamps and resample
        fix_and_resample_csv(source_file_path, target_file_path)

print(f"Fixed and resampled files saved to {target_directory}")
