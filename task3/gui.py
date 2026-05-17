"""
gui.py - Beautiful Voice Assistant GUI
Run this file to launch the GUI version.
Make sure assistant.py is in the same folder.
Run: python gui.py
"""

import threading
import datetime
import customtkinter as ctk
from assistant import process_command, speak, listen, greet

ctk.set_appearance_mode("dark")
ctk.set_default_color_theme("blue")


class VoiceAssistantApp(ctk.CTk):
    def __init__(self):
        super().__init__()
        self.title("Voice Assistant")
        self.geometry("820x700")
        self.resizable(False, False)
        self.configure(fg_color="#0a0a12")
        self.is_listening = False
        self._build_ui()
        self.after(500, self._startup_greet)

    def _build_ui(self):
        # HEADER
        header = ctk.CTkFrame(self, fg_color="#10101c", corner_radius=0, height=72)
        header.pack(fill="x")
        header.pack_propagate(False)

        ctk.CTkLabel(
            header,
            text="  VOICE  ASSISTANT",
            font=ctk.CTkFont(family="Courier New", size=22, weight="bold"),
            text_color="#00d4ff"
        ).pack(side="left", padx=28, pady=18)

        self.status_label = ctk.CTkLabel(
            header,
            text="  READY",
            font=ctk.CTkFont(family="Courier New", size=13, weight="bold"),
            text_color="#00ff88"
        )
        self.status_label.pack(side="right", padx=28)

        # CHAT BOX
        chat_outer = ctk.CTkFrame(self, fg_color="#0a0a12")
        chat_outer.pack(fill="both", expand=True, padx=20, pady=(14, 0))

        self.chat_box = ctk.CTkTextbox(
            chat_outer,
            font=ctk.CTkFont(family="Courier New", size=14),
            fg_color="#0f0f1a",
            text_color="#dde8ff",
            border_color="#1e1e32",
            border_width=1,
            corner_radius=14,
            wrap="word",
            state="disabled",
            scrollbar_button_color="#1e1e32",
            scrollbar_button_hover_color="#2e2e52",
        )
        self.chat_box.pack(fill="both", expand=True)

        # QUICK COMMANDS
        quick_frame = ctk.CTkFrame(self, fg_color="#0a0a12")
        quick_frame.pack(fill="x", padx=20, pady=(10, 0))

        for cmd in ["Help", "Time", "Date", "Joke", "Reminders"]:
            ctk.CTkButton(
                quick_frame,
                text=cmd,
                font=ctk.CTkFont(family="Courier New", size=12),
                fg_color="#1a1a2e",
                hover_color="#2a2a4e",
                text_color="#00d4ff",
                border_color="#2a2a4e",
                border_width=1,
                corner_radius=20,
                height=30,
                width=90,
                command=lambda c=cmd: self._quick_command(c)
            ).pack(side="left", padx=4)

        # MIC BUTTON
        mic_outer = ctk.CTkFrame(self, fg_color="#0a0a12", height=110)
        mic_outer.pack(fill="x", padx=20, pady=(10, 0))
        mic_outer.pack_propagate(False)

        self.mic_btn = ctk.CTkButton(
            mic_outer,
            text="  TAP TO SPEAK",
            font=ctk.CTkFont(family="Courier New", size=16, weight="bold"),
            fg_color="#0f0f1a",
            hover_color="#001a22",
            text_color="#00d4ff",
            border_color="#00d4ff",
            border_width=2,
            corner_radius=40,
            height=58,
            width=300,
            command=self._toggle_listen
        )
        self.mic_btn.place(relx=0.5, rely=0.5, anchor="center")

        # TEXT INPUT
        input_frame = ctk.CTkFrame(self, fg_color="#0a0a12", height=66)
        input_frame.pack(fill="x", padx=20, pady=(6, 16))
        input_frame.pack_propagate(False)

        self.text_entry = ctk.CTkEntry(
            input_frame,
            placeholder_text="  Type a command and press Enter...",
            font=ctk.CTkFont(family="Courier New", size=13),
            fg_color="#0f0f1a",
            border_color="#1e1e32",
            text_color="#dde8ff",
            placeholder_text_color="#3a3a5a",
            corner_radius=12,
            height=44,
        )
        self.text_entry.pack(side="left", fill="x", expand=True, padx=(0, 10), pady=11)
        self.text_entry.bind("<Return>", lambda e: self._send_text())

        ctk.CTkButton(
            input_frame,
            text="Send",
            font=ctk.CTkFont(family="Courier New", size=13, weight="bold"),
            fg_color="#00d4ff",
            hover_color="#009abb",
            text_color="#0a0a12",
            corner_radius=12,
            height=44,
            width=100,
            command=self._send_text
        ).pack(side="right", pady=11)

    def _add_message(self, sender, text):
        self.chat_box.configure(state="normal")
        now = datetime.datetime.now().strftime("%H:%M")
        self.chat_box.insert("end", f"\n  [{now}]  ", "timestamp")
        if sender == "You":
            self.chat_box.insert("end", "You  ->  ", "you_label")
            self.chat_box.insert("end", f"{text}\n", "you_text")
        else:
            self.chat_box.insert("end", "Assistant  ->  ", "bot_label")
            self.chat_box.insert("end", f"{text}\n", "bot_text")
        self.chat_box.tag_config("timestamp", foreground="#303050")
        self.chat_box.tag_config("you_label", foreground="#ff4da6")
        self.chat_box.tag_config("you_text",  foreground="#f0d0ff")
        self.chat_box.tag_config("bot_label", foreground="#00d4ff")
        self.chat_box.tag_config("bot_text",  foreground="#c4e0ff")
        self.chat_box.configure(state="disabled")
        self.chat_box.see("end")

    def _set_status(self, text, color):
        self.status_label.configure(text=text, text_color=color)

    def _handle_response(self, command):
        self._add_message("You", command)
        response = process_command(command)
        if response == "QUIT":
            self._add_message("Assistant", "Goodbye! Have a great day!")
            threading.Thread(target=speak, args=("Goodbye! Have a great day!",), daemon=True).start()
            self.after(2000, self.destroy)
        else:
            self._add_message("Assistant", response)
            threading.Thread(target=speak, args=(response,), daemon=True).start()

    def _startup_greet(self):
        hour = datetime.datetime.now().hour
        if hour < 12:
            msg = "Good morning! I am your Voice Assistant. Say 'help' to see what I can do."
        elif hour < 18:
            msg = "Good afternoon! I am your Voice Assistant. Say 'help' to see what I can do."
        else:
            msg = "Good evening! I am your Voice Assistant. Say 'help' to see what I can do."
        self._add_message("Assistant", msg)
        threading.Thread(target=speak, args=(msg,), daemon=True).start()

    def _quick_command(self, cmd):
        mapping = {
            "Help":      "help",
            "Time":      "what time is it",
            "Date":      "what is today's date",
            "Joke":      "tell me a joke",
            "Reminders": "show my reminders",
        }
        self._handle_response(mapping.get(cmd, cmd.lower()))

    def _toggle_listen(self):
        if self.is_listening:
            return
        self.is_listening = True
        self.mic_btn.configure(text="  LISTENING...", fg_color="#1a0010", border_color="#ff006e", text_color="#ff006e")
        self._set_status("  LISTENING", "#ff006e")
        threading.Thread(target=self._listen_thread, daemon=True).start()

    def _listen_thread(self):
        import speech_recognition as sr
        recognizer = sr.Recognizer()
        with sr.Microphone() as source:
            recognizer.adjust_for_ambient_noise(source, duration=0.4)
            try:
                audio = recognizer.listen(source, timeout=6, phrase_time_limit=8)
            except sr.WaitTimeoutError:
                self.after(0, self._reset_mic)
                return
        try:
            command = recognizer.recognize_google(audio)
            self.after(0, lambda: self._handle_response(command))
        except sr.UnknownValueError:
            self.after(0, lambda: self._add_message("Assistant", "Sorry, I did not catch that. Please try again."))
        except sr.RequestError:
            self.after(0, lambda: self._add_message("Assistant", "Speech service unavailable. Check your internet."))
        self.after(0, self._reset_mic)

    def _reset_mic(self):
        self.is_listening = False
        self.mic_btn.configure(text="  TAP TO SPEAK", fg_color="#0f0f1a", border_color="#00d4ff", text_color="#00d4ff")
        self._set_status("  READY", "#00ff88")

    def _send_text(self):
        command = self.text_entry.get().strip()
        if command:
            self.text_entry.delete(0, "end")
            self._handle_response(command)


if __name__ == "__main__":
    app = VoiceAssistantApp()
    app.mainloop()