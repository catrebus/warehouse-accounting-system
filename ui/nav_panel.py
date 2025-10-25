from PyQt6.QtCore import Qt, QEasingCurve, QPropertyAnimation
from PyQt6.QtWidgets import QFrame, QVBoxLayout, QLabel, QWidget, QScrollArea, QPushButton



class AnimatedNavButton(QPushButton):
    def __init__(self, iconPath: str, text: str, description: str, parent=None):
        super().__init__(parent)

        self.setObjectName('navButton')

        # Установка атрибутов
        self.iconPath = iconPath
        self.text = text
        self.description = description

        # Базовое состояние
        self.setText('')
        self.setFixedSize(280, 60)
        self.setCursor(Qt.CursorShape.PointingHandCursor)

        # Главный layout
        mainLayout = QVBoxLayout()
        mainLayout.setContentsMargins(5, 5, 5, 5)
        mainLayout.setSpacing(5)

        # Заголовок кнопки
        header = QLabel(self.text)
        header.setObjectName('btnHeader')
        header.setStyleSheet("background:transparent;")
        header.setAlignment(Qt.AlignmentFlag.AlignCenter)
        mainLayout.addWidget(header)

        self.setLayout(mainLayout)


class NavPanel(QFrame):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setStyleSheet("""
            QFrame {
                background-color: #8A2BE2;
                border: none;
            }
        """)
        # Возможные размеры панели
        self.expandedWidth = 300
        self.collapsedWidth = 70

        # Панель свернута/развернута
        self.isExpanded = False
        self.isAnimating = False

        # Установка изначального размера
        self.setFixedWidth(self.collapsedWidth)

        # Анимация панели
        self.animation = QPropertyAnimation(self, b"minimumWidth", self)
        self.animation.setDuration(300)
        self.animation.setEasingCurve(QEasingCurve.Type.OutCubic)

        self.animation.finished.connect(self.on_animation_finished)

        # Инициализация пользовательского интерфейса
        self.init_ui()

    def init_ui(self):
        """Инициализация пользовательского интерфейса"""

        # Создание основного layout
        mainLayout = QVBoxLayout()
        mainLayout.setContentsMargins(5, 20, 5, 20)
        mainLayout.setSpacing(10)

        # Заголовок панели
        self.navHeader = QLabel('☰')
        self.navHeader.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.navHeader.setObjectName('navHeader')
        mainLayout.addWidget(self.navHeader)

        # Контейнер для кнопок панели
        self.btnContainer = QWidget()
        self.btnContainer.setObjectName('btnContainer')
        self.btnLayout = QVBoxLayout(self.btnContainer)
        self.btnLayout.setContentsMargins(0, 0, 0, 0)
        self.btnLayout.setSpacing(4)

        # Скролл для контейнера
        self.scroll = QScrollArea()
        self.scroll.setObjectName('btnScrollArea')
        self.scroll.setWidgetResizable(True)
        self.scroll.setHorizontalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAlwaysOff)
        self.scroll.setVerticalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAlwaysOff)
        self.scroll.setWidget(self.btnContainer)
        self.scroll.setFrameShape(QFrame.Shape.NoFrame)

        mainLayout.addWidget(self.scroll)

        # Данные для кнопок
        buttonsData = [
            ('assets/icons/app_icon.png', 'Тест 1', 'Описание 1'),
            ('assets/icons/app_icon.png', 'Тест 2', 'Описание 2'),
            ('assets/icons/app_icon.png', 'Тест 3', 'Описание 3'),
            ('assets/icons/app_icon.png', 'Тест 4', 'Описание 4'),
            ('assets/icons/app_icon.png', 'Тест 5', 'Описание 5'),
            ('assets/icons/app_icon.png', 'Тест 6', 'Описание 6'),
            ('assets/icons/app_icon.png', 'Тест 7', 'Описание 7'),
        ]

        # Стек кнопок
        self.navButtons = []

        # Создание и добавление кнопок
        for icon, text, desc in buttonsData:
            btn = AnimatedNavButton(icon, text, desc)
            btn.clicked.connect(self.handle_navbutton_clicked)
            self.btnLayout.addWidget(btn)
            self.navButtons.append(btn)
        self.btnLayout.addStretch()

        # Кнопка выхода
        self.exitButton = QPushButton('🚪')
        self.exitButton.setCursor(Qt.CursorShape.PointingHandCursor)
        self.exitButton.setObjectName('navPanelExitButton')
        self.exitButton.clicked.connect(lambda: (self.window() and self.window().close()))
        mainLayout.addWidget(self.exitButton)

        # Установка layout
        self.setLayout(mainLayout)


    def handle_navbutton_clicked(self):
        pass

    def enterEvent(self, event):
        """Евент раскрытия панели"""
        if not self.isExpanded and not self.isAnimating:
            self.start_expand()
            self.scroll.setVerticalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAsNeeded)
        super().enterEvent(event)

    def leaveEvent(self, event):
        """Евент сворачивания панели"""
        if not self.underMouse() and self.isExpanded and not self.isAnimating:
            self.start_collapse()
            self.scroll.setVerticalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAlwaysOff)
        super().leaveEvent(event)

    def start_expand(self):
        """Запуск анимации раскрытия"""
        self.isAnimating = True
        self.animation.stop()
        self.animation.setStartValue(self.width())
        self.animation.setEndValue(self.expandedWidth)
        self.animation.start()
        self.navHeader.setText('Меню')

    def start_collapse(self):
        """Запуск анимации сворчивания"""
        self.isAnimating = True
        self.animation.stop()
        self.animation.setStartValue(self.width())
        self.animation.setEndValue(self.collapsedWidth)
        self.animation.start()
        self.navHeader.setText('☰')

    def on_animation_finished(self):
        """Когда анимация закончилась"""
        self.isAnimating = False
        self.isExpanded = self.width() > (self.collapsedWidth + 10)

        if self.underMouse() and not self.isExpanded:
            self.start_expand()
        elif not self.underMouse() and self.isExpanded:
            self.start_collapse()