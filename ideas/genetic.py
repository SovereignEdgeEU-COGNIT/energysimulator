import random

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

# Fitness function to calculate emissions and validate constraints
def fitness(solution, workloads, clusters):
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

# Generate a random individual
def generate_individual(workloads, clusters):
    return {w: random.choice(list(clusters.keys())) for w in workloads}

# Crossover operation
def crossover(parent1, parent2):
    child = {}
    for w in workloads:
        child[w] = random.choice([parent1[w], parent2[w]])
    return child

# Mutation operation
def mutate(individual, mutation_rate=0.1):
    if random.random() < mutation_rate:
        workload_to_mutate = random.choice(list(workloads.keys()))
        individual[workload_to_mutate] = random.choice(list(clusters.keys()))

# Genetic Algorithm
def genetic_algorithm(workloads, clusters, population_size=50, generations=100, mutation_rate=0.1):
    # Initialize population
    population = [generate_individual(workloads, clusters) for _ in range(population_size)]

    # Evolution
    for generation in range(generations):
        # Evaluate fitness
        fitness_scores = [(individual, fitness(individual, workloads, clusters)) for individual in population]
        fitness_scores.sort(key=lambda x: x[1])  # Sort by fitness (lower is better)

        # Select the top half of the population
        selected = [ind for ind, _ in fitness_scores[:population_size // 2]]

        # Generate new population through crossover and mutation
        new_population = []
        while len(new_population) < population_size:
            parent1, parent2 = random.sample(selected, 2)
            child = crossover(parent1, parent2)
            mutate(child, mutation_rate)
            new_population.append(child)

        population = new_population

        # Print best solution in the generation
        best_individual, best_fitness = fitness_scores[0]
        print(f"Generation {generation}: Best Fitness = {best_fitness}")

    # Return the best solution found
    best_individual, best_fitness = fitness_scores[0]
    return best_individual, best_fitness

# Run the Genetic Algorithm
best_solution, best_fitness = genetic_algorithm(workloads, clusters)

# Output the results
print("Best Solution:", best_solution)
print("Total CO2 Emissions:", best_fitness)

