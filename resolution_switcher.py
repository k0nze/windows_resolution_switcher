import pystray
import pywintypes
import win32api
import win32con
from PIL import Image
from pystray import MenuItem as item


def on_set_resolution(width: int, height:int):
    # adapted from Peter Wood: https://stackoverflow.com/a/54262365
    devmode = pywintypes.DEVMODEType()
    devmode.PelsWidth = width
    devmode.PelsHeight = height

    devmode.Fields = win32con.DM_PELSWIDTH | win32con.DM_PELSHEIGHT

    win32api.ChangeDisplaySettings(devmode, 0)


def on_quit():
    icon.visible = False
    icon.stop()


if __name__ == "__main__":
    # adapted from Sebastin Ignacio Camilla Trinc: https://stackoverflow.com/a/48284187
    image = Image.open("icon.png")

    menu = (
        item('2160p', lambda: on_set_resolution(3840, 2160)), 
        item('1440p', lambda: on_set_resolution(2560, 1440)),
        item('Quit', on_quit)
        )

    icon = pystray.Icon("Resolution Switcher", image, "Resolution Switcher", menu)
    icon.run()
