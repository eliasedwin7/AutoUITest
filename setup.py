# setup.py
from setuptools import setup, find_packages

setup(
    name='gui-tester',
    version='0.1.0',
    description='A tool for GUI automation testing',
    author='Your Name',
    author_email='your.email@example.com',
    url='https://github.com/yourusername/gui-tester',  # Adjust URL as needed
    packages=find_packages(),
    install_requires=[
        'pyautogui',
        'pillow',
    ],
    classifiers=[
        'Programming Language :: Python :: 3',
        'License :: OSI Approved :: MIT License',
        'Operating System :: OS Independent',
    ],
    python_requires='>=3.6',
)
