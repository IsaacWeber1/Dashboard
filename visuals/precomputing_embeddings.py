import json
from sentence_transformers import SentenceTransformer

# Load the model for generating embeddings
model = SentenceTransformer('msmarco-distilbert-base-v4')

def generate_embedding(text):
    """Generate an embedding for a given text using the SentenceTransformer model."""
    return model.encode(text).tolist()  # Convert to list for JSON serialization

def recursive_compute_embeddings(node, parent_embedding=None, current_id=""):
    """
    Recursively compute embeddings for each node in the taxonomy tree and assign unique IDs.
    :param node: The current node in the taxonomy tree.
    :param parent_embedding: The embedding of the parent node's description.
    :param current_id: The current ID path (e.g., "6.4.2.2") for the node in the taxonomy.
    """
    node_description = node.get("_description", "")
    combined_description = (parent_embedding or "") + " " + node_description

    # Ensure only one embedding is computed per node
    if isinstance(node.get("_embedding"), list) and not isinstance(node["_embedding"][0], float):
        # This condition checks if there’s already a nested list (list of lists), indicating an issue
        print(f"Warning: Nested list found at node: {node_description}. Resetting to a single embedding.")
        node["_embedding"] = generate_embedding(combined_description)
    else:
        # Generate and store the embedding
        node["_embedding"] = generate_embedding(combined_description)

    # Assign the ID to the node
    node["_id"] = current_id

    # Recursively compute embeddings and assign IDs for child nodes
    for index, (key, child_node) in enumerate(node.items()):
        if not key.startswith("_"):
            child_id = f"{current_id}.{index}" if current_id else f"{index + 1}"
            recursive_compute_embeddings(child_node, combined_description, child_id)

def main():
    # Load the taxonomy tree from the JSON file
    with open('./mnt/data/taxonomy_tree.json', 'r') as file:
        taxonomy_tree = json.load(file)

    # Compute and store embeddings and assign IDs in the taxonomy tree
    recursive_compute_embeddings(taxonomy_tree)

    # Save the updated taxonomy tree with embeddings and IDs
    with open('./mnt/data/taxonomy_tree_with_embeddings.json', 'w') as file:
        json.dump(taxonomy_tree, file, indent=4)

    print("Taxonomy tree with embeddings saved to 'taxonomy_tree_with_embeddings.json'.")

if __name__ == "__main__":
    main()
