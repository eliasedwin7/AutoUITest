# AutoUITest

**AutoUITest** is a Python-based tool designed for automating GUI testing. It leverages libraries like `pyautogui`, `opencv-python`, `numpy`, and `easyocr` to simulate user interactions, take screenshots, compare images, and perform OCR (Optical Character Recognition).

## Features

- Automates GUI interactions such as clicking and key presses.
- Takes screenshots and compares them using Structural Similarity Index (SSIM).
- Extracts text from regions of the screen using OCR.
- Runs applications and performs predefined actions based on a configuration file.

## Requirements

- Python 3.6+
- Libraries: `pyautogui`, `opencv-python`, `numpy`, `easyocr`, `pillow`, `screeninfo`, `scikit-image`, `pandas`

## Installation

1. Clone the repository:
    ```sh
    git clone https://github.com/yourusername/gui-tester.git
    cd gui-tester
    ```

2. Install the required packages:
    ```sh
    pip install -r requirements.txt
    ```

3. Alternatively, you can install the package using `setup.py`:
    ```sh
    python setup.py install
    ```

## Usage

1. **Configuration File**:
    Create a [`config.json`](command:_github.copilot.openSymbolFromReferences?%5B%22%22%2C%5B%7B%22uri%22%3A%7B%22scheme%22%3A%22file%22%2C%22authority%22%3A%22%22%2C%22path%22%3A%22%2FC%3A%2FUsers%2FEdwin.Alias%2FVideos%2FAutoUITest-main%2Fmain.py%22%2C%22query%22%3A%22%22%2C%22fragment%22%3A%22%22%7D%2C%22pos%22%3A%7B%22line%22%3A26%2C%22character%22%3A12%7D%7D%5D%2C%22ec4d4c22-b831-4eb3-a038-579bf446b1a9%22%5D "Go to definition") file in the root directory. This file should contain the elements and actions to be performed. Example:

    ```json
    {
        "elements": [
            {
                "name": "example_element",
                "action": "click",
                "element_image": "example_element.png",
                "description": "Click on the example element",
                "expected_output": "expected_example_element.png"
            },
            {
                "name": "example_keypress",
                "action": "key",
                "key": "enter",
                "description": "Press the Enter key"
            }
        ]
    }
    ```

2. **Run the Script**:
    Execute the [`main.py`](command:_github.copilot.openRelativePath?%5B%7B%22scheme%22%3A%22file%22%2C%22authority%22%3A%22%22%2C%22path%22%3A%22%2Fc%3A%2FUsers%2FEdwin.Alias%2FVideos%2FAutoUITest-main%2Fmain.py%22%2C%22query%22%3A%22%22%2C%22fragment%22%3A%22%22%7D%2C%22ec4d4c22-b831-4eb3-a038-579bf446b1a9%22%5D "c:\Users\Edwin.Alias\Videos\AutoUITest-main\main.py") script to start the GUI automation testing:
    ```sh
    python main.py --config config.json
    ```

## Example

1. **Launch Applications**:
    The [`main.py`](command:_github.copilot.openRelativePath?%5B%7B%22scheme%22%3A%22file%22%2C%22authority%22%3A%22%22%2C%22path%22%3A%22%2Fc%3A%2FUsers%2FEdwin.Alias%2FVideos%2FAutoUITest-main%2Fmain.py%22%2C%22query%22%3A%22%22%2C%22fragment%22%3A%22%22%7D%2C%22ec4d4c22-b831-4eb3-a038-579bf446b1a9%22%5D "c:\Users\Edwin.Alias\Videos\AutoUITest-main\main.py") script will launch applications as specified in the `apps_to_run` list.

2. **Perform Actions**:
    The script will read the actions from the [`config.json`](command:_github.copilot.openSymbolFromReferences?%5B%22%22%2C%5B%7B%22uri%22%3A%7B%22scheme%22%3A%22file%22%2C%22authority%22%3A%22%22%2C%22path%22%3A%22%2FC%3A%2FUsers%2FEdwin.Alias%2FVideos%2FAutoUITest-main%2Fmain.py%22%2C%22query%22%3A%22%22%2C%22fragment%22%3A%22%22%7D%2C%22pos%22%3A%7B%22line%22%3A26%2C%22character%22%3A12%7D%7D%5D%2C%22ec4d4c22-b831-4eb3-a038-579bf446b1a9%22%5D "Go to definition") file and perform them sequentially.

3. **Take Screenshots and Compare**:
    The script will take screenshots after each action and compare them with the reference images provided in the configuration file.

4. **Logs**:
    All actions and results are logged in the `ui.log` file.

## Contributing

Contributions are welcome! Please submit a pull request or open an issue to discuss any changes.

## License

This project is licensed under the MIT License - see the [`LICENSE`](command:_github.copilot.openRelativePath?%5B%7B%22scheme%22%3A%22file%22%2C%22authority%22%3A%22%22%2C%22path%22%3A%22%2Fc%3A%2FUsers%2FEdwin.Alias%2FVideos%2FAutoUITest-main%2FLICENSE%22%2C%22query%22%3A%22%22%2C%22fragment%22%3A%22%22%7D%2C%22ec4d4c22-b831-4eb3-a038-579bf446b1a9%22%5D "c:\Users\Edwin.Alias\Videos\AutoUITest-main\LICENSE") file for details.

## Author

Edwin Alias - eliasedwin7@gmail.com


