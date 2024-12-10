import requests
import json
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

# SOC codes for testing

soc_code = "17-2041.00"

# Search for careers related to the SOC code
search_url = urljoin(ONET_API_BASE_URL, f"online/occupations/{soc_code}/details")
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
        complete_tasks.append(task.get('statement', 'No task statement available').replace('.', '<new_task>'))

if search_response and 'education' in search_response:
    education_data = search_response.get('education', {}).get('level_required', {}).get('category', [])
    for education in education_data:
        complete_education.append(f"{education.get('name', 'No education name available')} ({education.get('score', {}).get('value', '')}%)")



print(f"Occupation: {occupation}")
print(f"Description: {description}")
print(f"Tasks: {''.join(complete_tasks)}")
print(f"Education: {', '.join(complete_education)}")
