import os
import json

def available_gpus_at_tick(start, end, processesStatus):
    reserved_gpus = 0
    processStartTimes = processesStatus["start_times"]
    processEndTimes   = processesStatus["end_times"]
    total_gpus        = processesStatus["total_gpus"]

    for i in range(len(processStartTimes)):
        p_start = processStartTimes[i]
        p_end   = processEndTimes[i]

        if not (end < p_start or start > p_end):
            reserved_gpus += 1
            if reserved_gpus >= total_gpus:
                return False, total_gpus - reserved_gpus

    return True, total_gpus - reserved_gpus

def find_processes_at_tick(tick, processesStatus):
    active_processes = []

    starts    = processesStatus["start_times"]
    ends      = processesStatus["end_times"]
    processes = processesStatus["processes"]  # references to the actual Process objects

    for i in range(len(processes)):
        if starts[i] <= tick <= ends[i]:
            active_processes.append(processes[i])

    return active_processes

class Reservation:
    def __init__(self):
        self.edgeclusters = {} 
        self.reservation = {}
        self.t = 0
        self.processes = []

    def set_edgeclusters(self, edgeclusters):
        self.edgeclusters = edgeclusters

        for edgecluster in edgeclusters:
            self.reservation[edgecluster] = []

    def planned_exectime(self):
        total = 0
        for clustername in self.reservation:
            for p in self.reservation[clustername]:
                total += p.total_length_seconds
        return total

    def dump_json(self, filename):
        j = []
        for clustername in self.reservation:
            for p in self.reservation[clustername]:
                j.append({"name": p.name, "tick": p.planned_start_time, "length": p.total_length_seconds, "cluster": p.planned_cluster_name})

        with open(filename, 'w') as f:
            f.write(json.dumps(j))

    def calculate_benefit_s(self, process, cluster_name, tick):
        start_time = tick
        end_time = tick + process.total_length_seconds
        co2_benefit = 0

        cluster = self.edgeclusters[cluster_name]

        #print(f"Calculating benefit for process {process.name} on cluster {cluster_name} at tick {tick} with length {process.total_length_seconds}s")

        for t in range(start_time, end_time):
            co2_benefit += cluster.carbon_intensity_future(t - self.t)

        return co2_benefit
    
    def calculate_energy(self, process, cluster_name, tick):
        start_time = tick
        end_time = tick + process.total_length_seconds
    
        # Switch to 5-minute resolution
        start_interval = start_time // 300  # 300 seconds = 5 minutes
        end_interval = (end_time + 299) // 300  # Ensure full coverage
        co2 = 0
    
        cluster = self.edgeclusters[cluster_name]
    
        for interval in range(start_interval, end_interval):
            t = interval * 300  # Convert interval to seconds
            co2 += cluster.carbon_intensity_future(t - self.t) * 300
    
        return co2 * process.power_draw_mean
    
    def find_smallest_energy(self, possible_assignments):
        if not possible_assignments:
            return None 

        smallest_benefit_assignment = min(possible_assignments, key=lambda x: x[0])
        return smallest_benefit_assignment
    
    def find_next_timeslot(self, possible_assignments):
        if not possible_assignments:
            return None 

        smallest_benefit_assignment = min(possible_assignments, key=lambda x: x[2])
        return smallest_benefit_assignment
    
    def add_process(self, process):
        # max_deadline_seconds = 24 * 60 * 60 # Normalize the deadline to a range between 0 and max_deadline_seconds normalized_deadline = process.total_power_consumption %
        # normalized_deadline = process.total_power_consumption % max_deadline_seconds 
        # process.deadline = normalized_deadline
        #
        print("Adding process:", process.name, "Deadline:", process.deadline, "Length:", process.total_length_seconds)
        deadline_ticks = process.deadline
        forecast_ticks = range(self.t, self.t + deadline_ticks, 1)
       
        margin = 5

        possible_assignments = []
        processStatus = {}
        for cluster_name in self.edgeclusters.keys():
            processStatus[cluster_name] = {}
            processes = self.reservation[cluster_name]

            processStatus[cluster_name]["start_times"] = [p.planned_start_time for p in processes]
            processStatus[cluster_name]["end_times"] = [p.planned_start_time + p.total_length_seconds + margin for p in processes]
            processStatus[cluster_name]["total_gpus"] = self.edgeclusters[cluster_name].gpus

        timepacking = False
        for tick in forecast_ticks:
            for cluster_name in self.edgeclusters.keys():
                available_gpus, gpus = available_gpus_at_tick(tick, tick + process.total_length_seconds + margin, processStatus[cluster_name])
                #print(f"Cluster: {cluster_name}, Tick: {tick}, Available GPUs: {available_gpus}, GPUs: {gpus}")

                if available_gpus:
                    energy = self.calculate_energy(process, cluster_name, tick)
                    possible_assignments.append((energy, cluster_name, tick))
                else:
                    timepacking = False

        
        # sort by energy, reverse order = False
        #possible_assignments.sort(key=lambda x: x[0], reverse=False)

        #timepacking = True 

        if timepacking:
            best_assignment = self.find_next_timeslot(possible_assignments)
        else:
            best_assignment = self.find_smallest_energy(possible_assignments)
        
        # for i in range(len(possible_assignments)):
        #      print(f"Benefit: {possible_assignments[i][0]: .2f}, Cluster: {possible_assignments[i][1]}, Tick: {possible_assignments[i][2]}")

        if best_assignment is None:
            print(f"Unable to schedule process {process.name} within its deadline using bin-packing.")
            return False

        energy, best_cluster_name, best_tick = best_assignment

        # if process.name == "p_0":
        # if best_cluster_name == "Warsaw":
        #     print("Current tick:", self.t)
        #     print("Forecasts:", forecast_ticks)
        #     print("Process:", process.name, "Deadline:", process.deadline, "Length:", process.total_length_seconds)
        #     print("Length of possible assignments:", len(possible_assignments))
        #     print("Best assignment:", best_assignment)
        #
        #     counter = 0
        #     for best_assignment in possible_assignments:
        #         print(best_assignment)
        #         counter += 1
        #         if  counter > 10:
        #             break
        #
        #     self.dump_json("debug.json")
        #
        #     os._exit(1)


        print(best_cluster_name, best_tick, energy)

        process.planned_start_time = best_tick
        process.planned_cluster_name = best_cluster_name
        process.predicted_energy = energy
        self.reservation[best_cluster_name].append(process)
        estimated_co2_at_start_time = self.edgeclusters[process.planned_cluster_name].carbon_intensity_future(process.planned_start_time)
    
        print(f"{self.t}: Assigned {process.name} with length {process.total_length_seconds}s to {best_cluster_name} cluster at tick {best_tick} with energy{energy: .2f}.", f"Estimated CO2 intensity at start time:{estimated_co2_at_start_time: .2f} gCO2/kWh.")

        return True

    def select_processes(self, range=0):
        return self.select_processes_at_tick(self.t, range)

    def select_processes_at_tick(self, tick, range=0):
        processes = []
        for clustername in self.reservation:
            for p in self.reservation[clustername]:
                # plus minus the range
                planned_start_time = p.planned_start_time
                if planned_start_time - range <= tick <= planned_start_time + range:
                    processes.append(p)

        return processes

    def remove_process(self, processname):
        for clustername in self.reservation:
            for p in self.reservation[clustername]:
                if p.name == processname:
                    # remove p from the list
                    self.reservation[clustername].remove(p)

    def print(self):
        for clustername in self.reservation:
            print(f"Cluster: {clustername}")
            for p in self.reservation[clustername]:
                print(f"Tick: {self.t} Process: {p.name}, Start: {p.planned_start_time}, End: {p.planned_start_time + p.total_length_seconds}, Cluster: {p.planned_cluster_name}")

    def tick(self):
        self.t += 1
        for cluster_name in self.reservation:
            for process in self.reservation[cluster_name]:
                process.decrease_deadline()

    def set_tick(self, tick):
        self.t = tick

    def increase_tick(self, tick):
        self.t += tick

    def planned_processes(self):
        total = 0
        for clustername in self.reservation:
            total += len(self.reservation[clustername])
        return total
