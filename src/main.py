import asyncio
import os
import platform
import threading
from sys import exit

import dialite
import pypresence.exceptions
from pypresence import Presence
import rumps

from config import Config
from rpc import rp_updater
from utils import ostype, path
# Load configuration
config = Config()

# Do initial OS-specific stuff

macos_ver = platform.mac_ver()[0]

macos_legacy = bool(
    int(platform.mac_ver()[0].split(".")[0]) < 10
    and int(platform.mac_ver()[0].split(".")[1]) < 15
)


# Menu bar #


def toggle_playpause_icon():
    config.config["show_play_pause_icon"] = not config.config.get(
        "show_play_pause_icon", True
    )
    config.save()


def try_connect():
    try:
        RPC.connect()
        return True
    except (
            ConnectionRefusedError,
            FileNotFoundError,
            pypresence.exceptions.DiscordNotFound,
            pypresence.exceptions.DiscordError,
    ):
        return False


# Initiate RPC
RPC = Presence(
    config.config.get("client_id", "952320054870020146")
)  # Initialize the Presence client


def rp_thread():
    """Rich Presence thread function"""
    try:
        asyncio.get_event_loop()
    except:
        asyncio.set_event_loop(asyncio.new_event_loop())

    while True:
        # Try connecting until successful
        while True:
            if try_connect():
                print("Connected to Discord")
                break

        rp_updater(RPC)


def main():
    # Launch Rich Presence (RP) updating thread
    x = threading.Thread(target=rp_thread, daemon=True)
    x.start()

    # Start menu bar app

    class DarwinStatusBar(rumps.App):
        def __init__(self):
            super(DarwinStatusBar, self).__init__("AppleBeats")
            toggle = rumps.MenuItem("Toggle play/pause icon")
            toggle.state = (
                1 if config.config.get("show_play_pause_icon", True) else 0
            )
            self.menu = [
                toggle,
            ]

        @rumps.clicked("Toggle play/pause icon")
        def onoff(self, sender):
            toggle_playpause_icon()
            sender.state = config.config["show_play_pause_icon"]

    DarwinStatusBar().run()


if __name__ == "__main__":
    main()
