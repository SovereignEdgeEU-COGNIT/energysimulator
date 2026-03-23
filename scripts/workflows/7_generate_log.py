import os
import random
import csv
import argparse
import numpy as np

def generate_logs(source_directory, target_directory, rate, wait_time, num_logs):
    # Create the logs directory if it doesn't exist
    os.makedirs(target_directory, exist_ok=True)

    # Get the list of CSV files in the source directory
    csv_files = [file for file in os.listdir(source_directory) if file.endswith('.csv')]

    # Generate the specified number of logs
    for i in range(0, num_logs):
        log_file_name = f"log_{i}.csv"
        log_file_path = os.path.join(target_directory, log_file_name)

        # Shuffle the list randomly
        #random.shuffle(csv_files)

        # Write the shuffled file names and waiting times to the log file
        with open(log_file_path, 'w', newline='') as log_file:
            writer = csv.writer(log_file)
            writer.writerow(["File Name", "Random Wait (ticks)"])  # Header row

            for file_name in csv_files:
                # Calculate the random waiting time
                waiting_time = np.random.exponential(1.0 / rate)
                ticks_to_wait = int(waiting_time * wait_time)
                print(f"Log {i}: Waiting (random tick), file: {file_name}, tick: {ticks_to_wait}")
                writer.writerow([file_name, ticks_to_wait])

        print(f"Log {i} created and saved as '{log_file_path}'.")

# Main function for argument parsing
# python3 scripts/generate_log.py --wait 80 --num_logs 5
if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Generate a random log sequence with file names and waiting times.")
    parser.add_argument("--rate", type=float, default=1.0, help="Rate for exponential distribution (lambda).")
    parser.add_argument("--source_directory", type=str, default="./filtered_workloads_1s", help="Source directory with CSV files.")
    parser.add_argument("--target_directory", type=str, default="./logs", help="Target directory to save the log file.")
    parser.add_argument("--wait", type=int, required=True, help="Scaling factor for waiting time (ticks).")
    parser.add_argument("--num_logs", type=int, default=10, help="Number of log files to generate.")
    args = parser.parse_args()

    # Generate the log
    generate_logs(args.source_directory, args.target_directory, args.rate, args.wait, args.num_logs)
