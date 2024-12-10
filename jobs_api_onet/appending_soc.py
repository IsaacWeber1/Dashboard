import requests
import psycopg2
import json
import pandas as pd

# Replace these with your own O*NET credentials
ONET_USERNAME = 'epri'
ONET_PASSWORD = '5977jrb'

# Define the base URL for the O*NET API
ONET_API_BASE_URL = "https://services.onetcenter.org/ws/"

# Function to fetch data from O*NET API
def fetch_onet_data(url, params=None):
    headers = {
        'Authorization': 'Basic ZXByaTo1OTc3anJi',  # Base64 encoded credentials
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
def insert_data_into_db(soc_code, occupation, abilities, interests, work_values, skills, knowledge, work_context, technology, education, job_outlook):
    cur.execute("""
        INSERT INTO onet_data1 (soc_code, core_occupation, abilities, interests, work_values, skills, knowledge, work_context, technology, education, job_outlook)
        VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
        """, (soc_code, occupation, json.dumps(abilities), json.dumps(interests), json.dumps(work_values), json.dumps(skills), json.dumps(knowledge), json.dumps(work_context), json.dumps(technology), json.dumps(education), json.dumps(job_outlook)))
    conn.commit()

# New SOC codes
new_soc_codes = ["49-9043", "51-8021", "49-9052", "53-6051", "17-2061", "53-6099", "53-1043"]

# Fetch and insert data for each SOC code
for soc_code in new_soc_codes:
    search_url = ONET_API_BASE_URL + "mnm/search"
    params = {'keyword': soc_code}
    search_response = fetch_onet_data(search_url, params)
    if search_response and 'career' in search_response:
        for career in search_response['career']:
            career_url = career['href']
            career_data = fetch_onet_data(career_url)
            if career_data:
                occupation = career_data.get('title', None)

                # Fetch detailed data
                abilities_url = career_url + '/abilities'
                abilities = fetch_onet_data(abilities_url)
                
                interests_url = career_url + '/personality'
                interests = fetch_onet_data(interests_url)
                
                work_values_url = career_url + '/work_values'
                work_values = fetch_onet_data(work_values_url)
                
                skills_url = career_url + '/skills'
                skills = fetch_onet_data(skills_url)
                
                knowledge_url = career_url + '/knowledge'
                knowledge = fetch_onet_data(knowledge_url)
                
                work_context_url = career_url + '/work_context'
                work_context = fetch_onet_data(work_context_url)

                technology_url = career_url + '/technology'
                technology = fetch_onet_data(technology_url)

                education_url = career_url + '/education'
                education = fetch_onet_data(education_url)

                job_outlook_url = career_url + '/job_outlook'
                job_outlook = fetch_onet_data(job_outlook_url)
                
                insert_data_into_db(soc_code, occupation, abilities, interests, work_values, skills, knowledge, work_context, technology, education, job_outlook)

# Close the database connection
cur.close()
conn.close()
