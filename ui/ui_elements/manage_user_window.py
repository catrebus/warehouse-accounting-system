from PyQt6.QtCore import QSize, Qt
from PyQt6.QtGui import QIcon
from PyQt6.QtWidgets import QLabel, QVBoxLayout, QHBoxLayout, QLineEdit, QComboBox, QPushButton, QDialog, QMessageBox, \
    QCheckBox

from services.control_user_service import get_user_by_login, update_user
from services.info_from_db import get_roles


class ManageUserWindow(QDialog):
    """Диалоговое окно для управления характеристиками учетных записей"""
    def __init__(self):
        super().__init__()
        # Настройка параметров окна
        self.setWindowTitle("Управление пользователем")
        self.setWindowIcon(QIcon("assets/icons/app_icon.png"))
        self.setFixedSize(QSize(480,270))

        # Главный layout
        self.mainLayout = QVBoxLayout()

        # labal окна
        self.label = QLabel('Управление учетной записью')
        self.mainLayout.addWidget(self.label, alignment=Qt.AlignmentFlag.AlignCenter)
        self.mainLayout.addSpacing(10)

        # Layout для взаимодействия с учетной записью
        self.userLayout = QVBoxLayout()

        # Поле логина пользователя
        self.userLogin = QLineEdit(self)
        self.userLogin.setFixedWidth(300)
        self.userLogin.setPlaceholderText("Логин пользователя")
        self.userLayout.addWidget(self.userLogin, alignment=Qt.AlignmentFlag.AlignCenter)

        # Кнопка для открытия управления учетной записью
        self.confirmLogin = QPushButton("Изменить")
        self.confirmLogin.clicked.connect(self.open_user_controls)
        self.confirmLogin.setFixedWidth(300)
        self.userLayout.addWidget(self.confirmLogin, alignment=Qt.AlignmentFlag.AlignCenter)

        self.mainLayout.addLayout(self.userLayout)
        self.mainLayout.addStretch()

        # Кнопка выхода без сохранения
        self.btnLayout = QHBoxLayout()

        closeBtn = QPushButton("Выход")
        closeBtn.setFixedSize(200,40)
        closeBtn.clicked.connect(self.close)
        self.btnLayout.addWidget(closeBtn)
        self.mainLayout.addLayout(self.btnLayout)

        self.setLayout(self.mainLayout)

    def open_user_controls(self):
        """Режим изменения учетной записи"""
        # Получение информации об учетной записи
        self.user = get_user_by_login(self.userLogin.text())

        # Проверка на существования пользователя с введенным логином
        if not self.user:
            QMessageBox.warning(self, 'Ошибка', "Пользователь не найден")
            return None

        # Удаление ненужных элементов
        self.userLogin.deleteLater()
        self.confirmLogin.deleteLater()

        # Изменение label окна
        self.label.setText(f"Управление учетной записью: {self.user['login']}")

        # Информация о владельце учетной записи
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
        self.userLayout.addLayout(roleLayout)

        # Пользователь активен/неактивен
        isActiveLayout = QHBoxLayout()
        isActiveLayout.addWidget(QLabel(f"Активна/Неактивна: " ))
        self.isActive = QCheckBox()
        self.isActive.setChecked(self.user['isActive'])
        isActiveLayout.addWidget(self.isActive, alignment=Qt.AlignmentFlag.AlignLeft)
        self.userLayout.addLayout(isActiveLayout)

        # Кнопка сохранения изменений
        applyChangesBtn = QPushButton("Применить")
        applyChangesBtn.setFixedSize(200, 40)
        applyChangesBtn.clicked.connect(self.apply_changes)
        self.btnLayout.addWidget(applyChangesBtn)

        return None

    def apply_changes(self):
        """Сохранение изменений"""
        newRole = self.roles.currentText()
        newIsActive = self.isActive.isChecked()

        update_user(self.user['login'], newRole, newIsActive)
        QMessageBox.information(self, 'Успех', 'Учетная запись успешно обновлена')
        return None