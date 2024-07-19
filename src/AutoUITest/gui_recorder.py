import json
import pyautogui
import time
from pynput import mouse, keyboard
from threading import Timer, Thread
import cv2
import numpy as np
import logging
from collections import deque
import zlib

logging.basicConfig(level=logging.INFO)

class UserActionRecorder:
    def __init__(self, margin=50, idle_time_limit=10, matching_threshold=0.8):
        self.actions = []
        self.start_time = time.time()
        self.idle_time_limit = idle_time_limit
        self.margin = margin
        self.matching_threshold = matching_threshold
        self.timer = Timer(self.idle_time_limit, self.stop_recording)
        self.timer.start()
        self.bounding_box = None
        self.screenshots = {}
        self.window_history = deque(maxlen=10)  # To track window titles

    def reset_timer(self):
        self.timer.cancel()
        self.timer = Timer(self.idle_time_limit, self.stop_recording)
        self.timer.start()

    def stop_recording(self):
        self.save_to_json('user_actions.json')
        logging.info("Recording stopped due to inactivity.")
        self.mouse_listener.stop()
        self.keyboard_listener.stop()

    def record_click(self, x, y, button):
        button_name = str(button).split('.')[-1]
        action = {
            "action": "click",
            "x": x,
            "y": y,
            "button": button_name,
            "window": self.get_active_window(),
            "timestamp": time.time() - self.start_time
        }
        self.actions.append(action)
        self.update_bounding_box(x, y)
        self.capture_screenshot(x, y, button_name)
        self.reset_timer()

    def record_scroll(self, x, y, dx, dy):
        action = {
            "action": "scroll",
            "x": x,
            "y": y,
            "dx": dx,
            "dy": dy,
            "window": self.get_active_window(),
            "timestamp": time.time() - self.start_time
        }
        self.actions.append(action)
        self.update_bounding_box(x, y)
        self.reset_timer()

    def record_typing(self, key):
        key_name = str(key)
        action = {
            "action": "type",
            "key": key_name,
            "window": self.get_active_window(),
            "timestamp": time.time() - self.start_time
        }
        self.actions.append(action)
        self.reset_timer()

    def get_active_window(self):
        try:
            import pygetwindow as gw
            active_window = gw.getActiveWindow()
            if active_window:
                return active_window.title
        except ImportError:
            pass
        return None

    def save_to_json(self, filename):
        with open(filename, 'w') as f:
            compressed_data = zlib.compress(json.dumps({"elements": self.actions}).encode('utf-8'))
            f.write(compressed_data.decode('latin1'))

    def update_bounding_box(self, x, y):
        if self.bounding_box is None:
            self.bounding_box = [x - self.margin, y - self.margin, x + self.margin, y + self.margin]
        else:
            self.bounding_box[0] = min(self.bounding_box[0], x - self.margin)
            self.bounding_box[1] = min(self.bounding_box[1], y - self.margin)
            self.bounding_box[2] = max(self.bounding_box[2], x + self.margin)
            self.bounding_box[3] = max(self.bounding_box[3], y + self.margin)

    def capture_screenshot(self, x, y, button_name):
        screenshot = pyautogui.screenshot(region=self.bounding_box)
        screenshot = cv2.cvtColor(np.array(screenshot), cv2.COLOR_RGB2BGR)
        screenshot_path = f'screenshot_{button_name}_{x}_{y}.png'
        self.screenshots[screenshot_path] = screenshot
        cv2.imwrite(screenshot_path, screenshot)

    def perform_action(self, action):
        if action["action"] == "click":
            self.perform_click(action["x"], action["y"], action["button"])
        elif action["action"] == "type":
            self.perform_typing(action["key"])
        elif action["action"] == "scroll":
            self.perform_scroll(action["x"], action["y"], action["dx"], action["dy"])

    def perform_click(self, x, y, button):
        button = getattr(mouse.Button, button, mouse.Button.left)
        new_x, new_y = self.locate_element(x, y)
        if new_x is not None and new_y is not None:
            pyautogui.click(x=new_x, y=new_y, button=button)
        else:
            pyautogui.click(x=x, y=y, button=button)

    def perform_typing(self, key):
        try:
            pyautogui.typewrite(key.char if hasattr(key, 'char') else str(key))
        except AttributeError:
            special_keys = {
                'Key.space': ' ',
                'Key.enter': '\n',
                'Key.tab': '\t'
            }
            key_str = str(key)
            if key_str in special_keys:
                pyautogui.typewrite(special_keys[key_str])
            else:
                pyautogui.press(key_str.replace('Key.', ''))

    def perform_scroll(self, x, y, dx, dy):
        pyautogui.scroll(dy, x=x, y=y)

    def locate_element(self, x, y):
        for path, screenshot in self.screenshots.items():
            current_screenshot = pyautogui.screenshot()
            current_screenshot = cv2.cvtColor(np.array(current_screenshot), cv2.COLOR_RGB2BGR)
            res = cv2.matchTemplate(current_screenshot, screenshot, cv2.TM_CCOEFF_NORMED)
            _, max_val, _, max_loc = cv2.minMaxLoc(res)
            if max_val > self.matching_threshold:
                return max_loc[0] + (x - self.bounding_box[0]), max_loc[1] + (y - self.bounding_box[1])
        return None, None

    def start_recording(self):
        def start_mouse_listener():
            with mouse.Listener(
                on_click=self.on_click,
                on_scroll=self.on_scroll
            ) as listener:
                listener.join()

        def start_keyboard_listener():
            with keyboard.Listener(
                on_press=self.on_press
            ) as listener:
                listener.join()

        self.mouse_thread = Thread(target=start_mouse_listener)
        self.keyboard_thread = Thread(target=start_keyboard_listener)
        self.mouse_thread.start()
        self.keyboard_thread.start()
        self.mouse_thread.join()
        self.keyboard_thread.join()

    def on_click(self, x, y, button, pressed):
        if pressed:
            self.record_click(x, y, button)

    def on_scroll(self, x, y, dx, dy):
        self.record_scroll(x, y, dx, dy)

    def on_press(self, key):
        self.record_typing(key)

# Example usage:
if __name__ == "__main__":
    margin = 50  # Adjust margin size as needed
    idle_time_limit = 10  # Adjust idle time limit as needed
    matching_threshold = 0.8  # Adjust matching threshold as needed

    recorder = UserActionRecorder(margin=margin, idle_time_limit=idle_time_limit, matching_threshold=matching_threshold)
    logging.info("Start recording...")
    recorder.start_recording()
