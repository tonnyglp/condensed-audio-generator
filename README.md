# Condensed Audio Generator

> **Turn any YouTube casual talks (a.k.a Just Chatting) into dense, pause‑free audio for immersion practice — no subtitles required.**

---

## ✨  Why I built this

I’m learning Japanese through **passive immersion**, which means listening to spoken content while doing something else (e.g., walking, commuting, cooking).  
This works well, but casual talks are full of long pauses and back‑channel noises, so the “language input per minute” is low. A **condensed audio** version — speech only, no silence — makes every minute count.

Existing tools such as **subs2cia** can trim silence **but rely on subtitles** to locate speech. Casual YouTube chats rarely come with accurate captions.

**Condensed Audio Generator** solves the problem automatically:

* downloads a video’s audio,
* detects speech even over background music,
* removes every non‑speech gap,
* exports a smooth, evenly‑paced track you can play on any device.

No subtitles, no manual marking.

---

## ⚙️  Features

* **Subtitle‑free VAD** – Silero voice‑activity detection keeps words, skips silence/BGM  
* **Full‑band quality** – cuts the original 48 kHz stream; no high‑end loss  
* **Custom padding & breathing gaps** – avoids clipping consonants, keeps a natural rhythm  
* **EBU‑R128 loudness normalisation** – constant volume across chunks  
* **One‑command CLI** ↓  

```bash
python condense.py <VIDEO_URL>
```

* Output formats: **MP3 192 kb/s** (default), Opus, FLAC, WAV  
* Runs on CPU; GPU (CUDA) optional for faster processing  

---

## 🚀  Quick‑start

### 1. Clone the repo

```bash
git clone https://github.com/tonnyglp/condensed-audio-generator.git
cd condensed-audio-generator
```

### 2. Create & activate a virtual environment

| Platform | Create venv | **Activate** |
|----------|-------------|--------------|
| **macOS / Linux (bash/zsh)** | `python3 -m venv .venv` | `source .venv/bin/activate` |
| **Windows – PowerShell** | `python -m venv .venv` | `.venv\Scripts\Activate.ps1` |
| **Windows – cmd.exe** | `python -m venv .venv` | `.venv\Scripts\activate.bat` |

If PowerShell’s execution policy blocks the script, run `Set‑ExecutionPolicy -Scope Process RemoteSigned` once in the same window.

> **System requirement:** python3 and python3-venv must be installed and available on your `PATH`.

### 3. Install dependencies

Upgrade `pip`:

```bash
python -m pip install -U pip
```

For dependencies, a `requirements.txt` is provided.

```bash
pip install -r requirements.txt
```

> **System requirement:** FFmpeg (≥ 4.4) must be installed separately and available on your `PATH`.

*(If you prefer a minimal install, see the “Dependencies” section below.)*

### 4. Generate condensed audio

```bash
python condense.py <VIDEO_URL>
```

The finished file appears in `output/`:

```
output/
└── d853dc6cc29d4186bfd58355dce58fd1_dense.mp3
```

### Optional: when you’re done, leave the venv

```bash
deactivate
```

---

## 🔄 Next‑time (everyday) usage

Once you’ve cloned the repo, set up the venv, and installed the requirements, future runs are just three short commands.

```text
# 1. Open a terminal / PowerShell / cmd and cd into the repo:
cd condensed-audio-generator

# 2. Activate the virtual environment:
macOS / Linux  :  source .venv/bin/activate
Windows (PS)   :  .venv\Scripts\Activate.ps1
Windows (cmd)  :  .venv\Scripts\activate.bat

# 3. Run the tool with any options you like:
python condense.py <VIDEO_URL> [--format mp3|opus|flac|wav] [--pad 200] …

# Optional: when you’re done, leave the venv
deactivate
```

That’s all—you’re ready to create dense, pause‑free audio whenever you want, with no additional setup.

---

## 📦  Dependencies

| Package | Why | Tested version |
|---------|-----|----------------|
| **yt‑dlp** | Download best‑quality audio | 2025.03.31 |
| **torch 2.2.0 + torchaudio** | backend for Silero‑VAD | 2.2.0 |
| **silero‑vad** | light‑weight JIT VAD model | 5.1.2 |
| **pydub** & **ffmpeg** | slicing, encoding | pydub 0.25.1 • ffmpeg 6.1.1 |
| **soundfile, numpy\<2** | reading WAV, array ops | 0.13.1 • 1.26.4 |

> **Note:** PyTorch ≤ 2.2 wheels expect **NumPy 1.x**, so the requirements file pins `numpy<2` to avoid ABI errors.

---

## 📄  Usage

```text
usage: condense.py URL [--outdir DIR] [--format {mp3,opus,flac,wav}]
                       [--merge GAP] [--pad MS] [--gap MS]

positional arguments:
  URL                   YouTube link

options:
  --outdir DIR          destination folder (default: output/)
  --format …            mp3 | opus | flac | wav  (default: mp3)
  --merge GAP           merge segments ≤ GAP (s) apart (default: 1.0)
  --pad MS              pad each kept chunk (ms)   (default: 250)
  --gap MS              silence inserted between chunks (default: 0)
```

---

## 🏗️  How it works

1. **yt‑dlp** downloads best audio → `original.wav` (48 kHz stereo)  
2. **ffmpeg** makes a mono 16 kHz copy for VAD  
3. **Silero‑VAD** finds speech frames → `[start, end]` intervals  
4. Intervals are **padded** ± `--pad` ms & **merged** if closer than `--merge` s  
5. **pydub** slices the *original* 48 kHz file, inserts `--gap` ms silence between pieces  
6. **ffmpeg** applies EBU‑R128 `loudnorm` and encodes (MP3, Opus…)  

---

## 🗺️  Roadmap / TODO

* Keep original YouTube title for the output filename ✅  
* Confirmed support for multiple languages (Japanese, Chinese, English, …) ✅  
* Add fade‑in/out to remove clicks  
* Performance improvement (target: 2 min for 2 h video)  

PRs and ideas are very welcome.

---

## 🙏  Acknowledgements

* **Silero** – multilingual VAD model  
* **yt‑dlp** – robust YouTube extraction  
* **FFmpeg** & **PyDub** – the audio workhorses  
* Inspiration from **subs2cia**

---

## ⚠️  Disclaimer

Downloading YouTube content may violate YouTube’s Terms of Service in your
jurisdiction. This tool is provided **for personal study only**; you are
responsible for ensuring you have the right to download and process any media.

---

> © 2025 Maintained by [**@tonnyglp**](https://github.com/tonnyglp)
