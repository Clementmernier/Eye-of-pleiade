import sys
import os
import cv2

from PyQt6.QtWidgets import (
    QApplication, QWidget, QVBoxLayout, QPushButton,QLabel, QComboBox, QFileDialog, QStackedWidget)
import numpy as np

from PyQt6.QtCore import Qt, QTimer
from PyQt6.QtGui import QPixmap, QImage


def resource_path(filename):
    base = getattr(sys, '_MEIPASS', os.path.dirname(os.path.abspath(__file__)))
    return os.path.join(base, filename)



class MainMenu(QWidget):
    def __init__(self, stack):
        super().__init__()
        self.stack = stack

        self.layout = QVBoxLayout()

        self.logo = QLabel()
        self.logo.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.logo.setMinimumHeight(200)

        pixmap = QPixmap(resource_path("LogoCNES200.jpg"))

        self.logo.setPixmap(pixmap)

        self.layout.addWidget(self.logo)

        self.title = QLabel("Simulation Fauchée Satellite")
        self.layout.addWidget(self.title)

        self.camera_label = QLabel("Caméra USB : non détectée")
        self.layout.addWidget(self.camera_label)

        self.camera_list = QComboBox()
        self.layout.addWidget(self.camera_list)

        self.btn_detect = QPushButton("Détecter les caméras")
        self.btn_detect.clicked.connect(self.detect_cameras)
        self.layout.addWidget(self.btn_detect)

        self.folder_label = QLabel("Aucun dossier sélectionné")
        self.layout.addWidget(self.folder_label)

        self.btn_folder = QPushButton("Choisir dossier d'enregistrement")
        self.btn_folder.clicked.connect(self.choose_folder)
        self.layout.addWidget(self.btn_folder)

        self.btn_start = QPushButton("▶ Lancer la simulation")
        self.btn_start.clicked.connect(self.go_to_simulation)
        self.layout.addWidget(self.btn_start)

        self.setLayout(self.layout)
        self.detect_cameras()
        
    def detect_cameras(self):
        self.camera_list.clear()
        found = False

        for i in range(5):
            cap = cv2.VideoCapture(i)

            if cap.isOpened():
                ret, _ = cap.read()

                if ret:
                    self.camera_list.addItem(f"Caméra {i}", i)
                    found = True

            cap.release()

        self.camera_label.setText(
            "📷 Caméras détectées" if found else " ❌ Aucune caméra détectée"
        )

    def choose_folder(self):
        folder = QFileDialog.getExistingDirectory(self, "Choisir dossier")
        if folder:
            self.folder_label.setText(f"{folder}")

    def go_to_simulation(self):
        index = self.camera_list.currentData()
        if index is None:
            index = 0

        folder = self.folder_label.text()
        if folder == "Aucun dossier sélectionné":
            folder = "."

        sim = self.stack.parent().simulation
        sim.set_camera(index)
        sim.set_save_folder(folder)
        sim.start_sweep()
        self.stack.setCurrentIndex(1)



class SimulationPage(QWidget):
    def __init__(self, stack):
        super().__init__()

        self.stack = stack
        
        self.setWindowTitle("Simulation Fauchée Satellite")

        self.layout = QVBoxLayout()
        self.logo = QLabel()
        self.logo.setMinimumHeight(75)
        pixmap = QPixmap(resource_path("LogoCNES75.jpg"))
                

        self.logo.setPixmap(pixmap)
        self.layout.addWidget(self.logo)


        self.label = QLabel()
        self.layout.addWidget(self.label)

        from PyQt6.QtWidgets import QHBoxLayout
        btn_row = QHBoxLayout()

        self.btn_stop = QPushButton("⏹ Terminer la prise")
        self.btn_stop.clicked.connect(self.stop_sweep)
        btn_row.addWidget(self.btn_stop)

        self.btn_back = QPushButton("↩ Retour au menu")
        self.btn_back.clicked.connect(self.go_to_menu)
        btn_row.addWidget(self.btn_back)

        self.layout.addLayout(btn_row)

        self.setLayout(self.layout)

        self.cap = None
        self.save_folder = "."

        self.width = 1800
        self.height = 300

        self.buffer = np.zeros((self.height, self.width, 3), dtype=np.uint8)
        self.col_index = 0
        self.sweep_done = False

        self.timer = QTimer()
        self.timer.timeout.connect(self.update_frame)

    def set_camera(self, camera_index):
        if self.cap:
            self.cap.release()

        self.cap = cv2.VideoCapture(int(camera_index), cv2.CAP_ANY)

    def set_save_folder(self, folder):
        self.save_folder = folder

    def start_sweep(self):
        self.buffer = np.zeros((self.height, self.width, 3), dtype=np.uint8)
        self.col_index = 0
        self.sweep_done = False
        self.btn_stop.setEnabled(True)
        self.timer.start(30)

    def stop_sweep(self):
        if not self.sweep_done:
            self.timer.stop()
            self.sweep_done = True
            self.btn_stop.setEnabled(False)
            self.save_image()

    def go_to_menu(self):
        self.timer.stop()
        self.sweep_done = True
        self.stack.setCurrentIndex(0)

    # def update_frame(self):
    #     if self.cap is None:
    #         return

    #     ret, frame = self.cap.read()
    #     if not ret:
    #         return
    #     frame = cv2.resize(frame, (320, 240))

    #     center_row = frame[frame.shape[0] // 2, :]
    #     new_line = center_row.reshape(1, -1, 3)
    #     new_line = cv2.resize(new_line, (self.width, 1))

    #     self.buffer[:-1] = self.buffer[1:]

    #     self.buffer[-1] = new_line[0]

    #     self.display()
    def update_frame(self):
        if self.cap is None or self.sweep_done:
            return

        ret, frame = self.cap.read()
        if not ret:
            return

        frame = cv2.resize(frame, (320, 240))

        center_col = frame[:, frame.shape[1] // 2]
        new_col = center_col.reshape(-1, 1, 3)
        new_col = cv2.resize(new_col, (1, self.height))

        self.buffer[:, self.col_index] = new_col[:, 0]
        self.col_index += 1

        self.display()

        if self.col_index >= self.width:
            self.sweep_done = True
            self.timer.stop()
            self.save_image()

    def save_image(self):
        from datetime import datetime
        filename = datetime.now().strftime("fauchee_%Y%m%d_%H%M%S.png")
        path = os.path.join(self.save_folder, filename)
        cv2.imwrite(path, self.buffer)

    def display(self):
        img = cv2.cvtColor(self.buffer, cv2.COLOR_BGR2RGB)

        h, w, c = img.shape
        qimg = QImage(img.data, w, h, c * w, QImage.Format.Format_RGB888)

        self.label.setPixmap(QPixmap.fromImage(qimg))

    def closeEvent(self, event):
        if self.cap:
            self.cap.release()
        event.accept()

class App(QWidget):

    def __init__(self):
        super().__init__()

        self.setWindowTitle("Simulation Satellite")

        self.stack = QStackedWidget()

        self.menu = MainMenu(self.stack)
        self.simulation = SimulationPage(self.stack)

        self.stack.addWidget(self.menu)
        self.stack.addWidget(self.simulation)

        layout = QVBoxLayout()
        layout.addWidget(self.stack)

        self.setLayout(layout)


app = QApplication(sys.argv)
window = App()
window.resize(500, 400)
window.show()
sys.exit(app.exec())