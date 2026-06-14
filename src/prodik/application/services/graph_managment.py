from collections import defaultdict
from dataclasses import dataclass
from heapq import heappop, heappush
from math import inf

from prodik.domain.edge import Edge
from prodik.domain.node import NodeId


@dataclass
class GraphManagmentService:
    def find_shortest_path(
        self, edges: list[Edge], from_node_id: NodeId, to_node_id: NodeId
    ) -> list[Edge]:
        graph: dict[NodeId, list[Edge]] = defaultdict(list)
        for edge in edges:
            graph[edge.node_a_id].append(edge)
            graph[edge.node_b_id].append(edge)

        distances: dict[NodeId, float] = defaultdict(lambda: inf)
        distances[from_node_id] = 0
        previous_edges: dict[NodeId, Edge] = {}

        counter = 0
        priority_queue: list[tuple[float, int, NodeId]] = [
            (0, counter, from_node_id),
        ]

        while priority_queue:
            current_distance, _, current_node_id = heappop(priority_queue)

            if current_distance > distances[current_node_id]:
                continue
            if current_node_id == to_node_id:
                break

            for edge in graph[current_node_id]:
                neighbor_id = edge.other_end(current_node_id)
                distance = current_distance + edge.weight

                if distance >= distances[neighbor_id]:
                    continue

                distances[neighbor_id] = distance
                previous_edges[neighbor_id] = edge
                counter += 1
                heappush(priority_queue, (distance, counter, neighbor_id))

        if to_node_id not in previous_edges:
            return []

        path: list[Edge] = []
        current_node_id = to_node_id
        while current_node_id != from_node_id:
            edge = previous_edges[current_node_id]
            path.append(edge)
            current_node_id = edge.other_end(current_node_id)

        path.reverse()

        return path
