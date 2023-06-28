import discord
from discord.ext import commands

import logging
from pathlib import Path


class Bot(commands.Bot):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        status: dict[str, Exception | bool] = self.load_extensions("src.extensions", recursive=True, store=True)
        for key, value in status.items():
            print(key + ": " + ("loaded successfully" if value is True else f"failed: {value}"))



