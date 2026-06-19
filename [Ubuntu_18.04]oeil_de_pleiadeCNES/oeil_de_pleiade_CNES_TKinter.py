import os
import sys
import cv2
import tkinter as tk
from tkinter import filedialog, ttk
from PIL import Image, ImageTk
import numpy as np
from datetime import datetime

APP_TITLE = "Simulation Satellite CNES"
LOGO_FILE = "../logos/LogoCNES200.jpg"


def resource_path(filename):

    if hasattr(sys, "_MEIPASS"):
        return os.path.join(sys._MEIPASS, filename)

    return os.path.join(os.path.dirname(os.path.abspath(__file__)), filename)


class SatelliteApp:

    def __init__(self, root):

        self.root = root
        self.root.title(APP_TITLE)
        self.root.geometry("1200x700")
        self.root.configure(bg="white")

        self.cap = None
        self.camera_index = 0
        self.save_folder = os.getcwd()

        self.width = 1000
        self.height = 300

        self.buffer = np.full((self.height, self.width, 3), 255, dtype=np.uint8)

        self.col_index = 0
        self.running = False

        self.build_ui()

        self.detect_cameras()

    # --------------------------------------------------------
    # UI
    # --------------------------------------------------------

    def build_ui(self):

        self.logo_image = None

        try:
            logo = Image.open(resource_path(LOGO_FILE))
            logo = logo.resize((200, 200))
            self.logo_image = ImageTk.PhotoImage(logo)

            logo_label = tk.Label(
                self.root,
                image=self.logo_image,
                bg="white"
            )
            logo_label.pack(pady=10)

        except Exception:
            pass

        title = tk.Label(
            self.root,
            text="Simulation Fauchée Satellite",
            font=("Arial", 28, "bold"),
            fg="black",
            bg="white"
        )
        title.pack(pady=10)

        top_frame = tk.Frame(self.root, bg="white")
        top_frame.pack(pady=10)

        self.camera_label = tk.Label(
            top_frame,
            text="Caméra",
            font=("Arial", 14),
            fg="black",
            bg="white"
        )
        self.camera_label.pack()

        self.camera_combo = ttk.Combobox(
            top_frame,
            state="readonly",
            width=30
        )
        self.camera_combo.pack(pady=5)

        btn_detect = tk.Button(
            top_frame,
            text="Détecter les caméras",
            font=("Arial", 14),
            command=self.detect_cameras,
            height=2,
            width=25
        )
        btn_detect.pack(pady=5)

        btn_folder = tk.Button(
            top_frame,
            text="Choisir dossier sauvegarde",
            font=("Arial", 14),
            command=self.choose_folder,
            height=2,
            width=25
        )
        btn_folder.pack(pady=5)

        self.folder_label = tk.Label(
            top_frame,
            text=self.save_folder,
            font=("Arial", 10),
            fg="black",
            bg="white"
        )
        self.folder_label.pack(pady=5)

        btn_frame = tk.Frame(self.root, bg="white")
        btn_frame.pack(pady=10)

        self.start_btn = tk.Button(
            btn_frame,
            text="▶ LANCER",
            font=("Arial", 20, "bold"),
            bg="green",
            fg="white",
            width=15,
            height=2,
            command=self.start_sweep
        )
        self.start_btn.grid(row=0, column=0, padx=20)

        self.stop_btn = tk.Button(
            btn_frame,
            text="■ TERMINER",
            font=("Arial", 20, "bold"),
            bg="red",
            fg="white",
            width=15,
            height=2,
            state="disabled",
            command=self.stop_sweep
        )
        self.stop_btn.grid(row=0, column=1, padx=20)

        self.image_label = tk.Label(self.root, bg="white")
        self.image_label.pack(pady=20)

    # --------------------------------------------------------
    # Camera
    # --------------------------------------------------------

    def detect_cameras(self):

        self.camera_combo["values"] = []

        cameras = []

        for i in range(5):

            cap = cv2.VideoCapture(i)

            if cap.isOpened():

                ret, _ = cap.read()

                if ret:
                    cameras.append(f"Caméra {i}")

            cap.release()

        self.camera_combo["values"] = cameras

        if cameras:
            self.camera_combo.current(0)

    def open_camera(self):

        selected = self.camera_combo.current()

        if selected < 0:
            selected = 0

        self.camera_index = selected

        if self.cap:
            self.cap.release()

        self.cap = cv2.VideoCapture(self.camera_index)

    # --------------------------------------------------------
    # Folder
    # --------------------------------------------------------

    def choose_folder(self):

        folder = filedialog.askdirectory()

        if folder:

            self.save_folder = folder

            self.folder_label.config(text=folder)

    # --------------------------------------------------------
    # Simulation
    # --------------------------------------------------------

    def start_sweep(self):

        self.open_camera()

        self.buffer = np.full(
            (self.height, self.width, 3),
            255,
            dtype=np.uint8
        )

        self.col_index = 0

        self.running = True

        self.start_btn.config(state="disabled")
        self.stop_btn.config(state="normal")

        self.update_frame()

    def stop_sweep(self):

        self.running = False

        self.start_btn.config(state="normal")
        self.stop_btn.config(state="disabled")

        self.save_image()

    def update_frame(self):

        if not self.running:
            return

        if self.cap is None:
            return

        ret, frame = self.cap.read()

        if not ret:

            self.root.after(30, self.update_frame)
            return

        frame = cv2.resize(frame, (320, 240))

        center_col = frame[:, frame.shape[1] // 2]

        new_col = center_col.reshape(-1, 1, 3)

        new_col = cv2.resize(new_col, (1, self.height))

        if self.col_index < self.width:

            self.buffer[:, self.col_index] = new_col[:, 0]

            self.col_index += 1

        self.display_buffer()

        if self.col_index >= self.width:

            self.stop_sweep()
            return

        self.root.after(30, self.update_frame)

    # --------------------------------------------------------
    # Display
    # --------------------------------------------------------

    def display_buffer(self):

        rgb = cv2.cvtColor(self.buffer, cv2.COLOR_BGR2RGB)

        image = Image.fromarray(rgb)

        photo = ImageTk.PhotoImage(image=image)

        self.image_label.configure(image=photo)

        self.image_label.image = photo

    # --------------------------------------------------------
    # Save
    # --------------------------------------------------------

    def save_image(self):

        filename = datetime.now().strftime(
            "fauchee_%Y%m%d_%H%M%S.png"
        )

        path = os.path.join(self.save_folder, filename)

        cv2.imwrite(path, self.buffer)

        print("Image sauvegardée :", path)

    # --------------------------------------------------------
    # Close
    # --------------------------------------------------------

    def on_close(self):

        self.running = False

        if self.cap:
            self.cap.release()

        self.root.destroy()


# ------------------------------------------------------------
# MAIN
# ------------------------------------------------------------

root = tk.Tk()

app = SatelliteApp(root)

root.protocol("WM_DELETE_WINDOW", app.on_close)

root.mainloop()
