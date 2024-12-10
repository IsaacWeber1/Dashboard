import psycopg2
import pandas as pd


# Database connection
conn = psycopg2.connect("dbname=epri user=isaac password=passEPRIword host=epri.cjcsqa8ckwo0.us-east-2.rds.amazonaws.com")
cur = conn.cursor()




for i, row in df.iterrows():
    sql = """
    insert into requirements_clusters1 (requirement_id, cluster)
    values (%s, %s)
    """
    cur.execute(sql, tuple(row))

conn.commit()

cur.close()
conn.close()