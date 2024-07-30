"""
Module to test GUI interactions by performing actions on the Clock application.
"""

import json
from pathlib import Path
from gui_handler import GUIHandler

# Initialize the GUIHandler with a base directory
base_dir = Path("output")
handler = GUIHandler(base_dir)

# Attempt to open the Clock application
handler.run_app("ms-clock:")

# Perform actions based on the configuration
config = {
    "elements": [
        {
            "name": "World clock",
            "type": "button",
            "action": "click",
            "element_image": "clock/worldclock_button.png",
            "expected_output": "clock/worldclock_output.png",
            "description": "Click World Clock Button",
        },
        {
            "name": "Stopwatch",
            "type": "button",
            "action": "click",
            "element_image": "clock/stopwatch_button.png",
            "expected_output": "clock/stopwatch_output.png",
            "description": "Click Stopwatch Button",
        },
        {
            "name": "Alarm",
            "type": "button",
            "action": "click",
            "element_image": "clock/alarm_button.png",
            "expected_output": "clock/alarm_output.png",
            "description": "Click Alarm Button",
        },
    ]
}

# Save config to a file
config_path = base_dir / "config.json"
with open(config_path, "w", encoding="utf-8") as f:
    json.dump(config, f)

# Uncomment the lines below one by one to run each step
handler.perform_action(config["elements"][0])  # Perform action on the first element
handler.perform_action(config["elements"][1])  # Perform action on the second element
handler.perform_action(config["elements"][2])  # Perform action on the third element

# Compare screenshots
# Note: You need to take and save the expected
# output screenshots manually or via the script before comparison
# handler.compare_screenshots(
#     "clock/alarm_output.png",
#     "output/screenshots/Alarm_Button_<timestamp>.png"
# )

# Run all actions and compare - Uncomment if method exists and is implemented
# handler.run_actions_and_compare("config.json")

# Assuming find_text_coordinates and find_element_coordinates are methods in GUIHandler
# Uncomment to test them if implemented
# handler.find_text_coordinates("World clock")
# handler.find_element_coordinates("clock/worldclock_button.PNG")

# Uncomment to test moving the mouse to specific coordinates
# handler.move_mouse_to(57, 261)
# handler.move_mouse_to(150, 24)
