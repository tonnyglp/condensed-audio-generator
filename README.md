# Condensed Audio Generator

> **Turn any Japanese YouTube conversation into dense, pause‑free audio for immersion practice — no subtitles required.**

[![Python](https://img.shields.io/badge/python-3.9%2B-blue.svg)](https://www.python.org/) [![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](#license) [![CI](https://img.shields.io/github/actions/workflow/status/tonnyglp/condensed-audio-generator/tests.yml?label=CI)](https://github.com/tonnyglp/condensed-audio-generator/actions)

---

## ✨  Why I built this

I’m learning Japanese through “immersion listening”.  
Existing tools such as **subs2cia** can trim silence **but rely on subtitles** to know where speech happens. Casual YouTube chats rarely come with accurate subs — and manual caption‑cleaning is tedious.

**Condensed Audio Generator** does the same job **automatically**:

* downloads a video’s audio,
* detects speech even over background music,
* chops out every non‑speech gap,
* exports a smooth, evenly‑paced track you can loop on your phone.

No subtitles, no hand‑marking.

---

## ⚙️  Features

* **Subtitle‑free VAD** – Silero voice‑activity detection keeps words, skips silence/BGM  
* **Full‑band quality** – cuts the original 48 kHz stream; no high‑end loss  
* **Custom padding & breathing gaps** – avoids clipping consonants, keeps natural rhythm  
* **EBU‑R128 loudness normalisation** – constant volume across all chunks  
* **One‑command CLI**:  

```bash
python condense.py https://youtu.be/VIDEO_ID
```

* Output formats: **MP3 192 kb/s** (default), Opus, FLAC, WAV  
* Works on CPU; GPU optional for faster runs  
* Clean **MIT** licence

---

## 🚀  Quick‑start

```bash
# 1. clone
git clone https://github.com/tonnyglp/condensed-audio-generator.git
cd condensed-audio-generator

# 2. create & activate venv
python3 -m venv .venv
source .venv/bin/activate
python -m pip install -U pip

# 3. install deps (NumPy 1.x for PyTorch 2.2 wheels)
pip install -r requirements.txt          # or: pip install yt-dlp torch torchaudio ...

# 4. generate condensed audio
python condense.py https://www.youtube.com/watch?v=dQw4w9WgXcQ
```

The result appears in `output/` with the **same title as the video**:

```
output/
└── 【日本語雑談】推し漫画とゲーム_dense.mp3
```

---

## 📄  Usage

```text
usage: condense.py URL [--outdir DIR] [--format {mp3,opus,flac,wav}]
                       [--merge GAP] [--pad MS] [--gap MS]

positional arguments:
  URL                   YouTube link

options:
  --outdir DIR          destination folder (default: output/)
  --format …            mp3 | opus | flac | wav  (default: mp3)
  --merge GAP           merge segments ≤ GAP s apart (default: 0.30)
  --pad MS              pad every kept chunk (ms)   (default: 80)
  --gap MS              silence inserted between chunks (default: 150)
```

### Example

```bash
# Podcast‑like pacing, Opus 160 kb/s
python condense.py https://youtu.be/abcdef --merge 0.4 --gap 250 --format opus
```

---

## 🏗️  How it works

1. **yt‑dlp** downloads best audio → `original.wav` (48 kHz stereo)  
2. **ffmpeg** makes a mono 16 kHz **copy** for VAD  
3. **Silero‑VAD** finds speech frames → `[start, end]` intervals  
4. Intervals are **padded** ± `--pad` ms & **merged** if closer than `--merge` s  
5. **pydub** slices the *original* 48 kHz file, inserts `--gap` ms silence between pieces  
6. **ffmpeg** applies EBU‑R128 `loudnorm` and encodes (MP3, Opus…)  

Total time: ~ 8 min for a 2 h chat on M2 Air (ARM‑CPU only).

---

## 🗺️  Roadmap / TODO

* [ ] **Keep original YouTube title** for output filename (done!)  
* [ ] 5 ms fade‑in/out to remove clicks  
* [ ] Performance: explore parallel chunk rendering to drop 2 h → 2 min  
* [ ] Interactive GUI (Streamlit)  
* [ ] Docker image & PyPI package  

Contributions welcome — see below!

---

## 🤝  Contributing

1. Fork & create a feature branch.  
2. Follow **black**, **isort**, **ruff** for linting.  
3. Run `pytest`.  
4. Open a PR; GitHub CI will run the tests.

Please file bugs or feature requests via **GitHub Issues**.

---

## 🙏  Acknowledgements

* **Silero team** for the tiny, multilingual VAD model  
* **yt‑dlp** community for robust YouTube extraction  
* **FFmpeg** & **PyDub** projects  
* Inspiration from **subs2cia**

---

## ⚠️  Disclaimer

Downloading YouTube content may violate YouTube’s Terms of Service in your
jurisdiction. This tool is provided **for personal‑use study only**; you are
responsible for ensuring you have the right to download and process any media.

---

## 📜  License

This project is released under the **MIT License**.  
See [`LICENSE`](LICENSE) for full text.

---

> 2025 · Maintained by [**@tonnyglp**](https://github.com/tonnyglp)
