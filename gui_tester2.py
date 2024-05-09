import json
import os
import pyautogui
from PIL import Image, ImageChops
import logging
import time

# Set up logging
logging.basicConfig(filename='gui_tester_advanced.log', level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

# Create directories for storing screenshots and differences
screenshots_dir = "screenshots"
differences_dir = "differences"
os.makedirs(screenshots_dir, exist_ok=True)
os.makedirs(differences_dir, exist_ok=True)

# Define a primary monitor region (adjust based on your screen resolution)
primary_monitor = {
    "left": 0,
    "top": 0,
    "width": 1880,  # Example resolution width
    "height": 1080  # Adjust height to exclude taskbar (e.g., 40px less)
}


class AdvancedGUITester:
    def __init__(self):
        self.logs = []

    def click(self, x, y, description="Click"):
        """Simulate a click and log the action."""
        screen_x = primary_monitor["left"] + x
        screen_y = primary_monitor["top"] + y

        pyautogui.click(screen_x, screen_y)
        self.logs.append(f"{description} at ({screen_x}, {screen_y})")
        logging.info(f"{description} at ({screen_x}, {screen_y})")
        time.sleep(2)

    def press_key(self, key, description="Key Press"):
        """Simulate a key press and log the action."""
        pyautogui.press(key)
        self.logs.append(f"{description} '{key}'")
        logging.info(f"{description} '{key}'")
        time.sleep(1)

    def screenshot(self, file_name, description="Screenshot"):
        """Take a screenshot of the primary monitor and save it."""
        screenshot = pyautogui.screenshot(region=(primary_monitor["left"],
                                                  primary_monitor["top"],
                                                  primary_monitor["width"],
                                                  primary_monitor["height"]))
        screenshot_path = os.path.join(screenshots_dir, file_name)
        screenshot.save(screenshot_path)
        self.logs.append(f"{description} saved as {file_name}")
        logging.info(f"{description} saved as {file_name}")
        time.sleep(1)
        return screenshot_path

    def compare_images(self, image1_path, image2_path):
        """Compare two images and return True if they are identical."""
        img1 = Image.open(image1_path).convert('RGB')
        img2 = Image.open(image2_path).convert('RGB')
        diff = ImageChops.difference(img1, img2)

        # Save the difference image if differences are found
        if diff.getbbox():
            diff_name = f"diff_{os.path.basename(image2_path)}"
            diff_path = os.path.join(differences_dir, diff_name)
            diff.save(diff_path)
            return False

        return True

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
                new_screenshot_path = self.screenshot(new_screenshot, description)

            elif action_type == 'key':
                self.press_key(action['key'], description)
                new_screenshot_path = self.screenshot(new_screenshot, description)

            # Compare the newly taken screenshot with the reference one
            reference_screenshot = action.get('screenshot')
            if reference_screenshot and not self.compare_images(reference_screenshot, new_screenshot_path):
                logging.warning(f"Difference found for {description}. Reference: {reference_screenshot}, New: {new_screenshot_path}")
            else:
                logging.info(f"No differences found for {description}. Reference matches new screenshot.")

# Example usage of the AdvancedGUITester with the JSON actions
if __name__ == "__main__":
    tester = AdvancedGUITester()
    tester.run_actions_and_compare("filtered_recorded_actions.json")
