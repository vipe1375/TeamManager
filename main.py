import discord
from discord.ext import commands
import os

from dotenv import load_dotenv

load_dotenv()

token_tm = os.getenv("token_tm")

intents = discord.Intents.all()


class TMBot(commands.Bot):
    def __init__(self) -> None:
        super().__init__(command_prefix = '*', intents=intents, application_id=965686318518644756)

    async def setup_hook(self) -> None:
        await self.load_extension("cog1")
        await bot.tree.sync()

    async def on_ready(self):
        print('Prêt !')

bot = TMBot()
bot.run(token_tm)