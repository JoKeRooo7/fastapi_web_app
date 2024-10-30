import asyncio
import pydot
from sqlalchemy import create_engine, inspect
from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession, async_sessionmaker
from sqlalchemy.orm import sessionmaker

DATABASE_URL = "sqlite+aiosqlite:///database_model/my_database.db"

engine = create_async_engine(DATABASE_URL, echo=True)

async def create_db():
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)

async def create_er_diagram():
    async with engine.connect() as conn:
        inspector = inspect(conn)

        graph = pydot.Dot(graph_type='graph')

        for table_name in inspector.get_table_names():
            columns = inspector.get_columns(table_name)
            label = f"{table_name}\n" + "\n".join([col['name'] for col in columns])
            graph.add_node(pydot.Node(table_name, label=label, shape='box'))

        for table_name in inspector.get_table_names():
            foreign_keys = inspector.get_foreign_keys(table_name)
            for fk in foreign_keys:
                src_table = table_name
                dst_table = fk['referred_table']
                graph.add_edge(pydot.Edge(src_table, dst_table))

        graph.write_png('er_diagram.png')
        print("ER diagram saved as er_diagram.png.")

async def main():
    await create_db()
    await create_er_diagram()

asyncio.run(main())


