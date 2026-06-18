from dataclasses import dataclass

@dataclass(frozen=True)
class RelationTuple:
    subject: str
    relation: str
    object: str

@dataclass
class Rule:
    object_type: str
    relation: str
    computed_userset: str
