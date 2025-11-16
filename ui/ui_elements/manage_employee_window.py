from PyQt6.QtCore import QSize, Qt, QRegularExpression
from PyQt6.QtGui import QIcon, QRegularExpressionValidator
from PyQt6.QtWidgets import QLabel, QVBoxLayout, QHBoxLayout, QLineEdit, QComboBox, QPushButton, QDialog, QMessageBox, \
    QCheckBox, QListWidget, \
    QListWidgetItem

from services.control_user_service import get_employee_by_id, update_employee
from services.info_from_db import get_posts, get_warehouses


class ManageEmployeeWindow(QDialog):
    def __init__(self):
        """Диалоговое окно управления сотрудником"""
        super().__init__()
        # Настройка параметров окна
        self.setWindowTitle("Изменение информации о сотруднике")
        self.setWindowIcon(QIcon("assets/icons/app_icon.png"))
        self.setFixedSize(QSize(500, 400))

        # Главный layout
        self.mainLayout = QVBoxLayout()

        # label окна
        self.label = QLabel('Изменение информации о сотруднике')
        self.mainLayout.addWidget(self.label, alignment=Qt.AlignmentFlag.AlignCenter)
        self.mainLayout.addSpacing(10)

        # Поле id сотрудника
        self.employeeIdLine = QLineEdit(self)
        self.employeeIdLine.setPlaceholderText("Id сотрудника")
        self.employeeIdLine.setFixedWidth(300)
        self.employeeIdLine.setValidator(QRegularExpressionValidator(QRegularExpression(r'^\d*$')))
        self.mainLayout.addWidget(self.employeeIdLine, alignment=Qt.AlignmentFlag.AlignCenter)

        # Кнопка перехода к изменению информации
        self.confirmEmployeeIdBtn = QPushButton('Изменить')
        self.confirmEmployeeIdBtn.setFixedWidth(300)
        self.confirmEmployeeIdBtn.clicked.connect(self.open_employee_controls)
        self.mainLayout.addWidget(self.confirmEmployeeIdBtn, alignment=Qt.AlignmentFlag.AlignCenter)

        # Layout для полей
        self.fieldsLayout = QVBoxLayout()
        self.fieldsLayout.setSpacing(10)
        self.mainLayout.addLayout(self.fieldsLayout)
        self.mainLayout.addStretch()

        # Кнопка закрытия окна без сохранения
        self.btnLayout = QHBoxLayout()

        closeBtn = QPushButton("Выход")
        closeBtn.setFixedSize(200, 40)
        closeBtn.clicked.connect(self.close)
        self.btnLayout.addWidget(closeBtn)
        self.mainLayout.addLayout(self.btnLayout)

        self.setLayout(self.mainLayout)

    def open_employee_controls(self):
        """Режим изменения информации о сотруднике"""
        # Получение нынешней информации о сотруднике
        try:
            employee = get_employee_by_id(int(self.employeeIdLine.text()))
        except ValueError:
            QMessageBox.warning(self, 'Ошибка', 'Некорректный id пользователя')
            return None

        # Проверка на успешность получения информации
        if not employee['success']:
            QMessageBox.warning(self, 'Ошибка', employee['data'])
            return None

        # Сохранение информации о сотруднике
        self.employeeData = employee['data']

        # Измененный label окна
        self.label.setText(f'Изменение информации о сотруднике: {self.employeeData['id']}')
        self.employeeIdLine.deleteLater()
        self.confirmEmployeeIdBtn.deleteLater()

        # Поле фамилия
        lastNameLayout = QHBoxLayout()
        lastNameLabel = QLabel("Фамилия: ")
        lastNameLabel.setFixedWidth(150)
        self.lastName = QLineEdit(self)
        self.lastName.setPlaceholderText("Фамилия сотрудника")
        self.lastName.setMaxLength(100)
        self.lastName.setValidator(QRegularExpressionValidator(QRegularExpression(r'[A-Za-zA-Яа-яЁё]*$')))
        self.lastName.setText(self.employeeData['lastName'])
        lastNameLayout.addWidget(lastNameLabel)
        lastNameLayout.addWidget(self.lastName)

        self.fieldsLayout.addLayout(lastNameLayout)

        # Поле имя
        firstNameLayout = QHBoxLayout()
        firstNameLabel = QLabel("Имя: ")
        firstNameLabel.setFixedWidth(150)
        self.firstName = QLineEdit(self)
        self.firstName.setPlaceholderText("Имя сотрудника")
        self.firstName.setMaxLength(50)
        self.firstName.setValidator(QRegularExpressionValidator(QRegularExpression(r'[A-Za-zA-Яа-яЁё]*$')))
        self.firstName.setText(self.employeeData['firstName'])
        firstNameLayout.addWidget(firstNameLabel)
        firstNameLayout.addWidget(self.firstName)

        self.fieldsLayout.addLayout(firstNameLayout)

        # Поле серия паспорта
        passportSeriesLayout = QHBoxLayout()
        passportSeriesLabel = QLabel("Серия паспорта: ")
        passportSeriesLabel.setFixedWidth(150)
        self.passportSeries = QLineEdit(self)
        self.passportSeries.setPlaceholderText("Серия паспорта сотрудника")
        self.passportSeries.setMaxLength(4)
        self.passportSeries.setValidator(QRegularExpressionValidator(QRegularExpression(r'^\d*$')))
        self.passportSeries.setText(self.employeeData['passportSeries'])
        passportSeriesLayout.addWidget(passportSeriesLabel)
        passportSeriesLayout.addWidget(self.passportSeries)

        self.fieldsLayout.addLayout(passportSeriesLayout)

        # Поле номер паспорта
        passportNumberLayout = QHBoxLayout()
        passportNumberLabel = QLabel("Номер паспорта:")
        passportNumberLabel.setFixedWidth(150)
        self.passportNumber = QLineEdit(self)
        self.passportNumber.setPlaceholderText("Номер паспорта сотрудника")
        self.passportNumber.setMaxLength(6)
        self.passportNumber.setValidator(QRegularExpressionValidator(QRegularExpression(r'^\d*$')))
        self.passportNumber.setText(self.employeeData['passportNumber'])
        passportNumberLayout.addWidget(passportNumberLabel)
        passportNumberLayout.addWidget(self.passportNumber)

        self.fieldsLayout.addLayout(passportNumberLayout)

        # Поле номер телефона
        phoneNumberLayout = QHBoxLayout()
        phoneNumberLabel = QLabel("Номер телефона:")
        phoneNumberLabel.setFixedWidth(150)
        self.phoneNumber = QLineEdit(self)
        self.phoneNumber.setPlaceholderText("Номер телефона сотрудника")
        self.phoneNumber.setMaxLength(20)
        self.phoneNumber.setValidator(QRegularExpressionValidator(QRegularExpression(r'^\d*$')))
        self.phoneNumber.setText(self.employeeData['phoneNumber'])
        phoneNumberLayout.addWidget(phoneNumberLabel)
        phoneNumberLayout.addWidget(self.phoneNumber)

        self.fieldsLayout.addLayout(phoneNumberLayout)

        # Выбор должности
        postLayout = QHBoxLayout()
        postLabel = QLabel("Должность: ")
        postLabel.setFixedWidth(150)
        self.post = QComboBox(self)
        self.post.addItems(get_posts())
        self.post.setCurrentText(self.employeeData['post'])
        postLayout.addWidget(postLabel)
        postLayout.addWidget(self.post)

        self.fieldsLayout.addLayout(postLayout)

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

        for i in range(self.warehouse.count()):
            item = self.warehouse.item(i)
            if item.data(Qt.ItemDataRole.UserRole) in self.employeeData['warehouses']:
                item.setSelected(True)

        warehouseLayout.addWidget(warehouseLabel)
        warehouseLayout.addWidget(self.warehouse)

        self.fieldsLayout.addLayout(warehouseLayout)

        # Работает/уволен
        isActiveLayout = QHBoxLayout()
        isActiveLabel = QLabel("Работает: ")
        isActiveLabel.setFixedWidth(150)
        self.isActive = QCheckBox(self)
        self.isActive.setChecked(self.employeeData['isActive'])
        isActiveLayout.addWidget(isActiveLabel)
        isActiveLayout.addWidget(self.isActive)

        self.fieldsLayout.addLayout(isActiveLayout)

        # Кнопка сохранения изменений
        addEmployeeBtn = QPushButton("Применить")
        addEmployeeBtn.setFixedSize(200, 40)
        addEmployeeBtn.clicked.connect(self.update_employee_info)
        self.btnLayout.addWidget(addEmployeeBtn)

    def update_employee_info(self):
        """Сохранение изменений"""
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

        # Склады
        if len(warehouses) == 0:
            QMessageBox.warning(self, 'Ошибка', 'Выберите склад(ы)')
            return None

        """Изменение записи"""
        result = update_employee(self.employeeData['id'],firstName, lastName, passportSeries, passportNumber,
                                 phoneNumber, post,int(self.isActive.isChecked()), warehouses)
        if result['success']:
            QMessageBox.information(self, 'Успех', result['message'])
            return None
        else:
            QMessageBox.information(self, 'Ошибка', result['message'])
            return None