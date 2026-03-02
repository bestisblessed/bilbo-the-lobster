---
name: clip
description: Download highest quality from YouTube, clip a time range, save to ~/Desktop/Clips with working audio.
metadata: {"openclaw": {"emoji": "✂️", "requires": {"bins": ["yt-dlp", "ffmpeg"]}, "install": [{"id": "brew-ffmpeg", "kind": "brew", "formula": "ffmpeg", "bins": ["ffmpeg"], "label": "Install ffmpeg (brew)"}, {"id": "brew-ytdlp", "kind": "brew", "formula": "yt-dlp", "bins": ["yt-dlp"], "label": "Install yt-dlp (brew)"}, {"id": "apt-ffmpeg", "kind": "apt", "package": "ffmpeg", "bins": ["ffmpeg"], "label": "Install ffmpeg (apt)"}, {"id": "apt-ytdlp", "kind": "apt", "package": "yt-dlp", "bins": ["yt-dlp"], "label": "Install yt-dlp (apt)"}], "user-invocable": true}}
---

# clip

Downloads highest quality video from YouTube, clips a time range, saves to ~/Desktop/Clips.

## Example

```
/clip https://www.youtube.com/watch?v=Tyej_V2ilZA 0:00 3:17 holloway-bmf-walkout
```

## How to ask

**Give timestamps:** URL + start + end + optional name.
> Clip https://youtu.be/VIDEO_ID from 0:00 to 1:12, name it myclip

## Run

```bash
{baseDir}/clip.sh --url "https://youtu.be/VIDEO_ID" --start 0 --end 72 [--name "myclip"]
```

Times: seconds (`72`) or `HH:MM:SS`. Output: `~/Desktop/Clips/<name>.mp4`.
