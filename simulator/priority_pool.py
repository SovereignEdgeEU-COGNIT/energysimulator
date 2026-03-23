class PriorityPool:
    def __init__(self, power_threshold=100):
        self.power_threshold = power_threshold
        self.pool = []

    def add_process(self, process):
        self.pool.append(process)

    def is_empty(self):
        return len(self.pool) == 0

    def size(self):
        return len(self.pool)

    def remove_process(self, process_name):
        for process in self.pool:
            if process.name == process_name:
                self.pool.remove(process)

    def print_pool(self):
        print("------------------------------------ pool ------------------------------------")
        for process in self.pool:
            print("Process:", process.name, "Energy:", process.total_power_consumption, "Power", process.power_draw_mean, "Deadline:", process.deadline)

    def select_processes(self):
        higheffect_processes = []
        loweffect_processes = []
        must_run_processes = []

        print("power_threshold:", self.power_threshold)

        if len(self.pool) == 0:
            return higheffect_processes, loweffect_processes, must_run_processes
       
        for process in self.pool:
            if process.deadline <= 0:
                must_run_processes.append(process)
            else:
                if process.power_draw_mean > self.power_threshold:
                    higheffect_processes.append(process)
                else:
                    loweffect_processes.append(process)

        higheffect_processes.sort(key=lambda x: x.power_draw_mean, reverse=True)
        loweffect_processes.sort(key=lambda x: x.power_draw_mean, reverse=True)

        return higheffect_processes, loweffect_processes, must_run_processes

    def tick(self):
        for process in self.pool:
            process.decrease_deadline()
