# Discord Music Player Bot

A high-performance, asynchronous Discord music bot built with **Discord.py** and **yt-dlp**. This bot enables seamless high-quality audio streaming from YouTube directly into voice channels, featuring a robust queuing system and playlist integration.



## Key Features

* **Dynamic Queuing:** Implements a `deque` (Double-Ended Queue) for $O(1)$ performance when managing song transitions and additions.
* **Intelligent Search:** Supports direct YouTube URLs and natural language search queries using `yt-dlp`'s extraction engine.
* **Playlist Integration:** Recursively parses YouTube playlists to batch-add tracks to the active session.
* **Non-Blocking I/O:** Utilizes `asyncio` to ensure the bot remains responsive to commands while processing heavy audio streams in the background.
* **Playback Controls:** Includes standard media commands: `!play`, `!skip`, `!queue`, `!stop`, and `!leave`.

## Tech Stack

* **Wrapper:** [Discord.py](https://discordpy.readthedocs.io/)
* **Audio Processing:** [FFmpeg](https://ffmpeg.org/) (Opus Codec)
* **Data Extraction:** [yt-dlp](https://github.com/yt-dlp/yt-dlp)
* **Concurrency:** Python `asyncio` & `threading`

