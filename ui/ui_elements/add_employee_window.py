from PyQt6.QtCore import QSize, Qt, QRegularExpression
from PyQt6.QtGui import QIcon, QRegularExpressionValidator
from PyQt6.QtWidgets import QLabel, QVBoxLayout, QHBoxLayout, QLineEdit, QComboBox, QPushButton, QDialog, QMessageBox, \
    QListWidget, \
    QListWidgetItem

from services.control_user_service import add_employee
from services.info_from_db import get_posts, get_warehouses


class AddEmployeeWindow(QDialog):
    """Диалоговое окно для добавления сотрудника"""
    def __init__(self):
        super().__init__()

        # Настройка параметров окна
        self.setWindowTitle("Добавление сотрудника")
        self.setWindowIcon(QIcon("assets/icons/app_icon.png"))
        self.setFixedSize(QSize(500, 400))

        # Главный layout
        mainLayout = QVBoxLayout()

        # Label окна
        label = QLabel('Добавление сотрудника')
        mainLayout.addWidget(label, alignment=Qt.AlignmentFlag.AlignCenter)
        mainLayout.addSpacing(10)

        # Layout для полей ввода
        fieldsLayout = QVBoxLayout()
        fieldsLayout.setSpacing(10)

        # Поле фамилия
        lastNameLayout = QHBoxLayout()
        lastNameLabel = QLabel("Фамилия: ")
        lastNameLabel.setFixedWidth(150)
        self.lastName = QLineEdit(self)
        self.lastName.setPlaceholderText("Фамилия сотрудника")
        self.lastName.setMaxLength(100)
        self.lastName.setValidator(QRegularExpressionValidator(QRegularExpression(r'[A-Za-zA-Яа-яЁё]*$')))
        lastNameLayout.addWidget(lastNameLabel)
        lastNameLayout.addWidget(self.lastName)

        fieldsLayout.addLayout(lastNameLayout)

        # Поле имя
        firstNameLayout = QHBoxLayout()
        firstNameLabel = QLabel("Имя: ")
        firstNameLabel.setFixedWidth(150)
        self.firstName = QLineEdit(self)
        self.firstName.setPlaceholderText("Имя сотрудника")
        self.firstName.setMaxLength(50)
        self.firstName.setValidator(QRegularExpressionValidator(QRegularExpression(r'[A-Za-zA-Яа-яЁё]*$')))
        firstNameLayout.addWidget(firstNameLabel)
        firstNameLayout.addWidget(self.firstName)

        fieldsLayout.addLayout(firstNameLayout)

        # Поле серия паспорта
        passportSeriesLayout = QHBoxLayout()
        passportSeriesLabel = QLabel("Серия паспорта: ")
        passportSeriesLabel.setFixedWidth(150)
        self.passportSeries = QLineEdit(self)
        self.passportSeries.setPlaceholderText("Серия паспорта сотрудника")
        self.passportSeries.setMaxLength(4)
        self.passportSeries.setValidator(QRegularExpressionValidator(QRegularExpression(r'^\d*$')))
        passportSeriesLayout.addWidget(passportSeriesLabel)
        passportSeriesLayout.addWidget(self.passportSeries)

        fieldsLayout.addLayout(passportSeriesLayout)

        # Поле номер паспорта
        passportNumberLayout = QHBoxLayout()
        passportNumberLabel = QLabel("Номер паспорта:")
        passportNumberLabel.setFixedWidth(150)
        self.passportNumber = QLineEdit(self)
        self.passportNumber.setPlaceholderText("Номер паспорта сотрудника")
        self.passportNumber.setMaxLength(6)
        self.passportNumber.setValidator(QRegularExpressionValidator(QRegularExpression(r'^\d*$')))
        passportNumberLayout.addWidget(passportNumberLabel)
        passportNumberLayout.addWidget(self.passportNumber)

        fieldsLayout.addLayout(passportNumberLayout)

        # Поле номер телефона
        phoneNumberLayout = QHBoxLayout()
        phoneNumberLabel = QLabel("Номер телефона:")
        phoneNumberLabel.setFixedWidth(150)
        self.phoneNumber = QLineEdit(self)
        self.phoneNumber.setPlaceholderText("Номер телефона сотрудника")
        self.phoneNumber.setMaxLength(20)
        self.phoneNumber.setValidator(QRegularExpressionValidator(QRegularExpression(r'^\d*$')))
        phoneNumberLayout.addWidget(phoneNumberLabel)
        phoneNumberLayout.addWidget(self.phoneNumber)

        fieldsLayout.addLayout(phoneNumberLayout)

        # Выбор должности
        postLayout = QHBoxLayout()
        postLabel = QLabel("Должность: ")
        postLabel.setFixedWidth(150)
        self.post = QComboBox(self)
        self.post.addItem("Выберите должность сотрудника")
        self.post.addItems(get_posts())
        postLayout.addWidget(postLabel)
        postLayout.addWidget(self.post)

        fieldsLayout.addLayout(postLayout)

        # Выбор складов
        warehouseLayout = QHBoxLayout()
        warehouseLabel = QLabel("Склады: ")
        warehouseLabel.setFixedWidth(150)
        self.warehouse = QListWidget(self)
        self.warehouse.setSelectionMode(QListWidget.SelectionMode.MultiSelection)

        warehouses = get_warehouses()
        for id, name in warehouses:
            item = QListWidgetItem(name)
            item.setData(Qt.ItemDataRole.UserRole, id)
            self.warehouse.addItem(item)

        warehouseLayout.addWidget(warehouseLabel)
        warehouseLayout.addWidget(self.warehouse)

        fieldsLayout.addLayout(warehouseLayout)

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
        addEmployeeBtn.clicked.connect(self.add_employee)
        btnLayout.addWidget(addEmployeeBtn)

        mainLayout.addLayout(btnLayout)


        self.setLayout(mainLayout)

    def add_employee(self):

        # Получение информации
        firstName = self.firstName.text().strip()
        lastName = self.lastName.text().strip()
        passportSeries = self.passportSeries.text().strip()
        passportNumber = self.passportNumber.text().strip()
        phoneNumber = self.phoneNumber.text().strip()
        post = self.post.currentText()

        warehouses = []
        for warehouseId in self.warehouse.selectedItems():
            warehouses.append(warehouseId.data(Qt.ItemDataRole.UserRole))

        """Валидация"""

        # Фамилия
        if len(lastName) == 0:
            QMessageBox.warning(self, 'Ошибка', 'Поле "Фамилия" должно быть заполнено')
            return None

        # Имя
        if len(firstName) == 0:
            QMessageBox.warning(self, 'Ошибка', 'Поле "Имя" должно быть заполнено')
            return None

        # Серия паспорта
        if len(passportSeries) != 4:
            QMessageBox.warning(self, 'Ошибка', 'Серия паспорта должна содержать 4 цифры')
            return None

        # Номер паспорта
        if len(passportNumber) != 6:
            QMessageBox.warning(self, 'Ошибка', 'Номер паспорта должен содержать 6 цифр')
            return None

        # Номер телефона
        if len(phoneNumber) == 0:
            QMessageBox.warning(self, 'Ошибка', 'Поле "Номер телефона" должно быть заполнено')
            return None

        # Должность
        if post == self.post.itemText(0):
            QMessageBox.warning(self, 'Ошибка', 'Выберите должность сотрудника')
            return None

        # Склады
        if len(warehouses) == 0:
            QMessageBox.warning(self, 'Ошибка', 'Выберите склад(ы)')
            return None

        """Добавление записи"""
        result = add_employee(firstName, lastName, passportSeries, passportNumber, phoneNumber, post, warehouses)
        if result['success']:
            QMessageBox.information(self,'Успех', 'Сотрудник успешно добавлен')
            return None
        else:
            QMessageBox.information(self, 'Ошибка', result['message'])
            return None