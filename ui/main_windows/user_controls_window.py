from PyQt6.QtCore import QSize, Qt, QSortFilterProxyModel, QRegularExpression
from PyQt6.QtGui import QIcon, QRegularExpressionValidator
from PyQt6.QtWidgets import QLabel, QWidget, QWIDGETSIZE_MAX, QVBoxLayout, QStackedLayout, QHBoxLayout, QTableView, \
    QHeaderView, QLineEdit, QComboBox, QPushButton, QDialog, QMessageBox, QCheckBox, QScrollArea, QListWidget, \
    QAbstractItemView, QListWidgetItem

from services.control_user_service import get_user_by_login, update_user, get_employees, add_employee, \
    get_employee_by_id, update_employee, create_invite_code
from services.info_from_db import get_users, get_roles, get_posts, get_warehouses
from ui.base_window import BaseWindow
from ui.ui_elements.nav_panel import NavPanel
from ui.ui_elements.table_model import TableModel


class MultiFilterProxyModelUsers(QSortFilterProxyModel):
    """Класс прокси модели для реализации фильтров в таблице пользователей"""
    def __init__(self):
        super().__init__()
        self.loginFilter = ''
        self.roleFilter = None
        self.lastNameFilter = ''
        self.firstNameFilter = ''
        self.isActiveFilter = None

    def filterAcceptsRow(self, sourceRow, sourceParent):
        model = self.sourceModel()

        # Текстовые фильтры
        login = model.data(model.index(sourceRow, 0), Qt.ItemDataRole.DisplayRole).lower()
        role = model.data(model.index(sourceRow, 1), Qt.ItemDataRole.DisplayRole).lower()
        lastName = model.data(model.index(sourceRow, 2), Qt.ItemDataRole.DisplayRole).lower()
        firstName = model.data(model.index(sourceRow, 3), Qt.ItemDataRole.DisplayRole).lower()

        if self.loginFilter and self.loginFilter.lower() not in login:
            return False
        if self.lastNameFilter and self.lastNameFilter.lower() not in lastName:
            return False
        if self.firstNameFilter and self.firstNameFilter.lower() not in firstName:
            return False

        # Фильтр по роли
        if self.roleFilter and self.roleFilter != "Все роли":
            if role.lower() != self.roleFilter.lower():
                return False

        # Фильтр активности
        if self.isActiveFilter is not None:
            isActive = model.data(model.index(sourceRow, 4), Qt.ItemDataRole.DisplayRole)
            try:
                if int(isActive) != self.isActiveFilter:
                    return False
            except (ValueError,TypeError):
                return False

        return True

class MultiFilterProxyModelEmoloyees(QSortFilterProxyModel):
    """Класс прокси модели для реализации фильтрации в таблице сотрудники"""
    def __init__(self):
        super().__init__()

        self.lastNameFilter = ''
        self.firstNameFilter = ''
        self.postFilter = None
        self.isActiveFilter = None

    def filterAcceptsRow(self, sourceRow, sourceParent):
        model = self.sourceModel()

        # Текстовые фильтры
        lastName = model.data(model.index(sourceRow, 2), Qt.ItemDataRole.DisplayRole).lower()
        firstName = model.data(model.index(sourceRow, 1), Qt.ItemDataRole.DisplayRole).lower()
        post = model.data(model.index(sourceRow, 6), Qt.ItemDataRole.DisplayRole).lower()

        if self.lastNameFilter and self.lastNameFilter.lower() not in lastName:
            return False
        if self.firstNameFilter and self.firstNameFilter.lower() not in firstName:
            return False

        # Фильтр по должности
        if self.postFilter and self.postFilter != "Все должности":
            if post.lower() != self.postFilter.lower():
                return False

        # Фильтр активности
        if self.isActiveFilter is not None:
            isActive = model.data(model.index(sourceRow, 8), Qt.ItemDataRole.DisplayRole)
            try:
                if int(isActive) != self.isActiveFilter:
                    return False
            except (ValueError, TypeError):
                return False

        return True

class ManageUserWindow(QDialog):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Управление пользователем")
        self.setWindowIcon(QIcon("assets/icons/app_icon.png"))
        self.setFixedSize(QSize(480,270))

        self.mainLayout = QVBoxLayout()
        self.label = QLabel('Управление учетной записью')
        self.mainLayout.addWidget(self.label, alignment=Qt.AlignmentFlag.AlignCenter)
        self.mainLayout.addSpacing(10)


        # Layout для взаимодействия с учетной записью
        self.userLayout = QVBoxLayout()

        self.userLogin = QLineEdit(self)
        self.userLogin.setFixedWidth(300)

        self.userLogin.setPlaceholderText("Логин пользователя")
        self.userLayout.addWidget(self.userLogin, alignment=Qt.AlignmentFlag.AlignCenter)

        self.confirmLogin = QPushButton("Изменить")
        self.confirmLogin.clicked.connect(self.open_user_controls)
        self.confirmLogin.setFixedWidth(300)
        self.userLayout.addWidget(self.confirmLogin, alignment=Qt.AlignmentFlag.AlignCenter)

        self.mainLayout.addLayout(self.userLayout)

        self.mainLayout.addStretch()

        self.btnLayout = QHBoxLayout()

        closeBtn = QPushButton("Выход")
        closeBtn.setFixedSize(200,40)
        closeBtn.clicked.connect(self.close)
        self.btnLayout.addWidget(closeBtn)

        self.mainLayout.addLayout(self.btnLayout)

        self.setLayout(self.mainLayout)

    def open_user_controls(self):
        self.user = get_user_by_login(self.userLogin.text())

        if not self.user:
            QMessageBox.warning(self, 'Ошибка', "Пользователь не найден")
            return None

        self.userLogin.deleteLater()
        self.confirmLogin.deleteLater()

        self.label.setText(f"Управление учетной записью: {self.user['login']}")

        self.userLayout.addWidget(QLabel(f"Фамилия сотрудника: {self.user['lastName']}"))
        self.userLayout.addWidget(QLabel(f"Имя сотрудника: {self.user['firstName']}"))

        # Роль пользователя
        roleLayout = QHBoxLayout()

        roleLayout.addWidget(QLabel(f"Роль учетной записи: "))

        self.roles = QComboBox()
        self.roles.setFixedWidth(200)
        self.roles.addItems(get_roles())
        self.roles.setCurrentText(self.user['role'])
        roleLayout.addWidget(self.roles, alignment=Qt.AlignmentFlag.AlignLeft)

        # Пользователь активен/неактивен

        isActiveLayout = QHBoxLayout()

        isActiveLayout.addWidget(QLabel(f"Активна/Неактивна: " ))

        self.isActive = QCheckBox()
        self.isActive.setChecked(self.user['isActive'])
        isActiveLayout.addWidget(self.isActive, alignment=Qt.AlignmentFlag.AlignLeft)


        self.userLayout.addLayout(roleLayout)
        self.userLayout.addLayout(isActiveLayout)

        applyChangesBtn = QPushButton("Применить")
        applyChangesBtn.setFixedSize(200, 40)
        applyChangesBtn.clicked.connect(self.apply_changes)
        self.btnLayout.addWidget(applyChangesBtn)

        return None

    def apply_changes(self):
        newRole = self.roles.currentText()
        newIsActive = self.isActive.isChecked()

        update_user(self.user['login'], newRole, newIsActive)
        QMessageBox.information(self, 'Успех', 'Учетная запись успешно обновлена')
        return None

class ManageEmployeeWindow(QDialog):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Изменение информации о сотруднике")
        self.setWindowIcon(QIcon("assets/icons/app_icon.png"))
        self.setFixedSize(QSize(500, 400))

        self.mainLayout = QVBoxLayout()

        self.label = QLabel('Изменение информации о сотруднике')
        self.mainLayout.addWidget(self.label, alignment=Qt.AlignmentFlag.AlignCenter)
        self.mainLayout.addSpacing(10)

        self.employeeIdLine = QLineEdit(self)
        self.employeeIdLine.setPlaceholderText("Id сотрудника")
        self.employeeIdLine.setFixedWidth(300)
        self.employeeIdLine.setValidator(QRegularExpressionValidator(QRegularExpression(r'^\d*$')))
        self.mainLayout.addWidget(self.employeeIdLine, alignment=Qt.AlignmentFlag.AlignCenter)

        self.confirmEmployeeIdBtn = QPushButton('Изменить')
        self.confirmEmployeeIdBtn.setFixedWidth(300)
        self.confirmEmployeeIdBtn.clicked.connect(self.open_employee_controls)
        self.mainLayout.addWidget(self.confirmEmployeeIdBtn, alignment=Qt.AlignmentFlag.AlignCenter)

        # Лэйаут для полей
        self.fieldsLayout = QVBoxLayout()
        self.fieldsLayout.setSpacing(10)
        self.mainLayout.addLayout(self.fieldsLayout)


        self.mainLayout.addStretch()

        self.btnLayout = QHBoxLayout()

        closeBtn = QPushButton("Выход")
        closeBtn.setFixedSize(200, 40)
        closeBtn.clicked.connect(self.close)
        self.btnLayout.addWidget(closeBtn)

        self.mainLayout.addLayout(self.btnLayout)

        self.setLayout(self.mainLayout)

    def open_employee_controls(self):
        try:
            employee = get_employee_by_id(int(self.employeeIdLine.text()))
        except ValueError:
            QMessageBox.warning(self, 'Ошибка', 'Некорректный id пользователя')
            return None

        if not employee['success']:
            QMessageBox.warning(self, 'Ошибка', employee['data'])
            return None

        self.employeeData = employee['data']

        self.label.setText(f'Изменение информации о сотруднике: {self.employeeData['id']}')
        self.employeeIdLine.deleteLater()
        self.confirmEmployeeIdBtn.deleteLater()

        # Фамилия
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

        # Имя
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

        # Серия паспорта
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

        # Номер паспорта
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

        # Телефон
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

        # Выбор должности
        postLayout = QHBoxLayout()
        postLabel = QLabel("Должность: ")
        postLabel.setFixedWidth(150)
        self.post = QComboBox(self)
        self.post.addItems(get_posts())
        self.post.setCurrentText(self.employeeData['post'])
        postLayout.addWidget(postLabel)
        postLayout.addWidget(self.post)

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

        # Работает/уволен
        isActiveLayout = QHBoxLayout()
        isActiveLabel = QLabel("Работает: ")
        isActiveLabel.setFixedWidth(150)
        self.isActive = QCheckBox(self)
        self.isActive.setChecked(self.employeeData['isActive'])
        isActiveLayout.addWidget(isActiveLabel)
        isActiveLayout.addWidget(self.isActive)

        # Позиционирование полей
        self.fieldsLayout.addLayout(lastNameLayout)
        self.fieldsLayout.addLayout(firstNameLayout)
        self.fieldsLayout.addLayout(passportSeriesLayout)
        self.fieldsLayout.addLayout(passportNumberLayout)
        self.fieldsLayout.addLayout(phoneNumberLayout)
        self.fieldsLayout.addLayout(postLayout)
        self.fieldsLayout.addLayout(warehouseLayout)
        self.fieldsLayout.addLayout(isActiveLayout)

        # Кнопки
        addEmployeeBtn = QPushButton("Изменить")
        addEmployeeBtn.setFixedSize(200, 40)
        addEmployeeBtn.clicked.connect(self.update_employee_info)
        self.btnLayout.addWidget(addEmployeeBtn)




    def update_employee_info(self):

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
        result = update_employee(self.employeeData['id'],firstName, lastName, passportSeries, passportNumber, phoneNumber, post,int(self.isActive.isChecked()), warehouses)
        if result['success']:
            QMessageBox.information(self, 'Успех', result['message'])
            return None
        else:
            QMessageBox.information(self, 'Ошибка', result['message'])
            return None


class AddEmployeeWindow(QDialog):
    def __init__(self):
        super().__init__()

        self.setWindowTitle("Добавление сотрудника")
        self.setWindowIcon(QIcon("assets/icons/app_icon.png"))
        self.setFixedSize(QSize(500, 400))

        mainLayout = QVBoxLayout()

        label = QLabel('Добавление сотрудника')
        mainLayout.addWidget(label, alignment=Qt.AlignmentFlag.AlignCenter)
        mainLayout.addSpacing(10)

        # Поля
        fieldsLayout = QVBoxLayout()
        fieldsLayout.setSpacing(10)

        # Фамилия
        lastNameLayout = QHBoxLayout()
        lastNameLabel = QLabel("Фамилия: ")
        lastNameLabel.setFixedWidth(150)
        self.lastName = QLineEdit(self)
        self.lastName.setPlaceholderText("Фамилия сотрудника")
        self.lastName.setMaxLength(100)
        self.lastName.setValidator(QRegularExpressionValidator(QRegularExpression(r'[A-Za-zA-Яа-яЁё]*$')))
        lastNameLayout.addWidget(lastNameLabel)
        lastNameLayout.addWidget(self.lastName)

        # Имя
        firstNameLayout = QHBoxLayout()
        firstNameLabel = QLabel("Имя: ")
        firstNameLabel.setFixedWidth(150)
        self.firstName = QLineEdit(self)
        self.firstName.setPlaceholderText("Имя сотрудника")
        self.firstName.setMaxLength(50)
        self.firstName.setValidator(QRegularExpressionValidator(QRegularExpression(r'[A-Za-zA-Яа-яЁё]*$')))
        firstNameLayout.addWidget(firstNameLabel)
        firstNameLayout.addWidget(self.firstName)

        # Серия паспорта
        passportSeriesLayout = QHBoxLayout()
        passportSeriesLabel = QLabel("Серия паспорта: ")
        passportSeriesLabel.setFixedWidth(150)
        self.passportSeries = QLineEdit(self)
        self.passportSeries.setPlaceholderText("Серия паспорта сотрудника")
        self.passportSeries.setMaxLength(4)
        self.passportSeries.setValidator(QRegularExpressionValidator(QRegularExpression(r'^\d*$')))
        passportSeriesLayout.addWidget(passportSeriesLabel)
        passportSeriesLayout.addWidget(self.passportSeries)

        # Номер паспорта
        passportNumberLayout = QHBoxLayout()
        passportNumberLabel = QLabel("Номер паспорта:")
        passportNumberLabel.setFixedWidth(150)
        self.passportNumber = QLineEdit(self)
        self.passportNumber.setPlaceholderText("Номер паспорта сотрудника")
        self.passportNumber.setMaxLength(6)
        self.passportNumber.setValidator(QRegularExpressionValidator(QRegularExpression(r'^\d*$')))
        passportNumberLayout.addWidget(passportNumberLabel)
        passportNumberLayout.addWidget(self.passportNumber)

        # Телефон
        phoneNumberLayout = QHBoxLayout()
        phoneNumberLabel = QLabel("Номер телефона:")
        phoneNumberLabel.setFixedWidth(150)
        self.phoneNumber = QLineEdit(self)
        self.phoneNumber.setPlaceholderText("Номер телефона сотрудника")
        self.phoneNumber.setMaxLength(20)
        self.phoneNumber.setValidator(QRegularExpressionValidator(QRegularExpression(r'^\d*$')))
        phoneNumberLayout.addWidget(phoneNumberLabel)
        phoneNumberLayout.addWidget(self.phoneNumber)

        # Выбор должности
        postLayout = QHBoxLayout()
        postLabel = QLabel("Должность: ")
        postLabel.setFixedWidth(150)
        self.post = QComboBox(self)
        self.post.addItem("Выберите должность сотрудника")
        self.post.addItems(get_posts())
        postLayout.addWidget(postLabel)
        postLayout.addWidget(self.post)

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

        # Позиционирование полей
        fieldsLayout.addLayout(lastNameLayout)
        fieldsLayout.addLayout(firstNameLayout)
        fieldsLayout.addLayout(passportSeriesLayout)
        fieldsLayout.addLayout(passportNumberLayout)
        fieldsLayout.addLayout(phoneNumberLayout)
        fieldsLayout.addLayout(postLayout)
        fieldsLayout.addLayout(warehouseLayout)

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

class CreateInviteCodeWindow(QDialog):
    def __init__(self):
        super().__init__()

        self.setWindowTitle("Добавление сотрудника")
        self.setWindowIcon(QIcon("assets/icons/app_icon.png"))
        self.setFixedSize(QSize(500, 200))

        mainLayout = QVBoxLayout()

        label = QLabel('Создание пригласительного кода')
        mainLayout.addWidget(label, alignment=Qt.AlignmentFlag.AlignCenter)
        mainLayout.addSpacing(10)

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

        # Роль для будущей учетной записи
        roleLayout = QHBoxLayout()
        roleLabel = QLabel('Роль: ')
        roleLabel.setFixedWidth(150)
        self.roleBox = QComboBox()
        self.roleBox.addItem("Выберите роль пользователя")
        self.roleBox.addItems(get_roles())
        roleLayout.addWidget(roleLabel)
        roleLayout.addWidget(self.roleBox)

        # Позиционирование полей
        fieldsLayout.addLayout(employeeIdLayout)
        fieldsLayout.addLayout(codeLayout)
        fieldsLayout.addLayout(roleLayout)

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
        if not self.employeeIdLine.text().strip():
            QMessageBox.warning(self, 'Ошибка', 'Введите id пользователя')
            return None
        employeeId = int(self.employeeIdLine.text().strip())

        if len(self.codeLine.text().strip()) < 5:
            QMessageBox.warning(self, 'Ошибка', 'Текст кода должен содержать хотя бы 5 символов')
            return None
        code = self.codeLine.text().strip()

        if self.roleBox.currentIndex() == 0:
            QMessageBox.warning(self, 'Ошибка', 'Выберите роль будущей учетной записи')
            return None
        role = self.roleBox.currentText()

        result = create_invite_code(code,employeeId,role)
        if result['success']:
            QMessageBox.information(self,'Успех', result['message'])
            return None
        else:
            QMessageBox.warning(self, 'Ошибка', result['message'])
            return None

class UserControlsWindow(BaseWindow):

    # Характеристики окна
    widowTitle: str = 'Система складского учета - Контроль учетных записей'
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
        contentLayout.setContentsMargins(50,10,0,10)
        contentLayout.setSpacing(0)

        scrollArea = QScrollArea()
        scrollArea.setWidgetResizable(True)
        scrollArea.setWidget(contentWidget)
        scrollArea.setHorizontalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAlwaysOff)

        # Заголовок страницы
        titleLabel = QLabel("Контроль учетных записей")
        titleLabel.setFixedHeight(40)
        titleLabel.setAlignment(Qt.AlignmentFlag.AlignCenter)
        contentLayout.addWidget(titleLabel, alignment=Qt.AlignmentFlag.AlignTop)
        contentLayout.addSpacing(10)

        # Layout с информацией на странице
        infoLayout = QVBoxLayout()
        infoLayout.setContentsMargins(50,20,50,20)

        # Layout с элементами для работы с учетными записями
        usersLayout = QVBoxLayout()

        # Заголовок элементов для работы с учетными записями
        usersLabel = QLabel("Учетные записи")
        usersLabel.setFixedWidth(620)
        usersLabel.setAlignment(Qt.AlignmentFlag.AlignCenter)
        usersLayout.addWidget(usersLabel, alignment=Qt.AlignmentFlag.AlignCenter)
        usersLayout.addSpacing(5)

        # Данные для таблицы с пользователями
        usersHeaders = ["Логин", "Роль", "Фамилия", "Имя", "Активен"]
        usersData = get_users()
        usersModel = TableModel(usersData, usersHeaders)

        #Модель для фильтрации
        self.usersFilterModel = MultiFilterProxyModelUsers()
        self.usersFilterModel.setSourceModel(usersModel)


        # Виджет таблицы
        usersTable = QTableView()
        usersTable.verticalHeader().setVisible(False)
        usersTable.setModel(self.usersFilterModel)
        usersTable.resizeColumnsToContents()
        usersTable.setAlternatingRowColors(True)
        usersTable.setSelectionBehavior(usersTable.SelectionBehavior.SelectRows)
        usersTable.setFixedSize(620, 200)
        usersTable.horizontalHeader().setSectionResizeMode(QHeaderView.ResizeMode.Stretch)
        usersLayout.addWidget(usersTable, alignment=Qt.AlignmentFlag.AlignCenter)


        # Элементы для фильтрации
        employeesFilterFields = QVBoxLayout()

        self.loginFilter = QLineEdit()
        self.loginFilter.setFixedSize(620, 30)
        self.loginFilter.textChanged.connect(self.update_users_filters)
        self.loginFilter.setPlaceholderText("Логин")


        self.lastNameFilter = QLineEdit()
        self.lastNameFilter.setFixedSize(620, 30)
        self.lastNameFilter.textChanged.connect(self.update_users_filters)
        self.lastNameFilter.setPlaceholderText("Фамилия")


        self.firstNameFilter = QLineEdit()
        self.firstNameFilter.setFixedSize(620, 30)
        self.firstNameFilter.textChanged.connect(self.update_users_filters)
        self.firstNameFilter.setPlaceholderText("Имя")


        self.roleFilter = QComboBox()
        self.roleFilter.setFixedSize(620, 30)
        self.roleFilter.currentTextChanged.connect(self.update_users_filters)
        self.roleFilter.addItem("Все роли")
        self.roleFilter.addItems(get_roles())

        employeesFilterFields.addWidget(self.roleFilter, alignment=Qt.AlignmentFlag.AlignCenter)
        employeesFilterFields.addWidget(self.loginFilter, alignment=Qt.AlignmentFlag.AlignCenter)
        employeesFilterFields.addWidget(self.lastNameFilter, alignment=Qt.AlignmentFlag.AlignCenter)
        employeesFilterFields.addWidget(self.firstNameFilter, alignment=Qt.AlignmentFlag.AlignCenter)

        usersFilterButtons = QHBoxLayout()

        usersFilterButtons.addStretch()
        filterActive = QPushButton("Активные")
        filterActive.setFixedSize(205,30)
        filterActive.clicked.connect(lambda: self.set_users_active_filter(1))
        usersFilterButtons.addWidget(filterActive, alignment=Qt.AlignmentFlag.AlignCenter)

        filterInactive = QPushButton("Неактивные")
        filterInactive.setFixedSize(205,30)
        filterInactive.clicked.connect(lambda: self.set_users_active_filter(0))
        usersFilterButtons.addWidget(filterInactive, alignment=Qt.AlignmentFlag.AlignCenter)

        turnOffActiveFilter = QPushButton("Все")
        turnOffActiveFilter.setFixedSize(205,30)
        turnOffActiveFilter.clicked.connect(lambda: self.set_users_active_filter(None))
        usersFilterButtons.addWidget(turnOffActiveFilter, alignment=Qt.AlignmentFlag.AlignCenter)
        usersFilterButtons.addStretch()


        usersLayout.addLayout(usersFilterButtons)
        usersLayout.addLayout(employeesFilterFields)

        # Изменение учетной записи
        manageUserButton = QPushButton("Изменить учетную запись")
        manageUserButton.setFixedSize(620,30)
        manageUserButton.clicked.connect(self.manage_user)
        usersLayout.addWidget(manageUserButton, alignment=Qt.AlignmentFlag.AlignCenter)


        usersLayout.addSpacing(40)
        infoLayout.addLayout(usersLayout)

        # Сотрудники
        employeeLayout = QVBoxLayout()

        employeesLabel = QLabel("Сотрудники")
        employeeLayout.addWidget(employeesLabel, alignment=Qt.AlignmentFlag.AlignCenter)
        employeeLayout.addSpacing(5)

        employeeHeaders = ["id", "Имя", "Фамилия", "Серия\nпаспорта", "Номер\nпаспорта", "Телефон", "Должность", "Дата", "Работает"]
        employeesData = get_employees()
        employeesModel = TableModel(employeesData, employeeHeaders)

        # Модель для фильтрации
        self.employeesFilterModel = MultiFilterProxyModelEmoloyees()
        self.employeesFilterModel.setSourceModel(employeesModel)

        # Виджет таблицы
        employeesTable = QTableView()
        employeesTable.verticalHeader().setVisible(False)
        employeesTable.setModel(self.employeesFilterModel)
        employeesTable.resizeColumnsToContents()
        employeesTable.setAlternatingRowColors(True)
        employeesTable.setSelectionBehavior(employeesTable.SelectionBehavior.SelectRows)
        employeesTable.setFixedSize(800, 200)
        employeesTable.horizontalHeader().setSectionResizeMode(QHeaderView.ResizeMode.Stretch)
        employeeLayout.addWidget(employeesTable, alignment=Qt.AlignmentFlag.AlignCenter)

        # Элементы для фильтрации сотрудников
        employeesFilterFields = QVBoxLayout()

        self.employeeLastNameFilter = QLineEdit()
        self.employeeLastNameFilter.setFixedSize(620, 30)
        self.employeeLastNameFilter.textChanged.connect(self.update_employees_filters)
        self.employeeLastNameFilter.setPlaceholderText("Фамилия")

        self.employeeFirstNameFilter = QLineEdit()
        self.employeeFirstNameFilter.setFixedSize(620, 30)
        self.employeeFirstNameFilter.textChanged.connect(self.update_employees_filters)
        self.employeeFirstNameFilter.setPlaceholderText("Имя")

        self.postFilter = QComboBox()
        self.postFilter.setFixedSize(620, 30)
        self.postFilter.currentTextChanged.connect(self.update_employees_filters)
        self.postFilter.addItem("Все должности")
        self.postFilter.addItems(get_posts())

        employeesFilterFields.addWidget(self.postFilter, alignment=Qt.AlignmentFlag.AlignCenter)
        employeesFilterFields.addWidget(self.employeeLastNameFilter, alignment=Qt.AlignmentFlag.AlignCenter)
        employeesFilterFields.addWidget(self.employeeFirstNameFilter, alignment=Qt.AlignmentFlag.AlignCenter)

        employeesFilterButtons = QHBoxLayout()

        employeesFilterButtons.addStretch()
        employeeFilterActive = QPushButton("Активные")
        employeeFilterActive.setFixedSize(205, 30)
        employeeFilterActive.clicked.connect(lambda: self.set_employees_active_filter(1))
        employeesFilterButtons.addWidget(employeeFilterActive, alignment=Qt.AlignmentFlag.AlignCenter)

        employeeFilterInactive = QPushButton("Неактивные")
        employeeFilterInactive.setFixedSize(205, 30)
        employeeFilterInactive.clicked.connect(lambda: self.set_employees_active_filter(0))
        employeesFilterButtons.addWidget(employeeFilterInactive, alignment=Qt.AlignmentFlag.AlignCenter)

        employeeTurnOffActiveFilter = QPushButton("Все")
        employeeTurnOffActiveFilter.setFixedSize(205, 30)
        employeeTurnOffActiveFilter.clicked.connect(lambda: self.set_employees_active_filter(None))
        employeesFilterButtons.addWidget(employeeTurnOffActiveFilter, alignment=Qt.AlignmentFlag.AlignCenter)
        employeesFilterButtons.addStretch()

        employeeLayout.addLayout(employeesFilterButtons)
        employeeLayout.addLayout(employeesFilterFields)

        # Добавление сотрудника
        addEmployeeButton = QPushButton("Добавить сотрудника")
        addEmployeeButton.setFixedSize(620, 30)
        addEmployeeButton.clicked.connect(self.add_employee)
        employeeLayout.addWidget(addEmployeeButton, alignment=Qt.AlignmentFlag.AlignCenter)

        # Редактирование сотрудника
        manageEmployeeButton = QPushButton("Изменить запись о сотруднике")
        manageEmployeeButton.setFixedSize(620, 30)
        manageEmployeeButton.clicked.connect(self.manage_employee)
        employeeLayout.addWidget(manageEmployeeButton, alignment=Qt.AlignmentFlag.AlignCenter)

        employeeLayout.addSpacing(40)

        infoLayout.addLayout(employeeLayout)

        # Пригласительные коды
        inviteCodeLayout = QVBoxLayout()
        inviteCodeLabel = QLabel('Пригласительный код')
        inviteCodeLayout.addWidget(inviteCodeLabel, alignment=Qt.AlignmentFlag.AlignCenter)
        inviteCodeLayout.addSpacing(5)

        createInviteCodeBtn = QPushButton('Создать пригласительный код')
        createInviteCodeBtn.setFixedSize(300, 50)
        createInviteCodeBtn.clicked.connect(self.create_invite_code)
        inviteCodeLayout.addWidget(createInviteCodeBtn, alignment=Qt.AlignmentFlag.AlignCenter)

        infoLayout.addLayout(inviteCodeLayout)
        infoLayout.addStretch()

        contentLayout.addLayout(infoLayout)



        mainLayout.addWidget(scrollArea)

        """Навигационная панель"""
        self.navPanel = NavPanel(self)
        mainLayout.addWidget(self.navPanel)


        self.setLayout(mainLayout)

    def update_users_filters(self):
        self.usersFilterModel.loginFilter = self.loginFilter.text()
        self.usersFilterModel.lastNameFilter = self.lastNameFilter.text()
        self.usersFilterModel.firstNameFilter = self.firstNameFilter.text()
        self.usersFilterModel.roleFilter = self.roleFilter.currentText()
        self.usersFilterModel.invalidateFilter()

    def update_employees_filters(self):
        self.employeesFilterModel.firstNameFilter = self.employeeFirstNameFilter.text()
        self.employeesFilterModel.lastNameFilter = self.employeeLastNameFilter.text()
        self.employeesFilterModel.postFilter = self.postFilter.currentText()
        self.employeesFilterModel.invalidateFilter()

    def set_users_active_filter(self, value):
        self.usersFilterModel.isActiveFilter = value
        self.usersFilterModel.invalidateFilter()

    def set_employees_active_filter(self, value):
        self.employeesFilterModel.isActiveFilter = value
        self.employeesFilterModel.invalidateFilter()

    def update_users_table(self):
        newUsersData = get_users()
        self.usersFilterModel.sourceModel().update_data(newUsersData)
        self.usersFilterModel.invalidateFilter()

    def update_employees_table(self):
        newEmployeesData = get_employees()
        self.employeesFilterModel.sourceModel().update_data(newEmployeesData)
        self.employeesFilterModel.invalidateFilter()

    def manage_user(self):
        manageUserWindow = ManageUserWindow()
        manageUserWindow.exec()
        self.update_users_table()

    def manage_employee(self):
        manageEmployeeWindow = ManageEmployeeWindow()
        manageEmployeeWindow.exec()
        self.update_employees_table()

    def add_employee(self):
        addUserWindow = AddEmployeeWindow()
        addUserWindow.exec()
        self.update_employees_table()

    def create_invite_code(self):
        createInviteCodeWindow = CreateInviteCodeWindow()
        createInviteCodeWindow.exec()