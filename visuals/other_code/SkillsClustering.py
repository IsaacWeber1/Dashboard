import pandas as pd
from sentence_transformers import SentenceTransformer
from scipy.cluster.hierarchy import linkage, dendrogram, fcluster
import numpy as np

def cluster_skills():
    # Load the CSV file
    df = pd.read_csv('../mnt/data/reformatted_skills.csv')

    # Extract the relevant columns
    sentences = df['skill'].tolist()
    skill_ids = df['skill_id'].tolist()

    # Load the pre-trained model
    model = SentenceTransformer('all-MiniLM-L6-v2')

    # Generate embeddings for the sentences
    embeddings = model.encode(sentences)

    # Perform hierarchical clustering
    Z = linkage(embeddings, method='ward')

    # Define multiple thresholds for different clustering levels
    thresholds = np.linspace(0.5, 10.0, num=20)  # Generates 20 threshold levels between 0.5 and 10.0

    # Create a DataFrame to hold all clusters at different thresholds
    clusters_df = pd.DataFrame({'skill_id': skill_ids, 'skill': sentences})

    # For each threshold, generate clusters and add them as a column in the DataFrame
    for i, threshold in enumerate(thresholds):
        clusters = fcluster(Z, t=threshold, criterion='distance')
        clusters_df[f'Cluster_Threshold_{round(threshold, 2)}'] = clusters

    # Save the DataFrame with cluster assignments to a new CSV file
    clusters_df.to_csv('../mnt/extras/skill_clusters.csv', index=False)
    print("Clustered data exported to 'skill_clusters.csv'.")

if __name__ == "__main__":
    cluster_skills()
