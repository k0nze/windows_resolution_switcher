from contextlib import suppress
import pystray
import pywintypes
import win32api
import win32con
from PIL import Image
from pystray import MenuItem as item


def get_aspect_ratio(width, height):
    return round(width / height, 2)


def get_all_resolutions():
    i = 0
    resolutions = []
    seen = set()
    max_width = 0
    max_height = 0
    with suppress(Exception):
        while True:
            ds = win32api.EnumDisplaySettings(None, i)
            res = (ds.PelsWidth, ds.PelsHeight)
            if res not in seen:
                seen.add(res)
                if ds.PelsWidth > max_width:
                    max_width = ds.PelsWidth
                if ds.PelsHeight > max_height:
                    max_height = ds.PelsHeight
                resolutions.append((ds.PelsWidth, ds.PelsHeight))
            i += 1
    aspect_ratio = get_aspect_ratio(max_width, max_height)
    # return resolutions with same aspect ratio as max resolution
    return sorted(filter(lambda res: get_aspect_ratio(*res) == aspect_ratio,
                         resolutions),
                  key=lambda item: item[1])


def on_set_resolution(width: int, height: int):
    # adapted from Peter Wood: https://stackoverflow.com/a/54262365
    devmode = pywintypes.DEVMODEType()
    devmode.PelsWidth = width
    devmode.PelsHeight = height

    devmode.Fields = win32con.DM_PELSWIDTH | win32con.DM_PELSHEIGHT

    win32api.ChangeDisplaySettings(devmode, 0)


def set_res_curry(width, height):
    # ensure correct values are used when lambda executes
    return lambda: on_set_resolution(width, height)


def get_res_item_text(width, height, show_height=False):
    # formats either W x H or Wp
    return f'{width} x {height}' if show_height else f'{width}p'


def on_exit():
    icon.visible = False
    icon.stop()

if __name__ == '__main__':
    image = Image.open('icon.png')
    menu = [
        item(f'{res[1]}p', set_res_curry(*res))
        for res in get_all_resolutions()
    ]
    menu.append(item('Exit', on_exit))

    icon = pystray.Icon('Resolution Switcher', image, 'Resolution Switcher', menu)
    icon.run()
