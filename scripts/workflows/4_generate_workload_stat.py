import pandas as pd
import os

# Source and target directories
source_directory = "./filtered_workloads_1s"
target_directory = "./filtered_workloads_1s_stats"

# Ensure the target directory exists
os.makedirs(target_directory, exist_ok=True)

# Function to summarize selected columns in a CSV file
def summarize_csv(file_path, output_path):
    # Read the CSV file
    df = pd.read_csv(file_path)
    
    # Columns of interest
    selected_columns = ['power_draw_W', 'utilization_gpu_pct', 
                        'utilization_memory_pct', 'memory_free_MiB', 'memory_used_MiB']
    
    # Filter to only include selected columns
    df = df[selected_columns]
    
    # Calculate summary statistics
    summary = {
        "mean": df.mean(numeric_only=True),
        "median": df.median(numeric_only=True),
        "min": df.min(numeric_only=True),
        "max": df.max(numeric_only=True),
        "std": df.std(numeric_only=True),
        "range": df.max(numeric_only=True) - df.min(numeric_only=True),
        "sum": df.sum(numeric_only=True),
        "count_zero": (df == 0).sum(numeric_only=True),
        "zero_ratio": (df == 0).sum(numeric_only=True) / len(df),
        "total_length_seconds": len(df),
        "total_power_consumption": df['power_draw_W'].sum()
    }
    
    # Create a DataFrame for the summary
    summary_df = pd.DataFrame(summary).reset_index()
    
    # Rename columns
    summary_df.columns = ['column_name', 'mean', 'median', 'min', 'max', 'std', 'range', 
                          'sum', 'count_zero', 'zero_ratio', 'total_length_seconds', 'total_power_consumption']
    
    # Save the summary to a new CSV file
    summary_df.to_csv(output_path, index=False)

# Process each file in the source directory
for file_name in os.listdir(source_directory):
    if file_name.endswith('.csv'):
        # Full path to the source file
        source_file_path = os.path.join(source_directory, file_name)
        
        # Generate the summary file name
        summary_file_name = f"{os.path.splitext(file_name)[0]}_stats.csv"
        summary_file_path = os.path.join(target_directory, summary_file_name)
        
        # Generate and save the summary
        summarize_csv(source_file_path, summary_file_path)

print(f"Summary files saved to {target_directory}")
