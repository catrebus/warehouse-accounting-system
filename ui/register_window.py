from PyQt6.QtCore import pyqtSignal, QSize, Qt
from PyQt6.QtGui import QColor, QPixmap, QIcon
from PyQt6.QtWidgets import QPushButton, QVBoxLayout, QFrame, QGraphicsDropShadowEffect, QHBoxLayout, QLabel, QWidget, \
    QLineEdit

from services.auth_service import register_user
from ui.base_window import BaseWindow


class RegisterWindow(BaseWindow):
    # Сигналы для перехода
    switchToLogin = pyqtSignal()
    switchToMain = pyqtSignal()

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
        self.inviteCode = QLineEdit()
        self.inviteCode.setObjectName('inviteCode')
        self.inviteCode.setAlignment(Qt.AlignmentFlag.AlignTop)
        inviteIcon = QIcon('assets/icons/letter_icon.png')
        self.inviteCode.addAction(inviteIcon, QLineEdit.ActionPosition.LeadingPosition)
        self.inviteCode.setFixedWidth(300)
        self.inviteCode.setPlaceholderText('Пригласительный код')

        # Поле ввода логина
        self.usernameInput = QLineEdit()
        self.usernameInput.setObjectName('usernameInput')
        userIcon = QIcon('assets/icons/login_icon.png')
        self.usernameInput.addAction(userIcon, QLineEdit.ActionPosition.LeadingPosition)
        self.usernameInput.setFixedWidth(300)
        self.usernameInput.setPlaceholderText('Логин')

        # Поле ввода пароля
        self.passwordInput = QLineEdit()
        self.passwordInput.setObjectName('passwordInput')
        passwordIcon = QIcon('assets/icons/key_icon.png')
        self.passwordInput.addAction(passwordIcon, QLineEdit.ActionPosition.LeadingPosition)
        self.passwordInput.setFixedWidth(300)
        self.passwordInput.setPlaceholderText('Пароль')
        self.passwordInput.setEchoMode(QLineEdit.EchoMode.Password)

        # Поле подтверждения поля
        self.confirmPasswordInput = QLineEdit()
        self.confirmPasswordInput.setObjectName('passwordInput')
        passwordIcon = QIcon('assets/icons/key_icon.png')
        self.confirmPasswordInput.addAction(passwordIcon, QLineEdit.ActionPosition.LeadingPosition)
        self.confirmPasswordInput.setFixedWidth(300)
        self.confirmPasswordInput.setPlaceholderText('Подтверждение пароля')
        self.confirmPasswordInput.setEchoMode(QLineEdit.EchoMode.Password)

        #Кнопка зарегистрироваться
        handleRegisterButton = QPushButton('Зарегистрироваться')  # Кнопка регистрации
        handleRegisterButton.setObjectName('handleRegisterButton')
        handleRegisterButton.clicked.connect(self.handle_switch_to_main)
        handleRegisterButton.setFixedWidth(300)

        # Кнопка перехода на окно авторизации
        swithToLogin = QPushButton('Вход')
        swithToLogin.setObjectName('switchToLoginButton')
        swithToLogin.clicked.connect(self.handle_switch_to_login)
        swithToLogin.setFixedSize(33, 20)

        # Подложка для формы регистрации
        self.card = QFrame()
        self.card.setObjectName('cardRegister')
        self.card.setFixedSize(400, 420)

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
        self.cardLayout.addWidget(self.inviteCode, alignment=Qt.AlignmentFlag.AlignCenter)
        self.cardLayout.addWidget(self.usernameInput, alignment=Qt.AlignmentFlag.AlignCenter)
        self.cardLayout.addWidget(self.passwordInput, alignment=Qt.AlignmentFlag.AlignCenter)
        self.cardLayout.addWidget(self.confirmPasswordInput, alignment=Qt.AlignmentFlag.AlignCenter)
        self.cardLayout.addSpacing(10)
        self.cardLayout.addWidget(handleRegisterButton, alignment=Qt.AlignmentFlag.AlignBottom)

        # Размещение на правой стороне
        rightLayout = QVBoxLayout()
        rightLayout.addWidget(self.card)
        rightLayout.addWidget(swithToLogin, alignment=Qt.AlignmentFlag.AlignTop)
        rightLayout.setContentsMargins(0, 50, 70, 0)

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

    def set_to_default(self):
        self.inviteCode.clear()
        self.usernameInput.clear()
        self.passwordInput.clear()
        self.confirmPasswordInput.clear()

    """Переходы между окнами"""
    def handle_switch_to_login(self):
        self.set_to_default()
        self.switchToLogin.emit()

    def handle_switch_to_main(self):
        if self.passwordInput.text() == self.confirmPasswordInput.text():
            result = register_user(self.inviteCode.text(), self.usernameInput.text(), self.passwordInput.text())
            print(result)
            self.set_to_default()
        # self.set_to_default()
        # self.switchToMain.emit()
