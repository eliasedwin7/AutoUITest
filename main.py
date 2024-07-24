import json
import logging
import time
from pathlib import Path
from src.AutoUITest.gui_handler import GUIHandler
from  src.AutoUITest.action_recorder import UserActionRecorder  # Ensure this import points to your recorder module
import argparse

# Set up logging
logging.basicConfig(filename='ui.log', level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

def run_from_config(handler, config_path):
    with open(config_path, 'r') as file:
        config = json.load(file)
    elements = config['elements']

    for element in elements:
        handler.perform_action(element)
        time.sleep(5)
        new_screenshot = f'{element["name"].replace(" ", "_").replace(".", "")}_{int(time.time())}.png'
        new_screenshot_path = handler.screenshot(new_screenshot, element['name'])
        reference_screenshot = element.get('expected_output')

        if reference_screenshot and not handler.compare_screenshots(reference_screenshot, new_screenshot_path):
            print(f"Difference found for {element['name']}. Reference: {reference_screenshot}, New: {new_screenshot_path}")
            logging.warning(f"Difference found for {element['name']}. Reference: {reference_screenshot}, New: {new_screenshot_path}")
        else:
            print(f"No differences found for {element['name']}. Reference matches new screenshot.")

def start_recording(recorder):
    recorder.start_recording()
    try:
        print("Recording user actions. Press 'Ctrl+C' to stop recording.")
        while True:
            time.sleep(1)
    except KeyboardInterrupt:
        print("Recording stopped.")
        recorder.stop_recording()
        return recorder.save_to_json()

def main(config_path=None):
    # Define the base directory for input and output
    base_dir = Path(__file__).parent

    # Initialize the GUIHandler with the base directory
    handler = GUIHandler(base_dir)

    if config_path:
        run_from_config(handler, config_path)
    else:
        # Initialize the UserActionRecorder
        recorder = UserActionRecorder()
        recorded_actions_file = start_recording(recorder)
        print(f"Recorded actions saved to {recorded_actions_file}")

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Automate GUI testing or record user actions.")
    parser.add_argument('--config', type=str, help="Path to the JSON configuration file.")
    args = parser.parse_args()

    main(config_path=args.config)
