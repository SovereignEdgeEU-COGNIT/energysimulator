import csv
import os

from stats import get_process_power_draw_stat

class Process:
    def __init__(self, name, idx, initial_timestep, deadline, workload_csv_file, workloads_stats_dir):
        self.__name = name
        self.__idx = idx
        self.__deadline = deadline
        self.__initial_timestep = initial_timestep
        self.__timestep = self.__initial_timestep
        self.__duration = 0
        self.__workload_csv_file = workload_csv_file
        self.__workloads_stats_dir = workloads_stats_dir
        self.__cumulative_energy = 0.0
        self.__emission = 0.0
        self.__cumulative_emission = 0.0
        self.__current_carbon_intensity = 0.0
        self.__current_energy = 0.0
        self.__current_gpu_utilization = 0.0
        self.__current_memory_utilization = 0.0
        self.__power_draw_W_dict = {}
        self.__utilization_gpu_pct_dict = {}
        self.__utilization_memory_pct_dict = {}
        self.__planned_start_time = 0
        self.__planned_cluster_name = None
        self.__predicted_energy = 0.0

        with open(self.__workload_csv_file, mode='r') as csvfile:
            csvreader = csv.DictReader(csvfile)
            for row in csvreader:
                # print("----------------- row", idx)
                # print(row)
                # print("----------------- row end")

                timestamp = float(row['timestamp'])
                power_draw_W = float(row['power_draw_W'])
                utilization_gpu_pct = float(row['utilization_gpu_pct'])
                utilization_memory_pct = float(row['utilization_memory_pct'])
                self.__power_draw_W_dict[timestamp] = power_draw_W
                self.__utilization_gpu_pct_dict[timestamp] = utilization_gpu_pct
                self.__utilization_memory_pct_dict[timestamp] = utilization_memory_pct

        power_draw_mean, power_draw_median, total_power_consumption, total_length_seconds = get_process_power_draw_stat(self.__workloads_stats_dir, self.__idx)
        self.__power_draw_mean = power_draw_mean
        self.__power_draw_median = power_draw_median
        self.__total_power_consumption = total_power_consumption
        self.__total_length_seconds = total_length_seconds

    def tick(self):
        self.__timestep += 1
        if self.__timestep not in self.__power_draw_W_dict:
            print("Process", self.__name, "has finished")
            return True
       
        exectime = self.total_length_seconds
        remaining_time = exectime - self.__timestep


        #if self.__name == "p_166":
        #    print("Process", self.__name, "remaining time:", remaining_time)

        if remaining_time <= 0:
            #print("total_length_seconds", self.total_length_seconds, "timestep", self.__timestep, "exectime", exectime, "remaining_time", remaining_time, "Process", self.__name, "energy:", self.__current_energy, "carbon intensity:", self.__current_carbon_intensity, "emission:", self.__emission, "cumulative emission:", self.__cumulative_emission)
            return True

        self.__duration += 1

        current_energy = self.__power_draw_W_dict.get(self.__timestep, 0.0) / 3600.0

        self.__current_gpu_utilization = self.__utilization_gpu_pct_dict.get(self.__timestep, 0.0)
        self.__current_memory_utilization = self.__utilization_memory_pct_dict.get(self.__timestep, 0.0)
        
        # trapezoidal rule
        if self.__timestep > 1:
            self.__cumulative_energy += 0.5 * (self.__previous_energy + current_energy)
        else:
            self.__cumulative_energy += current_energy

        self.__previous_energy = current_energy

        #print("Process", self.__name, "energy:", current_energy, "carbon intensity:", self.__current_carbon_intensity, "emission:", current_energy * self.__current_carbon_intensity, "cumulative emission:", self.__cumulative_emission)

        self.__emission = current_energy * self.__current_carbon_intensity
        self.__cumulative_emission += self.__emission

        self.__current_energy = current_energy

        return False

    @property
    def name(self):
        return self.__name

    @property
    def carbon_intensity(self):
        return self.__current_carbon_intensity
    
    @carbon_intensity.setter
    def carbon_intensity(self, value):
        self.__current_carbon_intensity = value 
    
    @property
    def energy(self):
        return self.__current_energy

    @property
    def cumulative_energy(self):
        return self.__cumulative_energy / 1000
    
    @property
    def emission(self):
        return self.__emission
    
    @property
    def cumulative_emission(self):
        return self.__cumulative_emission / 1000
    
    @property
    def gpu_utilization(self):
        return self.__current_gpu_utilization

    @property
    def memory_utilization(self):
        return self.__current_memory_utilization

    @property
    def timestep(self):
        return self.__timestep

    @property
    def duration(self):
        return self.__duration

    @property
    def idx(self):
        return self.__idx

    @property
    def power_draw_mean(self):
        return self.__power_draw_mean

    @property
    def power_draw_median(self):
        return self.__power_draw_median

    @property
    def total_power_consumption(self):
        return self.__total_power_consumption

    @property
    def deadline(self):
        return self.__deadline

    # setter for deadline
    @deadline.setter
    def deadline(self, value):
        self.__deadline = value

    @property
    def total_length_seconds(self):
        return self.__total_length_seconds

    def decrease_deadline(self):
        self.__deadline -= 1

    @property
    def planned_start_time(self):
        return self.__planned_start_time

    @planned_start_time.setter
    def planned_start_time(self, value):
        self.__planned_start_time = value

    @property
    def planned_cluster_name(self):
        return self.__planned_cluster_name

    @planned_cluster_name.setter
    def planned_cluster_name(self, value):
        self.__planned_cluster_name = value

    @property
    def predicted_energy(self):
        return self.__predicted_energy

    @predicted_energy.setter
    def predicted_energy(self, value):
        self.__predicted_energy = value
