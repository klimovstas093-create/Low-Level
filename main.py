import traceback, os, applib
from base.MusicPlayer import MusicPlayer
import base.folders as folders
import base.functions as func

from PyQt6.QtWidgets import QApplication

from components.Block import Block
from components.Base import Base
from ui.ResourcePanel import ResourcePanel
from ui.MainWindow import MainWindow

from PyQt6.QtWidgets import QGraphicsItem

from base.font import application

def main()->int:
    try:
        folders.folder.plugins.init()

        folders.folder.plugins.call("pre_start", application)

        window = MainWindow()
        window.showFullScreen()

        resource_panel = ResourcePanel(window.GameWindow)
        resource_panel.show()
        resource_panel.setGeometry(10, 10, 200, 100)

        base = Base(window.GameWindow, 128, 128, "base", team="PlayerTeam", resource_panel=resource_panel)
        base.place()

        window.GameWindow.Base = base

        base.storage.add("lead", 3)

        folders.folder.plugins.call("start", window.GameWindow)

        MusicPlayer.start()

    except Exception as e:
        folders.folder.log.write(traceback.format_exc(), type="StartError", set_error=True)
        return 1
    try:
        return application.exec()
    except Exception as e:
        folders.folder.log.write(traceback.format_exc(), type="RuntimeError", set_error=True)
        return 1

if __name__ == "__main__":
    os._exit(max(main(), applib._exit_code))