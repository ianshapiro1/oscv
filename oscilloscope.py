import sounddevice as sd
import numpy as np
from blessed import Terminal
import subprocess
import time
import sys

term = Terminal()
WIDTH, HEIGHT = term.width, term.height - 5

def get_monitor_device():
    default_sink = subprocess.check_output(
        ["pactl", "get-default-sink"], text=True
    ).strip()

    sources = subprocess.check_output(["pactl", "list", "sources"], text=True)

    monitor_name = None
    current_source = {}
    for line in sources.splitlines():
        line = line.strip()
        if line.startswith("Name:"):
            current_source["name"] = line.split(":", 1)[1].strip()
        elif line.startswith("Device Description:"):
            current_source["desc"] = line.split(":", 1)[1].strip()
            # Check if source is the monitor of default sink
            if current_source.get("name", "").endswith(".monitor") and default_sink in current_source.get("name", ""):
                monitor_name = current_source["name"]
                break

    return monitor_name

def normalize(samples, height):
    max_val = np.max(np.abs(samples))
    if max_val == 0:
        return np.zeros_like(samples, dtype=int)
    return ((samples / max_val + 1) / 2 * (height - 1)).astype(int)

def draw_waveform(stereo_frame):
    WIDTH, HEIGHT = term.width, term.height - 5
    stereo_frame = stereo_frame[:WIDTH]
    left, right = stereo_frame[:, 0], stereo_frame[:, 1]
    left_norm = normalize(left, HEIGHT)
    right_norm = normalize(right, HEIGHT)

    print(term.home + term.clear, end="")
    for y in range(HEIGHT - 1, -1, -1):
        line = ""
        for x in range(len(left_norm)):
            if left_norm[x] == y and right_norm[x] == y:
                line += term.red("×")
            elif left_norm[x] == y:
                line += term.cyan("L")
            elif right_norm[x] == y:
                line += term.magenta("R")
            else:
                line += " "
        print(line)

def audio_callback(indata, frames, time, status):
    if status:
        print(status, file=sys.stderr)
    if frames == 0:
        return
    draw_waveform(indata.copy())

def main():
    monitor = get_monitor_device()
    print(f"Using audio source: {monitor}")

    try: 
        with sd.InputStream(
            device=monitor,
            channels=2,
            samplerate=44100,
            blocksize=1024,
            dtype='float32',
            callback=audio_callback
        ):
            with term.cbreak():
                while True:
                    time.sleep(0.05)
    except KeyboardInterrupt:
        print(term.normal + "\nExiting")

if __name__ == "__main__":
    main()
