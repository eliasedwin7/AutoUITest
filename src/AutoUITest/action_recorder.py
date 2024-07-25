import json
import pyautogui
import time
import threading
from pynput import mouse, keyboard

class UserActionRecorder:
    def __init__(self,base_dir,idle_time_limit=10):
        self.screenshots_dir = self.base_dir / "screenshots"
        os.makedirs(self.screenshots_dir, exist_ok=True)
        self.actions = []
        self.bounding_box = None
        self.idle_time_limit = idle_time_limit
        self.last_action_time = time.time()
        self.recording = False
        self.mouse_listener = None
        self.keyboard_listener = None

    def start_recording(self):
        self.recording = True
        self.mouse_listener = mouse.Listener(on_click=self.on_click)
        self.keyboard_listener = keyboard.Listener(on_press=self.on_press)
        self.mouse_listener.start()
        self.keyboard_listener.start()
        self.monitor_idle_time()

    def stop_recording(self):
        self.recording = False
        if self.mouse_listener:
            self.mouse_listener.stop()
        if self.keyboard_listener:
            self.keyboard_listener.stop()

    def on_click(self, x, y, button, pressed):
        if pressed:
            self.record_click(x, y)
            self.last_action_time = time.time()

    def on_press(self, key):
        try:
            self.record_typing(key.char)
        except AttributeError:
            self.record_typing(str(key))
        self.last_action_time = time.time()

    def record_click(self, x, y):
        self.actions.append({"action": "click", "x": x, "y": y})
        self.update_bounding_box(x, y)
        self.capture_screenshot(f'click_{x}_{y}_{int(time.time())}.png')

    def record_typing(self, text):
        self.actions.append({"action": "type", "text": text})
        self.capture_screenshot(f'type_{text}_{int(time.time())}.png')

    def save_to_json(self, filename):
        with open(filename, 'w') as f:
            json.dump(self.actions, f, indent=4)
        return filename

    def update_bounding_box(self, x, y):
        box_size = 50
        self.bounding_box = (x - box_size, y - box_size, box_size * 2, box_size * 2)

    def monitor_idle_time(self):
        def check_idle_time():
            while self.recording:
                if time.time() - self.last_action_time > self.idle_time_limit:
                    self.stop_recording()
                time.sleep(1)

        threading.Thread(target=check_idle_time, daemon=True).start()

    def stop_if_idle(self):
        if time.time() - self.last_action_time > self.idle_time_limit:
            self.stop_recording()

    def perform_action(self, action):
        if action["action"] == "click":
            pyautogui.click(action["x"], action["y"])
        elif action["action"] == "type":
            pyautogui.typewrite(action["text"])

    def capture_screenshot(self, filename):
        if self.bounding_box:
            screenshot = pyautogui.screenshot(region=self.bounding_box)
        else:
            screenshot = pyautogui.screenshot()
        screenshot.save((screenshots_dir/filename))

# Example usage (should be placed in a separate script or the main function)
if __name__ == "__main__":
    recorder = UserActionRecorder()
    recorder.start_recording()

    # Simulate user actions
    time.sleep(5)  # Keep recording for 5 seconds

    # Stop recording if idle
    recorder.stop_if_idle()

    # Save actions to a JSON file
    recorder.save_to_json('recorded_actions.json')
