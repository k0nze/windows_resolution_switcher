import ctypes
from contextlib import suppress
from functools import lru_cache

import pystray
import pywintypes
import win32api
import win32con
from PIL import Image
from pystray import MenuItem as item

# for cross platform https://stackoverflow.com/a/20996948/7732434?

CHANGE_DPI_SCALE = True
MENU_SHOW_HEIGHT = False


def get_aspect_ratio(width, height):
    return round(width / height, 2)


@lru_cache(maxsize=1)
def get_initial_res():
    user32 = ctypes.windll.user32
    user32.SetProcessDPIAware()
    return (user32.GetSystemMetrics(0), user32.GetSystemMetrics(1))


@lru_cache(maxsize=1)
def get_initial_dpi_scale():
    transformed_res = (win32api.GetSystemMetrics(0), win32api.GetSystemMetrics(1))
    raw_res = get_initial_res()
    return raw_res[0] / transformed_res[0]  # 125% is 1.25


# save cache
get_initial_dpi_scale()


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
    return sorted(filter(lambda res: get_aspect_ratio(*res) == aspect_ratio, resolutions),
                                key=lambda item: item[1])


dpi_vals = [1.00, 1.25, 1.50, 1.75, 2.00, 2.25, 2.50, 3.00, 3.50, 4.00, 4.50, 5.00]
dpi_vals_map = {dpi: i for i, dpi in enumerate(dpi_vals)}


def get_recommended_dpi_idx():
    dpi = ctypes.c_int(0)
    if ctypes.windll.user32.SystemParametersInfoA(0x009E, 0, ctypes.byref(dpi), 1) != 0:
        return -1 * dpi.value
    raise IndexError


def set_resolution(width: int, height: int):
    # adapted from Peter Wood: https://stackoverflow.com/a/54262365
    devmode = pywintypes.DEVMODEType()
    devmode.PelsWidth = width
    devmode.PelsHeight = height
    devmode.Fields = win32con.DM_PELSWIDTH | win32con.DM_PELSHEIGHT

    win32api.ChangeDisplaySettings(devmode, 0)

    if CHANGE_DPI_SCALE:
        # https://stackoverflow.com/a/62916586/7732434
        dpi_scale = get_initial_dpi_scale()
        initial_w = get_initial_res()[0]
        res_change = 1 - min(width, initial_w) / max(width, initial_w)
        dpi_scale += res_change if width > initial_w else -res_change
        with suppress(KeyError, IndexError):
            ref_idx = get_recommended_dpi_idx()
            # dpi of 1.5 -> 2 - 1 = rel index of 1
            # dpi of 1 -> 0 - 1 = rel index of -1
            rel_idx = dpi_vals_map[dpi_scale] - ref_idx
            ctypes.windll.user32.SystemParametersInfoA(0x009F, rel_idx, 0, 1)


def set_res_curry(width, height):
    # ensure correct values are used when lambda executes
    return lambda: set_resolution(width, height)


def get_res_item_text(width, height, show_height=False):
    # formats either W x H or Wp
    return f'{width} x {height}' if show_height else f'{width}p'


def on_exit():
    icon.visible = False
    icon.stop()


if __name__ == '__main__':

    image = Image.open('icon.png')
    menu = [item(f'{res[1]}p', set_res_curry(*res)) for res in get_all_resolutions()]
    menu.append(item('Exit', on_exit))
    icon = pystray.Icon('Resolution Switcher', image, 'Resolution Switcher', menu)
    icon.run()
