from PyQt6.QtCore import QSize
from PyQt6.QtGui import QIcon
from PyQt6.QtWidgets import QWidget, QWIDGETSIZE_MAX, QSizePolicy


class BaseWindow(QWidget):
    """Абстрактное окно для применения характеристик окон"""
    widowTitle:str = ''
    windowSize: QSize = QSize(0, 0)
    resizable: bool = False
    windowIconPath: str = ''

    def apply_window_properties(self, windowManager):
        windowManager.setWindowTitle(self.widowTitle)
        windowManager.setWindowIcon(QIcon(self.windowIconPath))

        windowManager.setMinimumSize(QSize(0, 0))
        windowManager.setMaximumSize(QSize(QWIDGETSIZE_MAX, QWIDGETSIZE_MAX))

        if not self.resizable:
            windowManager.setFixedSize(self.windowSize)

        else:
            windowManager.setMinimumSize(QSize(0, 0))
            windowManager.setMaximumSize(QSize(QWIDGETSIZE_MAX, QWIDGETSIZE_MAX))

            windowManager.resize(self.windowSize)
            windowManager.adjustSize()

            windowManager.setSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Expanding)



