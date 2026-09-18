# -*- coding: utf-8 -*-
import unittest
from unittest.mock import patch
import io
import sys
import tempfile
import os
from bmi_calculator import cli

class TestBMICLI(unittest.TestCase):

    @patch('builtins.input', side_effect=["abc", "-10", "0", "70.5"])
    def test_prompt_positive_float_reprompts(self, mock_input):
        """Test prompt_positive_float repeatedly asks until valid positive number."""
        captured = io.StringIO()
        sys.stdout = captured
        try:
            val = cli.prompt_positive_float("Enter weight: ", "Weight")
            self.assertEqual(val, 70.5)
        finally:
            sys.stdout = sys.__stdout__

        output = captured.getvalue()
        self.assertIn("Invalid input for Weight", output)
        self.assertIn("must be greater than 0", output)

    @patch('builtins.input', side_effect=["Alice", "68", "1.72", "n"])
    def test_run_cli_single_run(self, mock_input):
        """Test end-to-end CLI execution flow with named user."""
        captured = io.StringIO()
        sys.stdout = captured
        try:
            cli.run_cli(save_to_db=False)
        finally:
            sys.stdout = sys.__stdout__

        output = captured.getvalue()
        self.assertIn("BMI RESULT", output)
        self.assertIn("User          : Alice", output)
        self.assertIn("22.99", output)
        self.assertIn("Normal weight", output)

if __name__ == '__main__':
    unittest.main()