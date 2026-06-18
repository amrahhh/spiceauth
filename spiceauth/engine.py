from typing import List, Set, Tuple, Optional
from .backends.base import AbstractBackend
from .backends.memory import MemoryBackend
from .models import RelationTuple, Rule

class SpiceEngine:
    def __init__(self, backend: Optional[AbstractBackend] = None):
        if backend is None:
            self.backend = MemoryBackend()
        else:
            self.backend = backend

    async def write_tuples(self, tuples: List[RelationTuple]) -> None:
        await self.backend.write_tuples(tuples)

    async def define_rule(self, object_type: str, relation: str, computed_userset: str) -> None:
        await self.backend.write_rule(Rule(object_type, relation, computed_userset))

    async def check(self, subject: str, relation: str, object: str, visited: Optional[Set[Tuple[str, str, str]]] = None) -> bool:
        if visited is None:
            visited = set()
            
        req_key = (subject, relation, object)
        if req_key in visited:
            return False
        visited.add(req_key)

        # 1. Direct check
        direct_tuples = await self.backend.get_tuples(relation=relation, object=object)
        for t in direct_tuples:
            if t.subject == subject:
                return True
            # 2. Indirect check via group membership
            if await self.check(subject, "member", t.subject, visited):
                return True

        # 3. Rule-based check (Computed Usersets)
        object_type = object.split(":")[0] if ":" in object else ""
        if not object_type:
            return False
            
        rules = await self.backend.get_rules(object_type=object_type, relation=relation)
        
        for rule in rules:
            parts = rule.computed_userset.split(".")
            if len(parts) == 3 and parts[0] == "object":
                tuple_relation = parts[1]
                target_relation = parts[2]
                
                parent_tuples = await self.backend.get_tuples(relation=tuple_relation, object=object)
                for pt in parent_tuples:
                    parent_object = pt.subject
                    if await self.check(subject, target_relation, parent_object, visited):
                        return True
                        
        return False
