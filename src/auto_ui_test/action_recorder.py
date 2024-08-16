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

    def __init__(self, base_dir, idle_time_limit=10):
        self.base_dir = Path(base_dir)
        self.screenshots_dir = self.base_dir / "screenshots"
        os.makedirs(self.screenshots_dir, exist_ok=True)
        self.actions = []
        self.settings = {"idle_time_limit": idle_time_limit, "bounding_box": None}
        self.state = {"last_action_time": time.time(), "recording": False}
        self.listeners = {"mouse_listener": None, "keyboard_listener": None}

    def start_recording(self):
        """Start recording mouse and keyboard actions."""
        self.state["recording"] = True
        self.listeners["mouse_listener"] = mouse.Listener(on_click=self.on_click)
        self.listeners["keyboard_listener"] = keyboard.Listener(on_press=self.on_press)
        self.listeners["mouse_listener"].start()
        self.listeners["keyboard_listener"].start()
        self.monitor_idle_time()

    def stop_recording(self):
        """Stop recording actions."""
        self.state["recording"] = False
        if self.listeners["mouse_listener"]:
            self.listeners["mouse_listener"].stop()
        if self.listeners["keyboard_listener"]:
            self.listeners["keyboard_listener"].stop()

    def on_click(self, x, y,button, pressed):
        """Handle mouse click events."""
        if pressed:
            self.record_click(x, y,button)
            self.state["last_action_time"] = time.time()

    def on_press(self, key):
        """Handle keyboard press events."""
        try:
            self.record_typing(key.char)
        except AttributeError:
            self.record_typing(str(key))
        self.state["last_action_time"] = time.time()

    def record_click(self, x, y,button):
        """Record a mouse click action."""
        self.actions.append({"button": str(button),"action": "click", "x": x, "y": y})
        self.update_bounding_box(x, y)
        self.capture_screenshot(f"click_{x}_{y}_{int(time.time())}.png")

    def record_typing(self, text):
        """Record a typing action."""
        sanitized_text = re.sub(r"[^a-zA-Z0-9]", "_", str(text))
        self.actions.append({"action": "type", "text": sanitized_text})
        self.capture_screenshot(f"type_{sanitized_text}_{int(time.time())}.png")

    def save_to_json(self, filename):
        """Save recorded actions to a JSON file."""
        with open(filename, "w", encoding="utf-8") as f:
            json.dump(self.actions, f, indent=4)
        return filename

    def update_bounding_box(self, x, y):
        """Update the bounding box for screenshots."""
        box_size = 50
        self.settings["bounding_box"] = (
            x - box_size,
            y - box_size,
            box_size * 2,
            box_size * 2,
        )

    def monitor_idle_time(self):
        """Monitor idle time and stop recording if idle for too long."""

        def check_idle_time():
            while self.state["recording"]:
                if (
                    time.time() - self.state["last_action_time"]
                    > self.settings["idle_time_limit"]
                ):
                    self.stop_recording()
                time.sleep(1)

        threading.Thread(target=check_idle_time, daemon=True).start()

    def stop_if_idle(self):
        """Stop recording if idle time exceeds the limit."""
        if (
            time.time() - self.state["last_action_time"]
            > self.settings["idle_time_limit"]
        ):
            self.stop_recording()

    def perform_action(self, action):
        """Perform the recorded action."""
        if action["action"] == "click":
            pyautogui.click(action["x"], action["y"])
        elif action["action"] == "type":
            pyautogui.typewrite(action["text"])

    def capture_screenshot(self, filename):
        """Capture a screenshot."""
        if self.settings["bounding_box"]:
            screenshot = pyautogui.screenshot(region=self.settings["bounding_box"])
        else:
            screenshot = pyautogui.screenshot()
        screenshot.save(self.screenshots_dir / filename)


# Example usage (should be placed in a separate script or the main function)
if __name__ == "__main__":
    LOCAL_DIR = Path.home() / 'Downloads'
    print("Running the UI Recorder")
    recorder = UserActionRecorder(base_dir=LOCAL_DIR)
    recorder.start_recording()

    # Simulate user actions
    time.sleep(5)  # Keep recording for 5 seconds

    # Stop recording if idle
    recorder.stop_if_idle()

    # Save actions to a JSON file
    recorder.save_to_json("recorded_actions.json")
