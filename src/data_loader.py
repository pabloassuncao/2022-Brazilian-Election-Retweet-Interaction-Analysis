import networkx as nx
import os
import pickle
import sys

def load_graph(gml_path):
    """Loads the graph from a GML file."""
    print(f"Loading graph from {gml_path}...")
    if not os.path.exists(gml_path):
        raise FileNotFoundError(f"File not found: {gml_path}")
    
    try:
        G = nx.read_gml(gml_path, label='id')
        print(f"Graph loaded: {G.number_of_nodes()} nodes, {G.number_of_edges()} edges.")
        return G
    except Exception as e:
        print(f"Error loading graph: {e}")
        sys.exit(1)

def get_gcc(G):
    """Extracts the Giant Connected Component (GCC) from the graph."""
    print("Extracting Giant Connected Component (GCC)...")
    G_undirected = G.to_undirected()
    largest_cc_nodes = max(nx.connected_components(G_undirected), key=len)
    G_gcc = G_undirected.subgraph(largest_cc_nodes).copy()
    print(f"GCC extracted: {G_gcc.number_of_nodes()} nodes, {G_gcc.number_of_edges()} edges.")
    return G_gcc

def load_processed_data(cache_path):
    """Loads processed data from cache if available."""
    if os.path.exists(cache_path):
        print(f"Loading cached data from {cache_path}...")
        with open(cache_path, 'rb') as f:
            return pickle.load(f)
    return None

def save_processed_data(data, cache_path):
    """Saves processed data to cache."""
    print(f"Saving data to cache: {cache_path}...")
    with open(cache_path, 'wb') as f:
        pickle.dump(data, f)
