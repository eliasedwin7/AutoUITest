"""
Module for handling GUI automation tasks such as running applications, clicking,
key presses, taking screenshots, comparing screenshots, and extracting text using OCR.
"""

import logging
import os
import platform
import subprocess
import time
from pathlib import Path

import cv2
import easyocr
import pyautogui
from screeninfo import get_monitors
from skimage.metrics import structural_similarity as ssim


class GUIHandler:
    """
    Handles GUI automation tasks such as running applications, clicking, key presses,
    taking screenshots, comparing screenshots, and extracting text using OCR.
    """

    class ScreenSettings:  # pylint: disable=too-few-public-methods
        """
        Stores settings for the screen dimensions.
        """

        def __init__(self, x, y, width, height):
            self.x = x
            self.y = y
            self.width = width
            self.height = height

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
        self.ocr_reader = easyocr.Reader(["en"])
        self.logs = []
        self.screen_settings = self.ScreenSettings(0, 0, 0, 0)

        os.makedirs(self.screenshots_dir, exist_ok=True)
        os.makedirs(self.differences_dir, exist_ok=True)
        os.makedirs(self.matchable_areas_dir, exist_ok=True)

        self._initialize_monitor_settings()

    def _initialize_monitor_settings(self):
        """Initialize settings for the primary monitor."""
        monitors = get_monitors()
        primary_monitor = next(
            (monitor for monitor in monitors if monitor.is_primary), monitors[0]
        )
        self.screen_settings.x = primary_monitor.x
        self.screen_settings.y = primary_monitor.y
        self.screen_settings.width = primary_monitor.width
        self.screen_settings.height = primary_monitor.height

    def run_app(self, app_name):
        """
        Run an application and maximize it.

        Args:
            app_name (str): Name of the application to run.
        """
        system = platform.system()
        try:
            if system == "Windows":
                self._run_windows_app(app_name)
            elif system == "Linux":
                self._run_linux_app(app_name)
            else:
                logging.error("Unsupported operating system")
            time.sleep(5)  # Wait for the app to open
        except (subprocess.CalledProcessError, FileNotFoundError) as error:
            logging.error("Failed to run application %s: %s", app_name, error)
            self.search_and_run_app(app_name)

    def _run_windows_app(self, app_name):
        """Run a Windows application."""
        with subprocess.Popen(["start", app_name], shell=True):
            pass

    def _run_linux_app(self, app_name):
        """Run a Linux application."""
        with subprocess.Popen([app_name], shell=True):
            pass

    def search_and_run_app(self, app_name):
        """
        Search and run an application if it didn't launch directly and maximize it.

        Args:
            app_name (str): Name of the application to search and run.
        """
        system = platform.system()
        try:
            if system == "Windows":
                self._search_and_run_windows_app(app_name)
            elif system == "Linux":
                self._search_and_run_linux_app(app_name)
            else:
                logging.error("Unsupported operating system for search")
            time.sleep(5)  # Wait for the app to open
        except (pyautogui.FailSafeException, OSError) as error:
            logging.error(
                "Failed to search and run application %s: %s", app_name, error
            )

    def _search_and_run_windows_app(self, app_name):
        """Search and run a Windows application."""
        pyautogui.press("win")
        time.sleep(1)
        pyautogui.write(app_name)
        time.sleep(2)
        pyautogui.press("enter")

    def _search_and_run_linux_app(self, app_name):
        """Search and run a Linux application."""
        pyautogui.hotkey("ctrl", "alt", "t")
        time.sleep(1)
        pyautogui.write(f"{app_name} &")
        pyautogui.press("enter")

    def click(self, x, y, description="Click"):
        """
        Simulate a click and log the action.

        Args:
            x (int): X-coordinate for the click.
            y (int): Y-coordinate for the click.
            description (str): Description of the click action.
        """
        try:
            pyautogui.moveTo(
                self.screen_settings.x + 10, self.screen_settings.y + 10
            )  # Safe position
            time.sleep(1)
            pyautogui.click(self.screen_settings.x + x, self.screen_settings.y + y)
            self.logs.append(
                f"{description} at ({self.screen_settings.x + x}, {self.screen_settings.y + y})"
            )
            logging.info(
                "%s at (%d, %d)",
                description,
                self.screen_settings.x + x,
                self.screen_settings.y + y,
            )
            time.sleep(2)
        except (pyautogui.FailSafeException, OSError) as error:
            logging.error(
                "Failed to click at (%d, %d): %s",
                self.screen_settings.x + x,
                self.screen_settings.y + y,
                error,
            )

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
        except (pyautogui.FailSafeException, OSError) as error:
            logging.error("Failed to press key '%s': %s", key, error)

    def screenshot(self, file_name, description="Screenshot"):
        """
        Take a screenshot of the primary monitor and save it.

        Args:
            file_name (str): Name of the file to save the screenshot.
            description (str): Description of the screenshot action.
        """
        try:
            screenshot = pyautogui.screenshot(
                region=(
                    self.screen_settings.x,
                    self.screen_settings.y,
                    self.screen_settings.width,
                    self.screen_settings.height,
                )
            )
            screenshot_path = self.screenshots_dir / file_name
            screenshot.save(screenshot_path)
            self.logs.append(f"{description} saved as {file_name}")
            logging.info("%s saved as %s", description, file_name)
            time.sleep(1)
            return screenshot_path
        except (pyautogui.FailSafeException, OSError) as error:
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

            _, thresh = cv2.threshold(
                diff, 255 * (1 - threshold), 255, cv2.THRESH_BINARY_INV
            )

            contours, _ = cv2.findContours(
                thresh, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE
            )

            self._mark_matchable_areas(img1, contours, img1_path, "img1")
            self._mark_matchable_areas(img2_resized, contours, img2_path, "img2")

            return score >= threshold
        except (cv2.error, ValueError) as error:
            logging.error(
                "Failed to compare screenshots %s and %s: %s",
                img1_path,
                img2_path,
                error,
            )
            return False

    def _mark_matchable_areas(self, image, contours, img_path, label):
        """Mark matchable areas on the image based on contours and save it."""
        marked_image = image.copy()
        for contour in contours:
            (x, y, w, h) = cv2.boundingRect(contour)
            cv2.rectangle(marked_image, (x, y), (x + w, y + h), (0, 255, 0), 2)

        marked_image_path = (
            self.matchable_areas_dir
            / f"matchable_areas_{label}_{Path(img_path).stem}.png"
        )
        cv2.imwrite(str(marked_image_path), marked_image)
        logging.info("Marked matchable areas saved as %s", marked_image_path)

    def extract_text(self, image_path):
        """
        Extract text from an image using OCR.

        Args:
            image_path (str): Path to the image file.

        Returns:
            str: Extracted text from the image.
        """
        try:
            result = self.ocr_reader.readtext(image_path)
            extracted_text = " ".join([text for _, text, _ in result])
            logging.info("Extracted text from %s: %s", image_path, extracted_text)
            return extracted_text
        except (cv2.error, OSError) as error:
            logging.error("Failed to extract text from %s: %s", image_path, error)
            return ""
