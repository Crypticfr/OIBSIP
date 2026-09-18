import sys

try:
    import pyttsx3
    TTS_AVAILABLE = True
except ImportError:
    TTS_AVAILABLE = False
    print("Warning: pyttsx3 not found. Text-to-Speech will fallback to print.", file=sys.stderr)

import queue
import threading

class TextToSpeech:
    def __init__(self):
        self.listeners = []
        self.queue = queue.Queue()
        self.worker_thread = threading.Thread(target=self._tts_worker, daemon=True)
        self.worker_thread.start()

    def _tts_worker(self):
        engine = None
        if TTS_AVAILABLE:
            try:
                engine = pyttsx3.init()
                # Set a reasonable speaking rate
                engine.setProperty('rate', 170)
            except Exception as e:
                print(f"Warning: Failed to initialize pyttsx3 engine: {e}. Falling back to print.", file=sys.stderr)
                engine = None

        while True:
            item = self.queue.get()
            if item is None:
                break
            text, completion_evt, on_finish = item
            try:
                if engine:
                    engine.say(text)
                    engine.runAndWait()
            except Exception as e:
                print(f"Error during speech synthesis: {e}", file=sys.stderr)
            finally:
                if on_finish:
                    try:
                        on_finish()
                    except Exception as e:
                        print(f"Error in on_finish callback: {e}", file=sys.stderr)
                if completion_evt:
                    completion_evt.set()
                self.queue.task_done()

    def add_listener(self, callback):
        """Register a callback that receives every text spoken by the assistant."""
        if callback not in self.listeners:
            self.listeners.append(callback)

    def remove_listener(self, callback):
        """Unregister a previously added callback."""
        if callback in self.listeners:
            self.listeners.remove(callback)

    def speak(self, text: str, notify_listeners: bool = True, block: bool = True, on_finish: callable = None):
        """
        Speaks the text, or prints it if TTS engine is unavailable.
        Uses a dedicated thread to ensure thread-safety with COM on Windows.
        """
        print(f"Assistant: {text}")
        if notify_listeners:
            for callback in list(self.listeners):
                try:
                    callback(text)
                except Exception as e:
                    print(f"Speech listener callback error: {e}", file=sys.stderr)

        completion_evt = threading.Event() if block else None
        self.queue.put((text, completion_evt, on_finish))

        if block and completion_evt:
            completion_evt.wait()

tts_engine = TextToSpeech()

def speak(text: str, notify_listeners: bool = True, block: bool = True, on_finish: callable = None):
    """Global helper function to speak text."""
    tts_engine.speak(text, notify_listeners=notify_listeners, block=block, on_finish=on_finish)

def add_speech_listener(callback):
    """Register a listener for assistant speech events."""
    tts_engine.add_listener(callback)

def remove_speech_listener(callback):
    """Unregister a listener for assistant speech events."""
    tts_engine.remove_listener(callback)
