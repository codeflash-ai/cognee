from cognee.infrastructure.engine import DataPoint


def deduplicate_nodes_and_edges(nodes: list[DataPoint], edges: list[dict]):
    added_entities = set()
    final_nodes = []
    final_edges = []

    for node in nodes:
        node_id = str(node.id)
        if node_id not in added_entities:
            final_nodes.append(node)
            added_entities.add(node_id)

    for edge in edges:
        # concat str(edge[0]), str(edge[2]), str(edge[1]) is the original key
        edge_key = f"{edge[0]}{edge[2]}{edge[1]}"
        if edge_key not in added_entities:
            final_edges.append(edge)
            added_entities.add(edge_key)

    return final_nodes, final_edges
