import json
import os
import pyautogui
import cv2
import numpy as np
import easyocr
import logging
import time
from screeninfo import get_monitors
from pathlib import Path
import subprocess
import platform
from skimage.metrics import structural_similarity as ssim

# Set up logging
logging.basicConfig(filename='ui.log', level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

class GUIHandler:
    def __init__(self):
        # Create directories for storing screenshots and differences
        self.screenshots_dir = Path("output/screenshots")
        self.differences_dir = Path("output/differences")
        self.matchable_areas_dir = Path("output/matchable_areas")
        os.makedirs(self.screenshots_dir, exist_ok=True)
        os.makedirs(self.differences_dir, exist_ok=True)
        os.makedirs(self.matchable_areas_dir, exist_ok=True)

        # Initialize OCR reader
        self.ocr_reader = easyocr.Reader(['en'])

        # Get the primary monitor's resolution
        monitors = get_monitors()
        primary_monitor = next((monitor for monitor in monitors if monitor.is_primary), monitors[0])
        self.x = primary_monitor.x
        self.y = primary_monitor.y
        self.height = primary_monitor.height
        self.width = primary_monitor.width
        self.logs = []

    def run_app(self, app_name):
        """Run an application based on the OS and maximize it."""
        system = platform.system()
        try:
            if system == 'Windows':
                subprocess.Popen(['start', app_name], shell=True)
            elif system == 'Linux':
                subprocess.Popen([app_name], shell=True)
            else:
                logging.error("Unsupported operating system")
            time.sleep(5)  # Wait for the app to open
            #self.maximize_window_if_needed()
        except Exception as e:
            logging.error(f"Failed to run application {app_name}: {e}")
            self.search_and_run_app(app_name)

    def search_and_run_app(self, app_name):
        """Search and run the application if it didn't launch directly and maximize it."""
        system = platform.system()
        try:
            if system == 'Windows':
                pyautogui.press('win')
                time.sleep(1)
                pyautogui.write(app_name)
                time.sleep(2)
                pyautogui.press('enter')
            elif system == 'Linux':
                pyautogui.hotkey('ctrl', 'alt', 't')
                time.sleep(1)
                pyautogui.write(f'{app_name} &')
                pyautogui.press('enter')
            else:
                logging.error("Unsupported operating system for search")
            time.sleep(5)  # Wait for the app to open
            #self.maximize_window_if_needed()
        except Exception as e:
            logging.error(f"Failed to search and run application {app_name}: {e}")

    # Commented out the maximize window function
    """
    def maximize_window_if_needed(self):
        Maximize the currently active window if it's not already maximized.
        try:
            if platform.system() == 'Windows':
                pyautogui.hotkey('win', 'up')  # Maximize window
            elif platform.system() == 'Linux':
                pyautogui.hotkey('ctrl', 'super', 'up')  # Maximize window for some Linux environments
            time.sleep(3)  # Give some time for the window to maximize
        except Exception as e:
            logging.error(f"Failed to maximize the window: {e}")
    """

    def click(self, x, y, description="Click"):
        """Simulate a click and log the action."""
        try:
            pyautogui.moveTo(self.x + 10, self.y + 10)  # Move cursor to a safe position before clicking
            time.sleep(1)  # Ensure the cursor is moved before proceeding
            pyautogui.click(self.x + x, self.y + y)
            self.logs.append(f"{description} at ({self.x + x}, {self.y + y})")
            logging.info(f"{description} at ({self.x + x}, {self.y + y})")
            time.sleep(2)
        except Exception as e:
            logging.error(f"Failed to click at ({self.x + x}, {self.y + y}): {e}")

    def press_key(self, key, description="Key Press"):
        """Simulate a key press and log the action."""
        try:
            pyautogui.press(key)
            self.logs.append(f"{description} '{key}'")
            logging.info(f"{description} '{key}'")
            time.sleep(1)
        except Exception as e:
            logging.error(f"Failed to press key '{key}': {e}")

    def screenshot(self, file_name, description="Screenshot"):
        """Take a screenshot of the primary monitor and save it."""
        try:
            screenshot = pyautogui.screenshot(region=(self.x, self.y, self.width, self.height))
            screenshot_path = self.screenshots_dir / file_name
            screenshot.save(screenshot_path)
            self.logs.append(f"{description} saved as {file_name}")
            logging.info(f"{description} saved as {file_name}")
            time.sleep(1)
            return screenshot_path
        except Exception as e:
            logging.error(f"Failed to take screenshot {file_name}: {e}")
            return None

    def resize_image(self, image, target_size):
        """Resize image to the target size."""
        return cv2.resize(image, target_size, interpolation=cv2.INTER_AREA)

    def compare_screenshots(self, img1_path, img2_path, threshold=0.8):
        """Compare two screenshots using SSIM and return True if they are similar."""
        try:
            # Load images
            img1 = cv2.imread(str(img1_path))
            img2 = cv2.imread(str(img2_path))

            # Resize img2 to match img1 dimensions
            img2_resized = self.resize_image(img2, (img1.shape[1], img1.shape[0]))

            # Convert images to grayscale
            gray1 = cv2.cvtColor(img1, cv2.COLOR_BGR2GRAY)
            gray2 = cv2.cvtColor(img2_resized, cv2.COLOR_BGR2GRAY)

            # Compute Structural Similarity Index (SSIM)
            score, diff = ssim(gray1, gray2, full=True)
            
            # Normalize the difference image for visualization
            diff = (diff * 255).astype("uint8")

            # Apply threshold to get the matchable areas
            _, thresh = cv2.threshold(diff, 255 * (1 - threshold), 255, cv2.THRESH_BINARY_INV)

            # Find contours of the matchable areas
            contours, _ = cv2.findContours(thresh, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)

            # Draw bounding boxes around matchable areas
            matchable_areas_img1 = img1.copy()
            matchable_areas_img2 = img2_resized.copy()

            for contour in contours:
                (x, y, w, h) = cv2.boundingRect(contour)
                cv2.rectangle(matchable_areas_img1, (x, y), (x + w, y + h), (0, 255, 0), 2)
                cv2.rectangle(matchable_areas_img2, (x, y), (x + w, y + h), (0, 255, 0), 2)

            # Save the images with matchable areas highlighted
            cv2.imwrite(str(self.matchable_areas_dir / f"matchable_areas_img1_{Path(img1_path).stem}.png"), matchable_areas_img1)
            cv2.imwrite(str(self.matchable_areas_dir / f"matchable_areas_img2_{Path(img2_path).stem}.png"), matchable_areas_img2)

            return score >= threshold
        except Exception as e:
            logging.error(f"Failed to compare screenshots {img1_path} and {img2_path}: {e}")
            return False

    def find_element_coordinates(self, element_image_path):
        """Locate an element's coordinates using simple template matching."""
        try:
            screenshot = np.array(pyautogui.screenshot())
            gray_screenshot = cv2.cvtColor(screenshot, cv2.COLOR_BGR2GRAY)
            template = cv2.imread(element_image_path, 0)
            result = cv2.matchTemplate(gray_screenshot, template, cv2.TM_CCOEFF_NORMED)
            _, max_val, _, max_loc = cv2.minMaxLoc(result)
            threshold = 0.5  # Adjust this threshold as needed
            if max_val >= threshold:
                h, w = template.shape
                center_x = max_loc[0] + w // 2
                center_y = max_loc[1] + h // 2
                logging.info(f"Element found at ({center_x}, {center_y}) with matching value {max_val}")
                print(f"Element found at ({center_x}, {center_y}) with matching value {max_val}")
                return (center_x, center_y), max_val
            else:
                logging.error(f"No match found for {element_image_path}. Best match value: {max_val}")
                print(f"No match found for {element_image_path}. Best match value: {max_val}")
                return None, max_val
        except Exception as e:
            logging.error(f"Failed to find element coordinates for {element_image_path}: {e}")
            print(f"Failed to find element coordinates for {element_image_path}: {e}")
            return None, 0

    def find_text_coordinates(self, text):
        """Find the coordinates (x, y) and width and height of the specified text on the screen."""
        try:
            screenshot = np.array(pyautogui.screenshot())
            results = self.ocr_reader.readtext(screenshot, detail=1)
            for (bbox, recognized_text, confidence) in results:
                if recognized_text.strip().lower() == text.strip().lower():
                    (top_left, top_right, bottom_right, bottom_left) = bbox
                    x, y = int(top_left[0]), int(top_left[1])
                    w = int(top_right[0] - top_left[0])
                    h = int(bottom_left[1] - top_left[1])
                    logging.info(f"Text '{text}' found at ({x}, {y}, {w}, {h}) with confidence {confidence}")
                    print(f"Text '{text}' found at ({x}, {y}, {w}, {h}) with confidence {confidence}")
                    return (x, y, w, h), confidence
            logging.error(f"Text '{text}' not found on the screen.")
            return None, 0
        except Exception as e:
            logging.error(f"Failed to find text coordinates for '{text}': {e}")
            print(f"Failed to find text coordinates for '{text}': {e}")
            return None, 0

    def perform_action(self, element ,confidence=.75):
        """Perform an action and return the new state, reward, done status."""
        try:
            action = element['action']
            image_coords = None
            text_coords = None
            image_confidence = 0
            text_confidence = 0

            if 'element_image' in element:
                image_coords, image_confidence = self.find_element_coordinates(element['element_image'])
                print(f"Image coordinates: {image_coords}, Confidence: {image_confidence}")
                if image_coords == (None, None):
                    logging.error("Element image not found on the screen.")

            if 'name' in element:
                text_coords, text_confidence = self.find_text_coordinates(element['name'])
                print(f"Text coordinates: {text_coords}, Confidence: {text_confidence}")
                if text_coords is None:
                    logging.error(f"Text '{element['name']}' not found on the screen.")

            if text_coords and text_confidence >= confidence:
                x, y, _, _ = text_coords
            elif image_coords and image_confidence >=confidence:
                x, y = image_coords
            elif image_coords and text_coords:
                x_image, y_image = image_coords
                x_text, y_text, _, _ = text_coords
                if abs(x_image - x_text) < 50 and abs(y_image - y_text) < 50:  # Adjust the threshold as needed
                    x, y = (x_image + x_text) // 2, (y_image + y_text) // 2
                else:
                    logging.error("Image and text coordinates are too far apart.")
                    return None, 0, True
            else:
                logging.error("No valid coordinates found.")
                return None, 0, True

            logging.info(f"Performing action '{action}' on coordinates ({x}, {y})")

            if action == "click":
                self.click(int(x), int(y), element['description'])
            elif action == "key":
                self.press_key(element['key'], element['description'])

            new_state = np.array(pyautogui.screenshot())
            return new_state, 0, False
        except Exception as e:
            logging.error(f"Failed to perform action {element['description']}: {e}")
            print(f"Failed to perform action {element['description']}: {e}")
            return None, 0, True

    def run_actions_and_compare(self, json_file_path):
        """Run the actions from the JSON file and compare screenshots."""
        try:
            with open(json_file_path, 'r') as file:
                config = json.load(file)
            self.current_test = config['elements']  # Access elements from the config

            for element in self.current_test:
                self.perform_action(element)
                time.sleep(5)
                new_screenshot = f'{element["name"].replace(" ", "_").replace(".", "")}_{int(time.time())}.png'
                new_screenshot_path = self.screenshot(new_screenshot, element['name'])
                reference_screenshot = element.get('expected_output')

                if reference_screenshot and not self.compare_screenshots(reference_screenshot, new_screenshot_path):
                    print(f"Difference found for {element['name']}. Reference: {reference_screenshot}, New: {new_screenshot_path}")
                    logging.warning(f"Difference found for {element['name']}. Reference: {reference_screenshot}, New: {new_screenshot_path}")
                else:
                    print(f"No differences found for {element['name']}. Reference matches new screenshot.")
        except Exception as e:
            logging.error(f"Failed to run actions and compare screenshots: {e}")

# # Example usage
# if __name__ == "__main__":
#     handler = GUIHandler()
#     handler.run_app('ms-clock:')  # Attempt to open the Clock application
#     # Comment out the maximize function for now
#     # handler.maximize_window_if_needed()
#     handler.run_actions_and_compare("config.json")
