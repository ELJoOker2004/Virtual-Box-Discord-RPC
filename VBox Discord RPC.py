import psutil
from pypresence import Presence
import time
from pywinauto import Desktop

# Configuration
client_id = '1196387943800131626'  # Replace with your Discord application's client ID
large_image_key_kali_linux = 'https://i.imgur.com/cPbTgcv.png'  # URL for Kali Linux
large_image_key_windows_flare = 'https://i.imgur.com/gVetf1Z.png'  # URL for Windows or FLARE
default_large_image_key = 'https://i.imgur.com/zARBelj.png'  # Default URL

def get_virtualbox_windows():
    virtualbox_windows = []
    for process in psutil.process_iter(['pid', 'name']):
        if 'VirtualBoxVM' in process.info['name']:
            try:
                windows = Desktop(backend="uia").windows(process=process.info['pid'])
                for window in windows:
                    title = window.window_text()
                    if " [Running]" in title:
                        parsed_title = title.split(" [Running]")[0].strip()
                    elif " [Paused]" in title:
                        parsed_title = title.split(" [Paused]")[0].strip()
                    else:
                        parsed_title = title.strip()
                    virtualbox_windows.append(parsed_title)
            except Exception as e:
                print(f"Could not get windows for process {process.info['pid']}: {e}")
    return virtualbox_windows

def determine_large_image_key(window_title):
    lower_title = window_title.lower()
    if 'kali' in lower_title or 'linux' in lower_title:
        return large_image_key_kali_linux
    elif 'windows' in lower_title or 'flare' in lower_title:
        return large_image_key_windows_flare
    else:
        return default_large_image_key

def main():
    rpc = Presence(client_id)
    rpc.connect()
    start_time = {}
    current_index = 0

    while True:
        virtualbox_windows = get_virtualbox_windows()
        current_windows = set(virtualbox_windows)
        previous_windows = set(start_time.keys())

        # Update start times for new windows
        for window_title in current_windows:
            if window_title not in start_time:
                start_time[window_title] = int(time.time())
                print(f"VirtualBox window '{window_title}' found. Setting Discord presence.")

        # Rotate through the windows
        if virtualbox_windows:
            window_title = virtualbox_windows[current_index]
            large_image_key = determine_large_image_key(window_title)
            rpc.update(
                state=window_title,
                details="Virtual Machine",
                large_image=large_image_key,
                large_text=window_title,
                start=start_time[window_title]
            )
            current_index = (current_index + 1) % len(virtualbox_windows)

        time.sleep(10)  # Check every 10 seconds

if __name__ == "__main__":
    main()
