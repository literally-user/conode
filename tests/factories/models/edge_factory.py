from dataclasses import dataclass
from math import ceil
from random import choice, randint
from uuid import uuid4

from prodik.application.interfaces.repositories import EdgeRepository
from prodik.domain.company import Company
from prodik.domain.context import Context
from prodik.domain.edge import Edge, EdgeId
from prodik.domain.node import Node


@dataclass(slots=True)
class EdgeFactory:
    edge_repository: EdgeRepository

    async def create_edge(
        self,
        node_a: Node,
        node_b: Node,
        company: Company,
        context: Context,
        weight: float = 0,
    ) -> Edge:
        edge = Edge.new(
            edge_id=EdgeId(uuid4()),
            node_a=node_a,
            node_b=node_b,
            company=company,
            context=context,
            weight=weight,
        )
        await self.edge_repository.create(edge)
        return edge

    async def generate_random_graph(
        self,
        nodes: list[Node],
        company: Company,
        context: Context,
        coupling: float = 1.0,
    ) -> list[Edge]:
        edges = []

        for _ in range(ceil(len(nodes) * 2 * coupling)):
            while True:
                node_a, node_b = choice(nodes), choice(nodes)
                if node_a != node_b:
                    break

            edges.append(
                await self.create_edge(
                    node_a,
                    node_b,
                    company=company,
                    context=context,
                    weight=randint(1, 100),
                )
            )

        return edges
