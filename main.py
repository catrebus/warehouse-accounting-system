import os
import sys

from PyQt6.QtGui import QFontDatabase, QFont
from PyQt6.QtWidgets import QApplication, QStackedWidget

from ui.main_windows.inventory_window import InventoryWindow
from ui.main_windows.shipments_window import ShipmentsWindow
from ui.main_windows.transfers_window import TransfersWindow
from ui.reg_auth_windows.login_window import LoginWindow
from ui.main_windows.main_window import MainWindow
from ui.reg_auth_windows.register_window import RegisterWindow
from ui.main_windows.user_controls_window import UserControlsWindow
from utils.app_state import AppState


# Загрузка стилей
def load_stylesheets(*files):
    content=''
    for file in files:
        with open(file, 'r', encoding='utf-8') as f:
            content+=f.read() + '\n'
    return content


# Загрузка основного шрифта приложения
def load_font():
    font_dir = os.path.join("assets", "fonts")

    # Фильтрация .ttf файлов в папке
    for file in os.listdir(font_dir):
        if file.endswith(".ttf"):
            path = os.path.join(font_dir, file)
            font_id = QFontDatabase.addApplicationFont(path)
            if font_id == -1:
                print(f"Не удалось загрузить: {file}")
            else:
                families = QFontDatabase.applicationFontFamilies(font_id)
                print(f"Загружен шрифт: {families[0]} из {file}")

    # Список всех доступных шрифтов
    all_fonts = QFontDatabase.families()

    # Проверка наличия шрифта в списке доступных шрифтов
    for name in all_fonts:
        if "Ubuntu Mono" in name:
            return name
    return None


# Контроль всех окон приложения
class FixedWindowManager(QStackedWidget):
    """Менеджер для окон авторизации и регистрации"""
    def __init__(self):
        super().__init__()

        # Создание окон
        self.loginWindow = LoginWindow()
        self.registerWindow = RegisterWindow()


        # Добавление окон в менеджер
        self.addWidget(self.loginWindow)
        self.addWidget(self.registerWindow)


        # Подключение сигналов
        self.loginWindow.switchToRegister.connect(lambda: self.show_register(self.registerWindow))
        self.registerWindow.switchToLogin.connect(lambda: self.show_login(self.loginWindow))
        self.loginWindow.switchToMain.connect(self.show_main)
        self.registerWindow.switchToMain.connect(self.show_main)

        # Установка начального окна
        self.show_login(self.loginWindow)

    """Методы для переключения между окнами"""
    def show_login(self,window):
        window.apply_window_properties(self)
        self.setCurrentWidget(self.loginWindow)

    def show_register(self, window):
        window.apply_window_properties(self)
        self.setCurrentWidget(self.registerWindow)

    def show_main(self):
        self.hide()
        mainWindowManager.init_main_app(AppState.currentUser)
        mainWindowManager.show()


class ResizableWindowManager(QStackedWidget):
    """Менеджер для главных окон приложения"""
    def __init__(self):
        super().__init__()
        # Роль, под которой авторизировался пользователь
        self.userRole = None
        # Главные окна приложения
        self.mainWindow = None
        self.inventoryWindow = None
        self.shipmentsWindow = None
        self.transfersWindow = None
        self.userControlsWindow = None

    def init_main_app(self, user):
        self.userRole = user.role

        self.mainWindow = MainWindow(user)
        self.inventoryWindow = InventoryWindow(user)
        self.shipmentsWindow = ShipmentsWindow(user)
        self.transfersWindow = TransfersWindow(user)
        self.userControlsWindow = UserControlsWindow(user)

        # Стек страниц
        pages = []
        pages.append(self.mainWindow)
        pages.append(self.inventoryWindow)
        pages.append(self.shipmentsWindow)
        pages.append(self.transfersWindow)
        pages.append(self.userControlsWindow)

        # Подключение кнопок навигационной панели
        for i in range(len(pages)):
            pages[i].navPanel.switchToMainPage.connect(self.switch_to_main)
            pages[i].navPanel.switchToInventory.connect(self.switch_to_inventory)
            pages[i].navPanel.switchToShipments.connect(self.switch_to_shipments)
            pages[i].navPanel.switchToTransfers.connect(self.switch_to_transfers)
            pages[i].navPanel.switchToUserControls.connect(self.switch_to_user_controls)

        # Добавление окон в менеджер
        self.addWidget(self.mainWindow)
        self.addWidget(self.inventoryWindow)
        self.addWidget(self.shipmentsWindow)
        self.addWidget(self.transfersWindow)
        self.addWidget(self.userControlsWindow)

        # Установка начального окна
        self.mainWindow.apply_window_properties(self)
        self.setCurrentWidget(self.mainWindow)

    def switch_to_main(self):
        self.mainWindow.apply_window_properties(self)
        self.setCurrentWidget(self.mainWindow)

    def switch_to_inventory(self):
        self.inventoryWindow.refresh()
        self.inventoryWindow.apply_window_properties(self)
        self.setCurrentWidget(self.inventoryWindow)

    def switch_to_shipments(self):
        self.shipmentsWindow.refresh()
        self.shipmentsWindow.apply_window_properties(self)
        self.setCurrentWidget(self.shipmentsWindow)

    def switch_to_transfers(self):
        self.transfersWindow.refresh()
        self.transfersWindow.apply_window_properties(self)
        self.setCurrentWidget(self.transfersWindow)

    def switch_to_user_controls(self):
        self.userControlsWindow.apply_window_properties(self)
        self.setCurrentWidget(self.userControlsWindow)


if __name__ == "__main__":
    app = QApplication(sys.argv)

    # Применение шрифта
    font_name = load_font()
    if font_name:
        print('Основной шрифт установлен')
        app.setFont(QFont(font_name, 14))

    # Применение стилей
    app.setStyleSheet(load_stylesheets('styles/login.qss', 'styles/navigation_panel.qss'))

    # Создание менеджеров окон
    regAuthWindowManager = FixedWindowManager()
    mainWindowManager = ResizableWindowManager()

    # Активация менеджера окон
    regAuthWindowManager.show()

    sys.exit(app.exec())