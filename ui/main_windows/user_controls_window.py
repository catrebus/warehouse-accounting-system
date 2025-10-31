from PyQt6.QtCore import QSize, Qt, QSortFilterProxyModel
from PyQt6.QtGui import QIcon
from PyQt6.QtWidgets import QLabel, QWidget, QWIDGETSIZE_MAX, QVBoxLayout, QStackedLayout, QHBoxLayout, QTableView, \
    QHeaderView, QLineEdit, QComboBox, QPushButton, QDialog, QMessageBox, QCheckBox, QScrollArea

from services.control_user import get_user_by_login, update_user
from services.info_from_db import get_users, get_roles
from ui.base_window import BaseWindow
from ui.ui_elements.nav_panel import NavPanel
from ui.ui_elements.table_model import TableModel
import faulthandler
faulthandler.enable()

class MultiFilterProxyModelUsers(QSortFilterProxyModel):
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

class ManageUserWindow(QDialog):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Управление пользователем")
        self.setWindowIcon(QIcon("assets/icons/app_icon.png"))
        self.setFixedSize(QSize(480,270))

        self.mainLayout = QVBoxLayout()

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

        label = QLabel(f"Управление учетной записью: {self.user['login']}")
        self.userLayout.addWidget(label, alignment=Qt.AlignmentFlag.AlignCenter)
        self.userLayout.addSpacing(10)

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
        usersTable.setModel(self.usersFilterModel)
        usersTable.resizeColumnsToContents()
        usersTable.setAlternatingRowColors(True)
        usersTable.setSelectionBehavior(usersTable.SelectionBehavior.SelectRows)
        usersTable.setFixedSize(620, 200)
        usersTable.horizontalHeader().setSectionResizeMode(QHeaderView.ResizeMode.Stretch)
        usersLayout.addWidget(usersTable, alignment=Qt.AlignmentFlag.AlignCenter)


        # Элементы для фильтрации
        usersFilterFields = QVBoxLayout()



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

        usersFilterFields.addWidget(self.roleFilter, alignment=Qt.AlignmentFlag.AlignCenter)
        usersFilterFields.addWidget(self.loginFilter, alignment=Qt.AlignmentFlag.AlignCenter)
        usersFilterFields.addWidget(self.lastNameFilter, alignment=Qt.AlignmentFlag.AlignCenter)
        usersFilterFields.addWidget(self.firstNameFilter, alignment=Qt.AlignmentFlag.AlignCenter)

        usersFilterButtons = QHBoxLayout()

        usersFilterButtons.addStretch()
        filterActive = QPushButton("Активные")
        filterActive.setFixedSize(205,30)
        filterActive.clicked.connect(lambda: self.set_active_filter(1))
        usersFilterButtons.addWidget(filterActive, alignment=Qt.AlignmentFlag.AlignCenter)

        filterInactive = QPushButton("Неактивные")
        filterInactive.setFixedSize(205,30)
        filterInactive.clicked.connect(lambda: self.set_active_filter(0))
        usersFilterButtons.addWidget(filterInactive, alignment=Qt.AlignmentFlag.AlignCenter)

        turnOffActiveFilter = QPushButton("Все")
        turnOffActiveFilter.setFixedSize(205,30)
        turnOffActiveFilter.clicked.connect(lambda: self.set_active_filter(None))
        usersFilterButtons.addWidget(turnOffActiveFilter, alignment=Qt.AlignmentFlag.AlignCenter)
        usersFilterButtons.addStretch()


        usersLayout.addLayout(usersFilterButtons)
        usersLayout.addLayout(usersFilterFields)

        # Изменение учетной записи
        manageUserButton = QPushButton("Изменить учетную запись")
        manageUserButton.setFixedSize(620,30)
        manageUserButton.clicked.connect(self.manage_user)
        usersLayout.addWidget(manageUserButton, alignment=Qt.AlignmentFlag.AlignCenter)


        usersLayout.addSpacing(40)
        infoLayout.addLayout(usersLayout)

        # Создание пригласительного кода
        inviteCodeLayout = QVBoxLayout()

        inviteCodeLabel = QLabel("Пригласительный код")
        inviteCodeLayout.addWidget(inviteCodeLabel, alignment=Qt.AlignmentFlag.AlignCenter)




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

    def set_active_filter(self, value):
        self.usersFilterModel.isActiveFilter = value
        self.usersFilterModel.invalidateFilter()

    def update_users_table(self):
        newUsersData = get_users()
        self.usersFilterModel.sourceModel().update_data(newUsersData)
        self.usersFilterModel.invalidateFilter()


    def manage_user(self):
        manageUserWindow = ManageUserWindow()
        manageUserWindow.exec()
        self.update_users_table()
