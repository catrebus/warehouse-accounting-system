from PyQt6.QtCore import QSize, Qt
from PyQt6.QtWidgets import QLabel, QWidget, QWIDGETSIZE_MAX, QVBoxLayout, QStackedLayout

from ui.base_window import BaseWindow
from ui.ui_elements.nav_panel import NavPanel


class MainWindow(BaseWindow):

    # Характеристики окна
    widowTitle: str = 'Система складского учета - Главная страница'
    windowSize: QSize = QSize(960, 540)
    resizable: bool = True
    windowIconPath: str = 'assets/icons/app_icon.png'

    def __init__(self, user):
        super().__init__()
        self.user = user
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
        contentLayout.setContentsMargins(80,0,0,0)
        contentLayout.setSpacing(0)
        contentLayout.addStretch()

        # Заголовок
        titleLabel = QLabel("Система складского учета")
        titleLabel.setStyleSheet("font-size: 70px")
        contentLayout.addWidget(titleLabel, alignment=Qt.AlignmentFlag.AlignHCenter)

        # Приветствие
        hiLabel = QLabel(f'Добро пожаловать, {self.user.login}')
        hiLabel.setStyleSheet("font-size: 20px")
        contentLayout.addWidget(hiLabel, alignment=Qt.AlignmentFlag.AlignHCenter)

        contentLayout.addStretch()
        mainLayout.addWidget(contentWidget)

        """Навигационная панель"""
        self.navPanel = NavPanel(self)
        mainLayout.addWidget(self.navPanel)

        self.setLayout(mainLayout)
