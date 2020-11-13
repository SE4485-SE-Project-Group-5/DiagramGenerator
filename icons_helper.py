import glob
import hashlib
import os
import pathlib
import platform
import sys
import time

import win32api
import win32con
import win32gui
import win32ui

from config import BUNDLE_DIR


def save_icon(icon_path, save_path):
    if icon_path == "Error: No path found":
        return False

    icon_path = icon_path.replace("\\", "/")
    try:
        iconX = win32api.GetSystemMetrics(win32con.SM_CXICON)
        iconY = win32api.GetSystemMetrics(win32con.SM_CXICON)

        large, small = win32gui.ExtractIconEx(icon_path, 0)
        win32gui.DestroyIcon(small[0])

        hdc = win32ui.CreateDCFromHandle(win32gui.GetDC(0))
        hbmp = win32ui.CreateBitmap()
        hbmp.CreateCompatibleBitmap(hdc, iconX, iconY)
        hdc = hdc.CreateCompatibleDC()

        hdc.SelectObject(hbmp)
        hdc.DrawIcon((0, 0), large[0])

        bmpstr = hbmp.GetBitmapBits(True)
        from PIL import Image
        img = Image.frombuffer(
            'RGBA',
            (32, 32),
            bmpstr, 'raw', 'BGRA', 0, 1
        )
        extrema = img.convert("L").getextrema()
        if "Chrome" in icon_path:
            pass
            # print("TEST")
        if extrema[1] < 250:
            img.save(save_path)
        return True
    except Exception:
        return False


def find_and_save_all_icons(file_path='icons'):
    start_time = time.time()
    if not os.path.isdir(file_path):
        os.makedirs(file_path)

    def search_path(pathname):
        for filename in glob.iglob(pathname + '**/*.exe', recursive=True):
            encoded_file_path = str(hashlib.md5(filename.encode()).hexdigest())
            save_path = f'{file_path}/{encoded_file_path}.png'
            result = save_icon(filename, save_path)
            # print('Saved ' if result else 'Error on ' + parse_exe_name(filename))
            # print(f'\tpath: {save_path}\n\tfilename: {filename}')

    search_path("C:\\Program Files\\")
    search_path("C:\\Program Files (x86)\\")
    end_time = time.time()
    print("--- %s seconds for finding and saving all icons ---" %
          (end_time - start_time))


def find_icon_from_path(path, icons_folder=""):
    path = str(hashlib.md5(path.encode()).hexdigest())
    operating_system = str(platform.system()).lower()

    # os.path.join(pathlib.Path(__file__).parent.absolute(), 'icons')
    icons_folder = os.path.abspath(
        os.path.join(BUNDLE_DIR, 'static', 'icons'))
    for file in os.listdir(icons_folder):
        if file == path + ".png":
            return file
    return "default.png"


def parse_exe_name(exe_name):
    exe_split = exe_name.split("\\")
    return exe_split[2] + " " + exe_split[-1].split(".exe")[0]
