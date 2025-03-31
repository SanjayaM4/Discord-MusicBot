import discord
from discord.ext import commands
import yt_dlp
import asyncio
from collections import deque

intents = discord.Intents.all()
bot = commands.Bot(command_prefix='!', intents=intents)

song_queue = deque()

# Function to play the next song from the queue
def play_next(ctx):
    if song_queue:
        next_url, next_title = song_queue.popleft()
        voice_client = ctx.voice_client
        source = discord.FFmpegOpusAudio(next_url)
        voice_client.play(source, after=lambda e: play_next(ctx))
        asyncio.run_coroutine_threadsafe(ctx.send(f'Now playing: **{next_title}**'), bot.loop)

@bot.event
async def on_ready():
    print(f'Logged in as {bot.user}')

@bot.command(name='join')
async def join(ctx):
    voice_channel = ctx.author.voice.channel
    if not voice_channel:
        await ctx.send("You must be in a voice channel to use this command!")
        return

    if ctx.voice_client is None:
        await voice_channel.connect()
        await ctx.send(f"Joined {voice_channel.name}!")
    else:
        await ctx.send("I'm already connected to a voice channel!")

@bot.command(name='play')
async def play(ctx, *, query: str):
    voice_client = ctx.voice_client

    # Join the voice channel if not already connected
    if not voice_client:
        if ctx.author.voice:
            channel = ctx.author.voice.channel
            voice_client = await channel.connect()
        else:
            await ctx.send("You must be in a voice channel to summon me.")
            return

    ydl_opts = {
        'format': 'bestaudio/best',
        'noplaylist': True,
        'quiet': True,
        'extract_flat': False,
        'outtmpl': 'song.%(ext)s',
        'postprocessors': [{
            'key': 'FFmpegExtractAudio',
            'preferredcodec': 'mp3',
            'preferredquality': '192',
        }],
    }

    try:
        with yt_dlp.YoutubeDL(ydl_opts) as ydl:
            # If the query starts with a URL (playlist or single video), extract info
            if query.startswith("http"):
                info = ydl.extract_info(query, download=False)
                
                # Check if it's a playlist
                if 'entries' in info:  # If it's a playlist
                    for entry in info['entries']:
                        title = entry.get('title', 'Unknown Title')
                        url = entry['url']
                        song_queue.append((url, title))
                    await ctx.send(f"Added **{len(info['entries'])}** songs to the queue.")
                    if not voice_client.is_playing():
                        play_next(ctx)
                else:  # If it's a single video
                    audio_url = info['url']
                    title = info.get('title', 'Unknown Title')

                    # If a song is already playing, add to the queue
                    if voice_client.is_playing():
                        song_queue.append((audio_url, title))
                        await ctx.send(f'Queued: **{title}**')
                    else:
                        source = discord.FFmpegOpusAudio(audio_url)
                        voice_client.play(source, after=lambda e: play_next(ctx))
                        await ctx.send(f'Now playing: **{title}**')

            else:  # If it's a search query
                info = ydl.extract_info(f"ytsearch:{query}", download=False)['entries'][0]
                audio_url = info['url']
                title = info.get('title', 'Unknown Title')

                # If a song is already playing, add to the queue
                if voice_client.is_playing():
                    song_queue.append((audio_url, title))
                    await ctx.send(f'Queued: **{title}**')
                else:
                    source = discord.FFmpegOpusAudio(audio_url)
                    voice_client.play(source, after=lambda e: play_next(ctx))
                    await ctx.send(f'Now playing: **{title}**')

    except Exception as e:
        await ctx.send(f"Error while playing audio: {str(e)}")

@bot.command(name='queue')
async def show_queue(ctx):
    if song_queue:
        queue_list = "\n".join([f"{i + 1}. {title}" for i, (_, title) in enumerate(song_queue)])
        await ctx.send(f"**Current Queue:**\n{queue_list}")
    else:
        await ctx.send("The queue is empty.")

@bot.command(name='skip')
async def skip(ctx):
    voice_client = ctx.voice_client
    if voice_client and voice_client.is_playing():
        voice_client.stop()
        await ctx.send("Song skipped!")
    else:
        await ctx.send("No song is currently playing.")

@bot.command(name='stop')
async def stop(ctx):
    voice_client = ctx.voice_client
    if voice_client and voice_client.is_playing():
        voice_client.stop()
        song_queue.clear()
        await ctx.send("Playback stopped and queue cleared.")
    else:
        await ctx.send("I'm not currently playing any audio!")

@bot.command(name='leave')
async def leave(ctx):
    voice_client = ctx.voice_client
    if voice_client:
        song_queue.clear()
        await voice_client.disconnect()
        await ctx.send("Disconnected from the voice channel.")
    else:
        await ctx.send("I'm not connected to a voice channel!")



bot.run("token")

