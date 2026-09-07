# -*- coding: utf-8 -*-
import unittest
import tkinter as tk
from unittest.mock import patch, MagicMock
from assistant.gui import VoiceAssistantGUI
from assistant import tts

class TestVoiceAssistantGUI(unittest.TestCase):
    def setUp(self):
        self.root = tk.Tk()
        self.root.withdraw()  # Hide window during headless test execution
        self.app = VoiceAssistantGUI(self.root, show_splash=False)

    def tearDown(self):
        try:
            self.app._on_close()
        except Exception:
            pass

    def test_gui_initialization(self):
        """Test that GUI elements are properly initialized."""
        self.assertIsNotNone(self.app.transcript)
        self.assertIsNotNone(self.app.mic_btn)
        self.assertIsNotNone(self.app.send_btn)
        self.assertIsNotNone(self.app.entry)
        self.assertIn("Ready", self.app.status_badge.cget("text"))

    def test_speech_listener_callback(self):
        """Test that assistant speech appears in transcript."""
        test_message = "Test speech message"
        self.app._on_assistant_speech(test_message)
        self.root.update()
        content = self.app.transcript.get("1.0", tk.END)
        self.assertIn(test_message, content)

    @patch('assistant.gui.threading.Thread')
    def test_send_text_command(self, mock_thread):
        """Test typing a command and sending via GUI."""
        self.app.entry_var.set("what is the time")
        self.app.send_text_command()
        self.root.update()
        
        # Entry should be cleared
        self.assertEqual(self.app.entry_var.get(), "")
        # Transcript should include user message
        content = self.app.transcript.get("1.0", tk.END)
        self.assertIn("what is the time", content)
        # Background worker thread should have been spawned
        mock_thread.assert_called()

    @patch('assistant.gui.speak')
    def test_talkback_message(self, mock_speak):
        """Test talkback_message calls speak with notify_listeners=False."""
        self.app.talkback_message("Hello world")
        mock_speak.assert_called_once()
        args, kwargs = mock_speak.call_args
        self.assertEqual(args[0], "Hello world")
        self.assertFalse(kwargs.get("notify_listeners", True))

    @patch('assistant.gui.speak')
    def test_speaker_button_in_transcript(self, mock_speak):
        """Test that appending messages creates embedded speaker buttons."""
        self.app._append_message("Assistant", "Spoken response")
        self.root.update()
        content = self.app.transcript.get("1.0", tk.END)
        self.assertIn("Spoken response", content)
        # Directly invoke talkback
        self.app.talkback_message("Spoken response")
        self.root.update()

    def test_splash_screen(self):
        """Test splash screen renders title card and dismisses cleanly."""
        splash_root = tk.Tk()
        splash_root.withdraw()
        splash_app = VoiceAssistantGUI(splash_root, show_splash=True, splash_duration=50)
        self.assertIsNotNone(splash_app.splash_frame)
        # Dismiss
        splash_app._dismiss_splash()
        self.assertIsNone(splash_app.splash_frame)
        self.assertIsNotNone(splash_app.transcript)
        splash_root.destroy()

if __name__ == '__main__':
    unittest.main()