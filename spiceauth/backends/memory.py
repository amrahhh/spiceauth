from typing import List
from .base import AbstractBackend
from ..models import RelationTuple, Rule

class MemoryBackend(AbstractBackend):
    def __init__(self):
        self.tuples: List[RelationTuple] = []
        self.rules: List[Rule] = []

    async def write_tuples(self, tuples: List[RelationTuple]) -> None:
        self.tuples.extend(tuples)

    async def get_tuples(self, relation: str, object: str) -> List[RelationTuple]:
        return [
            t for t in self.tuples
            if t.relation == relation and t.object == object
        ]

    async def write_rule(self, rule: Rule) -> None:
        self.rules.append(rule)

    async def get_rules(self, object_type: str, relation: str) -> List[Rule]:
        return [
            r for r in self.rules
            if r.object_type == object_type and r.relation == relation
        ]
