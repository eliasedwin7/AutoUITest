import os
import time
import pyautogui

# Set the path to the directory where the tool is located
downloads_path = os.path.join(os.environ['USERPROFILE'], 'Downloads')
tool_directory_name = 'icms_focus_dev_8.0.5_archive'  # Adjust if needed
tool_directory_path = os.path.join(downloads_path, tool_directory_name)

# Define the paths to the images of the tabs
tab_system_image = 'tab_system.png'
tab_results_image = 'tab_results.png'
# Add paths to other tab images as needed

# A function to click on a tab
def click_tab(tab_image, confidence=0.8):
    try:
        # Find the location of the tab on screen
        location = pyautogui.locateCenterOnScreen(tab_image, confidence=confidence)
        if location is not None:
            pyautogui.click(location)
            print(f"Clicked on {tab_image}")
            return True
        else:
            print(f"{tab_image} not found on screen.")
            return False
    except pyautogui.ImageNotFoundException:
        print(f"Could not locate the image {tab_image} on the screen.")
        return False

# Function to switch to the application window (this will be a custom function depending on how you can activate the window)
def switch_to_application():
    # Dummy placeholder: you might want to use pygetwindow or other libraries that can focus on the window by name.
    # For example:
    # window = pygetwindow.getWindowsWithTitle('ICMS Focus')[0]
    # window.activate()
    pass

# Activate the application window
switch_to_application()

# Give it a moment to come to focus
time.sleep(2)

# Click on the 'System' tab
if click_tab(tab_system_image):
    time.sleep(1)  # Wait for the tab change if necessary
    # Add more logic here if needed (like checking the tab content)

# Click on the 'Results' tab
if click_tab(tab_results_image):
    time.sleep(1)  # Wait for the tab change if necessary
    # Add more logic here if needed

# ... Continue for other tabs as needed

