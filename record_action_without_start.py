from pynput import mouse, keyboard
import json
import time
import mss
import os

# Initialize an empty list to store recorded actions
recorded_actions = []

# Define a primary monitor region (adjust based on your screen resolution)
primary_monitor = {
    "left": 0,
    "top": 0,
    "width": 1880,  # Example resolution width
    "height": 1080  # Adjust height to exclude taskbar (e.g., 40px less)
}


# Directory to store screenshots
screenshots_dir = "screenshots"
os.makedirs(screenshots_dir, exist_ok=True)

# Function to map coordinates to the primary monitor
def map_to_primary(x, y):
    """Map the given coordinates to the primary monitor."""
    return {
        'x': max(primary_monitor['left'], min(x, primary_monitor['left'] + primary_monitor['width'])),
        'y': max(primary_monitor['top'], min(y, primary_monitor['top'] + primary_monitor['height']))
    }

# Function to capture a screenshot of the primary monitor excluding the taskbar
def take_screenshot(name):
    """Capture a region-specific screenshot and save it with a given name."""
    with mss.mss() as sct:
        screenshot = sct.grab(primary_monitor)
        screenshot_path = os.path.join(screenshots_dir, name)
        mss.tools.to_png(screenshot.rgb, screenshot.size, output=screenshot_path)
    return screenshot_path

# Mouse listener callbacks
def on_click(x, y, button, pressed):
    """Record clicks within the primary monitor and take a screenshot."""
    coords = map_to_primary(x, y)
    if pressed:
        description = f'Clicked {button}'
        screenshot_name = f'{description.replace(" ", "_").replace(".", "")}_{int(time.time())}.png'
        screenshot_path = take_screenshot(screenshot_name)
        recorded_actions.append({
            'type': 'click',
            'description': description,
            'x': coords['x'],
            'y': coords['y'],
            'screenshot': screenshot_path
        })

def on_scroll(x, y, dx, dy):
    """Record scroll events within the primary monitor and take a screenshot."""
    coords = map_to_primary(x, y)
    description = 'Scrolled'
    screenshot_name = f'{description.replace(" ", "_").replace(".", "")}_{int(time.time())}.png'
    screenshot_path = take_screenshot(screenshot_name)
    recorded_actions.append({
        'type': 'scroll',
        'description': description,
        'x': coords['x'],
        'y': coords['y'],
        'amount': dy,
        'screenshot': screenshot_path
    })

def on_key_press(key):
    """Record key presses and take a screenshot."""
    description = f'Pressed key {key}'
    screenshot_name = f'{description.replace(" ", "_").replace(".", "")}_{int(time.time())}.png'
    screenshot_path = take_screenshot(screenshot_name)
    try:
        recorded_actions.append({
            'type': 'key',
            'description': description,
            'key': key.char,
            'screenshot': screenshot_path
        })
    except AttributeError:
        recorded_actions.append({
            'type': 'key',
            'description': f'Pressed special key {key}',
            'key': str(key),
            'screenshot': screenshot_path
        })

# Function to save the recorded actions to JSON
def save_actions_to_json(output_file):
    """Save the recorded actions to a JSON file."""
    with open(output_file, 'w') as f:
        json.dump({'actions': recorded_actions}, f, indent=4)
    print(f"Actions saved to {output_file}")

# Start the mouse and keyboard listeners
def start_recording(output_file):
    """Start recording mouse and keyboard actions, mapping coordinates to the primary monitor."""
    mouse_listener = mouse.Listener(on_click=on_click, on_scroll=on_scroll)
    keyboard_listener = keyboard.Listener(on_press=on_key_press)

    # Start the listeners
    mouse_listener.start()
    keyboard_listener.start()

    # Keep the listeners active for 60 seconds or until stopped
    try:
        time.sleep(20)  # Adjust as needed
    except KeyboardInterrupt:
        pass
    finally:
        # Stop listeners
        mouse_listener.stop()
        keyboard_listener.stop()
        save_actions_to_json(output_file)

# Usage example
if __name__ == "__main__":
    start_recording("filtered_recorded_actions.json")
