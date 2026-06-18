import pytest
import pytest_asyncio
from sqlalchemy.ext.asyncio import create_async_engine, async_sessionmaker
from sqla_async_orm_queries import Model
from spiceauth.models import RelationTuple, Rule
from spiceauth.engine import SpiceEngine
from spiceauth.backends.memory import MemoryBackend
from spiceauth.backends.sqlalchemy import SQLAlchemyBackend

@pytest.mark.asyncio
async def test_memory_backend():
    auth = SpiceEngine(backend=MemoryBackend())
    await auth.write_tuples([
        RelationTuple(subject="user:amrah", relation="member", object="group:dev-team"),
        RelationTuple(subject="group:dev-team", relation="editor", object="project:alpha"),
        RelationTuple(subject="project:alpha", relation="parent", object="document:roadmap-2026")
    ])
    await auth.define_rule(
        object_type="document",
        relation="editor",
        computed_userset="object.parent.editor" 
    )

    is_allowed = await auth.check(subject="user:amrah", relation="editor", object="document:roadmap-2026")
    assert is_allowed is True

    # Negative test case
    is_allowed = await auth.check(subject="user:other", relation="editor", object="document:roadmap-2026")
    assert is_allowed is False


@pytest_asyncio.fixture
async def setup_db():
    engine = create_async_engine("sqlite+aiosqlite:///:memory:")
    async with engine.begin() as conn:
        await conn.run_sync(Model.metadata.create_all)
    
    SessionLocal = async_sessionmaker(autocommit=False, autoflush=False, expire_on_commit=False, bind=engine)
    Model.init_session(SessionLocal)
    
    yield
    
    async with engine.begin() as conn:
        await conn.run_sync(Model.metadata.drop_all)


@pytest.mark.asyncio
async def test_sqlalchemy_backend(setup_db):
    auth = SpiceEngine(backend=SQLAlchemyBackend())
    await auth.write_tuples([
        RelationTuple(subject="user:amrah", relation="member", object="group:dev-team"),
        RelationTuple(subject="group:dev-team", relation="editor", object="project:alpha"),
        RelationTuple(subject="project:alpha", relation="parent", object="document:roadmap-2026")
    ])
    await auth.define_rule(
        object_type="document",
        relation="editor",
        computed_userset="object.parent.editor" 
    )

    is_allowed = await auth.check(subject="user:amrah", relation="editor", object="document:roadmap-2026")
    assert is_allowed is True

    # Negative test case
    is_allowed = await auth.check(subject="user:other", relation="editor", object="document:roadmap-2026")
    assert is_allowed is False
