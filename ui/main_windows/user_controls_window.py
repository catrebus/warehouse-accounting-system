from PyQt6.QtCore import QSize, Qt, QSortFilterProxyModel
from PyQt6.QtWidgets import QLabel, QWidget, QWIDGETSIZE_MAX, QVBoxLayout, QStackedLayout, QHBoxLayout, QTableView, \
    QHeaderView, QLineEdit, QComboBox, QPushButton, QScrollArea

from services.control_user_service import get_employees
from services.info_from_db import get_users, get_roles, get_posts
from ui.base_window import BaseWindow
from ui.ui_elements.add_employee_window import AddEmployeeWindow
from ui.ui_elements.create_invitecode_window import CreateInviteCodeWindow
from ui.ui_elements.manage_employee_window import ManageEmployeeWindow
from ui.ui_elements.manage_user_window import ManageUserWindow
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

class MultiFilterProxyModelEmployees(QSortFilterProxyModel):
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


class UserControlsWindow(BaseWindow):

    # Характеристики окна
    widowTitle: str = 'Система складского учета - Контроль учетных записей'
    windowSize: QSize = QSize(960, 540)
    resizable: bool = True
    windowIconPath: str = 'assets/icons/app_icon.png'

    def __init__(self, user):
        super().__init__()
        """Получение данных о пользователе"""
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

        # Layout для контента страницы
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

        # Фильтрация по активности учетной записи
        usersFilterButtons = QHBoxLayout()

        usersFilterButtons.addStretch()
        filterActive = QPushButton("Активные")
        filterActive.setFixedSize(205, 30)
        filterActive.clicked.connect(lambda: self.set_users_active_filter(1))
        usersFilterButtons.addWidget(filterActive, alignment=Qt.AlignmentFlag.AlignCenter)

        filterInactive = QPushButton("Неактивные")
        filterInactive.setFixedSize(205, 30)
        filterInactive.clicked.connect(lambda: self.set_users_active_filter(0))
        usersFilterButtons.addWidget(filterInactive, alignment=Qt.AlignmentFlag.AlignCenter)

        turnOffActiveFilter = QPushButton("Все")
        turnOffActiveFilter.setFixedSize(205, 30)
        turnOffActiveFilter.clicked.connect(lambda: self.set_users_active_filter(None))
        usersFilterButtons.addWidget(turnOffActiveFilter, alignment=Qt.AlignmentFlag.AlignCenter)
        usersFilterButtons.addStretch()

        usersLayout.addLayout(usersFilterButtons)

        # Layout для элементов поиска и фильтрации учетных записей
        employeesFilterFields = QVBoxLayout()

        # Список ролей для фильтрации
        self.roleFilter = QComboBox()
        self.roleFilter.setFixedSize(620, 30)
        self.roleFilter.addItem("Все роли")
        self.roleFilter.addItems(get_roles())
        self.roleFilter.currentTextChanged.connect(self.update_users_filters)
        employeesFilterFields.addWidget(self.roleFilter, alignment=Qt.AlignmentFlag.AlignCenter)

        # Поле поиска по логину
        self.loginFilter = QLineEdit()
        self.loginFilter.setFixedSize(620, 30)
        self.loginFilter.textChanged.connect(self.update_users_filters)
        self.loginFilter.setPlaceholderText("Логин")
        employeesFilterFields.addWidget(self.loginFilter, alignment=Qt.AlignmentFlag.AlignCenter)

        # Поле поиска по фамилии
        self.userLastNameFilter = QLineEdit()
        self.userLastNameFilter.setFixedSize(620, 30)
        self.userLastNameFilter.textChanged.connect(self.update_users_filters)
        self.userLastNameFilter.setPlaceholderText("Фамилия")
        employeesFilterFields.addWidget(self.userLastNameFilter, alignment=Qt.AlignmentFlag.AlignCenter)

        # Поле поиска по имени
        self.userFirstNameFilter = QLineEdit()
        self.userFirstNameFilter.setFixedSize(620, 30)
        self.userFirstNameFilter.textChanged.connect(self.update_users_filters)
        self.userFirstNameFilter.setPlaceholderText("Имя")
        employeesFilterFields.addWidget(self.userFirstNameFilter, alignment=Qt.AlignmentFlag.AlignCenter)

        # Добавление элементов фильтрации
        usersLayout.addLayout(usersFilterButtons)
        usersLayout.addLayout(employeesFilterFields)

        # Кнопка изменения учетной записи
        manageUserButton = QPushButton("Изменить учетную запись")
        manageUserButton.setFixedSize(620,30)
        manageUserButton.clicked.connect(self.manage_user)
        usersLayout.addWidget(manageUserButton, alignment=Qt.AlignmentFlag.AlignCenter)


        usersLayout.addSpacing(40)
        infoLayout.addLayout(usersLayout)

        # Layout для элементов работы с сотрудниками
        employeeLayout = QVBoxLayout()

        # Заголовок элементов для работы с сотрудниками
        employeesLabel = QLabel("Сотрудники")
        employeeLayout.addWidget(employeesLabel, alignment=Qt.AlignmentFlag.AlignCenter)
        employeeLayout.addSpacing(5)

        # Данные для таблицы с сотрудниками
        employeeHeaders = ["id", "Имя", "Фамилия", "Серия\nпаспорта", "Номер\nпаспорта", "Телефон", "Должность", "Дата", "Работает"]
        employeesData = get_employees()
        employeesModel = TableModel(employeesData, employeeHeaders)

        # Модель для фильтрации
        self.employeesFilterModel = MultiFilterProxyModelEmployees()
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

        # Фильтрация ныне работающих и уволенных сотрудников
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

        # Элементы для фильтрации и поиска сотрудников
        employeesFilterFields = QVBoxLayout()

        # Фильтрация по должности
        self.postFilter = QComboBox()
        self.postFilter.setFixedSize(620, 30)
        self.postFilter.addItem("Все должности")
        self.postFilter.addItems(get_posts())
        self.postFilter.currentTextChanged.connect(self.update_employees_filters)
        employeesFilterFields.addWidget(self.postFilter, alignment=Qt.AlignmentFlag.AlignCenter)

        # Поиск по фамилии
        self.employeeLastNameFilter = QLineEdit()
        self.employeeLastNameFilter.setFixedSize(620, 30)
        self.employeeLastNameFilter.textChanged.connect(self.update_employees_filters)
        self.employeeLastNameFilter.setPlaceholderText("Фамилия")
        employeesFilterFields.addWidget(self.employeeLastNameFilter, alignment=Qt.AlignmentFlag.AlignCenter)

        # Поиск по имени
        self.employeeFirstNameFilter = QLineEdit()
        self.employeeFirstNameFilter.setFixedSize(620, 30)
        self.employeeFirstNameFilter.textChanged.connect(self.update_employees_filters)
        self.employeeFirstNameFilter.setPlaceholderText("Имя")
        employeesFilterFields.addWidget(self.employeeFirstNameFilter, alignment=Qt.AlignmentFlag.AlignCenter)

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

        # Создание пригласительного кода
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
        """Обновление фильтров для таблицы учетных записей"""
        self.usersFilterModel.roleFilter = self.roleFilter.currentText()
        self.usersFilterModel.loginFilter = self.loginFilter.text()
        self.usersFilterModel.lastNameFilter = self.userLastNameFilter.text()
        self.usersFilterModel.firstNameFilter = self.userFirstNameFilter.text()
        self.usersFilterModel.invalidateFilter()

    def update_employees_filters(self):
        """Обновление фильтров для таблицы сотрудников"""
        self.employeesFilterModel.postFilter = self.postFilter.currentText()
        self.employeesFilterModel.lastNameFilter = self.employeeLastNameFilter.text()
        self.employeesFilterModel.firstNameFilter = self.employeeFirstNameFilter.text()
        self.employeesFilterModel.invalidateFilter()

    def set_users_active_filter(self, value):
        """Установка фильтра учетных записей по активности"""
        self.usersFilterModel.isActiveFilter = value
        self.usersFilterModel.invalidateFilter()

    def set_employees_active_filter(self, value):
        """Установка фильтров работающих/уволенных сотрудников"""
        self.employeesFilterModel.isActiveFilter = value
        self.employeesFilterModel.invalidateFilter()

    def update_users_table(self):
        """Обновление данных для таблицы учетных записей"""
        newUsersData = get_users()
        self.usersFilterModel.sourceModel().update_data(newUsersData)
        self.usersFilterModel.invalidateFilter()

    def update_employees_table(self):
        """Обновление данных для таблицы сотрудников"""
        newEmployeesData = get_employees()
        self.employeesFilterModel.sourceModel().update_data(newEmployeesData)
        self.employeesFilterModel.invalidateFilter()

    def manage_user(self):
        """Открытие окна управления учетной записью"""
        manageUserWindow = ManageUserWindow()
        manageUserWindow.exec()
        self.update_users_table()

    def manage_employee(self):
        """Открытие окна управления сотрудником"""
        manageEmployeeWindow = ManageEmployeeWindow()
        manageEmployeeWindow.exec()
        self.update_employees_table()

    def add_employee(self):
        """Открытие окна добавления сотрудника"""
        addUserWindow = AddEmployeeWindow()
        addUserWindow.exec()
        self.update_employees_table()

    def create_invite_code(self):
        """Открытие окна создания пригласительного кода"""
        createInviteCodeWindow = CreateInviteCodeWindow()
        createInviteCodeWindow.exec()