"""
Module to record user actions (mouse clicks and keyboard inputs) and capture screenshots.
"""

import json
import time
import threading
import os
import re
from pathlib import Path
import pyautogui
from pynput import mouse, keyboard


class UserActionRecorder:
    """
    A class to record user actions (mouse clicks and keyboard inputs) and capture screenshots.
    """

    def __init__(self, base_dir, idle_time_limit=5):
        self.base_dir = Path(base_dir)
        self.screenshots_dir = self.base_dir / "screenshots"
        os.makedirs(self.screenshots_dir, exist_ok=True)
        self.actions = []
        self.settings = {"idle_time_limit": idle_time_limit, "bounding_box": None}
        self.state = {"last_action_time": time.time(), "recording": False}
        self.listeners = {
            "mouse_listener": None,
            "keyboard_listener": None,
            "stop_listener": None,
        }
        self.lock = threading.Lock()

    def start_recording(self):
        """Start recording mouse and keyboard actions."""
        with self.lock:
            self.state["recording"] = True
        self.listeners["mouse_listener"] = mouse.Listener(on_click=self.on_click)
        self.listeners["keyboard_listener"] = keyboard.Listener(on_press=self.on_press)
        self.listeners["stop_listener"] = keyboard.Listener(on_press=self.on_stop)
        self.listeners["mouse_listener"].start()
        self.listeners["keyboard_listener"].start()
        self.listeners["stop_listener"].start()
        self.monitor_idle_time()

    def stop_recording(self):
        """Stop recording actions."""
        with self.lock:
            self.state["recording"] = False
        if self.listeners["mouse_listener"]:
            self.listeners["mouse_listener"].stop()
        if self.listeners["keyboard_listener"]:
            self.listeners["keyboard_listener"].stop()
        if self.listeners["stop_listener"]:
            self.listeners["stop_listener"].stop()

    def on_click(self, pos_x, pos_y, button, pressed):
        """Handle mouse click events."""
        if pressed:
            self.record_click(pos_x, pos_y, button)
            with self.lock:
                self.state["last_action_time"] = time.time()

    def on_press(self, key):
        """Handle keyboard press events."""
        print(key)
        try:
            self.record_typing(key.char)
        except AttributeError:
            self.record_typing(str(key))
        with self.lock:
            self.state["last_action_time"] = time.time()

    def on_stop(self, key):
        """Handle stop recording event."""
        if key == keyboard.Key.esc:
            self.stop_recording()

    def record_click(self, pos_x, pos_y, button):
        """Record a mouse click action."""
        monitor = self.get_monitor(pos_x)
        screenshot_path = self.capture_screenshot(
            f"click_{pos_x}_{pos_y}_{int(time.time())}.png"
        )
        self.actions.append(
            {
                "button": str(button),
                "action": "click",
                "x": pos_x,
                "y": pos_y,
                "monitor": monitor,
                "screenshot": str(screenshot_path),
            }
        )
        self.update_bounding_box(pos_x, pos_y)

    def record_typing(self, text):
        """Record a typing action."""
        sanitized_text = re.sub(r"[^a-zA-Z0-9]", "_", str(text))
        screenshot_path = self.capture_screenshot(
            f"type_{sanitized_text}_{int(time.time())}.png"
        )
        monitor = self.get_monitor(pyautogui.position().x)
        self.actions.append(
            {
                "action": "type",
                "text": sanitized_text,
                "monitor": monitor,
                "screenshot": str(screenshot_path),
            }
        )

    def save_to_json(self, filename):
        """Save recorded actions to a JSON file."""
        data = {
            "bounding_box": self.settings["bounding_box"],
            "elements": self.actions,
            "metadata": self.get_metadata(),
        }
        with open(filename, "w", encoding="utf-8") as file:
            json.dump(data, file, indent=4)
        return filename

    def get_metadata(self):
        """Gather metadata for the recording session."""
        return {
            "start_time": time.ctime(self.state["last_action_time"]),
            "idle_time_limit": self.settings["idle_time_limit"],
            "total_actions": len(self.actions),
        }

    def update_bounding_box(self, pos_x, pos_y):
        """Update the bounding box for screenshots."""
        box_size = 50
        self.settings["bounding_box"] = (
            pos_x - box_size,
            pos_y - box_size,
            box_size * 2,
            box_size * 2,
        )

    def monitor_idle_time(self):
        """Monitor idle time and stop recording if idle for too long."""

        def check_idle_time():
            while True:
                with self.lock:
                    if not self.state["recording"]:
                        break
                    if (
                        time.time() - self.state["last_action_time"]
                        > self.settings["idle_time_limit"]
                    ):
                        self.stop_recording()
                        break
                time.sleep(1)

        idle_thread = threading.Thread(target=check_idle_time, daemon=True)
        idle_thread.start()

    def perform_action(self, action):
        """Perform the recorded action."""
        try:
            if action["action"] == "click":
                pyautogui.click(action["x"], action["y"])
            elif action["action"] == "type":
                pyautogui.typewrite(action["text"])
        except (pyautogui.FailSafeException, pyautogui.ImageNotFoundException) as error:
            print(f"Error performing action {action}: {error}")

    def capture_screenshot(self, filename):
        """Capture a screenshot."""
        if self.settings["bounding_box"]:
            screenshot = pyautogui.screenshot(region=self.settings["bounding_box"])
        else:
            screenshot = pyautogui.screenshot()
        screenshot_path = self.screenshots_dir / filename
        screenshot.save(screenshot_path)
        return screenshot_path

    def get_monitor(self, pos_x):
        """Determine which monitor the action is performed on."""
        screen_width, _ = pyautogui.size()
        if pos_x < screen_width:
            return 1
        if pos_x < 2 * screen_width:
            return 2
        return 3


# Example usage (should be placed in a separate script or the main function)
if __name__ == "__main__":
    LOCAL_DIR = Path.home() / "Downloads"
    print("Running the UI Recorder")
    recorder = UserActionRecorder(base_dir=LOCAL_DIR)
    try:
        recorder.start_recording()

        # The program will keep running until the user is idle for 5 seconds or presses Esc
        while recorder.state["recording"]:
            time.sleep(1)

    except KeyboardInterrupt:
        print("Recording stopped by user.")
        recorder.stop_recording()

    # Save actions to a JSON file
    recorder.save_to_json(LOCAL_DIR / "recorded_actions.json")
