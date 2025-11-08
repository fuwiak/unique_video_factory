# Reel Video Uniquization Details

- Source: `reel_video.mp4`
- Output: `reel_video_uniquized.mp4`
- Processing date: 2025-11-08

## Applied adjustments
- Trimmed 2 seconds from the start (`-ss 2`)
- Increased playback speed by 5% (`setpts=PTS/1.05`, `atempo=1.05`)
- Applied 5% crop with upscale for slight zoom (`crop=iw*0.95:ih*0.95` + `scale`)
- Enhanced contrast/saturation via `eq=contrast=1.15:saturation=1.1`
- Reduced audio loudness to 85% (`volume=0.85`)
- Re-encoded with new video bitrate 1.4 Mbit/s (`-b:v 1.4M`, `-maxrate 1.4M`, `-bufsize 2.8M`)
- Video codec: `libx264`, Audio codec: `aac 128k`

Command used:
```bash
ffmpeg -y -ss 2 -i reel_video.mp4 \
  -filter_complex "[0:v]crop=iw*0.95:ih*0.95,scale=trunc(iw/0.95/2)*2:trunc(ih/0.95/2)*2,eq=contrast=1.15:saturation=1.1,setpts=PTS/1.05[v];[0:a]volume=0.85,atempo=1.05[a]" \
  -map "[v]" -map "[a]" -c:v libx264 -preset medium \
  -b:v 1.4M -maxrate 1.4M -bufsize 2.8M \
  -c:a aac -b:a 128k reel_video_uniquized.mp4
```
