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
        self.listeners = {}
        self.lock = threading.Lock()

    def start_recording(self):
        """Start recording mouse and keyboard actions."""
        with self.lock:
            self.state["recording"] = True
        self.listeners["mouse_listener"] = mouse.Listener(on_click=self.on_click)
        self.listeners["keyboard_listener"] = keyboard.Listener(on_press=self.on_press)
        self.listeners["stop_listener"] = keyboard.Listener(on_press=self.on_stop)
        for listener in self.listeners.values():
            listener.start()
        self.monitor_idle_time()

    def stop_recording(self):
        """Stop recording actions."""
        with self.lock:
            self.state["recording"] = False
        for listener in self.listeners.values():
            listener.stop()

    def on_click(self, x, y, button, pressed):
        """Handle mouse click events."""
        if pressed:
            self.record_action("click", x, y, button=str(button))
            with self.lock:
                self.state["last_action_time"] = time.time()

    def on_press(self, key):
        """Handle keyboard press events."""
        try:
            text = key.char
        except AttributeError:
            text = str(key)
        self.record_action("type", pyautogui.position().x, text=text)
        with self.lock:
            self.state["last_action_time"] = time.time()

    def on_stop(self, key):
        """Handle stop recording event."""
        if key == keyboard.Key.esc:
            self.stop_recording()

    def record_action(self, action_type, x, y=None, button=None, text=None):
        """Record an action (click or type)."""
        monitor = self.get_monitor(x)
        sanitized_text = re.sub(r"[^a-zA-Z0-9]", "_", str(text)) if text else None
        filename_base = (
            f"{action_type}_{sanitized_text or f'{x}_{y}'}_{int(time.time())}"
        )
        screenshot_path = self.capture_screenshot(f"{filename_base}.png")
        bounding_box_screenshot_path = self.capture_bounding_box_screenshot(
            f"bbox_{filename_base}.png"
        )
        action = {
            "action": action_type,
            "x": x,
            "y": y,
            "monitor": monitor,
            "screenshot": str(screenshot_path),
            "bounding_box_screenshot": str(bounding_box_screenshot_path),
        }
        if button:
            action["button"] = button
        if text:
            action["text"] = sanitized_text
        self.actions.append(action)
        if action_type == "click":
            self.update_bounding_box(x, y)

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

        threading.Thread(target=check_idle_time, daemon=True).start()

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
        """Capture a screenshot of the entire screen."""
        screenshot = pyautogui.screenshot()
        screenshot_path = self.screenshots_dir / filename
        screenshot.save(screenshot_path)
        return screenshot_path

    def capture_bounding_box_screenshot(self, filename):
        """Capture a screenshot of the bounding box."""
        region = self.settings["bounding_box"]
        screenshot = (
            pyautogui.screenshot(region=region) if region else pyautogui.screenshot()
        )
        screenshot_path = self.screenshots_dir / filename
        screenshot.save(screenshot_path)
        return screenshot_path

    def get_monitor(self, x):
        """Determine which monitor the action is performed on."""
        screen_width, _ = pyautogui.size()
        return (x // screen_width) + 1


# Example usage (should be placed in a separate script or the main function)
if __name__ == "__main__":
    DOWNLOADS_DIR = Path.home() / "Downloads"
    print("Running the UI Recorder")
    recorder = UserActionRecorder(base_dir=DOWNLOADS_DIR)
    try:
        recorder.start_recording()

        # The program will keep running until the user is idle for 5 seconds or presses Esc
        while recorder.state["recording"]:
            time.sleep(1)

    except KeyboardInterrupt:
        print("Recording stopped by user.")
        recorder.stop_recording()

    # Save actions to a JSON file
    recorder.save_to_json(DOWNLOADS_DIR / "recorded_actions.json")
