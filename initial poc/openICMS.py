import zipfile
import os
import subprocess
import time
import pyautogui
from PIL import Image, ImageChops

# Set the paths for the Downloads directory and for the zip file
downloads_path = os.path.join(os.environ['USERPROFILE'], 'Downloads')
zip_file_name = 'icms_focus_dev_8.0.5_archive.zip'
executable_name = 'icms_focus_dev.exe'

# Full path to the zip file
zip_file_path = os.path.join(downloads_path, zip_file_name)

# Extract the zip file
with zipfile.ZipFile(zip_file_path, 'r') as zip_ref:
    zip_ref.extractall(downloads_path)

# Calculate the directory name (assuming it's the same as the zip file without the extension)
directory_name = zip_file_name.rsplit('.', 1)[0]
tool_directory_path = os.path.join(downloads_path, directory_name)

# Navigate to the directory where the tool was extracted
os.chdir(tool_directory_path)

# Launch the executable
process = subprocess.Popen(executable_name)

# Wait for the application to start and become the active window
time.sleep(7)

# Maximize the window using the 'win + up' shortcut
pyautogui.keyDown('win')
pyautogui.press('up')
pyautogui.keyUp('win')

# Wait a moment for the window to maximize
time.sleep(2)

# Take the first screenshot and save it
screenshot1 = pyautogui.screenshot()
screenshot_path1 = os.path.join(downloads_path, f"{directory_name}_screenshot1.png")
screenshot1.save(screenshot_path1)

# Perform some operation or wait before taking another screenshot
time.sleep(5)  # Adjust as necessary

# Take the second screenshot and save it
screenshot2 = pyautogui.screenshot()
screenshot_path2 = os.path.join(downloads_path, f"{directory_name}_screenshot2.png")
screenshot2.save(screenshot_path2)

def compare_images(image_path_1, image_path_2):
    """
    Compare two images and return the percentage of difference and the diff image.
    """
    # Open and convert images to the same mode and size for comparison
    image1 = Image.open(image_path_1).convert('RGB')
    image2 = Image.open(image_path_2).convert('RGB')

    # Ensure the images have the same size
    if image1.size != image2.size:
        raise ValueError("Images do not have the same size.")

    # Find the difference between the images
    diff = ImageChops.difference(image1, image2)

    # Calculate the number of different pixels
    num_diff_pixels = sum(1 for pixel in diff.getdata() if pixel != (0, 0, 0))

    # Calculate the percentage of different pixels
    total_pixels = image1.size[0] * image1.size[1]
    diff_percentage = (num_diff_pixels / total_pixels) * 100

    # Save the diff image if there are differences
    if num_diff_pixels > 0:
        diff_path = "diff_image.png"
        diff.save(diff_path)
        return False, diff_percentage, diff_path
    else:
        return True, 0, None

# Compare the two screenshots
are_equal, difference, diff_image_path = compare_images(screenshot_path1, screenshot_path2)

if are_equal:
    print("The screenshots are identical.")
else:
    print(f"The screenshots differ by {difference}% of pixels.")
    print(f"Diff image saved to: {diff_image_path}")
