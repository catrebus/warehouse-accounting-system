from PyQt6.QtCore import QSize, Qt, QRegularExpression
from PyQt6.QtGui import QIcon, QRegularExpressionValidator
from PyQt6.QtWidgets import QLabel, QVBoxLayout, QHBoxLayout, QLineEdit, QComboBox, QPushButton, QDialog, QMessageBox

from services.control_user_service import create_invite_code
from services.info_from_db import get_roles


class CreateInviteCodeWindow(QDialog):
    """Диалоговое окно для создания пригласительного кода"""
    def __init__(self):
        super().__init__()

        # Настройка параметров окна
        self.setWindowTitle("Добавление сотрудника")
        self.setWindowIcon(QIcon("assets/icons/app_icon.png"))
        self.setFixedSize(QSize(500, 200))

        # Главный layout
        mainLayout = QVBoxLayout()

        # Label окна
        label = QLabel('Создание пригласительного кода')
        mainLayout.addWidget(label, alignment=Qt.AlignmentFlag.AlignCenter)
        mainLayout.addSpacing(10)

        # Layout для полей ввода
        fieldsLayout = QVBoxLayout()

        # Поле id сотрудника
        employeeIdLayout = QHBoxLayout()
        employeeIdLabel = QLabel('Id сотрудника: ')
        employeeIdLabel.setFixedWidth(150)
        self.employeeIdLine = QLineEdit()
        self.employeeIdLine.setPlaceholderText('Id сотрудника')
        self.employeeIdLine.setValidator(QRegularExpressionValidator(QRegularExpression(r'^\d*$')))
        employeeIdLayout.addWidget(employeeIdLabel)
        employeeIdLayout.addWidget(self.employeeIdLine)
        fieldsLayout.addLayout(employeeIdLayout)

        # Поле кода
        codeLayout = QHBoxLayout()
        codeLabel = QLabel('Текст кода: ')
        codeLabel.setFixedWidth(150)
        self.codeLine = QLineEdit()
        self.codeLine.setPlaceholderText('Пригласительный код')
        self.codeLine.setValidator(QRegularExpressionValidator(QRegularExpression(r'^[A-Za-z0-9]*$')))
        self.codeLine.setMaxLength(50)
        codeLayout.addWidget(codeLabel)
        codeLayout.addWidget(self.codeLine)
        fieldsLayout.addLayout(codeLayout)

        # Роль для будущей учетной записи
        roleLayout = QHBoxLayout()
        roleLabel = QLabel('Роль: ')
        roleLabel.setFixedWidth(150)
        self.roleBox = QComboBox()
        self.roleBox.addItem("Выберите роль пользователя")
        self.roleBox.addItems(get_roles())
        roleLayout.addWidget(roleLabel)
        roleLayout.addWidget(self.roleBox)
        fieldsLayout.addLayout(roleLayout)

        # Добавление полей в окно
        mainLayout.addLayout(fieldsLayout)
        mainLayout.addStretch()

        # Кнопки
        btnLayout = QHBoxLayout()

        exitBtn = QPushButton("Выход")
        exitBtn.setFixedSize(200, 40)
        exitBtn.clicked.connect(self.close)
        btnLayout.addWidget(exitBtn)

        addEmployeeBtn = QPushButton("Добавить")
        addEmployeeBtn.setFixedSize(200, 40)
        addEmployeeBtn.clicked.connect(self.create_invite_code)
        btnLayout.addWidget(addEmployeeBtn)

        mainLayout.addLayout(btnLayout)

        self.setLayout(mainLayout)

    def create_invite_code(self):
        # Если поле id пустое
        if not self.employeeIdLine.text().strip():
            QMessageBox.warning(self, 'Ошибка', 'Введите id пользователя')
            return None
        employeeId = int(self.employeeIdLine.text().strip())

        # Если длина кода <5
        if len(self.codeLine.text().strip()) < 5:
            QMessageBox.warning(self, 'Ошибка', 'Текст кода должен содержать хотя бы 5 символов')
            return None
        code = self.codeLine.text().strip()

        # Если не выбрана роль
        if self.roleBox.currentIndex() == 0:
            QMessageBox.warning(self, 'Ошибка', 'Выберите роль будущей учетной записи')
            return None
        role = self.roleBox.currentText()

        # Добавление кода в систему
        result = create_invite_code(code,employeeId,role)
        if result['success']:
            QMessageBox.information(self,'Успех', result['message'])
            return None
        else:
            QMessageBox.warning(self, 'Ошибка', result['message'])
            return None