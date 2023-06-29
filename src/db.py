import os
from pathlib import Path
import typing as t

import aiosqlite
import discord


DB_PATH = Path("data/database.sqlite")


async def create_db() -> None:
    if not os.path.exists(DB_PATH):
        open(DB_PATH, "x").close()
    async with aiosqlite.connect(DB_PATH) as db:
        async with db.cursor() as cursor:
            cursor: aiosqlite.Cursor = cursor
            await cursor.execute(
                "CREATE TABLE IF NOT EXISTS economy (pocket INTEGER, bank INTEGER, user INTEGER, guild INTEGER)"
            )
            await cursor.execute(
                "CREATE TABLE IF NOT EXISTS commands (command TEXT, enabled INTEGER, guild INTEGER)"
            )


async def command_enabled(command: str, guild: int, enabled: bool = None, nuke: int = None):
    async with aiosqlite.connect(DB_PATH) as db:
        async with db.cursor() as cursor:
            cursor: aiosqlite.Cursor = cursor
            if nuke is not None:
                await cursor.execute("DELETE FROM commands WHERE guild = ?",
                                     (nuke,))
                return await db.commit()
            response = await cursor.execute("SELECT enabled FROM commands where command = ? AND guild = ?",
                                            (command, guild))
            response = await response.fetchone()
            if enabled is None:
                return response

            if response is None:
                await cursor.execute(
                    "INSERT INTO commands (command, enabled, guild) VALUES (?, ?, ?)",
                    (command, enabled, guild))
            else:
                await cursor.execute("UPDATE commands SET enabled = ? WHERE command = ? AND guild = ?",
                                     (enabled, command, guild))
            await db.commit()


async def make_member_cash(user: int, guild: int):
    async with aiosqlite.connect(DB_PATH) as db:
        async with db.cursor() as cursor:
            cursor: aiosqlite.Cursor = cursor
            await cursor.execute(
                    f"INSERT INTO economy (pocket, bank, user, guild) VALUES (?, ?, ?, ?)",
                    (0, 10000, user, guild))
            await db.commit()


async def get_member_cash(target: t.Literal["pocket", "bank"], user: int, guild: int):
    async with aiosqlite.connect(DB_PATH) as db:
        async with db.cursor() as cursor:
            cursor: aiosqlite.Cursor = cursor
            response = await cursor.execute(f"SELECT {target} FROM economy where user = ? AND guild = ?",
                                            (user, guild))
            response = await response.fetchone()
            if response is None:
                await make_member_cash(user=user, guild=guild)
                response = await get_member_cash(
                    target=target,
                    user=user,
                    guild=guild
                )

            return tuple(response)


async def set_member_cash(target: t.Literal["pocket", "bank"], amount: int, user: int, guild: int):
    async with aiosqlite.connect(DB_PATH) as db:
        async with db.cursor() as cursor:
            cursor: aiosqlite.Cursor = cursor
            await cursor.execute(f"UPDATE economy SET {target} = ? WHERE user = ? AND guild = ?",
                                 (amount, user, guild))
            await db.commit()
