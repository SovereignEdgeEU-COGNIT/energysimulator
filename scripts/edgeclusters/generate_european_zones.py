import requests
import csv

# Define the API endpoint
url = 'https://api.electricitymap.org/v3/zones'

# List of European country codes (ISO 3166-1 alpha-2)
european_country_codes = [
    'AL', 'AD', 'AM', 'AT', 'AZ', 'BY', 'BE', 'BA', 'BG', 'HR', 'CY', 'CZ', 'DK', 'EE', 'FI', 'FR', 
    'GE', 'DE', 'GR', 'HU', 'IS', 'IE', 'IT', 'KZ', 'XK', 'LV', 'LI', 'LT', 'LU', 'MT', 'MD', 'MC', 
    'ME', 'NL', 'MK', 'NO', 'PL', 'PT', 'RO', 'RU', 'SM', 'RS', 'SK', 'SI', 'ES', 'SE', 'CH', 'TR', 
    'UA', 'GB', 'VA'
]

# Send the GET request to the API
response = requests.get(url)

# Check if the request was successful
if response.status_code == 200:
    # Parse the JSON response
    data = response.json()

    # Open a CSV file for writing
    with open('european_zones.csv', 'w', newline='') as csvfile:
        # Define the CSV writer
        fieldnames = ['zone', 'countryName', 'zoneName', 'displayName']
        writer = csv.DictWriter(csvfile, fieldnames=fieldnames)

        # Write the header
        writer.writeheader()

        # Write the data rows for European countries
        for zone, info in data.items():
            if zone.split('-')[0] in european_country_codes:  # Check if the zone code is in the European list
                writer.writerow({
                    'zone': zone,
                    'countryName': info.get('countryName', ''),
                    'zoneName': info.get('zoneName', ''),
                    'displayName': info.get('displayName', '')
                })

    print("Data has been written to european_zones.csv")

else:
    print(f"Failed to fetch data. Status code: {response.status_code}, Message: {response.text}")
