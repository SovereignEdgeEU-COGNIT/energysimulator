import random
from deap import base, creator, tools, algorithms

# Problem Data
clusters = {
    "A": {"GPUs": 2, "CO2": 10},
    "B": {"GPUs": 2, "CO2": 100},
}
workloads = [
    {"id": 1, "power": 6, "duration": 100, "deadline": 6},
    {"id": 2, "power": 230, "duration": 100, "deadline": 10},
    {"id": 3, "power": 260, "duration": 100, "deadline": -100},
    {"id": 4, "power": 30, "duration": 100, "deadline": 200},
]

def calculate_fitness(schedule):
    penalty = 0
  
    # print("Clusters:", clusters)
    print("Schedule:", schedule)

    gpu_availability = {}
    for cluster in clusters:
        gpu_availability[cluster] = clusters[cluster]["GPUs"]

    energy_penalty = 0
    deadline_penalty = 0
    print("---------------------")
    for workload, cluster in zip(workloads, schedule):
        print("workload: ", workload)
        print("cluster: ", cluster)
        
        available_gpus = gpu_availability[cluster]
        if available_gpus <= 0:
            penalty += 10000
        
        gpu_availability[cluster] -= 1
        
        co2_intensity = clusters[cluster]["CO2"]
        power = workload["power"]
        emission = co2_intensity * power # * duration
        energy_penalty += emission

        if workload["deadline"] < 0:
            deadline_penalty += abs(workload["deadline"]) * 100

    min_energy_penalty = 0
    max_energy_penalty = 350 * 1000 # Max power = 350W, Max CO2 intensity = 1000

    # Normalize the penalty to the range 0-9999
    if max_energy_penalty > min_energy_penalty:
        normalized_energy_penalty = (energy_penalty - min_energy_penalty) / (max_energy_penalty- min_energy_penalty) * 9999
    else:
        normalized_energy_penalty = 0

    penalty += normalized_energy_penalty
    penalty += deadline_penalty
    
    print("Energy Penalty:",  energy_penalty)
    print("Normalized Energy Penalty:", normalized_energy_penalty)
    print("Deadline Penalty:", deadline_penalty)
    print("Total Penalty: ", penalty)

    return (-penalty,)

# Genetic Algorithm Setup
creator.create("FitnessMax", base.Fitness, weights=(1.0,))

#creator.create("FitnessMin", base.Fitness, weights=(-1.0,))
#creator.create("Individual", list, fitness=creator.FitnessMin)
creator.create("Individual", list, fitness=creator.FitnessMax)

toolbox = base.Toolbox()
toolbox.register("attr_cluster", lambda: random.choice(list(clusters.keys())))
#toolbox.register("attr_cluster", lambda: random.choice(list(clusters.keys()) + ["wait"]))
toolbox.register("individual", tools.initRepeat, creator.Individual, toolbox.attr_cluster, n=len(workloads))
toolbox.register("population", tools.initRepeat, list, toolbox.individual)

toolbox.register("evaluate", calculate_fitness)

# Custom mutation function to ensure valid cluster assignments
def mutate_individual(individual):
    for i in range(len(individual)):
        if random.random() < 0.2:  # Mutation probability
            #individual[i] = random.choice(list(clusters.keys()) + ["wait"])
            individual[i] = random.choice(list(clusters.keys()))
    return individual,

toolbox.register("mutate", mutate_individual)

toolbox.register("mate", tools.cxUniform, indpb=0.5)
toolbox.register("select", tools.selTournament, tournsize=3)

# Main GA Process
def main():
    #random.seed(42)
    random.seed(random.randint(0, 1000))
    population = toolbox.population(n=50)
    generations = 500
    
    # Statistics
    stats = tools.Statistics(lambda ind: ind.fitness.values)
    stats.register("avg", lambda x: round(sum(v[0] for v in x) / len(x), 2))
    stats.register("min", lambda x: min(v[0] for v in x))
    stats.register("max", lambda x: max(v[0] for v in x))

    # Run the Genetic Algorithm
    population, log = algorithms.eaSimple(
        population,
        toolbox,
        cxpb=0.7,  # Crossover probability
        mutpb=0.2,  # Mutation probability
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

