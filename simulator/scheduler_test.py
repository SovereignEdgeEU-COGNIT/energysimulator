import unittest
from edge_cluster import *
from process import *
from scheduler import *

class TestScheduler(unittest.TestCase):
    def test_scheduler(self):
        scheduler = Scheduler()
        edge_cluster = EdgeCluster("umea", 1, 1, "../carbon_1s_30d/SE-SE1.csv", 0.001101, "./test_output/umea.csv")
        scheduler.add_edge_cluster(edge_cluster)
        edge_cluster = EdgeCluster("stockholm", 1, 1, "../carbon_1s_30d/SE-SE3.csv", 0.001101, "./test_output/stockholm.csv")
        scheduler.add_edge_cluster(edge_cluster)
        edge_cluster = EdgeCluster("lund", 1, 1, "../carbon_1s_30d/SE-SE4.csv", 0.001101, "./test_output/lund.csv")
        scheduler.add_edge_cluster(edge_cluster)

        workloads_stats_dir = "../filtered_workloads_1s_stats"

        process = Process("test_process_1", 0, 0, 60, "../filtered_workloads/0.csv", workloads_stats_dir)
        ok = scheduler.run(process)
        if not ok:
            print(f"failed to run process <{process.name}>")
        
        process = Process("test_process_2", 0, 0, 60, "../filtered_workloads/1.csv", workloads_stats_dir)
        ok = scheduler.run(process)
        if not ok:
            print(f"failed to run process <{process.name}>")
        
        process = Process("test_process_3", 0, 0, 60, "../filtered_workloads/3.csv", workloads_stats_dir)
        ok = scheduler.run(process)
        if not ok:
            print(f"failed to run process <{process.name}>")

        for _ in range(1000):
            if scheduler.tick():
                break 
        
        print("total carbon emission [g]: ", scheduler.cumulative_emission)
        print("total energy [kWh]: ", scheduler.cumulative_energy)

if __name__ == '__main__':
    unittest.main()
