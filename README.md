# SpiceAuth 🌶️

SpiceAuth is a lightweight, high-performance ReBAC (Relationship-Based Access Control) engine for Python, inspired by Google's Zanzibar paper. 

In traditional RBAC systems, you check if a user has a specific "role". In ReBAC, permissions are determined by tracing relationships in a graph. SpiceAuth allows you to define complex hierarchies (like Folders -> Documents, or Organizations -> Teams -> Users) without hardcoding business logic into your application code.

## Installation

Install SpiceAuth via pip. It requires Python 3.9+.

```bash
pip install spiceauth
```

If you plan to use the production-ready asynchronous SQLAlchemy backend, install the required dependencies:

```bash
pip install spiceauth[dev] # Includes aiosqlite, pytest for testing
# For production, install your preferred async DB driver, e.g., asyncpg
```

## Core Concepts

SpiceAuth models permissions using a few simple concepts:

1. **Subjects**: The entity taking an action (e.g., `user:amrah`, `group:dev-team`).
2. **Objects**: The resource being accessed (e.g., `document:roadmap-2026`, `project:alpha`).
3. **Relations**: The type of link between a subject and an object (e.g., `viewer`, `editor`, `member`, `parent`).
4. **RelationTuples**: A concrete statement linking a subject, relation, and object.
5. **Rules**: Dynamic schemas that compute permissions based on relations (e.g., "The editor of a document's parent project is automatically an editor of the document").

## Quickstart (Memory Backend)

For testing or simple applications, you can use the in-memory backend. SpiceAuth is fully asynchronous.

```python
import asyncio
from spiceauth import SpiceEngine, RelationTuple

async def main():
    # 1. Initialize the engine with the default Memory backend
    auth = SpiceEngine()

    # 2. Write relation tuples
    await auth.write_tuples([
        # Amrah is a member of the dev-team
        RelationTuple(subject="user:amrah", relation="member", object="group:dev-team"),
        
        # The dev-team is the editor of Project Alpha
        RelationTuple(subject="group:dev-team", relation="editor", object="project:alpha"),
        
        # Project Alpha is the parent of the Roadmap Document
        RelationTuple(subject="project:alpha", relation="parent", object="document:roadmap-2026")
    ])

    # 3. Define a Rule for computed relationships (Inheritance)
    # Rule: If a user is an 'editor' of a document's 'parent', they are an 'editor' of the document.
    await auth.define_rule(
        object_type="document",
        relation="editor",
        computed_userset="object.parent.editor" 
    )

    # 4. Check permissions
    is_allowed = await auth.check(
        subject="user:amrah", 
        relation="editor", 
        object="document:roadmap-2026"
    )
    
    print(f"Can Amrah edit the document? {is_allowed}") # Output: True

if __name__ == "__main__":
    asyncio.run(main())
```

## Production Usage (SQLAlchemy Backend)

For production, you should use a persistent database. SpiceAuth comes with an asynchronous SQLAlchemy backend built on top of `sqla-async-orm-queries`.

```python
import asyncio
from sqlalchemy.ext.asyncio import create_async_engine, async_sessionmaker
from sqla_async_orm_queries import Model

from spiceauth import SpiceEngine
from spiceauth.backends.sqlalchemy import SQLAlchemyBackend

async def init_db():
    # Use your production async database URL here (e.g., PostgreSQL with asyncpg)
    engine = create_async_engine("sqlite+aiosqlite:///:memory:")
    
    # Create tables
    async with engine.begin() as conn:
        await conn.run_sync(Model.metadata.create_all)
    
    # Initialize the session maker for the ORM
    SessionLocal = async_sessionmaker(
        autocommit=False, 
        autoflush=False, 
        expire_on_commit=False, 
        bind=engine
    )
    Model.init_session(SessionLocal)

async def main():
    await init_db()
    
    # Initialize the engine with SQLAlchemy backend
    auth = SpiceEngine(backend=SQLAlchemyBackend())
    
    # Now you can use auth.write_tuples() and auth.check() just like the memory backend!
    # They will be safely persisted in your relational database.

if __name__ == "__main__":
    asyncio.run(main())
```

## How It Works Under The Hood

When you call `auth.check()`, SpiceAuth performs a Graph traversal (DFS) to resolve permissions:
1. **Direct Match**: Does the tuple `(subject, relation, object)` exist in the DB?
2. **Implicit Group Membership**: Does the subject have a `member` relation to a group that has the requested relation?
3. **Computed Rules**: Does the object's type have a rule (like `object.parent.editor`)? If so, the engine fetches the parent object and recursively checks if the subject is an editor of that parent.

Infinite loops and circular dependencies are automatically caught and prevented during traversal.