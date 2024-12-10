import json
import pandas as pd
from collections import defaultdict
from anytree import Node, RenderTree
from anytree.exporter import DotExporter
import logging

def build_taxonomy_hierarchy(taxonomy_df):
    # Extract and parse the 'New Unique ID' into levels
    taxonomy_hierarchy = defaultdict(dict)
    
    for _, row in taxonomy_df.iterrows():
        levels = row['Taxonomy ID'].split(".")
        description = row['Description']

        current_level = taxonomy_hierarchy
        for level in levels:
            if level.strip():
                if not isinstance(current_level, dict):
                    logging.error(f"Expected dictionary but found list at level {level}.")
                    return None
                current_level = current_level.setdefault(level, {})
        current_level["_description"] = description

    return taxonomy_hierarchy


def build_anytree_hierarchy(taxonomy_hierarchy, parent=None, level=""):
    for key, value in taxonomy_hierarchy.items():
        if key == "_description":  # Skip description keys in this recursive build
            continue
        node_name = f"{level}.{key}" if level else key  # Build the hierarchical name
        node = Node(f"{node_name} {value.get('_description', '')}", parent=parent)
        build_anytree_hierarchy(value, parent=node, level=node_name)  # Recursively build the hierarchy

def save_tree_as_text(root_node, file_name):
    with open(file_name, "w") as file:
        for pre, _, node in RenderTree(root_node):
            file.write(f"{pre}{node.name}\n")
    print(f"Tree structure saved as {file_name}")

def save_tree_as_json(taxonomy_hierarchy, file_name):
    with open(file_name, "w") as file:
        json.dump(taxonomy_hierarchy, file, indent=4)
    print(f"Tree structure saved as {file_name}")

def save_tree_as_image(root_node, file_name):
    DotExporter(root_node).to_picture(file_name)
    print(f"Tree structure saved as {file_name}")

def display_and_save_hierarchy(taxonomy_hierarchy):
    # Build the hierarchical structure using anytree
    root_node = Node("Taxonomy Root")
    build_anytree_hierarchy(taxonomy_hierarchy, parent=root_node)

    # Display the tree structure
    for pre, _, node in RenderTree(root_node):
        print(f"{pre}{node.name}")

    # Save the tree structure in different formats
    save_tree_as_text(root_node, "./mnt/data/taxonomy_tree.txt")
    save_tree_as_json(taxonomy_hierarchy, "./mnt/data/taxonomy_tree.json")
    save_tree_as_json(taxonomy_hierarchy, "../taxonomy_viewer/src/assets/taxonomy_tree.json")

def main():
    # Load the CSV file containing the taxonomy information
    taxonomy_file_path = './mnt/data/complete_taxonomy.csv'
    taxonomy_df = pd.read_csv(taxonomy_file_path)

    # Build the theoretical taxonomy hierarchy
    taxonomy_hierarchy = build_taxonomy_hierarchy(taxonomy_df)

    # Display and save the hierarchy
    display_and_save_hierarchy(taxonomy_hierarchy)

if __name__ == "__main__":
    main()
