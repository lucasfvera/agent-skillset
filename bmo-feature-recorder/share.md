# Hand off — email or message

Skip this file when destination is `local` or `pr`.

Mail and chat want **mp4**. From the clip directory:

```bash
ffmpeg -y -i "<slug>.webm" -c:v libx264 -pix_fmt yuv420p -movflags +faststart "<slug>.mp4"
```

If `ffmpeg` is missing, hand the webm and say mail may not play it.

Reply with:

- Absolute path to the file they should attach
- One-line caption (the feature in the user's words, tightened)

No zip unless they asked. Leave `.env`, passkeys, and the recorder off the attachment.

**Completion criterion:** the user has the attachable path and the caption.
