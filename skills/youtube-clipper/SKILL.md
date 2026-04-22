---
name: youtube-clipper
description: Download highest quality from YouTube, clip a time range, save to ~/Desktop/Clips with working audio.
metadata:
  openclaw:
    emoji: "✂️"
    requires:
      bins: ["yt-dlp", "ffmpeg"]
    install:
      - id: brew-ffmpeg
        kind: brew
        formula: ffmpeg
        bins: [ffmpeg]
        label: Install ffmpeg (brew)
      - id: brew-ytdlp
        kind: brew
        formula: yt-dlp
        bins: [yt-dlp]
        label: Install yt-dlp (brew)
      - id: apt-ffmpeg
        kind: apt
        package: ffmpeg
        bins: [ffmpeg]
        label: Install ffmpeg (apt)
      - id: apt-ytdlp
        kind: apt
        package: yt-dlp
        bins: [yt-dlp]
        label: Install yt-dlp (apt)
---

# youtube-clipper

1. Download highest quality video (best video + audio)
2. Clip the requested time range
3. Save to `~/Desktop/Clips`

## How to ask

**You give timestamps:** URL + start + end + optional name.

> Clip https://youtu.be/VIDEO_ID from 0:00 to 1:12, name it holloway-1

**Or describe the moment:** URL + what happens in the clip + optional length (~20s default). I'll propose timestamps; you can say "earlier/later" and we refine.

## Run

```bash
{baseDir}/youtube-clipper.sh --url "https://youtu.be/VIDEO_ID" --start 0 --end 72 [--name "myclip"]
```

Times: seconds (`72`) or `HH:MM:SS`. Output: `~/Desktop/Clips/<name>.mp4`. Omit `--name` to use the video title.
