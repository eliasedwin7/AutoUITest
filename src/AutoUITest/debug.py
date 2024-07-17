from GenricUI import GUIHandler

handler = GUIHandler()

# Run each function one at a time
handler.run_app('ms-clock:')  # Attempt to open the Clock application

# Perform actions
config = {
    "elements": [
        {
            "name": "World clock",
            "type": "button",
            "action": "click",
            "element_image": "clock/worldclock_button.png",
            "expected_output": "clock/worldclock_output.png",
            "description": "Click World Clock Button"
        },
        {
            "name": "Stopwatch",
            "type": "button",
            "action": "click",
            "element_image": "clock/stopwatch_button.png",
            "expected_output": "clock/stopwatch_output.png",
            "description": "Click Stopwatch Button"
        },
        {
            "name": "Alarm",
            "type": "button",
            "action": "click",
            "element_image": "clock/alarm_button.png",
            "expected_output": "clock/alarm_output.png",
            "description": "Click Alarm Button"
        }
    ]
}

# Save config to a file
# with open("config.json", "w") as f:
#     json.dump(config, f)

# Uncomment the lines below one by one to run each step
#handler.perform_action(config['elements'][0])  # Perform action on the first element
# handler.perform_action(config['elements'][1])  # Perform action on the second element
# handler.perform_action(config['elements'][2])  # Perform action on the third element

# Compare screenshots
# handler.compare_screenshots("clock/alarm_output.png", "output/screenshots/Alarm_Button_<timestamp>.png")

# Run all actions and compare
# handler.run_actions_and_compare("config.json")
handler.find_text_coordinates("World clock")

handler.find_element_coordinates("clock/worldclock_button.PNG")

#handler.move_mouse_to(57, 261)

handler.move_mouse_to(150, 24)
