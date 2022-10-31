from typing import Union
from tgbot.config import load_config, Config
import asyncpg
from asyncpg import Connection
from asyncpg.pool import Pool

config = load_config(".env")

class Database:
    def __init__(self):
        self.pool: Union[Pool, None] = None

    async def create(self):
        # conn = await asyncpg.connect(config.DB_URL)
        self.pool = await asyncpg.create_pool(
            user=config.db.user,
            password=config.db.password,
            host=config.db.host,
            database=config.db.database
        )

    async def execute(self, command, *args,
                      fetch: bool = False,
                      fetchval: bool = False,
                      fetchrow: bool = False,
                      execute: bool = False
                      ):
        async with self.pool.acquire() as connection:
            connection: Connection
            async with connection.transaction():
                if fetch:
                    result = await connection.fetch(command, *args)
                elif fetchval:
                    result = await connection.fetchval(command, *args)
                elif fetchrow:
                    result = await connection.fetchrow(command, *args)
                elif execute:
                    result = await connection.execute(command, *args)
            return result

    @staticmethod
    def format_args(sql, parameters: dict):
        sql += " AND ".join([
            f"{item} = ${num}" for num, item in enumerate(parameters.keys(),
                                                          start=1)
        ])
        return sql, tuple(parameters.values())

    # Users table queries

    async def add_user(self, id, full_name, phone_number, username, score, joined_date):
        sql = "INSERT INTO competition_telegramusers (id, full_name, phone_number, username, score, joined_date) VALUES($1, $2, $3, $4, $5, $6) returning *"
        return await self.execute(sql, id, full_name, phone_number, username, score, joined_date, fetchrow=True)

    async def select_all_users(self):
        sql = "SELECT * FROM competition_telegramusers ORDER BY score DESC"
        return await self.execute(sql, fetch=True)

    async def select_user(self, **kwargs):
        sql = "SELECT * FROM competition_telegramusers WHERE "
        sql, parameters = self.format_args(sql, parameters=kwargs)
        return await self.execute(sql, *parameters, fetchrow=True)

    async def set_phone_number(self, phone_number, id):
        sql = "UPDATE competition_telegramusers SET phone_number=$1 WHERE id=$2"
        return await self.execute(sql, phone_number, id, execute=True)

    async def update_user_score(self, id):
        sql = "UPDATE competition_telegramusers SET score = score + 5 WHERE id=$1"
        return await self.execute(sql, id, execute=True)

    async def add_invited_users(self, user_offered_id, user_invited_id, created_at):
        sql = "INSERT INTO competition_invitedusers (user_offered_id, user_invited_id, created_at) VALUES($1, $2, $3) returning *"
        return await self.execute(sql, user_offered_id, user_invited_id, created_at, fetchrow=True)

    async def count_users(self):
        sql = "SELECT COUNT(*) FROM competition_telegramusers"
        return await self.execute(sql, fetchval=True)

    async def delete_users(self):
        await self.execute("DELETE FROM competition_telegramusers WHERE TRUE", execute=True)

    # Channels table queries

    async def get_all_channels(self):
        sql = "SELECT username FROM competition_channels"
        return await self.execute(sql, fetch=True)

    async def select_all_channels(self):
        sql = "SELECT * FROM competition_channels"
        return await self.execute(sql, fetch=True)

db = Database()