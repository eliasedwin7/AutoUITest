import json
import pyautogui
from PIL import Image, ImageChops
import logging
import time

# Set up logging
logging.basicConfig(filename='gui_tester_advanced.log', level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')


class AdvancedGUITester:
    def __init__(self):
        self.logs = []

    def click(self, x, y, description="Click"):
        """Simulate a click and log the action."""
        pyautogui.click(x, y)
        self.logs.append(f"{description} at ({x}, {y})")
        logging.info(f"{description} at ({x}, {y})")
        time.sleep(2)

    def press_key(self, key, description="Key Press"):
        """Simulate key press and log the action."""
        pyautogui.press(key)
        self.logs.append(f"{description} '{key}'")
        logging.info(f"{description} '{key}'")
        time.sleep(1)

    def screenshot(self, file_name, description="Screenshot"):
        """Take a screenshot and save it."""
        screenshot = pyautogui.screenshot()
        screenshot.save(file_name)
        self.logs.append(f"{description} saved as {file_name}")
        logging.info(f"{description} saved as {file_name}")
        time.sleep(1)

    def compare_images(self, image1_path, image2_path):
        """Compare two images and return True if they are identical."""
        img1 = Image.open(image1_path).convert('RGB')
        img2 = Image.open(image2_path).convert('RGB')
        diff = ImageChops.difference(img1, img2)
        return not diff.getbbox()

    def run_actions_and_compare(self, json_file_path):
        """Run the actions from the JSON file and compare screenshots."""
        with open(json_file_path, 'r') as file:
            actions = json.load(file)

        for action in actions['actions']:
            action_type = action.get('type')
            description = action.get('description')
            new_screenshot = f'{description.replace(" ", "_").replace(".", "")}_{int(time.time())}.png'

            if action_type == 'click':
                self.click(action['x'], action['y'], description)
                self.screenshot(new_screenshot, description)

            elif action_type == 'key':
                self.press_key(action['key'], description)
                self.screenshot(new_screenshot, description)

            # Compare the newly taken screenshot with the reference one
            reference_screenshot = action.get('screenshot')
            if reference_screenshot and not self.compare_images(reference_screenshot, new_screenshot):
                logging.warning(f"Difference found for {description}. Reference: {reference_screenshot}, New: {new_screenshot}")
            else:
                logging.info(f"No differences found for {description}. Reference matches new screenshot.")

# Example usage of the AdvancedGUITester with the JSON actions
if __name__ == "__main__":
    tester = AdvancedGUITester()
    tester.run_actions_and_compare("recorded_actions_with_screenshots.json")
