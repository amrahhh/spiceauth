from typing import List
from sqlalchemy.orm import Mapped, mapped_column
from sqla_async_orm_queries import Model
from .base import AbstractBackend
from ..models import RelationTuple, Rule

class RelationTupleModel(Model):
    __tablename__ = "relation_tuples"

    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    subject: Mapped[str] = mapped_column(index=True)
    relation: Mapped[str] = mapped_column(index=True)
    object: Mapped[str] = mapped_column(index=True)

class RuleModel(Model):
    __tablename__ = "rules"

    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    object_type: Mapped[str] = mapped_column(index=True)
    relation: Mapped[str] = mapped_column(index=True)
    computed_userset: Mapped[str] = mapped_column()

class SQLAlchemyBackend(AbstractBackend):
    async def write_tuples(self, tuples: List[RelationTuple]) -> None:
        data = [
            {"subject": t.subject, "relation": t.relation, "object": t.object}
            for t in tuples
        ]
        if data:
            await RelationTupleModel.bulk_create(data)

    async def get_tuples(self, relation: str, object: str) -> List[RelationTuple]:
        records = await RelationTupleModel.select_all(
            RelationTupleModel.relation == relation,
            RelationTupleModel.object == object
        )
        return [
            RelationTuple(subject=r.subject, relation=r.relation, object=r.object)
            for r in records
        ]

    async def write_rule(self, rule: Rule) -> None:
        await RuleModel.create({
            "object_type": rule.object_type,
            "relation": rule.relation,
            "computed_userset": rule.computed_userset
        })

    async def get_rules(self, object_type: str, relation: str) -> List[Rule]:
        records = await RuleModel.select_all(
            RuleModel.object_type == object_type,
            RuleModel.relation == relation
        )
        return [
            Rule(object_type=r.object_type, relation=r.relation, computed_userset=r.computed_userset)
            for r in records
        ]
