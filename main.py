import os
import sys

from PyQt6.QtGui import QFontDatabase, QFont
from PyQt6.QtWidgets import QApplication
from ui.login_window import LoginWindow

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

if __name__ == "__main__":
    app = QApplication(sys.argv)

    # Применение шрифта
    font_name = load_font()
    if font_name:
        print('Основной шрифт установлен')
        app.setFont(QFont(font_name, 14))

    # Применение стилей
    app.setStyleSheet(load_stylesheets('styles/login.qss'))

    window = LoginWindow()
    window.show()
    sys.exit(app.exec())