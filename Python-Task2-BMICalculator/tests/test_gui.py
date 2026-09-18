# -*- coding: utf-8 -*-
import unittest
import tkinter as tk
import tempfile
import os
from bmi_calculator.gui import BMICalculatorGUI

class TestBMICalculatorGUI(unittest.TestCase):
    def setUp(self):
        self.root = tk.Tk()
        self.root.withdraw()  # Headless mode
        tf = tempfile.NamedTemporaryFile(suffix=".db", delete=False)
        self.temp_db = tf.name
        tf.close()
        self.app = BMICalculatorGUI(self.root, show_splash=False, db_path=self.temp_db)

    def tearDown(self):
        try:
            self.root.destroy()
        except Exception:
            pass
        if os.path.exists(self.temp_db):
            try:
                os.remove(self.temp_db)
            except Exception:
                pass

    def test_gui_initialization(self):
        """Verify that tabs, buttons, entries, and labels exist."""
        self.assertIsNotNone(self.app.notebook)
        self.assertIsNotNone(self.app.calc_btn)
        self.assertIsNotNone(self.app.entry_weight)
        self.assertIsNotNone(self.app.entry_height)
        self.assertIsNotNone(self.app.bmi_display_lbl)
        self.assertIsNotNone(self.app.category_badge)

    def test_calculation_flow(self):
        """Test typing values and triggering calculation."""
        self.app.entry_weight.insert(0, "70")
        self.app.entry_height.insert(0, "1.75")
        self.app.perform_calculation()

        self.assertEqual(self.app.bmi_display_lbl.cget("text"), "22.86")
        self.assertEqual(self.app.category_badge.cget("text"), "Normal weight")

        # Verify record added to DB
        records = self.app.db.get_all_records()
        self.assertEqual(len(records), 1)
        self.assertEqual(records[0]["bmi"], 22.86)

    def test_unit_switching(self):
        """Test switching between metric and imperial input modes."""
        self.assertEqual(self.app.unit_mode.get(), "metric")
        self.app.unit_mode.set("imperial")
        self.app._on_unit_change()

        # Should have feet and inches entries now
        self.assertTrue(hasattr(self.app, "entry_ft"))
        self.assertTrue(hasattr(self.app, "entry_in"))

    def test_splash_screen(self):
        """Test splash screen renders and dismisses cleanly."""
        splash_root = tk.Tk()
        splash_root.withdraw()
        splash_app = BMICalculatorGUI(splash_root, show_splash=True, splash_duration=50, db_path=self.temp_db)
        self.assertIsNotNone(splash_app.splash_frame)
        splash_app._dismiss_splash()
        self.assertIsNone(splash_app.splash_frame)
        splash_root.destroy()

    def test_multi_user_gui(self):
        """Test calculating and saving records for different users in GUI."""
        self.app.active_user.set("Charlie")
        self.app.entry_weight.insert(0, "80")
        self.app.entry_height.insert(0, "1.80")
        self.app.perform_calculation()

        records = self.app.db.get_all_records(user_name="Charlie")
        self.assertEqual(len(records), 1)
        self.assertEqual(records[0]["user_name"], "Charlie")
        self.assertEqual(records[0]["bmi"], 24.69)

        # Test filtering
        self.app.filter_user.set("Charlie")
        self.app._on_filter_changed()
        self.assertEqual(len(self.app.tree.get_children()), 1)

if __name__ == '__main__':
    unittest.main()