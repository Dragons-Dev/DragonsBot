import discord
from discord.ext import commands

import logging
from pathlib import Path

from src import db


class CustomFormatter(logging.Formatter):
    def format(self, record):
        log_fmt = FORMATS[record.levelno]
        formatter = logging.Formatter(log_fmt, style="{", datefmt="%d-%m-%y %H:%M:%S")
        return formatter.format(record)


FMT = "[{levelname:^9}] [{asctime}] [{name}] [{module}:{lineno}] : {message}"
FORMATS = {
    logging.DEBUG: f"\33[37m{FMT}\33[0m",
    logging.INFO: f"\33[36m{FMT}\33[0m",
    logging.WARNING: f"\33[33m{FMT}\33[0m",
    logging.ERROR: f"\33[31m{FMT}\33[0m",
    logging.CRITICAL: f"\33[1m\33[31m{FMT}\33[0m",
}
log = logging.getLogger(__name__)
log.setLevel(logging.DEBUG)
discord_log = logging.getLogger("discord")
discord_log.setLevel(logging.WARN)
console_handler = logging.StreamHandler()
console_handler.setLevel(logging.DEBUG)
console_handler.setFormatter(CustomFormatter())
log.addHandler(console_handler)
discord_log.addHandler(console_handler)


class Bot(commands.Bot):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.log = log
        status: dict[str, Exception | bool] = self.load_extensions("src.extensions", recursive=True, store=True)
        for key, value in status.items():
            if value is True:
                log.info(key + ": " + "loaded successfully")
            else:
                log.critical(key + ": " + str(value))

    async def on_guild_join(self, guild: discord.Guild):
        for command in self.walk_application_commands():
            await db.command_enabled(
                command=command.name,
                guild=guild.id,
                enabled=True
            )

    async def on_guild_remove(self, guild: discord.Guild):
        await db.command_enabled(
            command="*",
            guild=0,
            nuke=guild.id
        )
