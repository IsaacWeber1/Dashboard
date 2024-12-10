import pandas as pd
import seaborn as sns
import matplotlib.pyplot as plt
import os

data_path = './visuals/mnt/data/aggregated_heatmap_data_with_categories.csv'
heatmap_data = pd.read_csv(data_path, index_col=[0, 1])


import pandas as pd
import seaborn as sns
import matplotlib.pyplot as plt

def display_clustergram():
    # Load the generated workforce data
    heatmap_data = pd.read_csv(data_path, index_col=[0, 1])

    sns.clustermap(
        heatmap_data.drop(columns={'Category'}),
        cmap='coolwarm',
        figsize=(12, 10),
        annot=False,
        fmt=".1f",
        method='average',
        metric='euclidean',
        row_cluster=True,  # Ensures hierarchical clustering is applied to rows
        col_cluster=True,  # Ensures hierarchical clustering is applied to columns
        dendrogram_ratio=(.1, .2),  # Adjusts dendrogram size for better visibility
        cbar_pos=(0, .2, .03, .4),  # Adjust colorbar position for better layout
        xticklabels=True,
        yticklabels=True
    )
    plt.show()


def display_clustergrams_by_category():
    heatmap_data = pd.read_csv(data_path, index_col=[0, 1])

    # Get unique categories
    unique_categories = heatmap_data['Category'].unique()


    for category in unique_categories:
        # Filter data by the current category
        #category_occupations = job_clusters_df[job_clusters_df['Category'] == category]['unique_occupation']
        category_data = heatmap_data.loc[heatmap_data['Category'] == category]

        # Generate the clustermap for this category
        g = sns.clustermap(
            category_data.drop(columns={'Category'}),
            cmap='coolwarm',
            figsize=(12, 10),
            annot=False,
            fmt=".1f",
            method='average',
            metric='euclidean',
            row_cluster=True,
            col_cluster=False,
            dendrogram_ratio=(.1, .2),
            cbar_pos=(0, .2, .03, .4),
            xticklabels=True,
            yticklabels=True
        )
        for i in range(len(category_data)):
            g.ax_heatmap.axhline(i, color='black', lw=0.5)

        # Add title to each clustergram
        plt.title(f'Clustergram for Category: {category}')
        plt.show()



display_clustergram()
display_clustergrams_by_category()
