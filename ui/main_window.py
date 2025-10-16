from PyQt6.QtCore import QSize

from ui.base_window import BaseWindow


class MainWindow(BaseWindow):

    # Характеристики окна
    widowTitle: str = 'Система складского учета - Главная страница'
    windowSize: QSize = QSize(960, 540)
    resizable: bool = True
    windowIconPath: str = 'assets/icons/app_icon.png'

    def __init__(self):
        super().__init__()


        # Инициализация пользовательского интерфейса
        self.init_ui()

    def init_ui(self):
        """Инициализация пользовательского интерфейса"""
        pass