from pulp import LpMinimize, LpProblem, LpVariable, lpSum, value

# Problem data
workloads = {
    1: {"power": 100, "duration": 100, "deadline": 60},
    2: {"power": 23, "duration": 200, "deadline": 100},
    3: {"power": 26, "duration": 30, "deadline": 10},
    4: {"power": 300, "duration": 300, "deadline": 200},
}

clusters = {
    "A": {"gpus": 2, "co2_intensity": 10.0},  # CO2 intensity in gCO2/kWh
    "B": {"gpus": 6, "co2_intensity": 100.0},
}

# Convert CO2 intensity from gCO2/kWh to gCO2/J
for cluster in clusters.values():
    cluster["co2_intensity"] /= 3600 * 1000

# Initialize the MILP problem
problem = LpProblem("Carbon_Aware_Scheduler", LpMinimize)

# Decision variables: Assign workload i to cluster c
x = {(i, c): LpVariable(f"x_{i}_{c}", 0, 1, cat="Binary") for i in workloads for c in clusters}

# Objective: Minimize total CO2 emissions
problem += lpSum(
    workloads[i]["power"] * workloads[i]["duration"] * clusters[c]["co2_intensity"] * x[i, c]
    for i in workloads for c in clusters
)

# Constraints
# Each workload must be assigned to one cluster
for i in workloads:
    problem += lpSum(x[i, c] for c in clusters) == 1, f"OneClusterPerWorkload_{i}"

# Deadline constraints
for i in workloads:
    for c in clusters:
        problem += (
            workloads[i]["duration"] <= workloads[i]["deadline"] * x[i, c],
            f"Deadline_{i}_{c}",
        )

# GPU constraints for each cluster
for c in clusters:
    problem += (
        lpSum(x[i, c] for i in workloads) <= clusters[c]["gpus"],
        f"GPU_Limit_{c}",
    )

# Solve the problem
status = problem.solve()

# Debugging and Output
print("Status:", status)
if status == 1:  # Optimal solution found
    print("Objective (Total CO2 Emissions):", value(problem.objective))
    for i in workloads:
        for c in clusters:
            if value(x[i, c]) == 1:
                print(f"Workload {i} assigned to Cluster {c}")
else:
    print("Problem is infeasible or unbounded.")
    print("Check constraints or input data.")
    print(problem)

