import json
import pandas as pd
from scipy.spatial.distance import cosine
import logging
from sentence_transformers import SentenceTransformer

# Set up logging
logging.basicConfig(level=logging.DEBUG, format='%(asctime)s - %(levelname)s - %(message)s')

model = SentenceTransformer('msmarco-distilbert-base-v4')

# Load the taxonomy tree with precomputed embeddings
with open('./mnt/data/taxonomy_tree_with_embeddings.json', 'r') as file:
    taxonomy_tree = json.load(file)

# Load the skills data
skills_df = pd.read_csv('./mnt/data/reformatted_skills.csv')
#skills_df = pd.read_csv('./mnt/data/TEST_reformatted_skills.csv')

def recursive_taxonomy_search(skill_embedding, node, level=0, current_id=""):
    """
    Recursively search through the taxonomy tree to find the best matches for the given skill embedding.
    :param skill_embedding: The embedding of the skill.
    :param node: The current node in the taxonomy tree.
    :param level: The current depth in the recursion (for logging purposes).
    :param current_id: The current ID path (e.g., "1.1.1") of the node in the taxonomy.
    :return: The best matching nodes, the similarity scores, and the taxonomy IDs.
    """
    # Use the precomputed embedding stored in the node
    combined_embedding = node.get('_embedding', None)

    if combined_embedding is None:
        logging.warning(f"No embedding found for node '{node.get('_description', '')}'")
        return []

    similarity = 1 - cosine(skill_embedding, combined_embedding)
    logging.debug(f"Level {level}: Comparing with node '{node.get('_description', '')}' (Similarity: {similarity:.4f})")

    # Use the correct ID from the node if available
    node_id = node.get('_id', current_id)

    matches = [(node, similarity, node_id)]  # Store the current node as a match

    # Recursively search through child nodes
    for key, child_node in node.items():
        if key.startswith("_"):
            continue

        child_id = child_node.get('_id', f"{current_id}.{key}")
        matches.extend(recursive_taxonomy_search(skill_embedding, child_node, level + 1, current_id=child_id))

    return matches

def top_n_taxonomy_search(skill_embedding, taxonomy_tree, n):
    """
    Search the top N most similar top-level nodes and compare their subtrees.
    :param skill_embedding: The embedding of the skill.
    :param taxonomy_tree: The taxonomy tree to search.
    :param n: The number of top-level nodes to search deeper.
    :return: The best matching node, the similarity score, and the taxonomy ID.
    """
    top_level_results = []

    for index, (key, node) in enumerate(taxonomy_tree.items()):
        if key.startswith("_"):
            continue

        top_id = f"{index + 1}"
        matches = recursive_taxonomy_search(skill_embedding, node, level=0, current_id=top_id)
        top_level_results.extend(matches)

    # Sort matches by similarity
    top_level_results.sort(key=lambda x: x[1], reverse=True)

    # Determine the dynamic threshold (e.g., 80% of the highest similarity score)
    if top_level_results:
        threshold = top_level_results[0][1] * 0.90  # Adjust the 0.8 as needed

        # Filter out matches below the threshold
        filtered_results = [match for match in top_level_results if match[1] >= threshold]
        return filtered_results

    return []

def map_skills_to_taxonomy(taxonomy_tree, skills_df, n):
    """Map each skill to its best-fitting taxonomy node by considering the top N most similar top-level nodes."""
    skill_mappings = []

    for index, row in skills_df.iterrows():
        skill = row['skill']
        skill_id = row['skill_id']
        skill_embedding = model.encode(skill)

        logging.info(f"Processing skill {index + 1}/{len(skills_df)}: {skill} (ID: {skill_id})")

        matches = top_n_taxonomy_search(skill_embedding, taxonomy_tree, n)

        for match in matches:
            best_match_node, similarity_score, taxonomy_id = match
            skill_mappings.append({
                'skill_id': skill_id,
                'skill': skill,
                'Mapped Node': best_match_node.get('_description', 'Unmapped'),
                'Taxonomy ID': taxonomy_id,
                'Similarity Score': similarity_score
            })

    return pd.DataFrame(skill_mappings)

def main():
    # Map the skills to the taxonomy, considering the top 3 most similar top-level nodes
    skill_mappings_df = map_skills_to_taxonomy(taxonomy_tree, skills_df, 3)

    # Save the mapping results to a CSV file
    skill_mappings_df.to_csv('./mnt/data/threshold_skills_insertion.csv', index=False)

    print("Skill mappings have been saved to 'threshold_skills_insertion.csv'.")

if __name__ == "__main__":
    main()
