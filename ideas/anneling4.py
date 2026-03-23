import random
import math

# Problem data
workloads = {
    1: {"power": 100, "duration": 100, "deadline": 60},
    2: {"power": 23, "duration": 200, "deadline": 100},
    3: {"power": 26, "duration": 30, "deadline": 10},
    4: {"power": 300, "duration": 300, "deadline": 200},
}

clusters = {
    "A": {"gpus": 2, "co2_intensity": 10.0},
    "B": {"gpus": 6, "co2_intensity": 100.0},
}

# Convert CO2 intensity from gCO2/kWh to gCO2/J
for cluster in clusters.values():
    cluster["co2_intensity"] /= 3600 * 1000

# Helper function: Calculate emissions and validate solution
def calculate_emissions_with_gpu_availability(solution, workloads, clusters):
    total_emissions = 0
    cluster_usage = {c: [0] * clusters[c]["gpus"] for c in clusters}  # GPU availability timelines

    for workload, cluster in solution.items():
        cluster_data = clusters[cluster]
        workload_data = workloads[workload]

        # Find the earliest available GPU
        gpu_timelines = cluster_usage[cluster]
        earliest_start = min(gpu_timelines)
        gpu_index = gpu_timelines.index(earliest_start)

        # Check if the workload can start within its deadline
        start_time = max(earliest_start, 0)
        if start_time > workload_data["deadline"]:
            # Penalize if no GPU becomes available before the deadline
            return float('inf')

        # Calculate end time and update GPU availability
        end_time = start_time + workload_data["duration"]
        cluster_usage[cluster][gpu_index] = end_time

        # Calculate CO2 emissions
        emissions = (
            workload_data["power"]
            * workload_data["duration"]
            * cluster_data["co2_intensity"]
        )
        total_emissions += emissions

    return total_emissions

# Generate a valid initial solution
def generate_initial_solution(workloads, clusters):
    return {w: random.choice(list(clusters.keys())) for w in workloads}

# Simulated Annealing Algorithm with GPU availability and deadlines
def simulated_annealing(workloads, clusters, max_iter=1000, initial_temp=100, cooling_rate=0.95):
    # Generate a valid initial solution
    current_solution = generate_initial_solution(workloads, clusters)
    current_cost = calculate_emissions_with_gpu_availability(current_solution, workloads, clusters)

    best_solution = current_solution.copy()
    best_cost = current_cost

    temperature = initial_temp

    for iteration in range(max_iter):
        # Generate a neighbor by changing one random assignment
        new_solution = current_solution.copy()
        workload_to_change = random.choice(list(workloads.keys()))
        new_solution[workload_to_change] = random.choice(list(clusters.keys()))

        new_cost = calculate_emissions_with_gpu_availability(new_solution, workloads, clusters)

        # Accept the new solution if it's better or with a probability based on temperature
        if new_cost < current_cost or random.random() < math.exp((current_cost - new_cost) / temperature):
            current_solution = new_solution
            current_cost = new_cost

            # Update the best solution found so far
            if current_cost < best_cost:
                best_solution = current_solution
                best_cost = current_cost

        # Cool down the temperature
        temperature *= cooling_rate

        # Print progress every 100 iterations
        if iteration % 100 == 0:
            print(f"Iteration {iteration}: Current Cost = {current_cost}, Best Cost = {best_cost}")

    return best_solution, best_cost

# Run the Simulated Annealing Algorithm
best_solution, best_cost = simulated_annealing(workloads, clusters)

# Output the results
print("Best Solution:", best_solution)
print("Total CO2 Emissions:", best_cost)

