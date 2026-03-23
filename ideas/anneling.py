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

# Validate workloads
for w, data in workloads.items():
    if data["duration"] > data["deadline"]:
        print(f"Workload {w} cannot meet its deadline (Duration: {data['duration']}, Deadline: {data['deadline']}).")

# Helper function: Calculate total CO2 emissions for a solution
def calculate_emissions(solution):
    total_emissions = 0
    cluster_usage = {c: 0 for c in clusters}

    for workload, cluster in solution.items():
        cluster_data = clusters[cluster]
        workload_data = workloads[workload]

        # Ensure GPU constraints are met
        if cluster_usage[cluster] >= cluster_data["gpus"]:
            return float('inf')  # Penalty for invalid solutions

        # Ensure deadline constraints are met
        if workload_data["duration"] > workload_data["deadline"]:
            return float('inf')  # Penalty for invalid solutions

        # Calculate emissions
        total_emissions += (
            workload_data["power"]
            * workload_data["duration"]
            * cluster_data["co2_intensity"]
        )
        cluster_usage[cluster] += 1

    return total_emissions

# Generate a valid initial solution
def generate_initial_solution(workloads, clusters):
    solution = {}
    cluster_usage = {c: 0 for c in clusters}
    for w in workloads:
        for c in clusters:
            if cluster_usage[c] < clusters[c]["gpus"]:
                solution[w] = c
                cluster_usage[c] += 1
                break
    return solution

# Simulated Annealing Algorithm
def simulated_annealing(workloads, clusters, max_iter=1000, initial_temp=100, cooling_rate=0.95):
    # Generate a valid initial solution
    current_solution = generate_initial_solution(workloads, clusters)
    current_cost = calculate_emissions(current_solution)

    best_solution = current_solution.copy()
    best_cost = current_cost

    temperature = initial_temp

    for iteration in range(max_iter):
        # Generate a neighbor by changing one random assignment
        new_solution = current_solution.copy()
        workload_to_change = random.choice(list(workloads.keys()))
        new_solution[workload_to_change] = random.choice(list(clusters.keys()))

        new_cost = calculate_emissions(new_solution)

        # Handle infinite costs (invalid solutions)
        if new_cost == float('inf'):
            new_cost = 1e6  # Assign a high penalty cost

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

