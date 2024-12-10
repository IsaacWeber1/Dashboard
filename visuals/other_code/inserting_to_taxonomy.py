import json
import pandas as pd
from scipy.spatial.distance import cosine
import logging
from sentence_transformers import SentenceTransformer

# Set up logging
logging.basicConfig(level=logging.DEBUG, format='%(asctime)s - %(levelname)s - %(message)s')

model = SentenceTransformer('msmarco-distilbert-base-v4')

# Load the taxonomy tree with precomputed embeddings
with open('../mnt/data/taxonomy_tree_with_embeddings.json', 'r') as file:
    taxonomy_tree = json.load(file)

# Load the skills data
skills_df = pd.read_csv('../mnt/data/reformatted_skills.csv')

def recursive_taxonomy_search(skill_embedding, node, level=0, current_id=""):
    """
    Recursively search through the taxonomy tree to find the best match for the given skill embedding.
    :param skill_embedding: The embedding of the skill.
    :param node: The current node in the taxonomy tree.
    :param level: The current depth in the recursion (for logging purposes).
    :param current_id: The current ID path (e.g., "1.1.1") of the node in the taxonomy.
    :return: The best matching node, the similarity score, and the taxonomy ID.
    """
    # Use the precomputed embedding stored in the node
    combined_embedding = node.get('_embedding', None)

    if combined_embedding is None:
        logging.warning(f"No embedding found for node '{node.get('_description', '')}'")
        return node, 0, current_id  # Return the current node with a similarity of 0 if no embedding exists

    # Calculate the similarity between the skill and the current node
    similarity = 1 - cosine(skill_embedding, combined_embedding)

    # Initialize the best match as the current node
    best_match = node
    best_similarity = similarity
    best_id = current_id

    # Log the current level and node being processed
    logging.debug(f"Level {level}: Comparing with node '{node.get('_description', '')}' (Similarity: {similarity:.4f})")

    # Recursively search through child nodes
    for index, (key, child_node) in enumerate(node.items()):
        if key.startswith("_"):
            continue  # Skip non-branch keys

        # Create a new ID path for the child node (e.g., "1.1.2")
        child_id = f"{current_id}.{index + 1}" if current_id else f"{index + 1}"

        child_match, child_similarity, child_best_id = recursive_taxonomy_search(
            skill_embedding, child_node, level=level + 1, current_id=child_id
        )

        if child_similarity > best_similarity:
            best_match = child_match
            best_similarity = child_similarity
            best_id = child_best_id

    return best_match, best_similarity, best_id

def top_n_taxonomy_search(skill_embedding, taxonomy_tree, n):
    """
    Search the top N most similar top-level nodes and compare their subtrees.
    :param skill_embedding: The embedding of the skill.
    :param taxonomy_tree: The taxonomy tree to search.
    :param n: The number of top-level nodes to search deeper.
    :return: The best matching node, the similarity score, and the taxonomy ID.
    """
    top_level_results = []

    # Perform the first pass comparison at the top level
    for index, (key, node) in enumerate(taxonomy_tree.items()):
        if key.startswith("_"):
            continue  # Skip non-branch keys

        top_id = f"{index + 1}"
        _, top_similarity, _ = recursive_taxonomy_search(skill_embedding, node, level=0, current_id=top_id)
        top_level_results.append((node, top_similarity, top_id))

    # Sort by similarity and take the top N results
    top_level_results.sort(key=lambda x: x[n - 1], reverse=True)
    top_candidates = top_level_results[:n]

    # Now perform a full recursive search on the top N candidates
    best_match = None
    best_similarity = -1
    best_id = ""

    for node, _, top_id in top_candidates:
        candidate_match, candidate_similarity, candidate_id = recursive_taxonomy_search(
            skill_embedding, node, level=0, current_id=top_id
        )

        if candidate_similarity > best_similarity:
            best_match = candidate_match
            best_similarity = candidate_similarity
            best_id = candidate_id

    return best_match, best_similarity, best_id

def map_skills_to_taxonomy(taxonomy_tree, skills_df, n):
    """Map each skill to its best-fitting taxonomy node by considering the top N most similar top-level nodes."""
    skill_mappings = []

    for index, row in skills_df.iterrows():
        skill = row['skill']
        skill_id = row['skill_id']  # Assuming 'skill_id' is the column name in your CSV
        skill_embedding = model.encode(skill)

        logging.info(f"Processing skill {index + 1}/{len(skills_df)}: {skill} (ID: {skill_id})")

        best_match_node, similarity_score, taxonomy_id = top_n_taxonomy_search(skill_embedding, taxonomy_tree, n)

        skill_mappings.append({
            'Skill ID': skill_id,
            'Skill': skill,
            'Mapped Node': best_match_node.get('_description', 'Unmapped'),
            'Taxonomy ID': taxonomy_id,
            'Similarity Score': similarity_score
        })

    return pd.DataFrame(skill_mappings)

def main():
    # Map the skills to the taxonomy, considering the top 3 most similar top-level nodes
    skill_mappings_df = map_skills_to_taxonomy(taxonomy_tree, skills_df, 3)

    # Save the mapping results to a CSV file
    skill_mappings_df.to_csv('../mnt/extras/skill_taxonomy_mapping_with_ids.csv', index=False)

    print("Skill mappings have been saved to 'skill_taxonomy_mapping_with_ids.csv'.")

if __name__ == "__main__":
    main()
