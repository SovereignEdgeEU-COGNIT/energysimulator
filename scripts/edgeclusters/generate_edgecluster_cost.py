import json
import random
import csv


# To add a realistic cost for using high-end GPUs like the Nvidia H100 in your JSON, we need to factor in 
# regional differences and typical cloud pricing. The cost for an Nvidia H100 is generally between 
# €2-€4 per hour. However, since you want a cost per second, we can calculate that as €0.00055-€0.00111 per second.

def calculate_average_carbon_intensity(file_path):
    """
    Calculate the average carbon intensity from the CSV file.
    """
    try:
        with open(file_path, "r") as file:
            reader = csv.DictReader(file)
            intensities = [float(row["carbonIntensity"]) for row in reader if row["carbonIntensity"].isdigit()]
            return sum(intensities) / len(intensities) if intensities else 0
    except FileNotFoundError:
        print(f"File not found: {file_path}")
        return None

def add_cost(clusters):
    # Cost parameters
    min_cost = 0.00055  # €/second
    max_cost = 0.00111  # €/second

    # Process each cluster
    for cluster in clusters:
        # Read the carbon intensity file path
        carbon_intensity_file = cluster.get("carbon-intensity-trace")

        # Calculate average carbon intensity
        avg_carbon_intensity = calculate_average_carbon_intensity(carbon_intensity_file)

        if avg_carbon_intensity is None:
            # Assign default random cost if no valid intensity
            cluster["gpu_cost_euro_per_second"] = round(random.uniform(min_cost, max_cost), 6)
        else:
            # Normalize carbon intensity and compute cost
            normalized_intensity = max(0, min(1, avg_carbon_intensity / 1000))  # Scale between 0 and 1
            cluster["gpu_cost_euro_per_second"] = round(
                min_cost + (max_cost - min_cost) * (1 - normalized_intensity), 6
            )

    return clusters

def main():
    with open("./edge-clusters-carbonh.json", "r") as f:
        clusters = json.load(f)  # This returns a list of dictionaries

    json_output = add_cost(clusters)
    clusters = json.dumps(json_output, indent=4)

    with open("./edge-clusters-cost.json", "w") as f:
        f.write(json.dumps(json_output, indent=4))

if __name__ == "__main__":
    main()
