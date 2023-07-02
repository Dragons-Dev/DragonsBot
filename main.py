import discord
from discord.ext import commands


from src import Bot, db
from settings import TOKEN


bot = Bot.Bot(
    command_prefix=commands.when_mentioned_or(">"),
    case_insensitive=True,
    strip_after_prefix=True,
    intents=discord.Intents.all(),
    debug_guilds=[1121877936128151675],
    activity=discord.Activity(
        type=discord.ActivityType.playing, name="with Zeus"
    ),
    status=discord.Status.idle,
)


@bot.listen("on_ready", once=True)
async def on_ready() -> None:
    await db.create_db()
    bot.log.info(f"Logged in as: {bot.user.display_name}")


bot.run(token=TOKEN)
