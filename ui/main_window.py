from PyQt6.QtCore import QSize, Qt
from PyQt6.QtWidgets import QHBoxLayout, QLabel, QWidget, QWIDGETSIZE_MAX, QVBoxLayout, QStackedLayout

from ui.base_window import BaseWindow
from ui.nav_panel import NavPanel


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

        """Задний фон"""
        self.bgWidget = QWidget(self)
        self.bgWidget.setObjectName('bgWidget')
        self.bgWidget.resize(QSize(QWIDGETSIZE_MAX, QWIDGETSIZE_MAX))
        self.bgWidget.lower()

        """Главный layout"""
        mainLayout = QStackedLayout(self.bgWidget)
        mainLayout.setStackingMode(QStackedLayout.StackingMode.StackAll)
        mainLayout.setContentsMargins(0,0,0,0)
        mainLayout.setSpacing(0)

        """Контент страницы"""
        contentWidget = QWidget()
        contentLayout = QVBoxLayout(contentWidget)

        contentLabel = QLabel("Контент")
        contentLabel.setObjectName("content")
        contentLabel.setAlignment(Qt.AlignmentFlag.AlignCenter)
        contentLayout.addWidget(contentLabel)
        mainLayout.addWidget(contentWidget)


        """Навигационная панель"""
        self.navPanel = NavPanel(self)
        mainLayout.addWidget(self.navPanel)

        self.setLayout(mainLayout)