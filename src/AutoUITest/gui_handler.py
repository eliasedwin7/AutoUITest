# src/AutoUITest/gui_handler.py
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

class GUIHandler:
    def __init__(self, base_dir):
        # Define base directory
        self.base_dir = base_dir

        # Create directories for storing screenshots and differences
        self.screenshots_dir = self.base_dir / "screenshots"
        self.differences_dir = self.base_dir / "differences"
        self.matchable_areas_dir = self.base_dir / "matchable_areas"
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
        except Exception as e:
            logging.error(f"Failed to search and run application {app_name}: {e}")

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

    def perform_action(self, element):
        """Perform an action based on the element's description."""
        try:
            if element['action'] == 'click':
                element_image_path = self.base_dir / element['element_image']
                location = pyautogui.locateCenterOnScreen(str(element_image_path))
                if location:
                    self.click(location.x, location.y, element['description'])
                else:
                    logging.error(f"Element image {element['element_image']} not found on screen.")
            elif element['action'] == 'key':
                self.press_key(element['key'], element['description'])
        except Exception as e:
            logging.error(f"Failed to perform action {element['description']}: {e}")

    def extract_text(self, region):
        """Extract text from a region of the screen using OCR."""
        try:
            x, y, width, height = region
            screenshot = pyautogui.screenshot(region=(self.x + x, self.y + y, width, height))
            screenshot_path = self.screenshots_dir / f'ocr_{int(time.time())}.png'
            screenshot.save(screenshot_path)
            text = self.ocr_reader.readtext(str(screenshot_path), detail=0)
            extracted_text = " ".join(text)
            self.logs.append(f"Extracted text: {extracted_text}")
            logging.info(f"Extracted text: {extracted_text}")
            return extracted_text
        except Exception as e:
            logging.error(f"Failed to extract text from region {region}: {e}")
            return ""

    def save_logs(self, log_file_path):
        """Save logs to a file."""
        try:
            with open(log_file_path, 'w') as log_file:
                for log in self.logs:
                    log_file.write(f"{log}\n")
            logging.info(f"Logs saved to {log_file_path}")
        except Exception as e:
            logging.error(f"Failed to save logs to {log_file_path}: {e}")
