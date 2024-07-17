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

## Directory Structure

```
AutoUITest/
├── setup.py
├── README.md
├── main.py
├── config.json
└── src/
    └── AutoUITest/
        └── gui_handler.py
```

## Usage

1. **Configuration File**:
    Create a `config.json` file in the root directory. This file should contain the elements and actions to be performed. Example:

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
    Execute the `main.py` script to start the GUI automation testing:
    ```sh
    python main.py
    ```

## Example

1. **Launch Applications**:
    The `main.py` script will launch applications as specified in the `apps_to_run` list.

2. **Perform Actions**:
    The script will read the actions from the `config.json` file and perform them sequentially.

3. **Take Screenshots and Compare**:
    The script will take screenshots after each action and compare them with the reference images provided in the configuration file.

4. **Logs**:
    All actions and results are logged in the `ui.log` file.

## Contributing

Contributions are welcome! Please submit a pull request or open an issue to discuss any changes.

## License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## Author

Edwin Alias - eliasedwin7@gmail.com
