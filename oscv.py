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
    idx = int(input("\nSelect a monitor source by number: ")) - 1
    return monitors[idx]["name"]


####################
###  DRAW WAVES  ###
####################

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
                time.sleep(0.01)
        except KeyboardInterrupt:
            print(term.normal + "\nExiting")
        finally:
            proc.kill()

if __name__ == "__main__":
    main()
