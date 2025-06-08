# oscv

**oscv** turns your Linux terminal into a real-time stereo waveform visualizer


## Features

- Live stereo waveform display (L/R channel separation)
- Pulls audio from your system's monitor source
- Color-coded waveform for left/right/overlap

## Quick Start

Requirements: Python 3.7+, `pactl`, `sounddevice`, `blessed`, `numpy`

```bash
git clone https://github.com/yourusername/oscv
cd oscv
python3 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
python oscv.py
