import pandas as pd
import os

path_to_csv_files = '/scratch/cognit/filtered_workloads'
output_file = '/scratch/cognit/workload_summary.csv'

def create_summary_csv(path, num_files, output_file):
    summary_data = []

    for i in range(num_files):
        print("Processing file:", i)
        file_path = os.path.join(path, f"{i}.csv")
        if os.path.exists(file_path):
            df = pd.read_csv(file_path)
            df = df.dropna(subset=['power_draw_W', 'id_user', 'timelimit'])

            if not df.empty:
                avg_power = df.groupby('id_user')['power_draw_W'].mean().reset_index()
                avg_timelimit = df.groupby('id_user')['timelimit'].mean().reset_index()
                
                avg_summary = pd.merge(avg_power, avg_timelimit, on='id_user')
                avg_summary['file_id'] = i
                summary_data.append(avg_summary)

    if summary_data:
        summary_df = pd.concat(summary_data, ignore_index=True)
        summary_df = summary_df[['file_id', 'id_user', 'power_draw_W', 'timelimit']].rename(columns={'power_draw_W': 'avg_power', 'timelimit': 'avg_timelimit'})
        summary_df.to_csv(output_file, index=False)
        print(f"Summary CSV file created: {output_file}")
    else:
        print("No data found to create summary.")

num_files = 100000
create_summary_csv(path_to_csv_files, num_files, output_file)
