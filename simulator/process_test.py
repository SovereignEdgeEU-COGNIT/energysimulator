import unittest
from process import *

class TestProcess(unittest.TestCase):
    def test_process(self):
        workloads_stats_dir = "../filtered_workloads_1s_stats"
        process = Process("test_process", 29, 0, 60, "../filtered_workloads_1s/4.csv", workloads_stats_dir)
        process.carbon_intensity = 15
        
        print("total length [s]: ", process.total_length_seconds)
        for t in range(90000):
            if process.tick():
                print(t)
                break
       
        print("carbon emission [g]: ", process.cumulative_emission)
        print("energy [kWh]: ", process.cumulative_energy)
        print("timesteps: ", process.timestep)

if __name__ == '__main__':
    unittest.main()
