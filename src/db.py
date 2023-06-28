import os
from pathlib import Path

import aiosqlite
import discord


DB_PATH = Path("data/database.sqlite")


async def create_db() -> None:
    if not os.path.exists(DB_PATH):
        open(DB_PATH, "x").close()
    async with aiosqlite.connect(DB_PATH) as db:
        async with db.cursor() as cursor:
            cursor: aiosqlite.Cursor = cursor
            await cursor.execute("CREATE TABLE IF NOT EXISTS economy (cash REAL, user INTEGER, guild INTEGER)")
            await cursor.execute("CREATE TABLE IF NOT EXISTS commands (command TEXT, enabled INTEGER, guild INTEGER)")


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
