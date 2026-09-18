import argparse
from assistant.speech import listen
from assistant.commands import process_command
from assistant.tts import speak

def run_cli(text_mode: bool = False):
    speak("Initializing Voice Assistant. I am ready for your commands.")

    while True:
        # Listen for command
        command = listen(text_mode=text_mode)
        
        # Process command and check for exit
        should_exit = process_command(command)
        
        if should_exit:
            break

def main():
    parser = argparse.ArgumentParser(description="Python Voice Assistant (OIBSIP)")
    parser.add_argument('--cli', action='store_true', help="Run in terminal CLI mode instead of GUI")
    parser.add_argument('--text-mode', action='store_true', help="Force text input in CLI mode")
    parser.add_argument('--skip-splash', action='store_true', help="Skip the demo title card splash screen")
    args = parser.parse_args()

    if args.cli or args.text_mode:
        run_cli(text_mode=args.text_mode)
    else:
        try:
            from assistant.gui import launch_gui
            launch_gui(show_splash=not args.skip_splash)
        except Exception as e:
            print(f"Failed to launch GUI ({e}). Falling back to CLI mode.")
            run_cli(text_mode=args.text_mode)

if __name__ == "__main__":
    main()
