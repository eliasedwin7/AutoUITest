import unittest
from unittest.mock import patch, MagicMock
from pathlib import Path
import json
import time
import os
from action_recorder import UserActionRecorder

class TestUserActionRecorder(unittest.TestCase):

    def setUp(self):
        self.test_dir = Path("test_dir")
        self.test_dir.mkdir(exist_ok=True)
        self.recorder = UserActionRecorder(base_dir=self.test_dir)

    def tearDown(self):
        for item in self.test_dir.iterdir():
            if item.is_file():
                item.unlink()
        self.test_dir.rmdir()

    def test_initialization(self):
        self.assertEqual(self.recorder.base_dir, self.test_dir)
        self.assertTrue((self.test_dir / "screenshots").exists())
        self.assertEqual(self.recorder.settings["idle_time_limit"], 5)
        self.assertFalse(self.recorder.state["recording"])

    @patch('action_recorder.mouse.Listener')
    @patch('action_recorder.keyboard.Listener')
    def test_start_stop_recording(self, mock_keyboard_listener, mock_mouse_listener):
        self.recorder.start_recording()
        self.assertTrue(self.recorder.state["recording"])
        self.recorder.stop_recording()
        self.assertFalse(self.recorder.state["recording"])

    @patch('action_recorder.pyautogui.position')
    @patch('action_recorder.pyautogui.screenshot')
    def test_record_action(self, mock_screenshot, mock_position):
        mock_position.return_value = MagicMock(x=100, y=200)
        mock_screenshot.return_value = MagicMock()

        self.recorder.on_click(100, 200, "left", True)
        self.assertEqual(len(self.recorder.actions), 1)
        self.assertEqual(self.recorder.actions[0]["action"], "click")

        self.recorder.on_press(MagicMock(char='a'))
        self.assertEqual(len(self.recorder.actions), 2)
        self.assertEqual(self.recorder.actions[1]["action"], "type")

    @patch('action_recorder.pyautogui.screenshot')
    def test_save_to_json(self, mock_screenshot):
        mock_screenshot.return_value = MagicMock()
        self.recorder.on_click(100, 200, "left", True)
        json_file = self.test_dir / "test_actions.json"
        self.recorder.save_to_json(json_file)

        with open(json_file, "r", encoding="utf-8") as file:
            data = json.load(file)
            self.assertIn("elements", data)
            self.assertEqual(len(data["elements"]), 1)
            self.assertEqual(data["elements"][0]["action"], "click")

if __name__ == "__main__":
    unittest.main()