import sys

from PyQt6.QtGui import QIcon, QPixmap, QAction, QColor
from PyQt6.QtWidgets import (
    QWidget, QLineEdit, QLabel, QPushButton, QVBoxLayout, QHBoxLayout, QMessageBox, QApplication, QFrame,
    QGraphicsDropShadowEffect
)
from PyQt6.QtCore import Qt, QSize


class LoginWindow(QWidget):
    def __init__(self):
        super().__init__()
        self.setWindowTitle('Авторизация')
        self.setFixedSize(960, 540)
        self.setWindowIcon(QIcon('assets/icons/auth_icon4.png'))
        self.setObjectName('LoginWindow')
        # Инициализация пользовательского интерфейса
        self.init_ui()

    def init_ui(self):
        """Инициализация пользовательского интерфейса"""

        """Правая часть окна"""
        # Заголовок
        titleLabel = QLabel('Авторизация')
        titleLabel.setObjectName('titleLabel')
        titleLabel.setAlignment(Qt.AlignmentFlag.AlignHCenter)
        titleLabel.setFixedWidth(300)
        titleLabel.setFixedHeight(35)

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

        # Кнопка показать/скрыть пароль
        self.togglePasswordButton = QPushButton()
        self.togglePasswordButton.setObjectName('togglePasswordButton')
        self.togglePasswordButton.setIcon(QIcon('assets/icons/closed_eye_icon.png'))
        self.togglePasswordButton.setFixedWidth(45)
        self.togglePasswordButton.clicked.connect(self.toggle_password_visibility)

        # Лэйаут для поля пароля и кнопки показать/скрыть
        passwordLine = QHBoxLayout()
        passwordLine.addWidget(self.passwordInput)
        passwordLine.addWidget(self.togglePasswordButton)
        passwordLine.setAlignment(Qt.AlignmentFlag.AlignCenter)

        # Кнопка входа
        authButton = QPushButton('Вход') # Кнопка входа
        authButton.setObjectName('authButton')
        authButton.clicked.connect(self.handle_login)
        authButton.setFixedWidth(300)

        # Подложка для формы авторизации
        self.card = QFrame()
        self.card.setObjectName('card')
        self.card.setFixedSize(400, 300)

        cardLayout = QVBoxLayout(self.card)
        cardLayout.setContentsMargins(30, 30, 15, 30)

        # Эффекты для подложки
        cardEffect = QGraphicsDropShadowEffect()
        cardEffect.setBlurRadius(30)
        cardEffect.setXOffset(0)
        cardEffect.setYOffset(4)
        cardEffect.setColor(QColor(0, 0, 0, 120))
        self.card.setGraphicsEffect(cardEffect)

        # Размещение виджетов на подложке
        cardLayout.addWidget(titleLabel)
        cardLayout.addSpacing(25)

        cardLayout.addWidget(self.usernameInput)
        cardLayout.addSpacing(10)

        cardLayout.addLayout(passwordLine)
        cardLayout.addSpacing(10)

        cardLayout.addWidget(authButton)
        cardLayout.addSpacing(10)

        # Размещение
        rightLayout = QVBoxLayout()
        rightLayout.addWidget(self.card)
        rightLayout.setContentsMargins(0, 0, 70, 0)


        """Левая часть окна"""
        iconLabel = QLabel()
        padlockIcon = QPixmap('assets/icons/padlock_icon.png')
        padlockIcon = padlockIcon.scaled(360, 360, Qt.AspectRatioMode.KeepAspectRatio, Qt.TransformationMode.SmoothTransformation)
        iconLabel.setPixmap(padlockIcon)
        iconLabel.setAlignment(Qt.AlignmentFlag.AlignCenter)
        leftLayout = QHBoxLayout()
        leftLayout.addWidget(iconLabel)

        """Главный компоновщик"""
        mainLayout = QHBoxLayout()
        mainLayout.addLayout(leftLayout, stretch=1)
        mainLayout.addLayout(rightLayout, stretch=2)

        self.setLayout(mainLayout)

    def handle_login(self):
        pass

    def toggle_password_visibility(self):
        if self.passwordInput.echoMode() == QLineEdit.EchoMode.Password:
            self.passwordInput.setEchoMode(QLineEdit.EchoMode.Normal)
            self.togglePasswordButton.setIcon(QIcon('assets/icons/opened_eye_icon.png'))
        else:
            self.passwordInput.setEchoMode(QLineEdit.EchoMode.Password)
            self.togglePasswordButton.setIcon(QIcon('assets/icons/closed_eye_icon.png'))


