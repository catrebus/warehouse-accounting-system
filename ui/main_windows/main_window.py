from PyQt6.QtCore import QSize, Qt
from PyQt6.QtGui import QStandardItemModel
from PyQt6.QtWidgets import QLabel, QWidget, QWIDGETSIZE_MAX, QVBoxLayout, QStackedLayout, QTableView, \
    QAbstractItemView, QHeaderView

from services.info_from_db import get_upcoming_shipments
from ui.base_window import BaseWindow
from ui.ui_elements.nav_panel import NavPanel
from ui.ui_elements.table_model import TableModel


class MainWindow(BaseWindow):

    # Характеристики окна
    widowTitle: str = 'Система складского учета - Главная страница'
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
        contentLayout.setContentsMargins(80,10,10,10)
        contentLayout.setSpacing(0)


        # Заголовок
        titleLabel = QLabel("Главная страница")
        titleLabel.setFixedHeight(40)
        titleLabel.setAlignment(Qt.AlignmentFlag.AlignCenter)
        contentLayout.addWidget(titleLabel, alignment=Qt.AlignmentFlag.AlignTop)

        # Приветствие
        hiLabel = QLabel(f'Добро пожаловать, {self.user.login}')
        hiLabel.setFixedHeight(40)
        hiLabel.setAlignment(Qt.AlignmentFlag.AlignCenter)
        contentLayout.addWidget(hiLabel, alignment=Qt.AlignmentFlag.AlignTop)
        contentLayout.addSpacing(40)

        """Информация"""
        infoLayout = QVBoxLayout()

        shipmentsTableLabel = QLabel('Ближайшие поставки')
        infoLayout.addWidget(shipmentsTableLabel, alignment=Qt.AlignmentFlag.AlignCenter)
        infoLayout.addSpacing(10)


        # Данные для таблицы
        shipmentsHeaders = ["Поставщик", "Ответственный\nсотрудник", "Принимающий\nсклад", "Дата" ]
        shipmentsData = get_upcoming_shipments()
        shipmentsModel = TableModel(shipmentsData, shipmentsHeaders)

        # Виджет таблицы
        shipmentsTable = QTableView()
        shipmentsTable.setModel(shipmentsModel)
        shipmentsTable.resizeColumnsToContents()
        shipmentsTable.setAlternatingRowColors(True)
        shipmentsTable.setSelectionBehavior(shipmentsTable.SelectionBehavior.SelectRows)
        shipmentsTable.setFixedSize(620,200)
        shipmentsTable.horizontalHeader().setSectionResizeMode(QHeaderView.ResizeMode.Stretch)

        infoLayout.addWidget(shipmentsTable, alignment=Qt.AlignmentFlag.AlignCenter)

        contentLayout.addLayout(infoLayout)


        contentLayout.addStretch()
        mainLayout.addWidget(contentWidget)

        """Навигационная панель"""
        self.navPanel = NavPanel(self)
        mainLayout.addWidget(self.navPanel)


        self.setLayout(mainLayout)
