import networkx as nx
import community as community_louvain

def calculate_modularity(G, partition):
    """Calculates the modularity score of the partition."""
    try:
        # community_louvain.modularity expects a partition dict {node: comm_id}
        score = community_louvain.modularity(partition, G)
        return score
    except Exception as e:
        print(f"Error calculating modularity: {e}")
        return None

def calculate_partition_stats(G, partition):
    """Calculates basic stats for the partition."""
    communities = {}
    for node, comm_id in partition.items():
        if comm_id not in communities:
            communities[comm_id] = []
        communities[comm_id].append(node)
    
    num_communities = len(communities)
    sizes = [len(c) for c in communities.values()]
    max_size = max(sizes) if sizes else 0
    min_size = min(sizes) if sizes else 0
    avg_size = sum(sizes) / num_communities if num_communities > 0 else 0
    
    return {
        "num_communities": num_communities,
        "max_community_size": max_size,
        "min_community_size": min_size,
        "avg_community_size": avg_size
    }

def calculate_bubble_metrics(G, partition):
    """
    Calculates metrics related to 'bubbles':
    - Internal Density: Density of edges within the community.
    - Conductance: Fraction of edges leaving the community.
    """
    communities = {}
    for node, comm_id in partition.items():
        if comm_id not in communities:
            communities[comm_id] = []
        communities[comm_id].append(node)
    
    metrics = {}
    
    for comm_id, nodes in communities.items():
        # Skip very small communities to save time/noise
        if len(nodes) < 10:
            continue
            
        subgraph = G.subgraph(nodes)
        int_edges = subgraph.number_of_edges()
        size = len(nodes)
        
        # Internal Density
        possible_edges = size * (size - 1) / 2
        internal_density = int_edges / possible_edges if possible_edges > 0 else 0
        
        # Cut Size (edges leaving the community)
        cut_size = nx.cut_size(G, nodes)
        
        # Conductance (cut_size / min(volume(S), volume(V-S)))
        # Volume is sum of degrees
        vol_S = sum(dict(G.degree(nodes)).values())
        # Approximate volume of rest of graph (total_vol - vol_S)
        # For large graphs, just use vol_S as denominator if we assume S is small compared to V
        # But standard definition:
        # conductance = cut_size / min(vol_S, 2*m - vol_S)
        total_vol = 2 * G.number_of_edges()
        denom = min(vol_S, total_vol - vol_S)
        conductance = cut_size / denom if denom > 0 else 0
        
        metrics[comm_id] = {
            "size": size,
            "internal_density": internal_density,
            "conductance": conductance,
            "cut_size": cut_size
        }
        
    return metrics
