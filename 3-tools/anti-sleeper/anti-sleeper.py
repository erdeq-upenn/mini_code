import tkinter as tk
from threading import Thread, Event
import pyautogui
import time
import random

class AntiSleepApp:
    def __init__(self, root):
        self.root = root
        self.root.title("Anti-Sleep Mouse Mover")

        # Create start/stop buttons
        self.start_button = tk.Button(root, text="Start", command=self.start)
        self.start_button.pack(padx=20, pady=10)

        self.stop_button = tk.Button(root, text="Stop", command=self.stop, state=tk.DISABLED)
        self.stop_button.pack(padx=20, pady=10)

        self.stop_event = Event()
        self.thread = None

    def move_mouse(self):
        while not self.stop_event.is_set():
            x, y = pyautogui.position()
            dx = random.randint(-5, 5)
            dy = random.randint(-5, 5)
            pyautogui.moveTo(x + dx, y + dy, duration=0.2)
            time.sleep(6)  # Wait 60 seconds before next move

    def start(self):
        if not self.thread or not self.thread.is_alive():
            self.stop_event.clear()
            self.thread = Thread(target=self.move_mouse)
            self.thread.daemon = True
            self.thread.start()
            self.start_button.config(state=tk.DISABLED)
            self.stop_button.config(state=tk.NORMAL)

    def stop(self):
        self.stop_event.set()
        self.start_button.config(state=tk.NORMAL)
        self.stop_button.config(state=tk.DISABLED)

if __name__ == "__main__":
    root = tk.Tk()
    app = AntiSleepApp(root)
    root.mainloop()

