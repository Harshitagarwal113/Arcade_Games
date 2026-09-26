import sys
import asyncio
import pygame
from core.display import screen
from core.sounds import *
from ui.menu import main_menu

async def main():
    try:
        import platform
        if hasattr(platform, "window") and hasattr(platform.window, "infobox"):
            platform.window.infobox.style.display = "none"
    except Exception:
        pass
    await main_menu()

if __name__ == "__main__":
    asyncio.run(main())
