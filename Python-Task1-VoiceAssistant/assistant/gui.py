# -*- coding: utf-8 -*-
import tkinter as tk
from tkinter import ttk, scrolledtext
import threading
import datetime
from .speech import listen
from .commands import process_command
from .tts import speak, add_speech_listener, remove_speech_listener

import os

INTERN_NAME = os.environ.get("OIBSIP_NAME", "Subhajit Samajpati")
INTERN_TRACK = "Python Development"
TASK_TITLE = "Voice Assistant (Task 1)"

class VoiceAssistantGUI:
    def __init__(self, root: tk.Tk, show_splash: bool = True, splash_duration: int = 2800):
        self.root = root
        self.root.title("Voice Assistant - OIBSIP")
        self.root.geometry("540x700")
        self.root.minsize(460, 580)
        self.root.configure(bg="#1e1e2e")

        self.is_busy = False
        self.speaker_buttons = []
        self.splash_frame = None
        self._splash_after_id = None
        self._welcome_after_id = None

        # Register speech listener so TTS output appears in transcript
        self._speech_callback = lambda text: self.root.after(0, self._on_assistant_speech, text)
        add_speech_listener(self._speech_callback)

        # Cleanup on close
        self.root.protocol("WM_DELETE_WINDOW", self._on_close)

        if show_splash:
            self._show_splash_screen(duration_ms=splash_duration)
        else:
            self._build_ui()
            self._welcome_after_id = self.root.after(500, self._welcome)

    def _show_splash_screen(self, duration_ms: int = 2800):
        self.splash_frame = tk.Frame(self.root, bg="#11111b")
        self.splash_frame.pack(fill=tk.BOTH, expand=True)

        # Center card container
        card = tk.Frame(
            self.splash_frame,
            bg="#181825",
            padx=28,
            pady=32,
            highlightbackground="#89b4fa",
            highlightthickness=1
        )
        card.place(relx=0.5, rely=0.5, anchor=tk.CENTER, relwidth=0.88)

        badge = tk.Label(
            card,
            text="OASIS INFOBYTE (OIBSIP)",
            font=("Segoe UI", 12, "bold"),
            fg="#89b4fa",
            bg="#181825"
        )
        badge.pack(pady=(0, 4))

        subtitle = tk.Label(
            card,
            text="PROJECT DEMO WALKTHROUGH",
            font=("Segoe UI", 9, "bold"),
            fg="#6c7086",
            bg="#181825"
        )
        subtitle.pack(pady=(0, 20))

        # Divider
        divider = tk.Frame(card, height=1, bg="#313244")
        divider.pack(fill=tk.X, pady=(0, 18))

        # Required fields for OIBSIP demo video
        fields = [
            ("Full Name", INTERN_NAME, "#cdd6f4"),
            ("Assigned Track", INTERN_TRACK, "#a6e3a1"),
            ("Task Title", TASK_TITLE, "#f9e2af"),
        ]

        for label_text, value_text, color in fields:
            row = tk.Frame(card, bg="#181825")
            row.pack(fill=tk.X, pady=6)

            lbl = tk.Label(
                row,
                text=f"{label_text}:",
                font=("Segoe UI", 9, "bold"),
                fg="#a6adc8",
                bg="#181825",
                width=14,
                anchor="w"
            )
            lbl.pack(side=tk.LEFT)

            val = tk.Label(
                row,
                text=value_text,
                font=("Segoe UI", 11, "bold"),
                fg=color,
                bg="#181825",
                anchor="w"
            )
            val.pack(side=tk.LEFT, fill=tk.X, expand=True)

        divider2 = tk.Frame(card, height=1, bg="#313244")
        divider2.pack(fill=tk.X, pady=(18, 14))

        self.splash_timer_lbl = tk.Label(
            card,
            text="Initializing assistant in 3s... (click to skip)",
            font=("Segoe UI", 8, "italic"),
            fg="#585b70",
            bg="#181825"
        )
        self.splash_timer_lbl.pack()

        # Allow user to click to dismiss immediately
        self.splash_frame.bind("<Button-1>", lambda e: self._dismiss_splash())
        card.bind("<Button-1>", lambda e: self._dismiss_splash())

        # Auto transition after duration_ms
        self._splash_after_id = self.root.after(duration_ms, self._dismiss_splash)

    def _dismiss_splash(self):
        if self._splash_after_id:
            try:
                self.root.after_cancel(self._splash_after_id)
            except Exception:
                pass
            self._splash_after_id = None

        if self.splash_frame:
            self.splash_frame.destroy()
            self.splash_frame = None
            self._build_ui()
            self._welcome_after_id = self.root.after(400, self._welcome)

    def _build_ui(self):
        # 1. Header Frame
        header_frame = tk.Frame(self.root, bg="#181825", padx=16, pady=14)
        header_frame.pack(fill=tk.X, side=tk.TOP)

        title_label = tk.Label(
            header_frame,
            text="[Voice Assistant]",
            font=("Segoe UI", 16, "bold"),
            fg="#cdd6f4",
            bg="#181825"
        )
        title_label.pack(anchor="w")

        subtitle_label = tk.Label(
            header_frame,
            text="OIBSIP Python Development - Task 1",
            font=("Segoe UI", 9),
            fg="#a6adc8",
            bg="#181825"
        )
        subtitle_label.pack(anchor="w")

        # Status Badge
        self.status_badge = tk.Label(
            header_frame,
            text="● Ready",
            font=("Segoe UI", 10, "bold"),
            fg="#a6e3a1",
            bg="#313244",
            padx=10,
            pady=3,
            relief=tk.FLAT
        )
        self.status_badge.pack(anchor="e", pady=(4, 0))

        # 2. Quick Actions Frame
        quick_frame = tk.Frame(self.root, bg="#1e1e2e", padx=12, pady=8)
        quick_frame.pack(fill=tk.X)

        quick_label = tk.Label(
            quick_frame,
            text="Quick Commands:",
            font=("Segoe UI", 9),
            fg="#6c7086",
            bg="#1e1e2e"
        )
        quick_label.pack(side=tk.LEFT, padx=(0, 6))

        quick_commands = [
            ("Hello", "hello"),
            ("Time", "what is the time"),
            ("Date", "what is today's date"),
            ("Search", "search oasis infobyte"),
        ]

        for text, cmd in quick_commands:
            btn = tk.Button(
                quick_frame,
                text=text,
                font=("Segoe UI", 8, "bold"),
                bg="#313244",
                fg="#cdd6f4",
                activebackground="#45475a",
                activeforeground="#cdd6f4",
                relief=tk.FLAT,
                bd=0,
                padx=8,
                pady=2,
                cursor="hand2",
                command=lambda c=cmd: self.send_text_command(c)
            )
            btn.pack(side=tk.LEFT, padx=3)

        # 3. Transcript Frame
        transcript_frame = tk.Frame(self.root, bg="#1e1e2e", padx=12, pady=4)
        transcript_frame.pack(fill=tk.BOTH, expand=True)

        self.transcript = scrolledtext.ScrolledText(
            transcript_frame,
            wrap=tk.WORD,
            font=("Segoe UI", 10),
            bg="#181825",
            fg="#cdd6f4",
            insertbackground="#cdd6f4",
            bd=0,
            padx=12,
            pady=12,
            relief=tk.FLAT
        )
        self.transcript.pack(fill=tk.BOTH, expand=True)

        # Text styles
        self.transcript.tag_config("time", foreground="#585b70", font=("Segoe UI", 8))
        self.transcript.tag_config("user_tag", foreground="#89b4fa", font=("Segoe UI", 10, "bold"))
        self.transcript.tag_config("user_msg", foreground="#b4befe")
        self.transcript.tag_config("asst_tag", foreground="#a6e3a1", font=("Segoe UI", 10, "bold"))
        self.transcript.tag_config("asst_msg", foreground="#cdd6f4")
        self.transcript.tag_config("sys_msg", foreground="#f9e2af", font=("Segoe UI", 9, "italic"))
        self.transcript.config(state=tk.DISABLED)

        # 4. Microphone / Voice Action Card
        mic_card = tk.Frame(self.root, bg="#181825", padx=12, pady=10)
        mic_card.pack(fill=tk.X, padx=12, pady=(6, 4))

        self.mic_btn = tk.Button(
            mic_card,
            text="Tap to Speak (Mic)",
            font=("Segoe UI", 12, "bold"),
            bg="#89b4fa",
            fg="#11111b",
            activebackground="#b4befe",
            activeforeground="#11111b",
            relief=tk.FLAT,
            bd=0,
            pady=10,
            cursor="hand2",
            command=self.start_listening_thread
        )
        self.mic_btn.pack(fill=tk.X)

        # 5. Text Input Frame
        input_frame = tk.Frame(self.root, bg="#1e1e2e")
        input_frame.pack(fill=tk.X, padx=12, pady=(4, 12))

        self.entry_var = tk.StringVar()
        self.entry = tk.Entry(
            input_frame,
            textvariable=self.entry_var,
            font=("Segoe UI", 11),
            bg="#313244",
            fg="#cdd6f4",
            insertbackground="#cdd6f4",
            bd=0,
            relief=tk.FLAT
        )
        self.entry.pack(side=tk.LEFT, fill=tk.BOTH, expand=True, ipady=8, padx=(0, 8))
        self.entry.bind("<Return>", lambda event: self.send_text_command())

        self.send_btn = tk.Button(
            input_frame,
            text="Send",
            font=("Segoe UI", 10, "bold"),
            bg="#45475a",
            fg="#cdd6f4",
            activebackground="#585b70",
            activeforeground="#cdd6f4",
            relief=tk.FLAT,
            bd=0,
            padx=16,
            cursor="hand2",
            command=lambda: self.send_text_command()
        )
        self.send_btn.pack(side=tk.RIGHT, fill=tk.Y)

    def _welcome(self):
        self._welcome_after_id = None
        self._append_message("System", "Assistant is ready. Click 'Tap to Speak' or type a message below.", tag="sys_msg")
        threading.Thread(target=lambda: speak("Voice Assistant is ready. How can I help you?"), daemon=True).start()

    def _set_status(self, text: str, fg: str):
        self.status_badge.config(text=f"● {text}", fg=fg)

    def _append_message(self, sender: str, message: str, tag: str = None):
        self.transcript.config(state=tk.NORMAL)
        timestamp = datetime.datetime.now().strftime("%I:%M %p")
        
        self.transcript.insert(tk.END, f"[{timestamp}] ", "time")
        if sender == "You":
            self.transcript.insert(tk.END, f"{sender}: ", "user_tag")
            self.transcript.insert(tk.END, f"{message} ", "user_msg")
            self._insert_speaker_btn(message)
            self.transcript.insert(tk.END, "\n\n")
        elif sender == "Assistant":
            self.transcript.insert(tk.END, f"{sender}: ", "asst_tag")
            self.transcript.insert(tk.END, f"{message} ", "asst_msg")
            self._insert_speaker_btn(message)
            self.transcript.insert(tk.END, "\n\n")
        else:
            self.transcript.insert(tk.END, f"{message}\n\n", tag or "sys_msg")

        self.transcript.see(tk.END)
        self.transcript.config(state=tk.DISABLED)

    def _insert_speaker_btn(self, message: str):
        btn = tk.Button(
            self.transcript,
            text="🔊",
            font=("Segoe UI", 9),
            bg="#313244",
            fg="#89b4fa",
            activebackground="#45475a",
            activeforeground="#b4befe",
            relief=tk.FLAT,
            bd=0,
            padx=4,
            pady=0,
            cursor="hand2",
            command=lambda m=message: self.talkback_message(m)
        )
        if hasattr(self, "speaker_buttons"):
            self.speaker_buttons.append(btn)
        self.transcript.window_create(tk.END, window=btn)

    def talkback_message(self, message: str):
        """Talks back the specified message using pyttsx3 without duplicating it in transcript."""
        if not message or not message.strip():
            return

        self._set_status("Speaking...", "#89b4fa")
        speak(
            message,
            notify_listeners=False,
            block=False,
            on_finish=lambda: self.root.after(0, self._on_talkback_done)
        )

    def _on_talkback_done(self):
        if not self.is_busy:
            self._set_status("Ready", "#a6e3a1")

    def _on_assistant_speech(self, text: str):
        self._append_message("Assistant", text)

    def send_text_command(self, explicit_cmd: str = None):
        if self.is_busy:
            return
        
        cmd = explicit_cmd if explicit_cmd is not None else self.entry_var.get().strip()
        if not cmd:
            return

        self.entry_var.set("")
        self._append_message("You", cmd)
        
        threading.Thread(target=self._process_command_worker, args=(cmd,), daemon=True).start()

    def start_listening_thread(self):
        if self.is_busy:
            return
        threading.Thread(target=self._listen_worker, daemon=True).start()

    def _listen_worker(self):
        self.is_busy = True
        self.root.after(0, lambda: self._set_busy_state("Listening...", "#f38ba8", "Listening... (Speak now)"))

        try:
            command = listen(text_mode=False)
            if command and command not in ("ERROR_UNKNOWN", "ERROR_REQUEST"):
                self.root.after(0, lambda: self._append_message("You", command))
            self._process_command_worker(command)
        except Exception as e:
            self.root.after(0, lambda: self._append_message("System", f"Voice error: {e}", "sys_msg"))
            self.root.after(0, self._set_idle_state)

    def _process_command_worker(self, command: str):
        self.is_busy = True
        self.root.after(0, lambda: self._set_busy_state("Processing...", "#f9e2af", "Processing..."))

        should_exit = False
        try:
            should_exit = process_command(command)
        except Exception as e:
            self.root.after(0, lambda: self._append_message("System", f"Execution error: {e}", "sys_msg"))

        if should_exit:
            self.root.after(0, lambda: self._set_status("Closing...", "#f38ba8"))
            self.root.after(1500, self.root.destroy)
        else:
            self.root.after(0, self._set_idle_state)

    def _set_busy_state(self, status: str, color: str, btn_text: str):
        self._set_status(status, color)
        self.mic_btn.config(text=btn_text, bg=color, state=tk.DISABLED)
        self.send_btn.config(state=tk.DISABLED)

    def _set_idle_state(self):
        self.is_busy = False
        self._set_status("Ready", "#a6e3a1")
        self.mic_btn.config(text="Tap to Speak (Mic)", bg="#89b4fa", state=tk.NORMAL)
        self.send_btn.config(state=tk.NORMAL)

    def _on_close(self):
        if self._welcome_after_id:
            try:
                self.root.after_cancel(self._welcome_after_id)
            except Exception:
                pass
            self._welcome_after_id = None
        if self._splash_after_id:
            try:
                self.root.after_cancel(self._splash_after_id)
            except Exception:
                pass
            self._splash_after_id = None
        remove_speech_listener(self._speech_callback)
        self.root.destroy()

def launch_gui(show_splash: bool = True):
    root = tk.Tk()
    app = VoiceAssistantGUI(root, show_splash=show_splash)
    root.mainloop()

if __name__ == "__main__":
    launch_gui()