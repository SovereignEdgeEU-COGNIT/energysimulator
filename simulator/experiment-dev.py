from simulator import Simulator

max_processes = 10000
max_days = 2000
cluster_utilization_threshold = 1.0
workload_dir = "./filtered_workloads_1s"
workloads_stats_dir = "./filtered_workloads_1s_stats"
cluster_config = "./edge-clusters-small.json"
log_dir = "./logs/60"
log_file = "log_0.csv"

alg = "genetic_timepool"
results_dir = "./results/dev"
timepool_power_threshold = 150 # watts
timepool_process_maxwait = 60 * 2 # seconds
pool_size = 50
pool_alg = "mean"

def main():
    simulator = Simulator(alg,
                          timepool_power_threshold,
                          timepool_process_maxwait,
                          pool_size,
                          pool_alg,
                          max_processes,
                          max_days,
                          cluster_utilization_threshold,
                          log_dir,
                          log_file,
                          workload_dir,
                          workloads_stats_dir,
                          cluster_config,
                          results_dir)
    simulator.start()

if __name__ == "__main__":
    main()
