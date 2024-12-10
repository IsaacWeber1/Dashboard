import pandas as pd

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
            if keyword in ['Planner', 'Coordinator', 'Scheduler']:
                return "Scheduler (or related profession)"
            return keyword

    return "Other"

def aggregate_workforce_data():
    # Load the skills data
    skills_df = pd.read_csv('./mnt/data/reformatted_skills.csv')

    # Load the taxonomy mapping data
    skill_mapping_df = pd.read_csv('./mnt/data/threshold_skills_insertion.csv')

    # Load the occupation data
    occupation_data_df = pd.read_excel('./mnt/data/complete_canada_data.xlsx')

    # Load the occupation clusters data
    occupation_clusters_df = pd.read_csv('./mnt/data/occupation_clusters_individual.csv')

    # Load the empty taxonomy structure
    taxonomy_df = pd.read_csv('./mnt/data/complete_taxonomy.csv')

    # Step 1: Link Occupation Data to Categories
    occupation_with_category_df = pd.merge(
        occupation_data_df,
        occupation_clusters_df[['occupation_id', 'Category']],
        on='occupation_id',
        how='left'
    )
    print("Occupation Data with Categories:")
    print(occupation_with_category_df.head())  # Debugging output

    # Step 2: Link Skills to Requirements
    skills_with_taxonomy_df = pd.merge(
        skills_df,
        skill_mapping_df[['skill_id', 'Taxonomy ID']],
        on='skill_id',
        how='left'
    )
    print("\nSkills Data with Taxonomy Mapping:")
    print(skills_with_taxonomy_df.head())  # Debugging output

    # Step 3: Aggregate Skills for Each Requirement
    aggregated_requirements_df = pd.merge(
        occupation_with_category_df,
        skills_with_taxonomy_df,
        on='requirement_id',
        how='left'
    )
    print("\nAggregated Requirements Data:")
    print(aggregated_requirements_df[['Category', 'core_occupation', 'requirement_id', 'Taxonomy ID']].head())  # Debugging output

    # Step 4: Filter to Top-Level Taxonomy Categories
    top_level_taxonomies = taxonomy_df.loc[
        taxonomy_df['Taxonomy ID'].str.contains(r'^\d+(\.\d+)?$', regex=True)  # Regex to find top-level taxonomies
    ].copy()

    top_level_taxonomies['Cleaned Taxonomy ID'] = top_level_taxonomies['Taxonomy ID'].str.split('.').str[0]  # Keep only the top-level

    taxonomy_map = top_level_taxonomies.set_index('Cleaned Taxonomy ID')['Description'].to_dict()

    # Convert 'Taxonomy ID' to string and handle NaN values
    aggregated_requirements_df['Taxonomy ID'] = aggregated_requirements_df['Taxonomy ID'].astype(str)

    # Apply the top-level taxonomy mapping to the aggregated data
    aggregated_requirements_df['Top_Level_Taxonomy'] = aggregated_requirements_df['Taxonomy ID'].apply(
        lambda x: taxonomy_map.get(x.split('.')[0], f'Taxonomy {x}') if pd.notna(x) else 'Unknown Taxonomy'
    )

    # Step 5: Aggregate Data by core_occupation and Top-Level Taxonomy
    occupation_skill_matrix = aggregated_requirements_df.pivot_table(
        index='core_occupation',
        columns='Top_Level_Taxonomy',
        aggfunc='size',  # Count the occurrences of each taxonomy for each occupation
        fill_value=0
    )

    # Step 6: Add Categories Based on Occupation Keywords
    occupation_skill_matrix['Category'] = occupation_skill_matrix.index.map(map_occupation_to_category)

    # Sort the data by Category
    occupation_skill_matrix = occupation_skill_matrix.sort_values(by=['Category'])

    # Save the final pivot table with categories
    occupation_skill_matrix.to_csv('./mnt/data/aggregated_heatmap_data_with_categories.csv')
    print("\nGenerated 'aggregated_heatmap_data_with_categories.csv' successfully!")

if __name__ == "__main__":
    aggregate_workforce_data()