from PyQt6.QtGui import QCursor, QPixmap
from PyQt6.QtWidgets import QApplication
from base.folders import cursors
import sys

application = QApplication(sys.argv)

class CursorCreator:
    def create(path, x=27, y=27):
        return QCursor(QPixmap(f"{path}.png"), x, y)

class Cursor:
    Hand = CursorCreator.create(cursors.path("hand"))
    Cursor = CursorCreator.create(cursors.path("cursor"))
