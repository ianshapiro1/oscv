# oscv

**oscv** turns your Linux terminal into an oscilloscope visualizer
- Live stereo waveform display using color coded L/R channel separation
- Auto-detects audio monitors on PipeWire/PulseAudio through `pactl`
- Lightweight with minimal dependencies

## Usage

Requirements:  
Linux with PipeWire or PulseAudio compatibility layer  
Python 3.7+, `pactl`, `blessed`, `numpy`

```bash
git clone https://github.com/ianshapiro1/oscv.git
cd oscv
python3 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
python oscv.py
```

## Contributing

This project is meant to be a fun learning experience about native Linux audio and terminal graphics.  

Contributions are welcome. If you have any additions or changes, open a PR!  
If you have an idea for a feature or encouter an error, please open an issue.

--- 
Some features I have been thinking about:

- Package manager integration
    - Add oscv to AUR, PyPI, Homebrew, etc.

- Settings file / CLI flags
    - Toggle waveform characters, colors, update rate, layout styles (mono, stacked, mirrored)

- Better source compatibility
    - Improve device fallback across distros and handle edge cases with JACK & ALSA users

- Clean code & modularization
    - Separate capture and visual logic, improve error handling & layout

- Aesthetics
    - Experimenting with data processing (waveform smoothing, peak envelopes, FFT, Lissajous stereo shapes)