from PyQt6.QtCore import QSize, Qt
from PyQt6.QtWidgets import QLabel, QWidget, QWIDGETSIZE_MAX, QVBoxLayout, QStackedLayout

from ui.base_window import BaseWindow
from ui.main_windows.nav_panel import NavPanel


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
        contentLayout.setContentsMargins(80,10,0,10)
        contentLayout.setSpacing(0)


        # Заголовок
        titleLabel = QLabel("Главная страница")
        titleLabel.setFixedHeight(40)
        titleLabel.setAlignment(Qt.AlignmentFlag.AlignCenter)
        contentLayout.addWidget(titleLabel, alignment=Qt.AlignmentFlag.AlignTop)

        # Приветствие
        hiLabel = QLabel(f'Добро пожаловать, {self.user.login}')
        hiLabel.setFixedHeight(40)
        hiLabel.setAlignment(Qt.AlignmentFlag.AlignCenter)
        contentLayout.addWidget(hiLabel, alignment=Qt.AlignmentFlag.AlignTop)

        # Информация


        contentLayout.addStretch()
        mainLayout.addWidget(contentWidget)

        """Навигационная панель"""
        self.navPanel = NavPanel(self)
        mainLayout.addWidget(self.navPanel)


        self.setLayout(mainLayout)
