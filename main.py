# main.py
import json
import logging
import time
from pathlib import Path
from src.AutoUITest.gui_handler import GUIHandler

# Set up logging
logging.basicConfig(filename='ui.log', level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

def main():
    # Define the base directory for input and output
    base_dir = Path(__file__).parent

    # Initialize the GUIHandler with the base directory
    handler = GUIHandler(base_dir)

    # Define the path to the configuration JSON file
    json_file_path = base_dir / "config.json"

    # Run the application(s) as specified
    apps_to_run = ["ms-clock:", "notepad"]  # Add more applications as needed
    for app in apps_to_run:
        handler.run_app(app)
        time.sleep(10)  # Adjust the wait time if necessary

    # Perform actions and compare screenshots as per the JSON file
    try:
        with open(json_file_path, 'r') as file:
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

    except Exception as e:
        logging.error(f"Failed to run actions and compare screenshots: {e}")

if __name__ == "__main__":
    main()
