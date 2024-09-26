import discord
from discord.ext import commands

class MyCog(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @commands.Cog.listener()
    async def on_message(self, message):
        if message.author == self.bot.user:
            return

        # Handle message events here

    @commands.command()
    async def hello(self, ctx):
        await ctx.send("Hello!")

bot = commands.Bot(command_prefix="!")

bot.add_cog(MyCog(bot))
bot.run("YOUR_BOT_TOKEN")