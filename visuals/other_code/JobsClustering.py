import pandas as pd
from sentence_transformers import SentenceTransformer

def map_occupation_to_category(occupation):
    # Define the keyword-to-category mapping
    keywords = [
        "Engineer",
        "Technician",
        "Specialist",
        "Operator",
        "Inspector",
        "Mechanic",
        "Manager",
        "Technologist",
        "Trade",
        "Scheduler",
        "Planner",
        "Coordinator"
    ]

    occupation_lower = occupation.lower()

    for keyword in keywords:
        if keyword.lower() in occupation_lower:
            return keyword if (keyword != 'Planner' or keyword != 'Coordinator' or keyword != 'Scheduler') else "Scheduler (or related profession)"

    return "Other"

def cluster_occupations():
    # Load the CSV file
    df = pd.read_csv('../mnt/data/reformatted_occupations.csv')

    # Manually group occupations based on keywords
    df['Category'] = df['core_occupation'].apply(map_occupation_to_category)

    # Keep each occupation as a separate row, while categorizing it
    df.sort_values(by=['Category']).to_csv('../mnt/extras/occupation_clusters_individual.csv', index=False)

if __name__ == "__main__":
    cluster_occupations()







