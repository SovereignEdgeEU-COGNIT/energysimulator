import unittest
from edge_cluster import *
from process import *
from scheduler import *
from reservation import *

class TestReservation(unittest.TestCase):
    def test_scheduler(self):
        edgeclusters = {}
        edge_cluster = EdgeCluster("Lund", 1, 100, "../carbon_1s_30d/SE-SE4.csv", 0.001101, "./test_output/umea.csv")
        #edge_cluster = EdgeCluster("Umea", 1, 1, "../carbon_1s_30d/SE-SE1.csv", 0.001101, "./test_output/umea.csv")
        #edgeclusters[edge_cluster.name] = edge_cluster
        #edge_cluster = EdgeCluster("London", 1, 4, "../carbon_1s_30d/GB.csv", 0.001101, "./test_output/stockholm.csv")
        edgeclusters[edge_cluster.name] = edge_cluster
        #edge_cluster = EdgeCluster("Warsaw", 1, 1, "../carbon_1s_30d/PL.csv", 0.001101, "./test_output/stockholm.csv")
        #edgeclusters[edge_cluster.name] = edge_cluster

        workloads_stats_dir = "../filtered_workloads_1s_stats"

        # if False:
        #     reservation = Reservation()
        #     reservation.set_edgeclusters(edgeclusters)
        #     reservation.add_process(process1)
        #     reservation.dump_json("layout.json")
        #     return

        # process1 = Process("test_process_0", 0, 0, 60, "../filtered_workloads/0.csv", workloads_stats_dir)
        # process2 = Process("test_process_1", 1, 0, 60*60*24, "../filtered_workloads/1.csv", workloads_stats_dir)
        # process3 = Process("test_process_2", 2, 0, 60*60*24, "../filtered_workloads/2.csv", workloads_stats_dir)
        # process4 = Process("test_process_3", 3, 0, 60*60*24, "../filtered_workloads/3.csv", workloads_stats_dir)
        #
        processes = []
        for i in range(30):
            process = Process(f"p_{i}", i, 0, 60*60*24, f"../filtered_workloads_1s/{i}.csv", workloads_stats_dir)
            processes.append(process)

       
        reservation = Reservation()
        reservation.set_edgeclusters(edgeclusters)

        # reservation.add_process(process1)
        # reservation.add_process(process2)
        # reservation.add_process(process3)
        # reservation.add_process(process4)

        for process in processes:
            reservation.add_process(process)
            # random value between 0 and 600s
            #wait_time = random.randint(0, 600)
            #reservation.increase_tick(wait_time)
            print("Planned exectim, next 24h:", reservation.planned_exectime())

        #print(reservation.available_gpus_at_tick("Umea", 10))
        #print(reservation.available_gpus_at_tick("Umea", 28680, 28700))
        #print(reservation.available_gpus_at_tick("Umea", 28780))

        #print("available_gpus_at_tick: ", reservation.available_gpus_at_tick("Umea", 73500, 86396))

        reservation.print()
        reservation.dump_json("layout.json")

        #selected_processes = reservation.select_processes_at_tick(65)
        #for process in selected_processes:
         #   print(process.name)

        # selected_processes = reservation.select_processes_at_tick(46800)
        # for process in selected_processes:
        #     print(process.name)

        # print("-------------")
        # reservation.select_processes()
        # print("-------------")
        # 
        # print("Setting tick to process1.planned_start_time: ", process1.planned_start_time)
        # reservation.set_tick(process1.planned_start_time)
        #
        # print("-------------")
        # processes = reservation.select_processes()
        # for process in processes:
        #     print(process.name)
        # print("-------------")
        
        # reservation.remove_process(process.name)
        # 
        # print("-------------")
        # reservation.select_processes()
        # print("-------------")
        #
        # process = Process("test_process_2", 0, 0, 60, "../filtered_workloads/1.csv", workloads_stats_dir)
        # ok = scheduler.run(process)
        # if not ok:
        #     print(f"failed to run process <{process.name}>")
        # 
        # process = Process("test_process_3", 0, 0, 60, "../filtered_workloads/3.csv", workloads_stats_dir)
        # ok = scheduler.run(process)
        # if not ok:
        #     print(f"failed to run process <{process.name}>")
        #
        # for _ in range(1000000):
        #     if scheduler.tick():
        #         break 
        # 
        # print("total carbon emission [g]: ", scheduler.cumulative_emission)
        # print("total energy [kWh]: ", scheduler.cumulative_energy)

if __name__ == '__main__':
    unittest.main()
