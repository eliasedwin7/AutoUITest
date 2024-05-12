from pynput import mouse, keyboard
import pyautogui
import json
import time

# Initialize an empty list to store recorded actions
recorded_actions = []
last_mouse_position = {'x': None, 'y': None}

# Record the last mouse position only during significant actions
def record_mouse_position(x, y):
    """Update the last known mouse position."""
    last_mouse_position['x'] = x
    last_mouse_position['y'] = y

# Mouse listener callbacks
def on_click(x, y, button, pressed):
    """Record mouse clicks and take a screenshot after each click."""
    record_mouse_position(x, y)
    if pressed:
        description = f'Clicked {button}'
        screenshot_name = f'{description.replace(" ", "_").replace(".", "")}_{int(time.time())}.png'
        pyautogui.screenshot(screenshot_name)
        recorded_actions.append({
            'type': 'click',
            'description': description,
            'x': last_mouse_position['x'],
            'y': last_mouse_position['y'],
            'screenshot': screenshot_name
        })

def on_scroll(x, y, dx, dy):
    """Record scroll events and take a screenshot after each scroll."""
    record_mouse_position(x, y)
    description = 'Scrolled'
    screenshot_name = f'{description.replace(" ", "_").replace(".", "")}_{int(time.time())}.png'
    pyautogui.screenshot(screenshot_name)
    recorded_actions.append({
        'type': 'scroll',
        'description': description,
        'x': last_mouse_position['x'],
        'y': last_mouse_position['y'],
        'amount': dy,
        'screenshot': screenshot_name
    })

# Keyboard listener callbacks
def on_key_press(key):
    """Record key presses and take a screenshot after each key press."""
    description = f'Pressed key {key}'
    screenshot_name = f'{description.replace(" ", "_").replace(".", "")}_{int(time.time())}.png'
    pyautogui.screenshot(screenshot_name)
    recorded_actions.append({
        'type': 'key',
        'description': description,
        'key': str(key),
        'screenshot': screenshot_name
    })

# Function to save the recorded actions to JSON
def save_actions_to_json(output_file):
    """Save the recorded actions to a JSON file."""
    with open(output_file, 'w') as f:
        json.dump({'actions': recorded_actions}, f, indent=4)
    print(f"Actions saved to {output_file}")

# Start the mouse and keyboard listeners
def start_recording(output_file):
    """Start recording mouse and keyboard actions and save them to JSON."""
    mouse_listener = mouse.Listener(on_click=on_click, on_scroll=on_scroll)
    keyboard_listener = keyboard.Listener(on_press=on_key_press)

    mouse_listener.start()
    keyboard_listener.start()

    # Keep the listeners active for 60 seconds or until stopped
    try:
        time.sleep(60)  # Adjust as needed
    except KeyboardInterrupt:
        pass
    finally:
        # Stop listeners
        mouse_listener.stop()
        keyboard_listener.stop()
        save_actions_to_json(output_file)

# Usage example
if __name__ == "__main__":
    start_recording("recorded_actions_with_screenshots.json")
