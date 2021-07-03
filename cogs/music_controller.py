from discord.ext import commands
from discord_slash import cog_ext, SlashContext, ComponentContext
from discord_slash.utils.manage_commands import create_option
from requests.models import guess_filename
from src.parser import parse
import src.command_handler as handle
from src.constants import *
from config import GUILD_ID
from src.element.MusicBoxContext import MusicBoxContext
import discord
from cogs.event_listener import profiles

COMMAND_CHANNEL_WARNING = 'Accepted command.'


class MusicController(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @cog_ext.cog_slash(name="test",
                       guild_ids=GUILD_ID,
                       )
    async def _test(self, ctx: SlashContext):
        embed = discord.Embed(title="embed test")
        await ctx.send(content="test", embeds=[embed])

    async def process_slash_command(self, ctx: SlashContext, f):
        for profile in profiles:
            if profile.guild == ctx.guild:
                mbox_ctx = MusicBoxContext(prefix='/', profile=profile, name=ctx.name,
                                   slash_context=ctx, message=ctx.message, args=ctx.args, kwargs=ctx.kwargs)
                if ctx.channel == profile.command_channel:
                    await ctx.send(content=COMMAND_CHANNEL_WARNING)
                    await f(mbox_ctx)
                    await ctx.message.delete()
                    return
                else:
                    await ctx.defer(hidden=True)
                    status = await f(mbox_ctx)
                break

        await ctx.send(content=f"{status}", hidden=True)

    @cog_ext.cog_slash(name="youtube",
                       guild_ids=GUILD_ID,
                       description='Add a youtube video to the queue.',
                       options=[
                           create_option(
                               name="search",
                               description="Name or link of a youtube video",
                               option_type=3,
                               required=True
                           )
                       ])
    async def _youtube(self, ctx: SlashContext, search):
        await self.process_slash_command(ctx, parse)

    @cog_ext.cog_slash(name="prev",
                       guild_ids=GUILD_ID,
                       description='Goes to the previous song.')
    async def _prev(self, ctx: SlashContext):
        await self.process_slash_command(ctx, handle.player_prev)

    @cog_ext.cog_slash(name="next",
                       guild_ids=GUILD_ID,
                       description='Goes to the next song.')
    async def _next(self, ctx: SlashContext):
        await self.process_slash_command(ctx, handle.player_next)

    @cog_ext.cog_slash(name="play",
                       description='Plays or resumes a song.',
                       guild_ids=GUILD_ID,
                       options=[
                           create_option(
                               name="song_name_or_link_or_index",
                               description="Adds this song to the queue.",
                               option_type=3,
                               required=False
                           )
                       ])
    async def _play(self, ctx: SlashContext, song_name_or_link_or_index=None):
        if song_name_or_link_or_index:
            if not song_name_or_link_or_index.isnumeric() :
                await self.process_slash_command(ctx, parse)
            elif song_name_or_link_or_index.isnumeric():
                await self.process_slash_command(ctx, handle.play_index)
        else:
            await self.process_slash_command(ctx, handle.resume_player)

    @cog_ext.cog_slash(name="pause",
                       description='Pauses actively playing song',
                       guild_ids=GUILD_ID,
                       )
    async def _pause(self, ctx: SlashContext):
        await self.process_slash_command(ctx, handle.pause_player)

    @cog_ext.cog_slash(name="shuffle",
                       guild_ids=GUILD_ID,
                       description='Randomizes the order of songs in the queue.')
    async def _shuffle(self, ctx: SlashContext):
        await self.process_slash_command(ctx, handle.shuffle_player)

    async def process_button(self, ctx: ComponentContext, f):
        for profile in profiles:
            if profile.guild == ctx.guild:
                mbox_ctx = MusicBoxContext(prefix='', profile=profile, name=ctx.custom_id,
                                   slash_context=None, message=None, args=None, kwargs=None)
                await f(mbox_ctx)
                await ctx.edit_origin()
   
    @cog_ext.cog_component()
    async def prev_button(self, ctx: ComponentContext):
        await self.process_button(ctx, handle.player_prev)

    @cog_ext.cog_component()
    async def play_pause_button(self, ctx: ComponentContext):
        await self.process_button(ctx, handle.play_pause)

    @cog_ext.cog_component()
    async def next_button(self, ctx: ComponentContext):
        await self.process_button(ctx, handle.player_next)

    @cog_ext.cog_component()
    async def volume_down_button(self, ctx: ComponentContext):
        await self.process_button(ctx, handle.lower_volume)

    @cog_ext.cog_component()
    async def volume_up_button(self, ctx: ComponentContext):
        await self.process_button(ctx, handle.raise_volume)
        
def setup(bot):
    bot.add_cog(MusicController(bot))
