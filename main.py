import argparse
import json
import time
import logging
from src.auto_ui_test.action_recorder import UserActionRecorder  # Ensure this import points to your recorder module

# Set up logging
logging.basicConfig(
    filename="ui.log",
    level=logging.INFO,
    format="%(asctime)s - %(levelname)s - %(message)s",
)


def run_from_config(handler, config_path):
    """
    Run actions from a configuration file.

    Args:
        handler: The handler object to perform actions.
        config_path: Path to the configuration file.
    """
    with open(config_path, "r", encoding="utf-8") as file:
        config = json.load(file)
    elements = config["elements"]

    for element in elements:
        if element["action"] == "click":
            handler.click(element["x"], element["y"])
        time.sleep(5)
        new_screenshot = f'{element["action"].replace(" ", "_").replace(".", "")}_{int(time.time())}.png'
        new_screenshot_path = handler.screenshot(new_screenshot, element["action"])
        reference_screenshot = element.get("expected_output")

        if reference_screenshot and not handler.compare_screenshots(
            reference_screenshot, new_screenshot_path
        ):
            print(
                f"Difference found for {element['action']}. Reference: {reference_screenshot}, New: {new_screenshot_path}"
            )
            logging.warning(
                f"Difference found for {element['action']}. Reference: {reference_screenshot}, New: {new_screenshot_path}"
            )
        else:
            print(
                f"No differences found for {element['action']}. Reference matches new screenshot."
            )


def start_recording(recorder):
    """
    Start recording user actions.

    Args:
        recorder: The recorder object to record actions.
    """
    recorder.start_recording()
    try:
        print("Recording user actions. Press 'Ctrl+C' to stop recording.")
        while True:
            time.sleep(1)
    except KeyboardInterrupt:
        print("Recording stopped.")


def main():
    """
    Main function to parse arguments and start the appropriate action.
    """
    parser = argparse.ArgumentParser(description="Auto UI Test Tool")
    parser.add_argument(
        "--config", type=str, help="Path to the configuration file", required=False
    )
    parser.add_argument(
        "--record", action="store_true", help="Start recording user actions"
    )
    args = parser.parse_args()

    if args.record:
        recorder = UserActionRecorder()
        start_recording(recorder)
    elif args.config:
        handler = None  # Replace with actual handler initialization
        run_from_config(handler, args.config)
    else:
        print("Please provide either --config or --record option.")


if __name__ == "__main__":
    main()
