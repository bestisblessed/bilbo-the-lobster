# youtube-clipper

Download highest quality from a YouTube URL, clip a time range, save to `~/Desktop/Clips`.

## Setup

```bash
# macOS
brew install ffmpeg yt-dlp

# Linux
sudo apt install -y ffmpeg
pipx install yt-dlp
```

## Usage

```bash
./youtube-clipper.sh --url "https://youtu.be/VIDEO_ID" --start 0 --end 72 [--name "myclip"]
```

- **--url** — YouTube URL
- **--start** / **--end** — Time in seconds or HH:MM:SS
- **--name** — (optional) Output filename. Omit to use video title.

Output: `~/Desktop/Clips/<name>.mp4`
