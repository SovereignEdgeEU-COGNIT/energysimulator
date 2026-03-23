import os
import pandas as pd

# Input and output directories
input_dir = './carbon_1s'
output_dir = './carbon_1s_30d'

# Create the output directory if it doesn't exist
os.makedirs(output_dir, exist_ok=True)

# Number of rows to keep for 30 days
rows_to_keep = 30 * 24 * 60 * 60  # 2,592,000 rows

# Process each file in the input directory
for file_name in os.listdir(input_dir):
    if file_name.endswith('.csv'):  # Process only CSV files
        input_path = os.path.join(input_dir, file_name)
        output_path = os.path.join(output_dir, file_name)
        
        # Read the CSV file
        df = pd.read_csv(input_path)
        
        # Keep only the first 30 days of data
        df_30d = df.head(rows_to_keep)
        
        # Save the trimmed dataframe to the output directory
        df_30d.to_csv(output_path, index=False)

print(f"Trimmed files saved to {output_dir}")

