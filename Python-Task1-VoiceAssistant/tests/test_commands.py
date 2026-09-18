import unittest
from unittest.mock import patch, MagicMock
from assistant import commands

class TestCommands(unittest.TestCase):

    @patch('assistant.commands.speak')
    @patch('assistant.commands.datetime')
    def test_handle_greeting(self, mock_datetime, mock_speak):
        # Mock time to be morning (10 AM)
        mock_now = MagicMock()
        mock_now.hour = 10
        mock_datetime.datetime.now.return_value = mock_now

        self.assertTrue(commands.handle_greeting("hello assistant"))
        mock_speak.assert_called_with("Good morning! How can I help you today?")

        # Mock time to be afternoon (14 PM)
        mock_now.hour = 14
        self.assertTrue(commands.handle_greeting("hi there"))
        mock_speak.assert_called_with("Good afternoon! How can I help you today?")

        # Mock time to be evening (20 PM)
        mock_now.hour = 20
        self.assertTrue(commands.handle_greeting("hey"))
        mock_speak.assert_called_with("Good evening! How can I help you today?")

        # Capitalized greetings
        self.assertTrue(commands.handle_greeting("Hello"))
        self.assertTrue(commands.handle_greeting("HELLO"))
        self.assertTrue(commands.handle_greeting("Good Morning"))

        self.assertFalse(commands.handle_greeting("do something else"))

    @patch('assistant.commands.speak')
    @patch('assistant.commands.datetime')
    def test_handle_datetime(self, mock_datetime, mock_speak):
        mock_now = MagicMock()
        mock_now.strftime.side_effect = lambda fmt: "10:30 AM" if "%M" in fmt else "January 01, 2024"
        mock_datetime.datetime.now.return_value = mock_now

        self.assertTrue(commands.handle_datetime("what is the time"))
        mock_speak.assert_called_with("The current time is 10:30 AM.")

        # Capitalized time and date
        self.assertTrue(commands.handle_datetime("What is the TIME?"))
        self.assertTrue(commands.handle_datetime("tell me the DATE"))

        self.assertTrue(commands.handle_datetime("tell me the date"))
        mock_speak.assert_called_with("Today's date is January 01, 2024.")

        self.assertFalse(commands.handle_datetime("nothing here"))

    @patch('assistant.commands.speak')
    @patch('assistant.commands.webbrowser.open')
    def test_handle_search(self, mock_open, mock_speak):
        # Direct search without 'for'
        self.assertTrue(commands.handle_search("search fitgirl repacks"))
        mock_speak.assert_called_with("Searching the web for fitgirl repacks")
        mock_open.assert_called_with("https://www.google.com/search?q=fitgirl+repacks")

        self.assertTrue(commands.handle_search("search for python programming"))
        mock_speak.assert_called_with("Searching the web for python programming")
        mock_open.assert_called_with("https://www.google.com/search?q=python+programming")

        self.assertTrue(commands.handle_search("open google and search for oasis infobyte"))
        mock_open.assert_called_with("https://www.google.com/search?q=oasis+infobyte")

        self.assertTrue(commands.handle_search("google machine learning"))
        mock_speak.assert_called_with("Searching the web for machine learning")
        mock_open.assert_called_with("https://www.google.com/search?q=machine+learning")

        self.assertTrue(commands.handle_search("search"))
        mock_speak.assert_called_with("What would you like me to search for?")

        self.assertFalse(commands.handle_search("just do it"))

    @patch('assistant.commands.speak')
    def test_process_command_exits(self, mock_speak):
        self.assertTrue(commands.process_command("exit please"))
        mock_speak.assert_called_with("Goodbye! Have a great day.")

        self.assertTrue(commands.process_command("quit now"))
        self.assertTrue(commands.process_command("stop listening"))
        self.assertTrue(commands.process_command("bye"))
        self.assertTrue(commands.process_command("EXIT"))
        self.assertTrue(commands.process_command("Quit"))

    @patch('assistant.commands.speak')
    def test_process_command_errors(self, mock_speak):
        self.assertFalse(commands.process_command("ERROR_UNKNOWN"))
        mock_speak.assert_called_with("I couldn't quite catch that. Could you please repeat?")

        self.assertFalse(commands.process_command("ERROR_REQUEST"))
        mock_speak.assert_called_with("I'm having trouble connecting to the speech recognition service. Please check your internet.")

    @patch('assistant.commands.speak')
    def test_process_command_unrecognized(self, mock_speak):
        self.assertFalse(commands.process_command("do a backflip"))
        mock_speak.assert_called_with("I'm not sure how to help with that yet.")

if __name__ == '__main__':
    unittest.main()
