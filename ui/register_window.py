from PyQt6.QtCore import pyqtSignal, QSize, Qt
from PyQt6.QtGui import QColor, QPixmap
from PyQt6.QtWidgets import QPushButton, QVBoxLayout, QFrame, QGraphicsDropShadowEffect, QHBoxLayout, QLabel, QWidget

from ui.base_window import BaseWindow


class RegisterWindow(BaseWindow):
    # Сигналы для перехода
    switchToLogin = pyqtSignal()

    # Характеристики окна
    widowTitle: str = 'Система складского учета - Регистрация'
    windowSize: QSize = QSize(960, 540)
    resizable: bool = False
    windowIconPath: str = 'assets/icons/app_icon.png'

    def __init__(self):
        super().__init__()
        # Инициализация пользовательского интерфейса
        self.init_ui()

    def init_ui(self):
        """Инициализация пользовательского интерфейса"""

        """Правая часть окна"""
        # Заголовок
        titleLabel = QLabel('Регистрация')
        titleLabel.setObjectName('titleLabel')
        titleLabel.setAlignment(Qt.AlignmentFlag.AlignHCenter)
        titleLabel.setFixedSize(300,35)

        # Поле ввода пригласительного кода


        #Кнопка зарегистрироваться
        handleRegisterButton = QPushButton('Дальше')  # Кнопка входа
        handleRegisterButton.setObjectName('handleRegisterButton')
        handleRegisterButton.clicked.connect(self.handle_registration)
        handleRegisterButton.setFixedWidth(300)

        # Кнопка перехода на окно авторизации
        swithToLogin = QPushButton('Вход')
        swithToLogin.setObjectName('switchToLoginButton')
        swithToLogin.clicked.connect(self.switchToLogin)
        swithToLogin.setFixedSize(33, 20)

        # Подложка для формы авторизации
        self.card = QFrame()
        self.card.setObjectName('cardRegister')
        self.card.setFixedSize(400, 320)

        self.cardLayout = QVBoxLayout(self.card)
        self.cardLayout.setContentsMargins(50, 30, 50, 30)

        # Эффекты для подложки
        cardEffect = QGraphicsDropShadowEffect()
        cardEffect.setBlurRadius(30)
        cardEffect.setXOffset(0)
        cardEffect.setYOffset(4)
        cardEffect.setColor(QColor(0, 0, 0, 120))
        self.card.setGraphicsEffect(cardEffect)

        # Размещение виджетов на подложке
        self.cardLayout.addWidget(titleLabel, alignment=Qt.AlignmentFlag.AlignTop)

        self.cardLayout.addWidget(handleRegisterButton, alignment=Qt.AlignmentFlag.AlignBottom)

        # Размещение на правой стороне
        rightLayout = QVBoxLayout()
        rightLayout.addWidget(self.card)
        rightLayout.addWidget(swithToLogin, alignment=Qt.AlignmentFlag.AlignTop)
        rightLayout.setContentsMargins(0, 100, 70, 0)

        """Левая часть окна"""
        iconLabel = QLabel()
        padlockIcon = QPixmap('assets/icons/register_icon.png')
        padlockIcon = padlockIcon.scaled(360, 360, Qt.AspectRatioMode.KeepAspectRatio, Qt.TransformationMode.SmoothTransformation)
        iconLabel.setPixmap(padlockIcon)
        iconLabel.setAlignment(Qt.AlignmentFlag.AlignCenter)
        leftLayout = QHBoxLayout()
        leftLayout.addWidget(iconLabel)

        """Задний фон"""
        self.bgWidget = QWidget(self)
        self.bgWidget.setObjectName('bgWidget')
        self.bgWidget.resize(self.windowSize)
        self.bgWidget.lower()

        """Главный компоновщик"""
        mainLayout = QHBoxLayout(self.bgWidget)
        mainLayout.addLayout(leftLayout, stretch=1)
        mainLayout.addLayout(rightLayout, stretch=2)

        self.setLayout(mainLayout)

    def handle_registration(self):
        pass