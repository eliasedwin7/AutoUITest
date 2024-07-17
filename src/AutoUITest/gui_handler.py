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
    """
    Handles GUI automation tasks such as running applications, clicking, key presses,
    taking screenshots, comparing screenshots, and extracting text using OCR.
    """

    def __init__(self, base_dir):
        """
        Initialize the GUIHandler.

        Args:
            base_dir (Path): Base directory for storing screenshots and differences.
        """
        self.base_dir = base_dir
        self.screenshots_dir = self.base_dir / "screenshots"
        self.differences_dir = self.base_dir / "differences"
        self.matchable_areas_dir = self.base_dir / "matchable_areas"
        os.makedirs(self.screenshots_dir, exist_ok=True)
        os.makedirs(self.differences_dir, exist_ok=True)
        os.makedirs(self.matchable_areas_dir, exist_ok=True)

        self.ocr_reader = easyocr.Reader(['en'])

        monitors = get_monitors()
        primary_monitor = next((monitor for monitor in monitors if monitor.is_primary), monitors[0])
        self.x = primary_monitor.x
        self.y = primary_monitor.y
        self.height = primary_monitor.height
        self.width = primary_monitor.width
        self.logs = []

    def run_app(self, app_name):
        """
        Run an application and maximize it.

        Args:
            app_name (str): Name of the application to run.
        """
        system = platform.system()
        try:
            if system == 'Windows':
                subprocess.Popen(['start', app_name], shell=True)
            elif system == 'Linux':
                subprocess.Popen([app_name], shell=True)
            else:
                logging.error("Unsupported operating system")
            time.sleep(5)  # Wait for the app to open
        except Exception as error:
            logging.error("Failed to run application %s: %s", app_name, error)
            self.search_and_run_app(app_name)

    def search_and_run_app(self, app_name):
        """
        Search and run an application if it didn't launch directly and maximize it.

        Args:
            app_name (str): Name of the application to search and run.
        """
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
        except Exception as error:
            logging.error("Failed to search and run application %s: %s", app_name, error)

    def click(self, x, y, description="Click"):
        """
        Simulate a click and log the action.

        Args:
            x (int): X-coordinate for the click.
            y (int): Y-coordinate for the click.
            description (str): Description of the click action.
        """
        try:
            pyautogui.moveTo(self.x + 10, self.y + 10)  # Move cursor to a safe position before clicking
            time.sleep(1)  # Ensure the cursor is moved before proceeding
            pyautogui.click(self.x + x, self.y + y)
            self.logs.append(f"{description} at ({self.x + x}, {self.y + y})")
            logging.info("%s at (%d, %d)", description, self.x + x, self.y + y)
            time.sleep(2)
        except Exception as error:
            logging.error("Failed to click at (%d, %d): %s", self.x + x, self.y + y, error)

    def press_key(self, key, description="Key Press"):
        """
        Simulate a key press and log the action.

        Args:
            key (str): Key to press.
            description (str): Description of the key press action.
        """
        try:
            pyautogui.press(key)
            self.logs.append(f"{description} '{key}'")
            logging.info("%s '%s'", description, key)
            time.sleep(1)
        except Exception as error:
            logging.error("Failed to press key '%s': %s", key, error)

    def screenshot(self, file_name, description="Screenshot"):
        """
        Take a screenshot of the primary monitor and save it.

        Args:
            file_name (str): Name of the file to save the screenshot.
            description (str): Description of the screenshot action.
        """
        try:
            screenshot = pyautogui.screenshot(region=(self.x, self.y, self.width, self.height))
            screenshot_path = self.screenshots_dir / file_name
            screenshot.save(screenshot_path)
            self.logs.append(f"{description} saved as {file_name}")
            logging.info("%s saved as %s", description, file_name)
            time.sleep(1)
            return screenshot_path
        except Exception as error:
            logging.error("Failed to take screenshot %s: %s", file_name, error)
            return None

    @staticmethod
    def resize_image(image, target_size):
        """
        Resize an image to the target size.

        Args:
            image (ndarray): Image to resize.
            target_size (tuple): Target size as (width, height).

        Returns:
            ndarray: Resized image.
        """
        return cv2.resize(image, target_size, interpolation=cv2.INTER_AREA)

    def compare_screenshots(self, img1_path, img2_path, threshold=0.8):
        """
        Compare two screenshots using SSIM and return True if they are similar.

        Args:
            img1_path (Path): Path to the first image.
            img2_path (Path): Path to the second image.
            threshold (float): Similarity threshold for comparison.

        Returns:
            bool: True if images are similar, False otherwise.
        """
        try:
            img1 = cv2.imread(str(img1_path))
            img2 = cv2.imread(str(img2_path))
            img2_resized = self.resize_image(img2, (img1.shape[1], img1.shape[0]))

            gray1 = cv2.cvtColor(img1, cv2.COLOR_BGR2GRAY)
            gray2 = cv2.cvtColor(img2_resized, cv2.COLOR_BGR2GRAY)

            score, diff = ssim(gray1, gray2, full=True)
            diff = (diff * 255).astype("uint8")

            _, thresh = cv2.threshold(diff, 255 * (1 - threshold), 255, cv2.THRESH_BINARY_INV)

            contours, _ = cv2.findContours(thresh, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)

            matchable_areas_img1 = img1.copy()
            matchable_areas_img2 = img2_resized.copy()

            for contour in contours:
                (x, y, w, h) = cv2.boundingRect(contour)
                cv2.rectangle(matchable_areas_img1, (x, y), (x + w, y + h), (0, 255, 0), 2)
                cv2.rectangle(matchable_areas_img2, (x, y), (x + w, y + h), (0, 255, 0), 2)

            cv2.imwrite(str(self.matchable_areas_dir / f"matchable_areas_img1_{Path(img1_path).stem}.png"), matchable_areas_img1)
            cv2.imwrite(str(self.matchable_areas_dir / f"matchable_areas_img2_{Path(img2_path).stem}.png"), matchable_areas_img2)

            return score >= threshold
        except Exception as error:
            logging.error("Failed to compare screenshots %s and %s: %s", img1_path, img2_path, error)
            return False

    def perform_action(self, element):
        """
        Perform an action based on the element's description.

        Args:
            element (dict): Dictionary containing the action details.
        """
        try:
            if element['action'] == 'click':
                element_image_path = self.base_dir / element['element_image']
                location = pyautogui.locateCenterOnScreen(str(element_image_path))
                if location:
                    self.click(location.x, location.y, element['description'])
                else:
                    logging.error("Element image %s not found on screen.", element['element_image'])
            elif element['action'] == 'key':
                self.press_key(element['key'], element['description'])
        except Exception as error:
            logging.error("Failed to perform action %s: %s", element['description'], error)

    def extract_text(self, region):
        """
        Extract text from a region of the screen using OCR.

        Args:
            region (tuple): Tuple containing the region coordinates (x, y, width, height).

        Returns:
            str: Extracted text.
        """
        try:
            x, y, width, height = region
            screenshot = pyautogui.screenshot(region=(self.x + x, self.y + y, width, height))
            screenshot_path = self.screenshots_dir / f'ocr_{int(time.time())}.png'
            screenshot.save(screenshot_path)
            text = self.ocr_reader.readtext(str(screenshot_path), detail=0)
            extracted_text = " ".join(text)
            self.logs.append(f"Extracted text: {extracted_text}")
            logging.info("Extracted text: %s", extracted_text)
            return extracted_text
        except Exception as error:
            logging.error("Failed to extract text from region %s: %s", region, error)
            return ""

    def save_logs(self, log_file_path):
        """
        Save logs to a file.

        Args:
            log_file_path (Path): Path to the log file.
        """
        try:
            with open(log_file_path, 'w') as log_file:
                for log in self.logs:
                    log_file.write(f"{log}\n")
            logging.info("Logs saved to %s", log_file_path)
        except Exception as error:
            logging.error("Failed to save logs to %s: %s", log_file_path, error)
