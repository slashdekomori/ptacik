from sqlalchemy import text
from sqlalchemy.ext.asyncio import create_async_engine
from .config import settings
import asyncio
# Таблица workers
# discord_id: str ; index = 0
# penalty: int ; index = 1

class Database:
    engine = create_async_engine(settings.DATABASE_URL)

    async def add_worker_if_not_exists(self, id: str):
        async with self.engine.connect() as conn:
            result = await conn.execute(
                text("SELECT 1 FROM workers WHERE discord_id = :id"),
                {"id": id}
            )
            if result.first() is None:
                await conn.execute(
                    text("INSERT INTO workers (discord_id) VALUES (:id)"),
                    {"id": id}
                )
                await conn.commit()

    async def worker_exists(self,id: str):
            async with self.engine.connect() as conn:
                result = await conn.execute(
                    text("SELECT 1 FROM workers WHERE discord_id = :id"),
                    {"id": id}
                    )
                return result.first() is not None
            
        
    async def get_workers(self,id: str):
        async with self.engine.connect() as conn:
            if not await self.worker_exists(id):
                await self.add_worker_if_not_exists(id)

            result = await conn.execute(
                text("SELECT * FROM workers WHERE discord_id = :id"),
                {"id": id}
            )
            row = result.mappings().first()
            return row
        
    async def give_penalty(self,id: str):
        async with self.engine.connect() as conn:
            if not await self.worker_exists(id):
                await self.add_worker_if_not_exists(id)

            await conn.execute(
                text("UPDATE workers SET penalty = penalty + 1 WHERE discord_id = :id"),
                {"id": id}
                )
            await conn.commit()

    async def forgive_penalty_handle(self, id: str):
        async with self.engine.connect() as conn:
            if not await self.worker_exists(id):
                await self.add_worker_if_not_exists(id)

            await conn.execute(
                text("UPDATE workers SET penalty = penalty - 1 WHERE discord_id = :id AND penalty > 0"),
                {"id": id}
            )
            await conn.commit()


    async def start_work_handle(self,id: str, time_worked_seconds: int):
        async with self.engine.connect() as conn:
            if not await self.worker_exists(id):
                await self.add_worker_if_not_exists(id)

            await conn.execute(
                text("UPDATE workers SET work_time = work_time + :time_worked_seconds WHERE discord_id = :id"),
                {"id": id, "time_worked_seconds": time_worked_seconds}
                )
            await conn.commit()

    async def break_handle(self,id: str, break_time_seconds: int):
        async with self.engine.connect() as conn:
            if not await self.worker_exists(id):
                await self.add_worker_if_not_exists(id)

            await conn.execute(
                text("UPDATE workers SET break_time = break_time + :break_time_seconds WHERE discord_id = :id"),
                {"id": id, "break_time_seconds": break_time_seconds}
                )
            await conn.commit()

