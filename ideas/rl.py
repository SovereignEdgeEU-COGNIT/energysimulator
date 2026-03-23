import gym
import numpy as np
from gym import spaces
from stable_baselines3 import PPO

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


class SchedulingEnv(gym.Env):
    def __init__(self):
        super(SchedulingEnv, self).__init__()
        self.workloads = list(workloads.keys())
        self.num_clusters = len(clusters)
        self.num_workloads = len(self.workloads)

        # State: workload index + remaining GPU capacity + deadlines
        self.observation_space = spaces.Box(
            low=0,
            high=1000,  # Arbitrary large value for deadlines and GPU states
            shape=(1 + self.num_clusters + self.num_workloads,),
            dtype=np.float32,
        )

        # Action: Assign workload to a cluster
        self.action_space = spaces.Discrete(self.num_clusters)

        # Reset environment
        self.reset()

    def reset(self):
        self.current_workload_index = 0
        self.remaining_gpus = {c: clusters[c]["gpus"] for c in clusters}
        self.deadlines = [workloads[w]["deadline"] for w in self.workloads]
        self.total_emissions = 0
        return self._get_state()

    def _get_state(self):
        current_workload = self.current_workload_index
        gpu_availability = list(self.remaining_gpus.values())
        return np.array([current_workload] + gpu_availability + self.deadlines, dtype=np.float32)

    def step(self, action):
        cluster_names = list(clusters.keys())
        cluster = cluster_names[action]
        workload_id = self.workloads[self.current_workload_index]
        workload_data = workloads[workload_id]

        reward = 0
        done = False

        # Check if the cluster has available GPUs
        if self.remaining_gpus[cluster] > 0:
            # Calculate CO2 emissions
            emissions = (
                workload_data["power"]
                * workload_data["duration"]
                * clusters[cluster]["co2_intensity"]
            )
            self.total_emissions += emissions
            reward -= emissions

            # Update GPU availability
            self.remaining_gpus[cluster] -= 1

            # Check deadlines
            if workload_data["duration"] > workload_data["deadline"]:
                reward -= 1000  # Penalty for missing deadlines
        else:
            # Penalize invalid actions
            reward -= 1000

        # Move to the next workload
        self.current_workload_index += 1

        # Check if all workloads are processed
        if self.current_workload_index >= self.num_workloads:
            done = True

        return self._get_state(), reward, done, {}

    def render(self, mode="human"):
        print(f"Workload: {self.current_workload_index}, GPUs: {self.remaining_gpus}, Emissions: {self.total_emissions}")


# Initialize environment
env = SchedulingEnv()

# Train the PPO agent
model = PPO("MlpPolicy", env, verbose=1)
model.learn(total_timesteps=10000)

# Test the trained model
state = env.reset()
done = False
while not done:
    action, _ = model.predict(state)
    state, reward, done, _ = env.step(action)
    env.render()

# Output total emissions
print("Total CO2 Emissions:", env.total_emissions)

