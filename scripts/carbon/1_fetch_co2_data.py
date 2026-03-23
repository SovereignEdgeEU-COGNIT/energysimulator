import requests
import csv
from datetime import datetime
import time
import logging
import os

# Configuration
base_url = 'https://api.electricitymap.org/v3/carbon-intensity/history?zone='
auth_token = os.getenv('ELECTRICITYMAP_API_TOKEN', 'MnSINfplNTxqx')  # Use environment variable for the token
headers = {'auth-token': auth_token}
zones_file = 'european_zones.csv'
data_dir = './carbon'
sleep_interval = 3600  # 1 hour in seconds

logging.basicConfig(level=logging.INFO,
                    format='%(asctime)s - %(levelname)s - %(message)s',
                    handlers=[logging.FileHandler('carbon_data_fetch.log'),
                              logging.StreamHandler()])

zones = []
with open(zones_file, 'r', newline='') as csvfile:
    reader = csv.DictReader(csvfile)
    for row in reader:
        zones.append(row['zone'])

def fetch_and_append_data(zone):
    url = f"{base_url}{zone}"
    try:
        response = requests.get(url, headers=headers)
        response.raise_for_status()
    except requests.RequestException as e:
        logging.error(f"Failed to fetch data for {zone}: {e}")
        return
    
    try:
        data = response.json()
    except ValueError as e:
        logging.error(f"Error decoding JSON response for {zone}: {e}")
        return
    
    file_name = os.path.join(data_dir, f"{zone}.csv")
    
    existing_data = {}
    try:
        with open(file_name, 'r', newline='') as csvfile:
            reader = csv.DictReader(csvfile)
            for row in reader:
                existing_data[row['datetime']] = row
    except FileNotFoundError:
        logging.info(f"{file_name} not found. A new file will be created.")
    except Exception as e:
        logging.error(f"Error reading {file_name}: {e}")
    
    new_entries = 0
    updated_data = {entry['datetime']: entry for entry in data.get('history', [])}

    # Merge the existing data with the new data, overwriting old entries
    existing_data.update(updated_data)

    try:
        with open(file_name, 'w', newline='') as csvfile:
            fieldnames = ['datetime', 'carbonIntensity', 'isEstimated', 'estimationMethod']
            writer = csv.DictWriter(csvfile, fieldnames=fieldnames)
            
            writer.writeheader()
            for entry in sorted(existing_data.values(), key=lambda x: x['datetime']):
                writer.writerow({
                    'datetime': entry['datetime'],
                    'carbonIntensity': entry['carbonIntensity'],
                    'isEstimated': entry['isEstimated'],
                    'estimationMethod': entry.get('estimationMethod', '')
                })
                new_entries += 1
        
        logging.info(f"Updated {file_name} with {new_entries} entries")
    except Exception as e:
        logging.error(f"Error writing to {file_name}: {e}")

while True:
    for zone in zones:
        fetch_and_append_data(zone)
    current_time = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    logging.info(f"Sleeping for 1 hour... Current time: {current_time}")
    time.sleep(sleep_interval)

