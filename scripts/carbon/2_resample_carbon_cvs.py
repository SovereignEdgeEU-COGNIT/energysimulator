import os
import pandas as pd

# Define the directory paths
input_dir = './carbon'
output_dir = './carbon_1s'

# Create output directory if it doesn't exist
os.makedirs(output_dir, exist_ok=True)

# Process each CSV file in the input directory
for filename in os.listdir(input_dir):
    if filename.endswith('.csv'):
        # Read the input CSV file
        input_path = os.path.join(input_dir, filename)
        df = pd.read_csv(input_path)

        # Convert the first column (timestamp) to datetime
        df.iloc[:, 0] = pd.to_datetime(df.iloc[:, 0])

        # Set the timestamp column as the index
        df.set_index(df.columns[0], inplace=True)

        # Resample the DataFrame to 1-second intervals
        df_resampled = df.resample('1S').asfreq()

        # Ensure the DataFrame columns are of the correct types for interpolation
        df_resampled = df_resampled.infer_objects(copy=False)

        # Interpolate the missing values
        df_resampled = df_resampled.interpolate(method='linear')

        # Reset the index to have the timestamp as a column again
        df_resampled.reset_index(inplace=True)

        # Convert the timestamp column back to integer seconds starting from 0
        start_time = df_resampled.iloc[0, 0]
        df_resampled.iloc[:, 0] = (df_resampled.iloc[:, 0] - start_time).dt.total_seconds().astype(int)

        # Save the processed DataFrame to the output directory
        output_path = os.path.join(output_dir, filename)
        df_resampled.to_csv(output_path, index=False)

# List the output files to confirm
output_files = os.listdir(output_dir)
print(output_files)

