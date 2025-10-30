from sqlalchemy import text
from sqlalchemy.ext.asyncio import create_async_engine
from .pydanticConfig import settings


class Database:
    engine = create_async_engine(
        settings.DATABASE_URL,
        connect_args={"server_settings": {"timezone": "UTC"}},
    )

    async def get_conn(self):
        return await self.engine.connect()

    async def add_user_if_not_exists(self, id: str):
        async with self.engine.connect() as conn:
            result = await conn.execute(
                text("SELECT 1 FROM users WHERE discord_id = :id"), {"id": id}
            )
            if result.first() is None:
                await conn.execute(
                    text("INSERT INTO users (discord_id) VALUES (:id)"), {"id": id}
                )
                await conn.commit()
        return

    # Returns - {'discord_id': 456802396874735616, 'balance': 0, 'last_claimed': None, 'voice_time': 0, 'message_count': 0}
    async def get_user(self, id: str):
        async with self.engine.connect() as conn:
            await self.add_user_if_not_exists(id)

            result = await conn.execute(
                text("SELECT * FROM users WHERE discord_id = :id"), {"id": id}
            )
            row = result.mappings().first()
            return row

    async def get_transactions(self, id: str):
        async with self.engine.connect() as conn:
            await self.add_user_if_not_exists(id)

            result = await conn.execute(
                text("SELECT * FROM transactions WHERE discord_id = :id"), {"id": id}
            )
            rows = result.mappings().all()
            return rows

    async def add_transaction(
        self, discord_id: str, type_: int, quantity: int, description: str
    ):
        async with self.engine.connect() as conn:
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
            await conn.commit()

    async def plus_balance(self, id: str, val: int, description: str = "Manual"):
        if val < 0:
            return
        async with self.engine.connect() as conn:
            await self.add_user_if_not_exists(id)

            await conn.execute(
                text(
                    "UPDATE users SET balance = balance + :val WHERE discord_id = :id"
                ),
                {"id": id, "val": val},
            )
            await conn.commit()
            await self.add_transaction(id, 1, val, description)

    async def minus_balance(self, id: str, val: int, description: str = "Manual"):
        if val < 0:
            return
        async with self.engine.connect() as conn:
            await self.add_user_if_not_exists(id)
            result = await conn.execute(
                text(
                    "UPDATE users SET balance = balance - :val WHERE discord_id = :id AND balance >= :val"
                ),
                {"id": id, "val": val},
            )
            await conn.commit()

        # only add transaction if balance was actually changed
        if result.rowcount > 0:
            await self.add_transaction(id, 0, val, description)

    async def last_claimed(self, id: str, val: str):
        async with self.engine.connect() as conn:
            await self.add_user_if_not_exists(id)

            await conn.execute(
                text("UPDATE users SET last_claimed = :val WHERE discord_id = :id"),
                {"id": id, "val": val},
            )
            await conn.commit()
