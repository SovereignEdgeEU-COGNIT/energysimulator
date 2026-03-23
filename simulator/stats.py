import os
import pandas as pd

def get_process_power_draw_stat(workloads_stats, idx):
    power_draw_mean = 0.0
    power_draw_median = 0.0
    total_power_consumption = 0
    total_length_seconds = 0

    stats_file = os.path.join(workloads_stats, f"{idx}_stats.csv")
     
    if not os.path.isfile(stats_file):
        print(f"Stats file not found: {stats_file}")
        return power_draw_mean, power_draw_median, total_power_consumption, total_length_seconds
    try:
        df = pd.read_csv(stats_file)

        power_draw_row = df[df['column_name'] == 'power_draw_W']              
        if power_draw_row.empty:
            print(f"'power_draw_W' not found in stats file: {stats_file}")
            return power_draw_mean, power_draw_median, total_power_consumption, total_length_seconds

        power_draw_mean = float(power_draw_row.iloc[0]['mean'])
        power_draw_median = float(power_draw_row.iloc[0]['median'])
        total_power_consumption = int(power_draw_row.iloc[0]['total_power_consumption'])
        total_length_seconds = int(power_draw_row.iloc[0]['total_length_seconds'])

    except Exception as e:
        print(f"Error reading stats file {stats_file}: {e}")
        return power_draw_mean, power_draw_median, total_power_consumption, total_length_seconds

    return power_draw_mean, power_draw_median, total_power_consumption, total_length_seconds
