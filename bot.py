import discord
from discord.ext import tasks, commands
import aiohttp
import datetime
import json
import os
from typing import Dict, Optional

# Configuration
CHANNEL_ID = 1377675550575038498  # Replace with your Discord channel ID
CHECK_INTERVAL = 7200  # 2 hours in seconds
DATA_FILE = "last_videos.json"  # Stores last video IDs

# YouTube Channels (Updated July 2024)
CHANNELS = {
    "JEE Wallah": {
        "id": "UCBqXtwVwSnY8STBZz0TZ0Eg",  # @PW-JEEWallah
        "color": 0x00A67C,  # Green
        "thumbnail": "https://i.ytimg.com/vi/{video_id}/maxresdefault.jpg"
    },
    "Lakshya JEE": {
        "id": "UCBqXtwVwSnY8STBZz0TZ0Eg",  # @PW-LakshyaJEE (verify ID)
        "color": 0x3498DB,  # Blue
        "thumbnail": "https://i.ytimg.com/vi/{video_id}/hqdefault.jpg"
    },
    "Arjuna JEE": {
        "id": "UCBqXtwVwSnY8STBZz0TZ0Eg",  # @PW-ArjunaJEE (verify ID)
        "color": 0xE74C3C,  # Red
        "thumbnail": "https://i.ytimg.com/vi/{video_id}/hqdefault.jpg"
    }
}

# Initialize bot
intents = discord.Intents.default()
bot = commands.Bot(command_prefix="!", intents=intents)

async def get_latest_video(channel_id: str) -> Optional[Dict]:
    """Fetches latest video for a channel using YouTube API"""
    API_KEY = os.getenv("YOUTUBE_API_KEY")
    url = f"https://www.googleapis.com/youtube/v3/search?key={API_KEY}&channelId={channel_id}&part=snippet,id&order=date&maxResults=1"
    
    async with aiohttp.ClientSession() as session:
        async with session.get(url) as resp:
            if resp.status == 200:
                data = await resp.json()
                if data.get('items'):
                    video = data['items'][0]
                    return {
                        'id': video['id']['videoId'],
                        'title': video['snippet']['title'],
                        'url': f"https://youtu.be/{video['id']['videoId']}",
                        'published': video['snippet']['publishedAt']
                    }
    return None

def load_last_videos() -> Dict[str, str]:
    """Loads last posted video IDs"""
    if os.path.exists(DATA_FILE):
        with open(DATA_FILE, 'r') as f:
            return json.load(f)
    return {}

def save_last_videos(videos: Dict[str, str]):
    """Saves last posted video IDs"""
    with open(DATA_FILE, 'w') as f:
        json.dump(videos, f)

@tasks.loop(seconds=CHECK_INTERVAL)
async def check_new_videos():
    channel = bot.get_channel(CHANNEL_ID)
    if not channel:
        return

    last_videos = load_last_videos()
    new_videos = {}

    try:
        for name, config in CHANNELS.items():
            video = await get_latest_video(config['id'])
            if not video:
                continue

            # Skip if already posted
            if last_videos.get(name) == video['id']:
                new_videos[name] = video['id']
                continue

            # Create embed
            embed = discord.Embed(
                title=f"📢 New {name} Video!",
                description=f"[{video['title']}]({video['url']})",
                color=config['color'],
                timestamp=datetime.datetime.fromisoformat(video['published'].replace('Z', ''))
            embed.set_thumbnail(url=config['thumbnail'].format(video_id=video['id']))
            embed.set_footer(text=f"{name} | Uploaded")
            
            await channel.send(embed=embed)
            new_videos[name] = video['id']
            print(f"Posted new {name} video: {video['title']}")

        save_last_videos(new_videos)

    except Exception as e:
        print(f"Error: {e}")

@bot.event
async def on_ready():
    print(f'Bot connected as {bot.user.name} (ID: {bot.user.id})')
    check_new_videos.start()

# Start bot
bot.run(os.getenv('MTM3NzY4ODk2NzEwMDYyOTAwMg.Gzjk23.kdD27-QxOYBo2T3WHibo5u5ca62bAnjEiNqSL0'))
