import networkx as nx
import community as community_louvain

def run_louvain(G):
    """Runs the Louvain algorithm for community detection."""
    print("Running Louvain Algorithm...")
    partition = community_louvain.best_partition(G)
    return partition

def run_label_propagation(G):
    """Runs the Label Propagation algorithm."""
    print("Running Label Propagation Algorithm...")
    # returns a generator of sets of nodes
    communities_generator = nx.algorithms.community.label_propagation_communities(G)
    partition = {}
    for i, comm in enumerate(communities_generator):
        for node in comm:
            partition[node] = i
    return partition

def run_greedy_modularity(G):
    """Runs the Greedy Modularity algorithm (Clauset-Newman-Moore)."""
    print("Running Greedy Modularity Algorithm (this might be slow)...")
    # returns a list of sets of nodes
    communities_list = nx.algorithms.community.greedy_modularity_communities(G)
    partition = {}
    for i, comm in enumerate(communities_list):
        for node in comm:
            partition[node] = i
    return partition

def run_asyn_lpa(G):
    """Runs the Asynchronous Label Propagation Algorithm."""
    print("Running Asynchronous Label Propagation Algorithm...")
    # returns a generator of sets of nodes
    # weight=None to treat as unweighted, or specify weight string
    communities_generator = nx.algorithms.community.asyn_lpa_communities(G)
    partition = {}
    for i, comm in enumerate(communities_generator):
        for node in comm:
            partition[node] = i
    return partition

def run_girvan_newman(G):
    """
    Runs the Girvan-Newman algorithm.
    WARNING: This is O(m^2 n) and extremely slow for large graphs.
    It iterates to find the partition with the highest modularity.
    """
    print("Running Girvan-Newman Algorithm (WARNING: This is extremely slow)...")
    if G.number_of_edges() > 10000:
        print(f"WARNING: Graph has {G.number_of_edges()} edges. Girvan-Newman might take days.")
    
    # Returns an iterator over tuples of sets of nodes
    comp = nx.algorithms.community.girvan_newman(G)
    
    # Strategy: Iterate and track best modularity. 
    # Limit iterations to avoid infinite loops on large graphs if user insists
    max_iter = 20 
    
    import itertools
    
    # We need to convert the tuple of sets to a partition dict for modularity calc
    def to_partition_dict(communities):
        p = {}
        for i, c in enumerate(communities):
            for node in c:
                p[node] = i
        return p

    best_partition_map = None
    best_modularity = -1

    try:
        # We only look at the first few splits because of time constraints
        for communities in itertools.islice(comp, max_iter):
            partition = to_partition_dict(communities)
            # We need to calculate modularity using the library function or our wrapper
            # Our wrapper expects G and partition dict
            # We can use nx.community.quality.modularity directly for speed/simplicity
            mod = nx.community.quality.modularity(G, communities)
            
            print(f"  GN: Found {len(communities)} communities, Modularity: {mod:.4f}")
            
            if mod > best_modularity:
                best_modularity = mod
                best_partition_map = partition
            else:
                pass
                
    except Exception as e:
        print(f"Error in Girvan-Newman: {e}")
        if best_partition_map:
            return best_partition_map
        raise e

    return best_partition_map if best_partition_map else {}

def run_hierarchical(G, base_algo_func=run_louvain, meta_algo_func=run_greedy_modularity):
    """
    Runs a hierarchical community detection strategy (Coarsening).
    1. Run base_algo (e.g., Louvain) to get micro-communities.
    2. Build a Quotient Graph where nodes are the micro-communities.
    3. Run meta_algo (e.g., Greedy Modularity) on the Quotient Graph.
    4. Map results back to original nodes.
    """
    print("Running Hierarchical Strategy...")
    
    # Step 1: Base Partition
    print("  Step 1: Running base algorithm (Louvain) for micro-communities...")
    base_partition = base_algo_func(G)
    
    # Step 2: Build Quotient Graph
    print("  Step 2: Building Quotient Graph...")
    # Create a mapping from community_id to list of nodes
    comm_to_nodes = {}
    for node, comm_id in base_partition.items():
        if comm_id not in comm_to_nodes:
            comm_to_nodes[comm_id] = []
        comm_to_nodes[comm_id].append(node)
    
    # Create the quotient graph
    # Nodes are community IDs
    # Edges are weighted by the number of edges between communities in the original graph
    Q = nx.Graph()
    Q.add_nodes_from(comm_to_nodes.keys())
    
    # Iterate over original edges to build quotient edges
    # This can be slow, so we iterate carefully
    # Optimization: Iterate over edges of G, map endpoints to comms, add to Q
    
    edge_weights = {}
    
    for u, v in G.edges():
        c_u = base_partition[u]
        c_v = base_partition[v]
        
        if c_u != c_v:
            pair = tuple(sorted((c_u, c_v)))
            edge_weights[pair] = edge_weights.get(pair, 0) + 1
            
    for (c1, c2), weight in edge_weights.items():
        Q.add_edge(c1, c2, weight=weight)
        
    print(f"  Quotient Graph built: {Q.number_of_nodes()} super-nodes, {Q.number_of_edges()} edges.")
    
    # Step 3: Meta Algorithm
    print(f"  Step 3: Running meta algorithm on Quotient Graph...")
    # Note: Meta algo must handle weighted graphs if possible, or we treat as unweighted
    # Greedy modularity in networkx handles weights if 'weight' attr is present?
    # nx.algorithms.community.greedy_modularity_communities uses 'weight' param
    
    # We need to wrap the meta algo call because our wrappers might not expose weight param
    # But our wrappers take G. If G has 'weight' edge attributes, some algos use it.
    # Let's assume meta_algo_func is one of our wrappers.
    
    # Special handling if meta_algo is greedy_modularity to ensure it uses weights if available
    # Actually our run_greedy_modularity just calls nx...greedy_modularity_communities(G)
    # which defaults to weight='weight'. So we are good if we set 'weight' attr.
    
    meta_partition = meta_algo_func(Q)
    
    # Step 4: Map back
    print("  Step 4: Mapping back to original nodes...")
    final_partition = {}
    
    for comm_id, meta_comm_id in meta_partition.items():
        # comm_id is the node in Q (which is a community in G)
        # meta_comm_id is the new community ID assigned to this super-node
        
        # Assign all original nodes in this micro-community to the new meta-community
        for node in comm_to_nodes[comm_id]:
            final_partition[node] = meta_comm_id
            
    return final_partition

def run_leiden(G):
    """Runs the Leiden algorithm."""
    print("Running Leiden Algorithm...")
    try:
        import leidenalg
        import igraph
    except ImportError:
        print("Error: leidenalg or igraph not installed. Please run 'pip install leidenalg igraph'.")
        return {}

    # Convert NetworkX graph to igraph
    # This can be memory intensive
    print("  Converting NetworkX graph to igraph...")
    
    # Mapping: NetworkX nodes can be anything (int, str). igraph nodes are 0-indexed ints.
    # We need to map back.
    nodes = list(G.nodes())
    node_map = {node: i for i, node in enumerate(nodes)}
    reverse_map = {i: node for i, node in enumerate(nodes)}
    
    # Create igraph
    # Edges as list of tuples (mapped)
    # Efficiently create edges list
    edges = [(node_map[u], node_map[v]) for u, v in G.edges()]
    
    H = igraph.Graph(n=len(nodes), edges=edges, directed=G.is_directed())
    
    # Run Leiden
    # partition_type=leidenalg.ModularityVertexPartition usually for modularity maximization
    print("  Executing Leiden...")
    # n_iterations=-1 runs until convergence
    partition = leidenalg.find_partition(H, leidenalg.ModularityVertexPartition, n_iterations=-1)
    
    # Map back results
    final_partition = {}
    # partition is a VertexClustering object, iterable yields lists of node indices
    for i, cluster_nodes in enumerate(partition):
        for node_idx in cluster_nodes:
            original_node = reverse_map[node_idx]
            final_partition[original_node] = i
            
    return final_partition
