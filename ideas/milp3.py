from pulp import LpMinimize, LpProblem, LpVariable, lpSum, value

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

# Create a MILP problem
problem = LpProblem("Optimal_Workload_Scheduler", LpMinimize)

# Decision variables: Assign workload i to cluster c
x = {(i, c): LpVariable(f"x_{i}_{c}", 0, 1, cat="Binary") for i in workloads for c in clusters}

# Decision variables: Start time of workload i
start = {i: LpVariable(f"start_{i}", 0) for i in workloads}

# Auxiliary variables: Active[i, t, c] indicates if workload i is active at time t on cluster c
time_horizon = max(workload["deadline"] for workload in workloads.values())
active = {
    (i, t, c): LpVariable(f"active_{i}_{t}_{c}", 0, 1, cat="Binary")
    for i in workloads
    for t in range(time_horizon + 1)
    for c in clusters
}

# Objective: Minimize total CO2 emissions
problem += lpSum(
    workloads[i]["power"] * workloads[i]["duration"] * clusters[c]["co2_intensity"] * x[i, c]
    for i in workloads for c in clusters
)

# Constraints

# Each workload must be assigned to one cluster
for i in workloads:
    problem += lpSum(x[i, c] for c in clusters) == 1, f"OneClusterPerWorkload_{i}"

# Deadline constraints: Start time must respect deadlines
for i in workloads:
    problem += start[i] <= workloads[i]["deadline"], f"Deadline_{i}"

# Active time constraints: Ensure active[i, t, c] is valid
for i in workloads:
    for t in range(time_horizon + 1):
        for c in clusters:
            # A workload can only be active if it has been assigned to the cluster
            problem += active[i, t, c] <= x[i, c], f"ActiveAssignment_{i}_{t}_{c}"
            # A workload can only be active between its start and end times
            problem += active[i, t, c] <= (t >= start[i]), f"ActiveStart_{i}_{t}_{c}"
            problem += active[i, t, c] <= (t < start[i] + workloads[i]["duration"]), f"ActiveEnd_{i}_{t}_{c}"

# GPU capacity constraints
for c in clusters:
    for t in range(time_horizon + 1):
        problem += (
            lpSum(active[i, t, c] for i in workloads) <= clusters[c]["gpus"],
            f"GPU_Limit_{c}_{t}",
        )

# Solve the problem
problem.solve()

# Output the results
print("Status:", problem.status)
if problem.status == 1:  # Solution is optimal
    print("Objective (Total CO2 Emissions):", value(problem.objective))
    for i in workloads:
        for c in clusters:
            if value(x[i, c]) == 1:
                print(f"Workload {i} assigned to Cluster {c} at start time {value(start[i])}")
else:
    print("No feasible solution found.")

