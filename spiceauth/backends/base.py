from abc import ABC, abstractmethod
from typing import List
from ..models import RelationTuple, Rule

class AbstractBackend(ABC):
    @abstractmethod
    async def write_tuples(self, tuples: List[RelationTuple]) -> None:
        pass

    @abstractmethod
    async def get_tuples(self, relation: str, object: str) -> List[RelationTuple]:
        pass

    @abstractmethod
    async def write_rule(self, rule: Rule) -> None:
        pass

    @abstractmethod
    async def get_rules(self, object_type: str, relation: str) -> List[Rule]:
        pass
