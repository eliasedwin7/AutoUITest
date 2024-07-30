# setup.py
from setuptools import setup, find_packages

setup(
    name="auto_ui_test",
    version="0.1.0",
    description="A tool for GUI automation testing",
    author="Edwin Alias",
    author_email="eliasedwin7@gmail.com",
    url="https://github.com/yourusername/gui-tester",  # Adjust URL as needed
    packages=find_packages(),
    install_requires=[
        "pyautogui",
        "opencv-python",
        "numpy",
        "easyocr",
        "pillow",
        "screeninfo",
        "scikit-image",
        "pandas",
    ],
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
    ],
    python_requires=">=3.6",
)
