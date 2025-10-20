from typing import Dict, List, Tuple


def transform_insights_to_graph(context: List[Tuple[Dict, Dict, Dict]]):
    nodes = {}
    edges = {}

    for triplet in context:
        src, rel, tgt = triplet

        src_id = src["id"]
        tgt_id = tgt["id"]

        nodes[src_id] = {
            "id": src_id,
            "label": src.get("name", src_id),
            "type": src["type"],
        }
        nodes[tgt_id] = {
            "id": tgt_id,
            "label": tgt.get("name", tgt_id),
            "type": tgt["type"],
        }
        edges[f"{src_id}_{rel['relationship_name']}_{tgt_id}"] = {
            "source": src_id,
            "target": tgt_id,
            "label": rel["relationship_name"],
        }

    return {
        "nodes": list(nodes.values()),
        "edges": list(edges.values()),
    }
