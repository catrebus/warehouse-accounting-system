import sys

from PyQt6.QtGui import QIcon, QPixmap, QAction
from PyQt6.QtWidgets import (
    QWidget, QLineEdit, QLabel, QPushButton, QVBoxLayout, QHBoxLayout, QMessageBox, QApplication
)
from PyQt6.QtCore import Qt, QSize


class LoginWindow(QWidget):
    def __init__(self):
        super().__init__()
        self.setWindowTitle('Авторизация')
        self.setFixedSize(960, 540)
        self.setWindowIcon(QIcon('assets/icons/310869.png'))
        self.setObjectName('LoginWindow')
        # Инициализация пользовательского интерфейса
        self.init_ui()

    def init_ui(self):
        """Инициализация пользовательского интерфейса"""

        """Правая часть окна"""
        titleLabel = QLabel('Авторизация')
        titleLabel.setObjectName('titleLabel')
        titleLabel.setAlignment(Qt.AlignmentFlag.AlignCenter)
        titleLabel.setFixedWidth(300)

        # Поле логина
        self.usernameInput = QLineEdit()
        self.usernameInput.setObjectName('usernameInput')
        userIcon = QIcon('assets/icons/login_icon.png')
        self.usernameInput.addAction(userIcon, QLineEdit.ActionPosition.LeadingPosition)
        self.usernameInput.setFixedWidth(300)
        self.usernameInput.setPlaceholderText('Логин')

        # Поле ввода пароля

        passwordLine = QHBoxLayout()

        # Кнопка показать/скрыть пароль
        self.togglePasswordButton = QPushButton()
        self.togglePasswordButton.setObjectName('togglePasswordButton')
        self.togglePasswordButton.setIcon(QIcon('assets/icons/closed_eye_icon.png'))
        self.togglePasswordButton.setFixedWidth(45)
        self.togglePasswordButton.clicked.connect(self.toggle_password_visibility)


        self.passwordInput = QLineEdit() # Поле пароля
        self.passwordInput.setObjectName('passwordInput')

        passwordIcon = QIcon('assets/icons/key_icon.png')
        self.passwordInput.addAction(passwordIcon, QLineEdit.ActionPosition.LeadingPosition)

        self.passwordInput.setFixedWidth(300)
        self.passwordInput.setPlaceholderText('Пароль')
        self.passwordInput.setEchoMode(QLineEdit.EchoMode.Password)

        passwordLine.addWidget(self.passwordInput)
        passwordLine.addWidget(self.togglePasswordButton)

        # Кнопка входа
        authButton = QPushButton('Вход') # Кнопка входа
        authButton.setObjectName('authButton')
        authButton.clicked.connect(self.handle_login)
        authButton.setFixedWidth(300)

        # Размещение
        rightLayout = QVBoxLayout()

        rightLayout.addWidget(titleLabel)
        rightLayout.addSpacing(25)

        rightLayout.addWidget(self.usernameInput)
        rightLayout.addSpacing(10)

        rightLayout.addLayout(passwordLine)
        rightLayout.addSpacing(25)

        rightLayout.addWidget(authButton)

        rightLayout.setAlignment(Qt.AlignmentFlag.AlignTop)
        rightLayout.setContentsMargins(0, 125, 70,0)

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
        

