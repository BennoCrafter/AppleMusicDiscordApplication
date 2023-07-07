import os
import platform
import subprocess
import time
from sys import exit

import dialite
import pypresence.exceptions

from config import Config
from utils import get_cover_art_url, log, ostype, path
from get_apple_music_link import GetAppleMusicLink
from server import Server

config = Config()

# OS-specific code
macos_ver = platform.mac_ver()[0]

macos_legacy = bool(
    int(platform.mac_ver()[0].split(".")[0]) < 10
    and int(platform.mac_ver()[0].split(".")[1]) < 15
)


def get_music_info():
    # Get info using AppleScript and then parse
    if macos_legacy:
        # Legacy script for pre-catalina macOS
        script_loc = os.path.join(
            path, "scripts", "getmusicinfo-legacy.applescript"
        )
    else:
        # Normal script for macOS
        script_loc = os.path.join(path, "scripts", "getmusicinfo.applescript")

    p = subprocess.Popen(["osascript", script_loc], stdout=subprocess.PIPE)
    info = p.stdout.read().decode("utf-8").strip().split("\\")
    print(info)
    if info[0] == "STOPPED":
        # try apple music on phone
        server = Server()
        server.run()
        info = server.load_current_song().split("/")
        print(info)
    return info

def get_rp(info, statuses):
    """Get additional Rich Presence data"""
    # .split(',')[0] is an attempt to fix issue #5
    elapsed = int(float(info[4].split(",")[0].strip()))
    apple_music_links = GetAppleMusicLink(info[2], info[1])
    formatting_args = {
        "status": "PLAYING" if info[0] == "PLAYING" else "Paused",
        "state": info[0],
        "song": info[1],
        "artist": info[2],
        "album": info[3],
    }

    # Format arguments
    status = {}

    status["large_text"] = statuses["large_text"].format(**formatting_args)
    status["details"] = statuses["details"].format(**formatting_args)
    status["state"] = statuses["state"].format(**formatting_args)
    status["buttons"] = [
        {
            "label": "Open Song on Apple Music",
            "url": apple_music_links.links[0]  # Replace with the actual URL
        }
    ]
    status["small_image"] = (
        ("play" if info[0] == "PLAYING" else "pause")
        if config.config.get("show_play_pause_icon", True)
        else None
    )
    status["start"] = (time.time() - elapsed) if info[0] == "PLAYING" else None

    return status


def rp_updater(RPC):
    """Rich Presence loop"""
    statuses = {
        "large_text": config.config.get("large_text")
        or "Using AppleBeats :)",
        "details": config.config.get("details") or "{song}",
        "state": config.config.get("state") or "By {artist} on {album}",
    }

    err_count = 0

    last_played = time.time()

    artwork = "logo"
    current_song = None

    while True:
        try:
            info = get_music_info()

            if info[0] == "PLAYING" and (time.time()) < (last_played + (10 * 60)):
                if current_song != (info[1], info[2]):
                    artwork = get_cover_art_url(info[1], info[2], info[3]) or "logo"
                    current_song = (info[1], info[2])

                status = get_rp(info, statuses)

                status["large_image"] = artwork

                last_played = time.time()

                RPC.update(**status)
            else:
                RPC.clear()
        except pypresence.exceptions.PyPresenceException as e:
            print(
                f"Disconnected from Discord (maybe Discord is closed or invalid client ID?). Error: {e}"
            )
            return
        except Exception as e:
            log.exception(e)
            err_count += 1

            if err_count < 3:
                msg = "An unexpected error has occured while trying to update your Discord status!"
                dialite.fail("AppleBeats", msg)
                time.sleep(1)  # Sleep an extra second

            if err_count > 5:
                dialite.fail("AppleBeats", "Too many errors, exiting...")
                exit(1)

        time.sleep(0.8)
