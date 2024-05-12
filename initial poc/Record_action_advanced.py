from pynput import mouse, keyboard
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
    record_mouse_position(x, y)
    if pressed:
        recorded_actions.append({
            'type': 'click',
            'description': f'Clicked {button}',
            'x': last_mouse_position['x'],
            'y': last_mouse_position['y']
        })

def on_scroll(x, y, dx, dy):
    record_mouse_position(x, y)
    recorded_actions.append({
        'type': 'scroll',
        'description': 'Scrolled',
        'x': last_mouse_position['x'],
        'y': last_mouse_position['y'],
        'amount': dy
    })

# Keyboard listener callbacks
def on_key_press(key):
    recorded_actions.append({
        'type': 'key',
        'description': f'Pressed key {key}',
        'key': str(key)
    })

# Function to save the recorded actions to JSON
def save_actions_to_json(output_file):
    with open(output_file, 'w') as f:
        json.dump({'actions': recorded_actions}, f, indent=4)
    print(f"Actions saved to {output_file}")

# Start the mouse and keyboard listeners
def start_recording(output_file):
    # Listeners for mouse and keyboard
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
