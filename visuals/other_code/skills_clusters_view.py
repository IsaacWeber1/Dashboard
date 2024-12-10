import pandas as pd
from sentence_transformers import SentenceTransformer
from scipy.cluster.hierarchy import linkage, dendrogram, fcluster
import matplotlib.pyplot as plt
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
import tkinter as tk
from tkinter import filedialog

class ClusteringApp:
    def __init__(self, root):
        self.root = root
        self.root.title("Hierarchical Clustering Tool")

        # Bind the closing event
        self.root.protocol("WM_DELETE_WINDOW", self.on_closing)

        # Load the CSV file
        self.df = pd.read_csv('../mnt/data/reformatted_skills.csv')

        # Extract the relevant columns
        self.sentences = self.df['skill'].tolist()
        self.skill_ids = self.df['skill_id'].tolist()

        # Load the pre-trained model
        self.model = SentenceTransformer('all-MiniLM-L6-v2')

        # Generate embeddings for the sentences
        self.embeddings = self.model.encode(self.sentences)

        # Perform hierarchical clustering
        self.Z = linkage(self.embeddings, method='ward')

        # Create a figure for the dendrogram
        self.fig, self.ax = plt.subplots(figsize=(10, 7))

        # Create the slider with a more granular range
        self.slider = tk.Scale(root, from_=0.5, to=10.0, resolution=0.01, orient=tk.HORIZONTAL, label="Distance Threshold")
        self.slider.set(1.0)  # Set the initial position
        self.slider.pack()

        # Label to display the number of clusters
        self.cluster_label = tk.Label(root, text="Number of Clusters: ")
        self.cluster_label.pack()

        # Button to update the plot and cluster count
        self.update_button = tk.Button(root, text="Update Dendrogram", command=self.update_dendrogram)
        self.update_button.pack()

        # Button to export the data
        self.export_button = tk.Button(root, text="Export Clustered Data", command=self.export_data)
        self.export_button.pack()

        # Embed the plot in the Tkinter window
        self.canvas = FigureCanvasTkAgg(self.fig, master=root)
        self.canvas.get_tk_widget().pack()

        # Initial plot
        self.update_dendrogram()

    def update_dendrogram(self):
        # Clear the previous plot
        self.ax.clear()

        # Get the current value of the slider
        threshold = self.slider.get()

        # Update the dendrogram
        dendrogram(self.Z, ax=self.ax, labels=self.skill_ids, leaf_rotation=90, color_threshold=threshold)
        self.ax.axhline(y=threshold, color='r', linestyle='--')
        self.ax.set_title('Hierarchical Clustering Dendrogram')
        self.ax.set_xlabel('Skill ID')
        self.ax.set_ylabel('Distance')

        # Calculate the number of clusters
        clusters = fcluster(self.Z, t=threshold, criterion='distance')
        num_clusters = len(set(clusters))

        # Update the cluster count label
        self.cluster_label.config(text=f"Number of Clusters: {num_clusters}")

        # Redraw the canvas
        self.canvas.draw()

    def export_data(self):
        # Get the current value of the slider
        threshold = self.slider.get()

        # Extract cluster assignments based on the current threshold
        clusters = fcluster(self.Z, t=threshold, criterion='distance')

        # Add cluster assignments to the DataFrame
        self.df['Cluster'] = clusters

        # Save the DataFrame with cluster assignments to a new CSV file
        save_path = filedialog.asksaveasfilename(defaultextension=".csv",
                                                 filetypes=[("CSV files", "*.csv"), ("All files", "*.*")])
        if save_path:
            self.df.to_csv(save_path, index=False)
            tk.messagebox.showinfo("Export Successful", f"Clustered data exported to {save_path}")

    def on_closing(self):
        self.root.quit()
        self.root.destroy()

# Create the main window
root = tk.Tk()
app = ClusteringApp(root)

# Run the Tkinter event loop
root.mainloop()