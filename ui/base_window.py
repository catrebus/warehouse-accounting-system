from PyQt6.QtCore import QSize
from PyQt6.QtGui import QIcon
from PyQt6.QtWidgets import QWidget, QWIDGETSIZE_MAX, QSizePolicy, QMainWindow


class BaseWindow(QWidget):
    """Абстрактное окно для применения характеристик окон"""
    widowTitle:str = ''
    windowSize: QSize = QSize(0, 0)
    resizable: bool = False
    windowIconPath: str = ''

    def apply_window_properties(self, windowManager):
        windowManager.setWindowTitle(self.widowTitle)
        windowManager.setWindowIcon(QIcon(self.windowIconPath))

        if not self.resizable:
            windowManager.setFixedSize(self.windowSize)
        else:
            windowManager.setMinimumSize(self.windowSize)
            windowManager.setMaximumSize(QSize(QWIDGETSIZE_MAX, QWIDGETSIZE_MAX))

            windowManager.setSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Expanding)







