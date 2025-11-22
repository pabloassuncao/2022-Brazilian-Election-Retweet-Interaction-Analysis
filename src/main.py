import os
import sys
import json
import networkx as nx
import pandas as pd
from src import data_loader, algorithms, metrics

# Configuration
RAW_DATA_PATH = "data/raw/eleicoes_2022.gml"
CACHE_DIR = "data/processed"
RESULTS_DIR = "results"
GCC_CACHE_PATH = os.path.join(CACHE_DIR, "gcc_graph.pkl")

# Visualization Configuration
EXPORT_TOP_50K = True
TOP_50K_LIMIT = 5000

EXPORT_INDIVIDUAL_COMMUNITIES = False
INDIVIDUAL_COMMUNITY_LIMIT = 50000  # Max nodes per individual community file

EXPORT_COMBINED_TOP_COMMUNITIES = True
COMBINED_TOP_COMMUNITIES_COUNT = 5
COMBINED_TOTAL_NODE_LIMIT = 5000   # Total nodes in the combined graph

# Options: 'EQUAL' (split limit equally) or 'PROPORTIONAL' (split based on community size)
COMBINED_NODE_DISTRIBUTION = 'PROPORTIONAL'

# Algorithm Configuration
# Available: "louvain", "label_propagation", "greedy_modularity", "asyn_lpa", "girvan_newman"
#            "hierarchical_greedy", "hierarchical_girvan", "leiden"
# WARNING: "greedy_modularity" and "girvan_newman" are very slow/memory intensive on large graphs.
# Use USE_SUBGRAPH = True for them.
ALGORITHMS_TO_RUN = ["leiden"] 
# ALGORITHMS_TO_RUN = ["louvain", "label_propagation", "greedy_modularity", "asyn_lpa"] # Full run (risky) 
# ALGORITHMS_TO_RUN = ["louvain", "label_propagation", "greedy_modularity", "asyn_lpa"] # Full run (risky) 
# ALGORITHMS_TO_RUN = ["louvain", "label_propagation", "greedy_modularity", "asyn_lpa"] # Full run (risky) 

# Subgraph Configuration (Recommended for slow algorithms like Girvan-Newman)
USE_SUBGRAPH = False
SUBGRAPH_SIZE = 1000 # Number of nodes for the subgraph (Top Degree)

def save_results(algorithm_name, partition, mod_score, bubble_metrics, G_gcc):
    """Saves analysis results to files."""
    print(f"Saving results for {algorithm_name}...")
    
    # 1. Save Metrics
    metrics_data = {
        "algorithm": algorithm_name,
        "modularity": mod_score,
        "bubble_metrics": bubble_metrics
    }
    
    metrics_file = os.path.join(RESULTS_DIR, "metrics", f"{algorithm_name}_metrics.json")
    with open(metrics_file, 'w') as f:
        json.dump(metrics_data, f, indent=4)
        
    # 2. Save Partition (CSV for easy loading)
    df = pd.DataFrame(list(partition.items()), columns=['node_id', 'community_id'])
    partition_file = os.path.join(RESULTS_DIR, "partitions", f"{algorithm_name}_partition.csv")
    df.to_csv(partition_file, index=False)
    
    # Pre-calculate degrees for sorting
    degrees = dict(G_gcc.degree())

    # 3. Export Visualization (Top N nodes)
    if EXPORT_TOP_50K:
        print(f"Exporting GEXF for Gephi (Top {TOP_50K_LIMIT} nodes)...")
        try:
            top_nodes = sorted(degrees, key=degrees.get, reverse=True)[:TOP_50K_LIMIT]
            G_sub = G_gcc.subgraph(top_nodes).copy()
            for node in G_sub.nodes():
                G_sub.nodes[node]['community'] = partition.get(node, -1)
                G_sub.nodes[node]['degree'] = degrees[node]
            
            visual_path = os.path.join(RESULTS_DIR, "visual", f"{algorithm_name}_top{TOP_50K_LIMIT}.gexf")
            nx.write_gexf(G_sub, visual_path)
            print(f"Saved visualization to {visual_path}")
        except Exception as e:
            print(f"Error exporting top nodes visualization: {e}")

    # Group nodes by community for next steps
    communities = {}
    for node, comm_id in partition.items():
        if comm_id not in communities:
            communities[comm_id] = []
        communities[comm_id].append(node)
    
    # Sort communities by size
    sorted_communities = sorted(communities.items(), key=lambda x: len(x[1]), reverse=True)[:COMBINED_TOP_COMMUNITIES_COUNT]

    # 4. Export Top Communities individually
    if EXPORT_INDIVIDUAL_COMMUNITIES:
        print(f"Exporting Top {COMBINED_TOP_COMMUNITIES_COUNT} Communities as separate GEXF files...")
        try:
            for comm_id, nodes in sorted_communities:
                if len(nodes) > INDIVIDUAL_COMMUNITY_LIMIT:
                    nodes = sorted(nodes, key=lambda n: degrees.get(n, 0), reverse=True)[:INDIVIDUAL_COMMUNITY_LIMIT]

                comm_sub = G_gcc.subgraph(nodes).copy()
                for n in comm_sub.nodes():
                    comm_sub.nodes[n]['degree'] = degrees.get(n, 0)
                    
                comm_path = os.path.join(RESULTS_DIR, "visual", f"{algorithm_name}_community_{comm_id}.gexf")
                nx.write_gexf(comm_sub, comm_path)
                print(f"Saved community {comm_id} ({len(nodes)} nodes) to {comm_path}")
        except Exception as e:
            print(f"Error exporting individual communities: {e}")

    # 5. Export Combined Top Communities
    if EXPORT_COMBINED_TOP_COMMUNITIES:
        print(f"Exporting Combined Top {COMBINED_TOP_COMMUNITIES_COUNT} Communities...")
        try:
            top_nodes_combined = []
            
            # Calculate limits per community
            if COMBINED_NODE_DISTRIBUTION == 'EQUAL':
                limit_per_comm = COMBINED_TOTAL_NODE_LIMIT // COMBINED_TOP_COMMUNITIES_COUNT
                limits = {comm_id: limit_per_comm for comm_id, _ in sorted_communities}
            elif COMBINED_NODE_DISTRIBUTION == 'PROPORTIONAL':
                total_nodes_in_top = sum(len(nodes) for _, nodes in sorted_communities)
                limits = {}
                for comm_id, nodes in sorted_communities:
                    # Proportion of the total limit based on community size relative to the sum of top communities
                    prop = len(nodes) / total_nodes_in_top
                    limits[comm_id] = int(prop * COMBINED_TOTAL_NODE_LIMIT)
            else:
                # Default to equal if unknown
                limit_per_comm = COMBINED_TOTAL_NODE_LIMIT // COMBINED_TOP_COMMUNITIES_COUNT
                limits = {comm_id: limit_per_comm for comm_id, _ in sorted_communities}

            for comm_id, nodes in sorted_communities:
                limit = limits.get(comm_id, 0)
                if len(nodes) > limit:
                    nodes_limited = sorted(nodes, key=lambda n: degrees.get(n, 0), reverse=True)[:limit]
                else:
                    nodes_limited = nodes
                top_nodes_combined.extend(nodes_limited)
                
            G_top_combined = G_gcc.subgraph(top_nodes_combined).copy()
            for n in G_top_combined.nodes():
                G_top_combined.nodes[n]['community'] = partition.get(n, -1)
                G_top_combined.nodes[n]['degree'] = degrees.get(n, 0)
                
            combined_path = os.path.join(RESULTS_DIR, "visual", f"{algorithm_name}_top{COMBINED_TOP_COMMUNITIES_COUNT}_combined.gexf")
            nx.write_gexf(G_top_combined, combined_path)
            print(f"Saved combined top communities to {combined_path}")

        except Exception as e:
            print(f"Error exporting combined visualization: {e}")
    
    print(f"Results saved to {RESULTS_DIR}")

def main():
    print("--- Starting Social Network Analysis Pipeline ---")
    
    # 1. Load Graph & GCC
    G_gcc = data_loader.load_processed_data(GCC_CACHE_PATH)
    if G_gcc is None:
        G = data_loader.load_graph(RAW_DATA_PATH)
        G_gcc = data_loader.get_gcc(G)
        data_loader.save_processed_data(G_gcc, GCC_CACHE_PATH)
    else:
        print("Loaded GCC from cache.")
    
    # Apply Subgraph if configured
    if USE_SUBGRAPH:
        print(f"WARNING: Running on a SUBGRAPH of size {SUBGRAPH_SIZE} (Top Degree Nodes).")
        degrees = dict(G_gcc.degree())
        top_nodes = sorted(degrees, key=degrees.get, reverse=True)[:SUBGRAPH_SIZE]
        G_work = G_gcc.subgraph(top_nodes).copy()
        print(f"Subgraph created: {G_work.number_of_nodes()} nodes, {G_work.number_of_edges()} edges.")
    else:
        G_work = G_gcc

    # 2. Run Algorithms
    all_algos = {
        "louvain": algorithms.run_louvain,
        "label_propagation": algorithms.run_label_propagation,
        "greedy_modularity": algorithms.run_greedy_modularity,
        "asyn_lpa": algorithms.run_asyn_lpa,
        "girvan_newman": algorithms.run_girvan_newman,
        # Hierarchical variants
        "hierarchical_greedy": lambda g: algorithms.run_hierarchical(g, meta_algo_func=algorithms.run_greedy_modularity),
        "hierarchical_girvan": lambda g: algorithms.run_hierarchical(g, meta_algo_func=algorithms.run_girvan_newman),
        "leiden": algorithms.run_leiden
    }
    
    # Filter algorithms based on configuration
    algos = {k: v for k, v in all_algos.items() if k in ALGORITHMS_TO_RUN}
    
    comparison_results = []
    
    for name, func in algos.items():
        print(f"\n--- Processing {name} ---")
        
        # Check cache (only if NOT using subgraph, to avoid cache pollution/mismatch)
        # Actually, we could cache subgraphs too but let's keep it simple and only cache full runs
        partition = None
        partition_file = os.path.join(RESULTS_DIR, "partitions", f"{name}_partition.csv")
        
        if not USE_SUBGRAPH and os.path.exists(partition_file):
             # Load from CSV if exists and we are using the full graph
             print(f"Loading partition from {partition_file}...")
             df = pd.read_csv(partition_file)
             # Ensure node_id is int (matches graph)
             partition = dict(zip(df['node_id'].astype(int), df['community_id']))
        
        if partition is None:
            partition = func(G_work)
            
        # Metrics
        print(f"Calculating metrics for {name}...")
        mod_score = metrics.calculate_modularity(G_work, partition)
        bubble_metrics = metrics.calculate_bubble_metrics(G_work, partition)
        part_stats = metrics.calculate_partition_stats(G_work, partition)
        
        print(f"Modularity: {mod_score:.4f}")
        print(f"Communities found: {part_stats['num_communities']}")
        
        # Save
        save_results(name, partition, mod_score, bubble_metrics, G_work)
        
        comparison_results.append({
            "algorithm": name,
            "modularity": mod_score,
            "num_communities": part_stats['num_communities'],
            "avg_community_size": part_stats['avg_community_size']
        })

    # 4. Save Comparison
    pd.DataFrame(comparison_results).to_csv(os.path.join(RESULTS_DIR, "metrics", "comparison.csv"), index=False)
    print("\n--- Pipeline Complete ---")

if __name__ == "__main__":
    main()
