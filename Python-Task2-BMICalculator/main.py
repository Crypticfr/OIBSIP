# -*- coding: utf-8 -*-
"""
Main entry point for BMI Calculator (OIBSIP Task 2).
Supports both Graphical Interface (default) and Command-Line Interface (--cli).
"""
import argparse
import sys

def main():
    parser = argparse.ArgumentParser(description="BMI Calculator - Oasis Infobyte (OIBSIP) Task 2")
    parser.add_argument("--cli", action="store_true", help="Run the command-line interface instead of the GUI")
    parser.add_argument("--skip-splash", action="store_true", help="Skip the demo video title card splash screen in GUI")
    args = parser.parse_args()

    if args.cli:
        from bmi_calculator.cli import run_cli
        run_cli()
    else:
        try:
            from bmi_calculator.gui import launch_gui
            launch_gui(show_splash=not args.skip_splash)
        except Exception as e:
            print(f"Failed to launch GUI ({e}). Falling back to CLI mode.\n")
            from bmi_calculator.cli import run_cli
            run_cli()

if __name__ == "__main__":
    main()