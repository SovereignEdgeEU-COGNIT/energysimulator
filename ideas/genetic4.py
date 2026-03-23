import random
from deap import base, creator, tools, algorithms

# Problem Data
clusters = {
    "A": {"GPUs": 2, "CO2": 10},
    "B": {"GPUs": 2, "CO2": 100},
}
workloads = [
    {"id": 1, "power": 6, "duration": 1000, "deadline": 6},
    {"id": 2, "power": 230, "duration": 200, "deadline": 10},
    {"id": 3, "power": 260, "duration": 30, "deadline": 10},
    {"id": 4, "power": 30, "duration": 300, "deadline": 200},
]

# Fitness Function
def calculate_fitness(schedule):
    penalty = 0
    gpu_availability = {cluster: clusters[cluster]["GPUs"] for cluster in clusters}
    cluster_usage = {cluster: 0 for cluster in clusters}

    for workload, cluster in zip(workloads, schedule):
        if gpu_availability[cluster] > 0:
            gpu_availability[cluster] -= 1  # Assign GPU
            cluster_usage[cluster] += 1
        else:
            penalty += 1000  # Severe penalty for invalid allocation

    # Penalize imbalance in usage between clusters
    max_usage = max(cluster_usage.values())
    min_usage = min(cluster_usage.values())
    imbalance_penalty = (max_usage - min_usage) * 100  # Encourage balanced usage

    # Penalize underutilized GPUs
    underutilization_penalty = sum(gpu_availability.values()) * 50

    penalty += imbalance_penalty + underutilization_penalty

    return (-penalty,)  # Maximize penalty

# Genetic Algorithm Setup
creator.create("FitnessMax", base.Fitness, weights=(1.0,))
creator.create("Individual", list, fitness=creator.FitnessMax)

toolbox = base.Toolbox()

# Attribute and individual initialization
toolbox.register("attr_cluster", lambda: random.choice(list(clusters.keys())))
toolbox.register("individual", tools.initRepeat, creator.Individual, toolbox.attr_cluster, n=len(workloads))

# Custom population initializer
def initialize_population(n, workloads, clusters):
    population = []
    for _ in range(n):
        individual = []
        gpu_availability = {cluster: clusters[cluster]["GPUs"] for cluster in clusters}
        for workload in workloads:
            valid_clusters = [c for c, gpus in gpu_availability.items() if gpus > 0]
            if valid_clusters:
                cluster = random.choice(valid_clusters)
                gpu_availability[cluster] -= 1
            else:
                cluster = random.choice(list(clusters.keys()))  # Allow infeasible allocation
            individual.append(cluster)
        population.append(creator.Individual(individual))
    return population

toolbox.register("population", initialize_population, workloads=workloads, clusters=clusters)

# Fitness evaluation
toolbox.register("evaluate", calculate_fitness)

# Crossover, mutation, and selection
toolbox.register("mate", tools.cxUniform, indpb=0.5)

def mutate_individual(individual):
    for i in range(len(individual)):
        if random.random() < 0.2:  # Mutation probability
            individual[i] = random.choice(list(clusters.keys()))
    return individual,

toolbox.register("mutate", mutate_individual)
toolbox.register("select", tools.selTournament, tournsize=3)

# Main GA Process
def main():
    # random.seed(42)

    random.seed(random.randint(0, 1000))

    population = toolbox.population(n=100)  # Increase population size
    generations = 300  # Increase generations

    # Statistics
    stats = tools.Statistics(lambda ind: ind.fitness.values)
    stats.register("avg", lambda x: round(sum(v[0] for v in x) / len(x), 2))
    stats.register("min", lambda x: min(v[0] for v in x))
    stats.register("max", lambda x: max(v[0] for v in x))

    # Run the Genetic Algorithm
    population, log = algorithms.eaSimple(
        population,
        toolbox,
        cxpb=0.8,  # Higher crossover probability
        mutpb=0.3,  # Higher mutation probability
        ngen=generations,
        stats=stats,
        verbose=True,
    )

    # Output Best Result
    best_individual = tools.selBest(population, k=1)[0]
    print("Best Schedule:", best_individual)
    print("Best Fitness:", best_individual.fitness.values[0])

if __name__ == "__main__":
    main()

