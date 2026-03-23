import random
import csv
import os
import sys
sys.path.append('/home/johan/dev/github/johankristianss/carbonsim/simulator/genetic')
from priority_pool import PriorityPool
from reservation import Reservation
import os

class Scheduler:
    def __init__(self, csv_filename='./scheduler.csv', workloads_stats_dir='./filtered_workloads_1s_stats', alg='random', power_threshold=150, co2_intensity_threshold=20):
        self.__edge_clusters_dict = {}
        self.tick_count = 0
        self.csv_filename = csv_filename
        self.csvfile = open(self.csv_filename, 'w', newline='')
        self.writer = csv.DictWriter(self.csvfile, fieldnames=['tick', 'cumulative_emission', 'cumulative_energy', 'utilization', 'total_gpu_cost'])
        self.writer.writeheader()
        self.workloads_stats_dir = workloads_stats_dir
        self.__c02_intensity_threshold = co2_intensity_threshold
        self.__alg = alg
        self.__power_threshold = power_threshold
        self.__priority_pool = PriorityPool(power_threshold=self.__power_threshold)
        self.__reservation = Reservation()

        self.average_utilization_sum = 0
        self.__scheduled_processs = 0

    def add_edge_cluster(self, edge_cluster):
        self.__edge_clusters_dict[edge_cluster.name] = edge_cluster
        edge_cluster.set_scheduler(self)

    def start(self):
        self.__reservation.set_edgeclusters(self.__edge_clusters_dict)

    def finalize(self):
        if self.__alg == 'reservation':
            if self.__reservation.planned_processes() > 0:
                self.__reservation.print()
                return False
            else:
                return True
        else:
            return True

    def background(self):
        #print("=============================== run background ================================")

        if self.__alg == 'greedy_binpack':
            #print("------------------------------- greedy_binpack background -------------------------------")
            high_effect_processes, low_effect_processes, must_run_processes = self.__priority_pool.select_processes()
            #self.__greedy_binpack_pool.print_pool()

            for process in must_run_processes:
                available_edge_clusters = [edge_cluster for edge_cluster in self.__edge_clusters_dict.values() if edge_cluster.available]

                if len(available_edge_clusters) > 0:
                    available_edge_clusters.sort(key=lambda edge_cluster: edge_cluster.carbon_intensity)
                    selected_edge_cluster = available_edge_clusters[0]
                    print("selected edge cluster: ", selected_edge_cluster.name)
                    if selected_edge_cluster.run(process):
                        self.__priority_pool.remove_process(process.name)

            for process in high_effect_processes:
                available_edge_clusters = [edge_cluster for edge_cluster in self.__edge_clusters_dict.values() if edge_cluster.available]
                available_edge_clusters = [c for c in available_edge_clusters if c.carbon_intensity <= self.__c02_intensity_threshold]
                if len(available_edge_clusters) > 0:
                    available_edge_clusters.sort(key=lambda edge_cluster: edge_cluster.carbon_intensity)
                    selected_edge_cluster = available_edge_clusters[0]
                    print("selected edge cluster: ", selected_edge_cluster.name)
                    if selected_edge_cluster.run(process):
                        self.__priority_pool.remove_process(process.name)
                    else:
                        print("failed to run process, no available gpus")
                else:
                    print("no available edge clusters with low carbon intensity")

            print("processing low energy processes")
            for process in low_effect_processes:
                available_edge_clusters = [edge_cluster for edge_cluster in self.__edge_clusters_dict.values() if edge_cluster.available]
                if len(available_edge_clusters) > 0:
                    available_edge_clusters.sort(key=lambda edge_cluster: edge_cluster.carbon_intensity)
                    selected_edge_cluster = available_edge_clusters[0]

                    if selected_edge_cluster.run(process):
                        self.__priority_pool.remove_process(process.name)

                # print pool size left after scheduling
            print("process not scheduled: ")
            self.__priority_pool.print_pool()
        
        if self.__alg == 'reservation':
            #print("------------------------------- reservation background -------------------------------")
            selected_processes = self.__reservation.select_processes()

            for process in selected_processes:
                selected_edge_cluster_name = process.planned_cluster_name
                selected_edge_cluster = self.__edge_clusters_dict[selected_edge_cluster_name]
                    
                if selected_edge_cluster.run(process):
                    print(self.tick_count, "Successfully started process:", process.name, "on planned edge cluster:", process.planned_cluster_name)
                else:
                    print(self.tick_count,"ERROR failed to start process:", process.name, "on planned edge cluster:", process.planned_cluster_name)
                    print("Tick: ", self.tick_count)
                    self.__reservation.print()
                    for self.__edge_cluster in self.__edge_clusters_dict.values():
                        self.__edge_cluster.print_status()

                    self.__reservation.dump_json("error.json")
                    os._exit(1)

    def process_completed(self, process):
        if self.__alg == 'reservation':
            self.__reservation.remove_process(process.name)
         
    def run(self, process):
        if self.__alg == 'greedy':
            print("----------------------- greedy scheduling -----------------------")
            ############# greedy scheduling ############
            available_edge_clusters = [edge_cluster for edge_cluster in self.__edge_clusters_dict.values() if edge_cluster.available]
            if not available_edge_clusters:
                return False

            available_edge_clusters.sort(key=lambda edge_cluster: edge_cluster.carbon_intensity)

            for edge_cluster in available_edge_clusters:
                if edge_cluster.run(process):
                    print("selected edge cluster: ", edge_cluster.name)
                    self.__scheduled_processs += 1
                    return True
       
            return False
        elif self.__alg == 'greedy_binpack':
            print("----------------------- greedy bin packing scheduling -----------------------")
            ############# greedy bin packing scheduling ############
            self.__priority_pool.add_process(process)
            self.__scheduled_processs += 1
            return True
        
        elif self.__alg == 'reservation':
            print("----------------------- reservation scheduling -----------------------")
            ############# reservation scheduling ############
            ok = self.__reservation.add_process(process)
            if ok:
                self.__scheduled_processs += 1
                return True
            else:
                return False
        
        elif self.__alg == 'random':
            print("-----------------------  random scheduling -----------------------")
            ############# random scheduling ############
            available_edge_clusters = [edge_cluster for edge_cluster in self.__edge_clusters_dict.values() if edge_cluster.available]
            if not available_edge_clusters:
                return False
            selected_edge_cluster = random.choice(available_edge_clusters)
            #print("selected edge cluster: ", selected_edge_cluster.name)
            self.__scheduled_processs += 1
            return selected_edge_cluster.run(process)
        else :
            print("Invalid scheduling algorithm")
            return False

    def tick(self):
        self.tick_count += 1
        for edge_cluster in self.__edge_clusters_dict.values():
             edge_cluster.tick()

        total_utilization = self.get_total_utilization()
        self.average_utilization_sum += total_utilization

        self.writer.writerow({
            'tick': self.tick_count,
            'cumulative_emission': self.cumulative_emission,
            'cumulative_energy': self.cumulative_energy,
            'utilization': self.get_total_utilization(),
            'total_gpu_cost': self.total_gpu_cost,
        })

        self.background()
        
        self.__priority_pool.tick()
        self.__reservation.tick()
        
    @property
    def num_edge_clusters(self):
        return len(self.__edge_clusters_dict)

    @property
    def num_available_edge_clusters(self):
        return len([edge_cluster for edge_cluster in self.__edge_clusters_dict.values() if edge_cluster.available])

    @property
    def num_running_processes(self):
        return sum([edge_cluster.num_running_processes for edge_cluster in self.__edge_clusters_dict.values()])

    def get_total_utilization(self):
        total_utilization = sum(edge_cluster.utilization for edge_cluster in self.__edge_clusters_dict.values())
        return total_utilization / self.num_edge_clusters if self.num_edge_clusters > 0 else 0

    @property
    def cumulative_energy(self):
        return sum([edge_cluster.cumulative_energy for edge_cluster in self.__edge_clusters_dict.values()])

    @property
    def cumulative_emission(self):
        return sum([edge_cluster.cumulative_emission for edge_cluster in self.__edge_clusters_dict.values()])
    
    @property
    def total_gpu_cost(self):
        return sum([edge_cluster.total_gpu_cost for edge_cluster in self.__edge_clusters_dict.values()])
    
    @property
    def total_processing_time(self):
        return sum([edge_cluster.total_processing_time for edge_cluster in self.__edge_clusters_dict.values()])
    
    @property
    def finished_processes(self):
        return sum([edge_cluster.finished_processes for edge_cluster in self.__edge_clusters_dict.values()])
  
    @property
    def scheduled_processes(self):
        return self.__scheduled_processs

    @property
    def total_processes(self):
        return sum([edge_cluster.total_processes for edge_cluster in self.__edge_clusters_dict.values()])

    @property
    def avg_utilization(self):
        return self.average_utilization_sum / self.tick_count

    @property
    def total_gpus(self):
        return sum([edge_cluster.gpus for edge_cluster in self.__edge_clusters_dict.values()])

    def print_reservation(self):
        self.__reservation.print()  
