import sys
sys.path.append('/home/johan/dev/github/johankristianss/carbonsim/simulator')

from simulator import Simulator

max_processes = 10000
max_days = 2000 
workload_dir = "./filtered_workloads_1s"
workloads_stats_dir = "./filtered_workloads_1s_stats"
cluster_config = "./edge-clusters-small.json"
log_dir = "./logs/100"
log_file = "log_2.csv"

alg = "random"
results_dir = "./results/100_small/random"
power_threshold = 150 # watts
process_maxwait = 60 * 2 # seconds
co2_intensity_threshold = 20 

def main():
    simulator = Simulator(alg,
                          power_threshold,
                          process_maxwait,
                          co2_intensity_threshold,
                          max_processes,
                          max_days,
                          log_dir,
                          log_file,
                          workload_dir,
                          workloads_stats_dir,
                          cluster_config,
                          results_dir)
    simulator.start()

if __name__ == "__main__":
    main()
