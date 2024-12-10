import psycopg2
import pandas as pd


# Database connection
conn = psycopg2.connect("dbname=epri user=isaac password=passEPRIword host=epri.cjcsqa8ckwo0.us-east-2.rds.amazonaws.com")
cur = conn.cursor()

# Path to the CSV file
excel_file_path = './h2_SOC_map.xlsx'
sheet_name = 'H2 Jobs'
df = pd.read_excel(excel_file_path, sheet_name=sheet_name)


for i, row in df.iterrows():
    sql = """
    INSERT INTO manual_soc_mapping (h2_soc_codes, h2_occ, soc_title, ed_req, work_req, training, skill, tech_cluster, eeo_classification, broad_description)
    VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
    """
    cur.execute(sql, tuple(row))

# Commit the transaction
conn.commit()

# Close the connection
cur.close()
conn.close()