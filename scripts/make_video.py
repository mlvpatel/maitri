"""Build a three minute submission video for Maitri.

Pipeline:
  1. Generate AI narration with edge-tts as a single MP3.
  2. Build slide images (PNG) for each scene with PIL.
  3. Pair each slide with its narration timing.
  4. Compose to MP4 with burned-in subtitles using ffmpeg via imageio-ffmpeg.

Output: assets/maitri_demo_video.mp4 at 1920x1080.

No emojis, no decorative symbols, plain prose on every slide.
"""

from __future__ import annotations

import asyncio
import shutil
import subprocess
import tempfile
import wave
from dataclasses import dataclass
from pathlib import Path

import edge_tts
import imageio_ffmpeg
from PIL import Image, ImageDraw, ImageFont


ROOT = Path(__file__).resolve().parents[1]
ASSETS = ROOT / "assets"
OUT = ASSETS / "maitri_demo_video.mp4"
OUT_VTT = ASSETS / "maitri_demo_video.vtt"
OUT_SRT = ASSETS / "maitri_demo_video.srt"

W, H = 1920, 1080

# Voice options at https://learn.microsoft.com/en-us/azure/cognitive-services/speech-service/language-support
VOICE = "en-IN-NeerjaNeural"

GREEN_DARK = (15, 74, 58)
GREEN_LIGHT = (27, 122, 62)
RED = (176, 0, 32)
AMBER = (176, 124, 0)
WHITE = (255, 255, 255)
SOFT = (220, 235, 226)
INK = (12, 28, 22)
BG = (250, 252, 250)


@dataclass
class Scene:
    seconds: float
    headline: str
    body: list[str]
    narration: str
    palette: str = "green"  # green | red | white


SCRIPT: list[Scene] = [
    Scene(
        seconds=8.0,
        headline="One woman every two minutes",
        body=[
            "In 2023 roughly two hundred and sixty thousand women",
            "died from causes related to pregnancy.",
        ],
        narration=(
            "In 2023, roughly two hundred and sixty thousand women died from causes related to pregnancy. "
            "One woman every two minutes."
        ),
        palette="red",
    ),
    Scene(
        seconds=10.0,
        headline="Saharsa district, Bihar",
        body=[
            "Nearest functioning maternal care facility,",
            "often fifteen kilometres from the woman.",
            "Frontline is a community health worker",
            "with a paper card and a low end phone.",
        ],
        narration=(
            "In places like Saharsa district in Bihar, the nearest maternal care facility is often fifteen "
            "kilometres away. The frontline is a community health worker with a paper card and a low end phone."
        ),
        palette="green",
    ),
    Scene(
        seconds=8.0,
        headline="Maitri",
        body=[
            "Seven Gemma 4 agents.",
            "An independent verifier rejects unsupported claims",
            "before they ever reach the field.",
        ],
        narration=(
            "Maitri is a seven agent maternal triage system built on Gemma 4. "
            "An independent verifier rejects unsupported claims before they ever reach the field."
        ),
        palette="green",
    ),
    Scene(
        seconds=14.0,
        headline="The Specialist drafts a risk assessment",
        body=[
            "Tier red. Severe pre eclampsia.",
            "Four cited claims with evidence chunk identifiers.",
            "One of them is a precise drug dose number.",
        ],
        narration=(
            "The Specialist agent drafts a risk assessment with cited claims. "
            "Tier red, severe pre eclampsia. One claim states an exact intravenous magnesium sulphate dose. "
            "The evidence does not support that number."
        ),
        palette="white",
    ),
    Scene(
        seconds=12.0,
        headline="Verifier rejected the draft",
        body=[
            "Unsupported claim caught.",
            "The system stops.",
            "An Optimizer writes a short rewrite directive.",
        ],
        narration=(
            "The independent Verifier catches the unsupported claim. The system stops. "
            "The Optimizer writes a short rewrite directive."
        ),
        palette="red",
    ),
    Scene(
        seconds=14.0,
        headline="Rewrite, re verify, accept",
        body=[
            "The Specialist runs again.",
            "The second draft is accepted by the Verifier.",
            "Only verified claims move forward.",
        ],
        narration=(
            "The Specialist runs again with the optimizer's hint. The second draft passes the Verifier. "
            "Only verified claims move forward."
        ),
        palette="green",
    ),
    Scene(
        seconds=14.0,
        headline="Safe referral packet",
        body=[
            "Saharsa District Hospital.",
            "Open, capable of obstetric surgery, ambulance available.",
            "Not the closer primary health centre.",
            "That one does not have the capability this case needs.",
        ],
        narration=(
            "The Referral and Facility agent picks Saharsa District Hospital. It is open, has obstetric "
            "surgery, and dispatches ambulances. The closer primary health centre is skipped because "
            "it does not have the capability this case needs."
        ),
        palette="green",
    ),
    Scene(
        seconds=14.0,
        headline="Three outputs in two languages",
        body=[
            "Clinical card for the community health worker.",
            "Warm message for the mother in Hindi.",
            "Separate message for the household decision maker.",
        ],
        narration=(
            "The Formatter produces a clinical card for the community health worker in English, a warm "
            "message for the mother in Hindi, and a separate message for the household decision maker, "
            "naming the cash transfer scheme she is eligible for."
        ),
        palette="green",
    ),
    Scene(
        seconds=12.0,
        headline="Every call is in an append only audit log",
        body=[
            "Eight audit calls per hero case.",
            "Per agent latency. Prompt versions. Evidence chunk identifiers.",
            "All readable as a JSON Lines artifact.",
        ],
        narration=(
            "Every model call is logged to an append only audit trail with per agent latency and the exact "
            "evidence chunks the model saw."
        ),
        palette="white",
    ),
    Scene(
        seconds=12.0,
        headline="Measured results",
        body=[
            "Verifier precision one, recall one, F1 one on the adversarial set.",
            "Nine of nine deterministic safety rule tests passing.",
            "Apache two license on code. Public live demo. Public repository.",
        ],
        narration=(
            "On a hand crafted adversarial set the verifier achieves precision one and recall one. "
            "The deterministic safety rule block passes its full unit suite. The code is Apache two licensed, "
            "the live demo is public, the repository is public."
        ),
        palette="green",
    ),
    Scene(
        seconds=8.0,
        headline="Maitri",
        body=[
            "A safety verified Gemma 4 maternal referral co pilot",
            "for the woman who cannot wait.",
        ],
        narration=(
            "Maitri. A safety verified Gemma 4 maternal referral co pilot for the woman who cannot wait."
        ),
        palette="green",
    ),
]


def _load_font(size: int, bold: bool = False) -> ImageFont.FreeTypeFont:
    candidates = [
        "/System/Library/Fonts/Supplemental/Arial Bold.ttf" if bold else "/System/Library/Fonts/Supplemental/Arial.ttf",
        "/System/Library/Fonts/HelveticaNeue.ttc",
        "/Library/Fonts/Arial.ttf",
    ]
    for path in candidates:
        try:
            return ImageFont.truetype(path, size=size)
        except OSError:
            continue
    return ImageFont.load_default()


def _gradient(size: tuple[int, int], left: tuple, right: tuple) -> Image.Image:
    w, h = size
    base = Image.new("RGB", (w, h), left)
    px = base.load()
    for x in range(w):
        t = x / max(w - 1, 1)
        r = int(left[0] + (right[0] - left[0]) * t)
        g = int(left[1] + (right[1] - left[1]) * t)
        b = int(left[2] + (right[2] - left[2]) * t)
        for y in range(h):
            px[x, y] = (r, g, b)
    return base


def render_scene(scene: Scene) -> Image.Image:
    palette = scene.palette
    if palette == "white":
        img = Image.new("RGB", (W, H), BG)
        title_color = INK
        body_color = (60, 70, 65)
    elif palette == "red":
        img = _gradient((W, H), (140, 0, 24), (200, 32, 64))
        title_color = WHITE
        body_color = SOFT
    else:
        img = _gradient((W, H), GREEN_DARK, GREEN_LIGHT)
        title_color = WHITE
        body_color = SOFT

    draw = ImageDraw.Draw(img)
    title_font = _load_font(96, bold=True)
    body_font = _load_font(54)
    brand_font = _load_font(28)

    # Brand at top right.
    draw.text((W - 220, 36), "MAITRI", font=brand_font, fill=title_color)

    draw.text((120, 220), scene.headline, font=title_font, fill=title_color)

    y = 380
    for line in scene.body:
        draw.text((120, y), line, font=body_font, fill=body_color)
        y += 78

    # Footer bar
    draw.rectangle((0, H - 8, W, H), fill=GREEN_LIGHT)
    return img


async def _synth_voice(text: str, out_path: Path) -> None:
    comm = edge_tts.Communicate(text, VOICE, rate="-2%")
    await comm.save(str(out_path))


def _audio_duration_seconds(path: Path) -> float:
    """Use ffprobe via imageio's ffmpeg to read duration without separate ffprobe binary."""
    ffmpeg_bin = imageio_ffmpeg.get_ffmpeg_exe()
    # ffmpeg writes duration on stderr; capture it
    out = subprocess.run(
        [ffmpeg_bin, "-i", str(path)],
        capture_output=True,
        text=True,
    )
    for line in out.stderr.splitlines():
        if "Duration:" in line:
            # Duration: 00:00:08.40, start: 0.000000, bitrate: ...
            ts = line.split("Duration:")[1].split(",")[0].strip()
            h, m, s = ts.split(":")
            return int(h) * 3600 + int(m) * 60 + float(s)
    raise RuntimeError(f"could not read audio duration: {path}")


def _format_srt_time(seconds: float) -> str:
    h = int(seconds // 3600)
    m = int((seconds % 3600) // 60)
    s = int(seconds % 60)
    ms = int(round((seconds - int(seconds)) * 1000))
    return f"{h:02d}:{m:02d}:{s:02d},{ms:03d}"


def write_srt(scene_times: list[tuple[Scene, float, float]], path: Path) -> None:
    lines: list[str] = []
    for i, (scene, start, end) in enumerate(scene_times, start=1):
        lines.append(str(i))
        lines.append(f"{_format_srt_time(start)} --> {_format_srt_time(end)}")
        wrapped = scene.narration
        lines.append(wrapped)
        lines.append("")
    path.write_text("\n".join(lines), encoding="utf-8")


def main() -> None:
    ASSETS.mkdir(parents=True, exist_ok=True)
    with tempfile.TemporaryDirectory() as tmp:
        tmp_path = Path(tmp)
        slides_dir = tmp_path / "slides"
        audio_dir = tmp_path / "audio"
        slides_dir.mkdir()
        audio_dir.mkdir()

        # Render slides and synthesize audio per scene.
        scene_times: list[tuple[Scene, float, float]] = []
        scene_audio_files: list[Path] = []
        per_scene_durations: list[float] = []
        t0 = 0.0
        for idx, scene in enumerate(SCRIPT):
            img = render_scene(scene)
            slide_path = slides_dir / f"scene_{idx:02d}.png"
            img.save(slide_path, "PNG")

            audio_path = audio_dir / f"scene_{idx:02d}.mp3"
            asyncio.run(_synth_voice(scene.narration, audio_path))
            dur = _audio_duration_seconds(audio_path)
            # Add a small tail of silence
            dur_with_pad = dur + 0.8
            scene_times.append((scene, t0, t0 + dur_with_pad))
            t0 += dur_with_pad
            scene_audio_files.append(audio_path)
            per_scene_durations.append(dur_with_pad)
            print(f"scene {idx}: {dur:.2f}s narration, {dur_with_pad:.2f}s total")

        # Build per scene video segments at the right duration.
        ffmpeg_bin = imageio_ffmpeg.get_ffmpeg_exe()
        segments: list[Path] = []
        for idx, (audio_path, dur) in enumerate(zip(scene_audio_files, per_scene_durations, strict=False)):
            slide_path = slides_dir / f"scene_{idx:02d}.png"
            seg_path = tmp_path / f"seg_{idx:02d}.mp4"
            subprocess.run(
                [
                    ffmpeg_bin, "-y",
                    "-loop", "1", "-t", f"{dur:.3f}", "-i", str(slide_path),
                    "-i", str(audio_path),
                    "-af", "apad=pad_dur=0.8",
                    "-shortest",
                    "-c:v", "libx264", "-pix_fmt", "yuv420p",
                    "-r", "24",
                    "-c:a", "aac", "-b:a", "192k",
                    str(seg_path),
                ],
                check=True,
                stdout=subprocess.DEVNULL,
                stderr=subprocess.DEVNULL,
            )
            segments.append(seg_path)

        # Concatenate segments using the concat demuxer.
        list_file = tmp_path / "concat.txt"
        list_file.write_text("\n".join(f"file '{p}'" for p in segments), encoding="utf-8")
        concat_mp4 = tmp_path / "concat.mp4"
        subprocess.run(
            [ffmpeg_bin, "-y", "-f", "concat", "-safe", "0", "-i", str(list_file),
             "-c", "copy", str(concat_mp4)],
            check=True,
            stdout=subprocess.DEVNULL,
            stderr=subprocess.DEVNULL,
        )

        # Subtitle file
        write_srt(scene_times, OUT_SRT)

        # Burn subtitles into the concat video and write the final file.
        subprocess.run(
            [ffmpeg_bin, "-y", "-i", str(concat_mp4),
             "-vf", f"subtitles={OUT_SRT}:force_style='FontName=Arial,FontSize=20,PrimaryColour=&H00FFFFFF&,OutlineColour=&H00000000&,BorderStyle=3,Outline=2,Shadow=0,Alignment=2,MarginV=70'",
             "-c:v", "libx264", "-pix_fmt", "yuv420p",
             "-c:a", "copy",
             str(OUT)],
            check=True,
        )

    total = t0
    print(f"video written: {OUT}  total {total:.1f}s")
    if total > 180.0:
        print(f"WARNING: total length {total:.1f}s exceeds 180s limit")
    else:
        print(f"OK: under the 180s ceiling with {180.0 - total:.1f}s headroom")


if __name__ == "__main__":
    main()
