#   ___     ____    ___   __  __  
#  / __`\  /',__\  /'___\/\ \/\ \ 
# /\ \L\ \/\__, `\/\ \__/\ \ \_/ |
# \ \____/\/\____/\ \____\\ \___/ 
#  \/___/  \/___/  \/____/ \/__/                 

# author: https://github.com/ianshapiro1

import numpy as np
from blessed import Terminal
import subprocess
import time

term = Terminal()
SAMPLE_RATE = 44100
CHANNELS = 2
CHUNK = 1024
BYTES_PER_SAMPLE = 2
FRAME_BYTES = CHUNK * CHANNELS * BYTES_PER_SAMPLE
FRAME_DELAY = 0.01
SMOOTHING_WINDOW = 5
WAVEFORM_VERTICAL_PADDING = 5 #write a function for this
prev_width, prev_height = None, None

#####################
###  GET MONITOR  ###
#####################

def list_monitor_sources():
    try:
        output = subprocess.check_output(["pactl", "list", "sources"], text=True)
    except FileNotFoundError:
        raise RuntimeError("pactl not found")

    monitors = []
    current = {}
    for line in output.splitlines():
        line = line.strip()
        if line.startswith("Source #"):
            if current.get("name", "").endswith(".monitor"):
                monitors.append(current)
            current = {}
        elif line.startswith("Name:"):
            current["name"] = line.split(":", 1)[1].strip()
        elif line.startswith("Description:"):
            current["desc"] = line.split(":", 1)[1].strip()

    if current.get("name", "").endswith(".monitor"):
        monitors.append(current)
    return monitors


def get_default_sink_monitor():
    try:
        sink = subprocess.check_output(["pactl", "get-default-sink"], text=True).strip()
    except subprocess.CalledProcessError:
        return None

    monitors = list_monitor_sources()
    for m in monitors:
        if m["name"].startswith(sink) and m["name"].endswith(".monitor"):
            return m
    return None


def get_monitor_device():
    mon = get_default_sink_monitor()
    if mon:
        print(f"Auto-selected monitor: {mon['desc']} ({mon['name']})")
        answer = input("Use this monitor? [Y/n]: ").strip().lower()
        if answer in ("", "y", "yes"):
            return mon["name"]

    monitors = list_monitor_sources()
    print("\nAvailable monitor sources:\n")
    for i, m in enumerate(monitors):
        print(f"{i+1}. {m['desc']} ({m['name']})")
    while True:
        try:
            idx = int(input("\nSelect a monitor source by number: ")) - 1
            if 0 <= idx < len(monitors):
                return monitors[idx]["name"]
            else:
                print("Invalid selection. Please choose a valid number.")
        except ValueError:
            print("Please enter a number.")
    return monitors[idx]["name"]


####################
###  DRAW WAVES  ###
####################

def normalize(samples, height):
    max_val = np.max(np.abs(samples))
    if max_val == 0:
        return np.zeros_like(samples, dtype=int)
    return ((samples / max_val + 1) / 2 * (height - 1)).astype(int)

def resample_to_width(samples, width):
    if samples.shape[0] == width:
        return samples
    else:
        idx = np.linspace(0, samples.shape[0] - 1, width).astype(int)
        return samples[idx]

def smooth(samples, window_size=SMOOTHING_WINDOW):
    if window_size <= 1:
        return samples
    kernel = np.ones(window_size) / window_size
    return np.convolve(samples, kernel, mode='same')

def draw_waveform(stereo_frame):
    global prev_width, prev_height
    width, height = term.width, term.height - WAVEFORM_VERTICAL_PADDING

    if (width, height) != (prev_width, prev_height):
        print(term.clear + term.move(0, 0), end='')
        prev_width, prev_height = width, height
        
    stereo_frame = resample_to_width(stereo_frame, width)
    left, right = stereo_frame[:, 0], stereo_frame[:, 1]
    left = smooth(left)
    right = smooth(right)
    left_norm = normalize(left, height)
    right_norm = normalize(right, height)

    print(term.move_y(0), end="")
    for y in range(height - 1, -1, -1):
        line = ""
        for x in range(len(left_norm)):
            if left_norm[x] == y and right_norm[x] == y:
                line += term.red("█")
            elif left_norm[x] == y:
                line += term.cyan("█")
            elif right_norm[x] == y:
                line += term.magenta("█")
            else:
                line += " "
        print(line)

def main():
    monitor_name = get_monitor_device()
    print(f"Using audio source: {monitor_name}")

    cmd = [
        "ffmpeg",
        "-f", "pulse",
        "-i", monitor_name,
        "-f", "s16le",
        "-acodec", "pcm_s16le",
        "-ac", str(CHANNELS),
        "-ar", str(SAMPLE_RATE),
        "-"
    ]

    with subprocess.Popen(cmd, stdout=subprocess.PIPE, stderr=subprocess.DEVNULL) as proc, term.fullscreen(), term.hidden_cursor():
        try:
            while True:
                raw = proc.stdout.read(FRAME_BYTES)
                if not raw:
                    break
                data = np.frombuffer(raw, dtype=np.int16).reshape(-1, CHANNELS)
                draw_waveform(data)
                time.sleep(FRAME_DELAY)
        except KeyboardInterrupt:
            print(term.normal + "\nExiting")
        finally:
            proc.kill()

if __name__ == "__main__":
    main()
