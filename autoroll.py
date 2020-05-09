import win32gui
import cv2
import pyautogui
import numpy as np
import time
import ctypes
import threading
from tkinter import *
from pynput import keyboard
from PIL import ImageGrab, Image, ImageDraw, ImageTk

root = Tk()

title = cv2.imread("title.png")
transform = cv2.imread("transform_e.png")
transform_d = cv2.imread("transform_d.png")
arrow = cv2.imread("arrow.png")
take = cv2.imread("take_e.png")
double = cv2.imread("x2.png", -1)
h, w = title.shape[:-1]
found = 0
toplist, winlist = [], []
labels = []
results = []
opencv_results = []
grays = []
overlays = []
checkboxes = []
start_x = 130
start_y = 64
targets = []
targets_double = []


def template_matching(image1, image2):
    image1_height, image1_width, channel = image1.shape[::]
    image2_height, image2_witdh, channel = image2.shape[::]
    if (image1_height >= image2_height) and (image1_width >= image2_witdh):
        result = cv2.matchTemplate(image1, image2, cv2.TM_SQDIFF_NORMED)
    elif (image1_height <= image2_height) and (image1_width <= image2_witdh):
        result = cv2.matchTemplate(image2, image1, cv2.TM_SQDIFF_NORMED)
    min_val, max_val, min_loc, max_loc = cv2.minMaxLoc(result)
    return 1 - min_val, min_loc


def check_transform(altar):
    score, min_loc = template_matching(altar, transform)
    if score >= 0.99:
        return True
    else:
        return False


def check_trap(altar):
    score, min_loc = template_matching(altar, transform_d)
    score2, min_loc2 = template_matching(altar, take)
    if score >= 0.99 and score2 >= 0.99:
        return True
    else:
        return False


def check_coordinate(altar):
    column = (134, 170, 206, 242, 278, 314)
    row = (96, 136, 176, 216, 256, 296, 336)
    score, min_loc = template_matching(altar, arrow)
    if score >= 0.99:
        x = column.index(min_loc[0])
        y = row.index(min_loc[1])
        return [y+1, x+1], [y+1, x+1, 1]
    else:
        return None, None


def click_transform(top_x, top_y):
    pyautogui.moveTo(top_x+385, top_y+375)
    ctypes.windll.user32.mouse_event(2, 0, 0, 0, 0)
    time.sleep(0.1)
    ctypes.windll.user32.mouse_event(4, 0, 0, 0, 0)
    time.sleep(0.05)
    pyautogui.moveTo(top_x+200, top_y+375)


def click_confirm(x, y, top_x, top_y):
    pyautogui.moveTo(x+64, y+165)
    time.sleep(0.05)
    ctypes.windll.user32.mouse_event(2, 0, 0, 0, 0)
    time.sleep(0.05)
    ctypes.windll.user32.mouse_event(4, 0, 0, 0, 0)
    time.sleep(0.05)
    pyautogui.moveTo(top_x+200, top_y+375)


def click_take_item(top_x, top_y):
    pyautogui.moveTo(top_x+310, top_y+375)
    time.sleep(0.05)
    ctypes.windll.user32.mouse_event(2, 0, 0, 0, 0)
    time.sleep(0.05)
    ctypes.windll.user32.mouse_event(4, 0, 0, 0, 0)
    time.sleep(0.05)


def get_double_item(altar, coordinate_double):
    double_item = altar[95:95+34, 31:31+34]
    coordinate = coordinate_double[:-1]
    widget = root.grid_slaves(
        row=coordinate[0], column=coordinate[1])[0]
    try:
        index = int(re.findall("\d+", str(widget))[0])-1
    except:
        index = 0
    altar_image = opencv_results[index]
    '''cv2.imshow('xxx', altar)
    cv2.imshow('asd', double_item)
    cv2.imshow('cxz', altar_image)
    cv2.waitKey(0)
    cv2.destroyAllWindows()'''
    score, min_loc = template_matching(double_item, altar_image)
    if score >= 0.95:
        return True
    else:
        return False


running = False


def on_press(key):
    if key == keyboard.Key.space:
        global running
        running = False
        return False


def rolling():
    with keyboard.Listener(on_press=on_press) as listener:
        global running
        running = True
        while running == True:
            altar, top_x, top_y = update_altar_screen()
            transform_status = check_transform(altar)
            if transform_status is True:
                # start rolling
                click_transform(top_x, top_y)
                # wait until the roll stop
                while True:
                    time.sleep(0.5)
                    altar, top_x, top_y = update_altar_screen()
                    coordinate, coordinate_double = check_coordinate(altar)
                    if coordinate is not None:
                        get_trap = check_trap(altar)
                        break
                double_item = False
                if coordinate_double in targets:
                    double_item = get_double_item(altar, coordinate_double)
                if coordinate in targets or double_item is True or coordinate[0] == 1 or get_trap is True:
                    altar, top_x, top_y = update_altar_screen()
                    click_take_item(top_x, top_y)
                    time.sleep(0.4)
                    # if get_trap is False or coordinate[0] == 1:
                    while True:
                        confirmation, x, y = check_confirmation()
                        altar, top_x, top_y = update_altar_screen()
                        if confirmation is not False:
                            click_confirm(x, y, top_x, top_y)
                            break
                    time.sleep(0.4)
            else:
                break
        listener.join()


def rolls():
    pyautogui.moveTo(1, 1)
    time.sleep(0.05)
    ctypes.windll.user32.mouse_event(2, 0, 0, 0, 0)
    time.sleep(0.05)
    ctypes.windll.user32.mouse_event(4, 0, 0, 0, 0)
    newthread = threading.Thread(target=rolling)
    newthread.start()


def click(label):
    coord = []
    double = []
    info = label.grid_info()
    coord = [info['row'], info['column']]

    double = coord.copy()
    double.append(1)

    index = int(label._name)

    if label.image == results[index]:
        label.configure(image=overlays[index])
        label.image = overlays[index]
        targets.remove(coord)
        targets.append(double)
    elif label.image == overlays[index]:
        label.configure(image=grays[index])
        label.image = grays[index]
        targets.remove(double)
    else:
        label.configure(image=results[index])
        label.image = results[index]
        targets.append(coord)
    # print(targets)


def check_confirmation():
    confirmation = cv2.imread("confirmation.png")
    opencv_img = pyautogui.screenshot()
    opencv_img = cv2.cvtColor(np.array(opencv_img), cv2.COLOR_RGB2BGR)
    opencv_img_h, opencv_img_w = opencv_img.shape[:-1]
    if opencv_img_h == 768 and opencv_img_w == 1366:
        score, min_loc = template_matching(opencv_img, confirmation)
        top_x = min_loc[0]
        top_y = min_loc[1]
        bottom_x = min_loc[0] + 232
        if score >= 0.99:
            confirmation = opencv_img[top_y: top_y + 198, top_x:bottom_x]
            return confirmation, top_x, top_y
        else:
            return False, False, False


def enum_cb(hwnd, results):
    winlist.append((hwnd, win32gui.GetWindowText(hwnd)))


win32gui.EnumWindows(enum_cb, toplist)
ee_window = [
    (hwnd, title) for hwnd, title in winlist if "Eden Eternal               " in title
]


def update_altar_screen():
    opencv_img = pyautogui.screenshot()
    opencv_img = cv2.cvtColor(np.array(opencv_img), cv2.COLOR_RGB2BGR)
    opencv_img_h, opencv_img_w = opencv_img.shape[:-1]
    if opencv_img_h == 768 and opencv_img_w == 1366:
        score, min_loc = template_matching(opencv_img, title)
        top_x = min_loc[0]
        top_y = min_loc[1]
        bottom_x = min_loc[0] + w
        if score >= 0.99:
            altar = opencv_img[top_y: top_y + 415, top_x:bottom_x]
            return altar, top_x, top_y
        else:
            return 0, 0, 0


def refresh():
    try:
        targets.clear()
        results.clear()
        grays.clear()
        overlays.clear()
        _list = root.winfo_children()
        i = 0
        for item in _list:
            if item.winfo_class() == 'Label':
                item.destroy()
        while True:
            altar, top_x, top_y = update_altar_screen()
            if top_x != 0:
                for y in range(1, 8):
                    cur_y = start_y+(40*(y-1))
                    for x in range(1, 7):
                        cur_x = start_x+(36*(x-1))
                        result = altar[cur_y:cur_y+34, cur_x:cur_x+34]
                        opencv_results.append(result)
                        overlayed = result.copy()
                        gray = cv2.cvtColor(result, cv2.COLOR_BGR2GRAY)
                        b, g, r = cv2.split(result)
                        result = cv2.merge((r, g, b))
                        result = Image.fromarray(result)
                        result = ImageTk.PhotoImage(image=result)
                        results.append(result)

                        gray = Image.fromarray(gray)
                        gray = ImageTk.PhotoImage(image=gray)
                        grays.append(gray)

                        y1, y2 = 0, 0 + double.shape[0]
                        x1, x2 = 0, 0 + double.shape[1]
                        alpha_s = double[:, :, 3] / 255.0
                        alpha_l = 1.0 - alpha_s

                        for c in range(0, 3):
                            overlayed[y1:y2, x1:x2, c] = (
                                alpha_s * double[:, :, c] + alpha_l * overlayed[y1:y2, x1:x2, c])
                        b, g, r = cv2.split(overlayed)
                        overlayed = cv2.merge((r, g, b))
                        overlayed = Image.fromarray(overlayed)
                        overlayed = ImageTk.PhotoImage(image=overlayed)

                        overlays.append(overlayed)
                        label = Label(image=gray, name=str(i))
                        label.bind("<Button-1>", lambda event,
                                   label=label: click(label))
                        label.image = gray
                        labels.append(label)
                        label.grid(row=y, column=x)
                        i = i+1
                break
            else:
                time.sleep(3)
    except:
        pass


root.resizable(0, 0)
#label = Label(text="Pick items you want to get")
label.grid(row=0, column=0, columnspan=7)
r = Button(root, text="Load altar", command=refresh)
r.grid(row=10, column=1, columnspan=3)
b = Button(root, text="Start Rolling", command=rolls)
b.grid(row=10, column=4, columnspan=3)
root.attributes("-topmost", True)
root.mainloop()
refresh()
