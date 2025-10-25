import os
import sys

from PyQt6.QtCore import Qt, QSize
from PyQt6.QtGui import QFontDatabase, QFont
from PyQt6.QtWidgets import QApplication, QStackedWidget, QMainWindow, QWIDGETSIZE_MAX

from ui.login_window import LoginWindow
from ui.main_window import MainWindow
from ui.register_window import RegisterWindow


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
    def __init__(self):
        super().__init__()

        # Создание окон
        self.loginWindow = LoginWindow()
        self.registerWindow = RegisterWindow()
        self.mainWindow = MainWindow()

        # Добавление окон в менеджер
        self.addWidget(self.loginWindow)
        self.addWidget(self.registerWindow)
        self.addWidget(self.mainWindow)

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
        secondWindowManager.show()


class ResizableWindowManager(QStackedWidget):
    def __init__(self):
        super().__init__()

        self.mainWindow = MainWindow()

        self.addWidget(self.mainWindow)

        self.show_main(self.mainWindow)

    def show_main(self, window):
        window.apply_window_properties(self)
        self.setCurrentWidget(self.mainWindow)


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
    windowManager = FixedWindowManager()
    secondWindowManager = ResizableWindowManager()

    # Активация менеджера окон
    windowManager.show()

    sys.exit(app.exec())