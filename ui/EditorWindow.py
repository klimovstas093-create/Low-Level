from PyQt6 import QtWidgets

import time

from ui.GameWindow import GameWindow

class EditorWindow(GameWindow):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs, devmode=True)
        save_btn = QtWidgets.QPushButton("Save")
        load_btn = QtWidgets.QPushButton("Load")

        layout = QtWidgets.QVBoxLayout()

        layout.addStretch()
        layout.addWidget(save_btn)
        layout.addWidget(load_btn)
        layout.addStretch()

        widget = QtWidgets.QWidget()
        widget.setLayout(layout)
        widget.setFixedWidth(200)

        self.layout().addWidget(widget)

    def show(self):
        self.MainWindow.widget.setCurrentIndex(2)

    def game_tick(self):
        self.now = time.time()
        dt = self.now - self.last_time 
        self.last_time = self.now
        self.update_cam(dt)

