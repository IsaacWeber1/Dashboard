import requests
import psycopg2
import json
import pandas as pd
import base64
from urllib.parse import urljoin

# Replace these with your own O*NET credentials
ONET_USERNAME = 'epri'
ONET_PASSWORD = '5977jrb'

# Define the base URL for the O*NET API
ONET_API_BASE_URL = "https://services.onetcenter.org/ws/"

# Encode credentials dynamically
credentials = f"{ONET_USERNAME}:{ONET_PASSWORD}"
encoded_credentials = base64.b64encode(credentials.encode()).decode()

# Function to fetch data from O*NET API
def fetch_onet_data(url, params=None):
    headers = {
        'Authorization': f'Basic {encoded_credentials}',
        'Accept': 'application/json'
    }
    print(f"Requesting URL: {url} with params: {params}")
    response = requests.get(url, headers=headers, params=params)
    if response.status_code == 200:
        print(f"Success for URL: {url}")
        return response.json()
    else:
        print(f"Error fetching data for URL {url}: {response.status_code} {response.reason}")
        print(f"Response content: {response.text}")
        return None

# Database connection

conn = psycopg2.connect("dbname=epri user=isaac password=passEPRIword host=epri.cjcsqa8ckwo0.us-east-2.rds.amazonaws.com")
cur = conn.cursor()

# Function to insert data into the database
def insert_data_into_db(soc_code, occupation, description, complete_tasks, complete_education):
    cur.execute("""
        INSERT INTO onet_data3 (soc_code, core_occupation, base_job, tasks, qualifications)
        VALUES (%s, %s, %s, %s, %s)
        """, (soc_code, occupation, description, complete_tasks, complete_education))
    conn.commit()

# Load SOC codes from CSV
csv_file_path = './h2_SOC_map.csv'  # Update with your actual file path
soc_codes_df = pd.read_csv(csv_file_path)
soc_codes = soc_codes_df['SOC_code'].tolist()

# Fetch and insert data for each SOC code
for soc_code in soc_codes:
    search_url = urljoin(ONET_API_BASE_URL, f"online/occupations/{soc_code}.00/details")
    search_response = fetch_onet_data(search_url)
    complete_tasks = []
    complete_education = []
    if search_response and 'occupation' in search_response:
        occupation_data = search_response.get('occupation', None)
        if occupation_data:
            occupation = occupation_data.get('title', None)
            description = occupation_data.get('description', None)
    
    if search_response and 'tasks' in search_response:
        tasks_data = search_response.get('tasks', {}).get('task', [])
        for task in tasks_data:
            complete_tasks.append(task.get('statement', 'NULL'))
    
    if search_response and 'education' in search_response:
        education_data = search_response.get('education', {}).get('level_required', {}).get('category', [])
        for education in education_data:
            complete_education.append(f"{education.get('name', 'NULL')} ({education.get('score', {}).get('value', '')}%)")

    #print(f"{soc_code}\n{occupation}\n\n{''.join(complete_tasks)}\n\n{', '.join(complete_education)}")
    insert_data_into_db(soc_code, occupation, description, '<new_task>'.join(complete_tasks), ', '.join(complete_education))

# Close the database connection
cur.close()
conn.close()
