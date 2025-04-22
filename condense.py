#!/usr/bin/env python3

import argparse, subprocess, tempfile, uuid, re, shutil
from pathlib import Path
from silero_vad import load_silero_vad, read_audio, get_speech_timestamps
from pydub import AudioSegment

# ---------------------------------------------------------------------
# Helper functions
# ---------------------------------------------------------------------

def download_audio(url: str, workdir: Path):
    """
    1. Grab the best native audio track (usually 48 kHz).
    2. Keep it as 'original.wav'.
    3. Create a 16 kHz mono copy ONLY for VAD ('original.16k.wav').
    4. Also return the video title & channel name
    """
    title, channel = get_video_meta(url)
    orig = workdir / "original.wav"
    cmd = [
        "yt-dlp", "-f", "bestaudio", "--extract-audio",
        "--audio-format", "wav", "--audio-quality", "0",
        "--output", str(orig), url]
    subprocess.check_call(cmd)

    vad_wav = orig.with_suffix(".16k.wav")
    subprocess.check_call(
        ["ffmpeg", "-y", "-i", str(orig),
         "-ac", "1", "-ar", "16000", str(vad_wav)],
        stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
    return orig, vad_wav, title, channel


def run_vad(wav_path: Path, threshold: float = 0.6, pad_ms: int = 0):
    """
    Returns a list of (start_sec, end_sec) speech intervals.
    """
    model = load_silero_vad()            # lightweight JIT (~2 MB)
    wav = read_audio(str(wav_path))      # torch.Tensor, 16 kHz mono
    timestamps = get_speech_timestamps(
        wav,
        model,
        threshold=threshold,
        speech_pad_ms=pad_ms,
        return_seconds=True)             # ← direct seconds, no div by 16 k
    return [(t['start'], t['end']) for t in timestamps]


def merge_intervals(segments, max_gap=1.0):
    """
    Merge speech segments with a gap ≤ max_gap seconds.
    """
    if not segments:
        return []

    merged = [list(segments[0])]
    for start, end in segments[1:]:
        prev_start, prev_end = merged[-1]
        if start - prev_end <= max_gap:
            merged[-1][1] = end  # extend
        else:
            merged.append([start, end])
    return merged


def cut_and_concatenate(wav_path: Path, segments, out_path: Path, gap_ms: int = 0):
    """
    Use pydub to cut & join, then export to WAV.
    """
    audio = AudioSegment.from_wav(wav_path)
    silence = AudioSegment.silent(duration=gap_ms)
    output = AudioSegment.empty()
    for i, (start, end) in enumerate(segments):
        output += audio[start * 1000 : end * 1000]
        if i < len(segments) - 1:         # don’t trail the last chunk
            output += silence
    output.export(out_path, format="wav")


def encode_final(wav_path: Path, out_path: Path, codec: str = "mp3"):
    """
    ffmpeg → MP3 (or Opus / FLAC / …)
    """
    codec_map = {
        "mp3":  ["-codec:a", "libmp3lame", "-b:a", "192k"],   # bump to 192 k
        "opus": ["-codec:a", "libopus", "-b:a", "160k", "-application", "audio"],
        "flac": ["-codec:a", "flac"],
        "wav":  [],
    }
    args = codec_map.get(codec, [])
    cmd = ["ffmpeg", "-y", "-i", str(wav_path),
           "-af", "loudnorm=i=-16:tp=-1.5:lra=11",   # EBU‑R128
           *args, str(out_path)]
    subprocess.check_call(cmd, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)


def safe_filename(text: str, max_len: int = 100) -> str:
    """
    Replace characters that are forbidden on Windows/macOS/Linux with "_",
    collapse whitespace, and hard‑truncate to *max_len* UTF‑8 bytes.
    """
    text = re.sub(r'[\\/*?:"<>|]', "_", text)
    text = re.sub(r"\s+", " ", text).strip()
    return text.encode("utf‑8")[:max_len].decode("utf‑8", "ignore")


def get_video_meta(url: str) -> tuple[str, str]:
    """
    Return *(title, channel)* for *url* using yt‑dlp.
    """
    title   = subprocess.check_output(
        ["yt-dlp", "--no-playlist", "--get-title", url],
        text=True, stderr=subprocess.DEVNULL).strip()
    channel = subprocess.check_output(
        ["yt-dlp", "--no-playlist", "--print", "uploader", url],
        text=True, stderr=subprocess.DEVNULL).strip()
    return safe_filename(title), safe_filename(channel)


# ---------------------------------------------------------------------
# Main
# ---------------------------------------------------------------------

def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("url", help="YouTube URL")
    ap.add_argument("--outdir", default="output", help="directory for final files")
    ap.add_argument("--merge", type=float, default=1.0,
                    help="max gap (s) between segments to merge")
    ap.add_argument("--format", default="mp3",
                    choices=["mp3", "opus", "flac", "wav"],
                    help="output audio format")
    ap.add_argument("--pad", type=int, default=250,
                    help="padding in ms added before and after each speech chunk")
    ap.add_argument("--gap", type=int, default=0,
                    help="silence (ms) inserted between chunks")

    args = ap.parse_args()

    outdir = Path(args.outdir)
    outdir.mkdir(parents=True, exist_ok=True)

    tmp = Path(tempfile.mkdtemp())
    base = uuid.uuid4().hex
    raw_wav = tmp / f"{base}.wav"

    print("▶  Downloading & converting …")
    orig_wav, vad_wav, vid_title, vid_channel = download_audio(args.url, tmp)

    print("▶  Running VAD …")
    segs = run_vad(vad_wav, threshold=0.6, pad_ms=args.pad)
    segs = merge_intervals(segs, args.merge)
    kept = sum(end - st for st, end in segs)
    print(f"   kept {kept:.1f}s of speech in {len(segs)} chunks")

    print("▶  Cutting & concatenating …")
    dense_wav = tmp / f"{base}_dense.wav"
    cut_and_concatenate(orig_wav, segs, dense_wav, gap_ms=args.gap)

    print("▶  Encoding final output …")
    stem  = f"{vid_title} by {vid_channel} (condensed)"
    final = outdir / f"{stem}.{args.format}"
    encode_final(dense_wav, final, args.format)

    print("✅  Done:", final.resolve())
    shutil.rmtree(tmp)  # Cleanup

if __name__ == "__main__":
    main()
