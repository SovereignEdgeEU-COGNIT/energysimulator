import unittest
from edge_cluster import *
from process import *

class TestEdgeCluster(unittest.TestCase):
    def test_run_process(self):
        edge_cluster = EdgeCluster("test_cluster", 1, 1, "../carbon_1s_30d/SE-SE1.csv", 0.001101, "./test_output/test_cluster_output.csv")
        workloads_stats_dir = "./filtered_workloads_1s_stats"
        process = Process("test_process", 0, 0, 60, "../filtered_workloads/0.csv", workloads_stats_dir)
        edge_cluster.run(process)

        for _ in range(90000):
            if edge_cluster.tick():
                break 
        
        print("edge_cluster: carbon emission [g]: ", edge_cluster.cumulative_emission)
        print("edge_cluster: energy [kWh]: ", edge_cluster.cumulative_energy)
        print("edge_cluster: timesteps: ", edge_cluster.timestep)
        
        print("process: carbon emission [g]: ", process.cumulative_emission)
        print("process: energy [kWh]: ", process.cumulative_energy)
        print("process: timesteps: ", process.timestep)
        print("carbon intensity: ", edge_cluster.carbon_intensity)
        print("future carbon intensity: ", edge_cluster.carbon_intensity_future(60))

if __name__ == '__main__':
    unittest.main()
