from sqlalchemy import text
from sqlalchemy.ext.asyncio import create_async_engine
from .pydanticConfig import settings
from contextlib import asynccontextmanager

from datetime import timedelta

from functools import wraps
from typing import Callable, Any, Coroutine

def with_connection(func: Callable[..., Coroutine[Any, Any, Any]]):
    """
    Decorator for async DB methods that optionally accept a connection.
    If no 'conn' is provided, it will automatically open and close one
    using self.get_connection().
    """
    @wraps(func)
    async def wrapper(self, *args, conn=None, **kwargs):
        conn = kwargs.get("conn")

        if conn is not None:
            return await func(self, *args, **kwargs)

        async with self.get_connection() as temp_conn:
            return await func(self, *args, conn=temp_conn, **kwargs)
    return wrapper



class Database:
    engine = create_async_engine(
        settings.DATABASE_URL,
        connect_args={"server_settings": {"timezone": "UTC"}},
    )

    @asynccontextmanager
    async def get_connection(self):
        conn = await self.engine.connect()
        try:
            yield conn
        finally:
            await conn.close()



    @with_connection
    async def add_user_if_not_exists(self, discord_id, conn=None):
        async with conn.begin():
            result = await conn.execute(
                text("SELECT 1 FROM users WHERE discord_id = :discord_id"),
                {"discord_id": discord_id},
            )
            if result.first() is None:
                await conn.execute(
                    text("INSERT INTO users (discord_id) VALUES (:discord_id)"),
                    {"discord_id": discord_id},
                )



    @with_connection
    async def get_user(self, discord_id: int, conn=None):
        await self.add_user_if_not_exists(discord_id)

        result = await conn.execute(
            text("SELECT * FROM users WHERE discord_id = :discord_id"),
            {"discord_id": discord_id},
        )
        return result.mappings().first()



    @with_connection
    async def get_transactions(self, discord_id: int, conn=None):
        await self.add_user_if_not_exists(discord_id)

        result = await conn.execute(
            text(
                "SELECT * FROM transactions WHERE discord_id = :discord_id ORDER BY datetime DESC"
            ),
            {"discord_id": discord_id},
        )
        return result.mappings().all()



    @with_connection
    async def add_transaction(
        self, discord_id: int, type_: int, quantity: int, description: str, conn=None
    ):
        async with conn.begin():
            await conn.execute(
                text("""
                    INSERT INTO transactions (discord_id, type, quantity, description, datetime)
                    VALUES (:discord_id, :type, :quantity, :description, NOW())
                    """),
                {
                    "discord_id": discord_id,
                    "type": type_,
                    "quantity": quantity,
                    "description": description,
                },
            )



    @with_connection
    async def plus_balance(
        self, discord_id: int, val: int, description: str = "Manual", conn=None
    ):
        if val < 0:
            return

        await self.add_user_if_not_exists(discord_id)

        async with conn.begin():
            await conn.execute(
                text(
                    "UPDATE users SET balance = balance + :val WHERE discord_id = :discord_id"
                ),
                {"discord_id": discord_id, "val": val},
            )
            await self.add_transaction(discord_id, 1, val, description)



    @with_connection
    async def minus_balance(
        self, discord_id: int, val: int, description: str = "Manual", conn=None
    ):
        if val < 0:
            return

        await self.add_user_if_not_exists(discord_id)

        async with conn.begin():
            result = await conn.execute(
                text(
                    "UPDATE users SET balance = balance - :val WHERE discord_id = :discord_id AND balance >= :val"
                ),
                {"discord_id": discord_id, "val": val},
            )
            if result.rowcount > 0:
                await self.add_transaction(discord_id, 0, val, description)



    @with_connection
    async def last_claimed(self, discord_id: int, val: str, conn=None):
        await self.add_user_if_not_exists(discord_id)

        async with conn.begin():
            await conn.execute(
                text(
                    "UPDATE users SET last_claimed = :val WHERE discord_id = :discord_id"
                ),
                {"discord_id": discord_id, "val": val},
            )



    @with_connection
    async def add_voice_time(self, discord_id: int, val: timedelta, conn=None):
        val = int(val.total_seconds())
        if val < 0:
            return

        await self.add_user_if_not_exists(discord_id)

        async with conn.begin():
            await conn.execute(
                text(
                    "UPDATE users SET voice_time = voice_time + :val WHERE discord_id = :discord_id"
                ),
                {"discord_id": discord_id, "val": val},
            )



    @with_connection
    async def add_muted_voice_time(self, discord_id: int, val: timedelta, conn=None):
        val = int(val.total_seconds())
        if val < 0:
            return

        await self.add_user_if_not_exists(discord_id)

        async with conn.begin():
            await conn.execute(
                text(
                    "UPDATE users SET muted_time = muted_time + :val WHERE discord_id = :discord_id"
                ),
                {"discord_id": discord_id, "val": val},
            )
