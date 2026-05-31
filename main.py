import sys
import asyncio
import pygame
from core.display import screen
from core.sounds import *
from ui.menu import main_menu

async def main():
    await main_menu()

if __name__ == "__main__":
    asyncio.run(main())
