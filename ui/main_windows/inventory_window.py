from PyQt6.QtCore import QSize, Qt, QRegularExpression, QSortFilterProxyModel
from PyQt6.QtGui import QColor, QRegularExpressionValidator
from PyQt6.QtWidgets import QLabel, QWidget, QWIDGETSIZE_MAX, QVBoxLayout, QStackedLayout, QHBoxLayout, QTableView, \
    QHeaderView, QFrame, QGraphicsDropShadowEffect, QScrollArea, QComboBox, QPushButton, QLineEdit

from services.inventory_service import get_inventory
from ui.base_window import BaseWindow
from ui.ui_elements.nav_panel import NavPanel
from ui.ui_elements.table_model import TableModel
from utils.app_state import AppState


class MultiFilterProxyModelInventory(QSortFilterProxyModel):
    """Класс прокси модели для реализации фильтрации в таблице хранилища"""
    def __init__(self):
        super().__init__()

        self.productNameFilter = ''
        self.warehouseFilter = None

    def filterAcceptsRow(self, sourceRow, sourceParent):
        model = self.sourceModel()

        # Текстовый фильтр
        productName = model.data(model.index(sourceRow, 0), Qt.ItemDataRole.DisplayRole).lower()

        if self.productNameFilter and self.productNameFilter.lower() not in productName:
            return False

        # Фильтр по складу
        warehouse = model.data(model.index(sourceRow, 1), Qt.ItemDataRole.DisplayRole).lower()

        if self.warehouseFilter and self.warehouseFilter != "Все склады":
            if warehouse.lower() != self.warehouseFilter.lower():
                return False

        return True

class InventoryWindow(BaseWindow):

    # Характеристики окна
    widowTitle: str = 'Система складского учета - Хранилище'
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
        contentLayout.setContentsMargins(80,10,0,10)
        contentLayout.setSpacing(0)

        scrollArea = QScrollArea()
        scrollArea.setWidgetResizable(True)
        scrollArea.setWidget(contentWidget)

        # Заголовок окна
        titleLabel = QLabel("Хранилище")
        titleLabel.setFixedHeight(40)
        titleLabel.setAlignment(Qt.AlignmentFlag.AlignCenter)
        contentLayout.addWidget(titleLabel, alignment=Qt.AlignmentFlag.AlignTop)

        """ Управление хранящимися товарами """
        # Создание подложки для элементов управления
        self.inventoryCard = QFrame()
        self.inventoryCard.setObjectName('cardLogin')
        self.inventoryCard.setFixedSize(1000, 500)

        inventoryLayout = QVBoxLayout(self.inventoryCard)
        inventoryLayout.setContentsMargins(15, 15, 15, 15)

        cardEffect = QGraphicsDropShadowEffect()
        cardEffect.setBlurRadius(30)
        cardEffect.setXOffset(0)
        cardEffect.setYOffset(4)
        cardEffect.setColor(QColor(0, 0, 0, 120))
        self.inventoryCard.setGraphicsEffect(cardEffect)

        # Заголовок управления количеством товаров
        inventoryLayoutLabel = QLabel('Хранящиеся товары')
        inventoryLayoutLabel.setAlignment(Qt.AlignmentFlag.AlignCenter)
        inventoryLayout.addWidget(inventoryLayoutLabel, alignment=Qt.AlignmentFlag.AlignCenter)
        inventoryLayout.addSpacing(10)

        # Модель для таблицы хранящихся товаров
        inventoryHeaders = ['Название', 'Склад', 'Кол-во', 'Изменено']
        inventoryData = get_inventory(AppState.currentUser.warehouses)
        inventoryModel = TableModel(inventoryData, inventoryHeaders)

        # Модель для фильтрации
        self.inventoryFilterModel = MultiFilterProxyModelInventory()
        self.inventoryFilterModel.setSourceModel(inventoryModel)

        # Таблица хранящихся товаров
        inventoryTable = QTableView()
        inventoryTable.verticalHeader().setVisible(False)
        inventoryTable.setModel(self.inventoryFilterModel)
        inventoryTable.resizeColumnsToContents()
        inventoryTable.setAlternatingRowColors(True)
        inventoryTable.setSelectionBehavior(inventoryTable.SelectionBehavior.SelectRows)
        inventoryTable.setFixedSize(615, 200)
        inventoryTable.setColumnWidth(0, 200)
        inventoryTable.setColumnWidth(1, 100)
        inventoryTable.setColumnWidth(2, 100)
        inventoryTable.setColumnWidth(3, 200)
        inventoryLayout.addWidget(inventoryTable, alignment=Qt.AlignmentFlag.AlignCenter)

        # Layout для элементов фильтрации
        inventoryFilterLayout = QVBoxLayout()

        # Поиск по названию
        self.productNameFilter = QLineEdit()
        self.productNameFilter.setFixedSize(620, 30)
        self.productNameFilter.textChanged.connect(self.update_inventory_filters)
        self.productNameFilter.setPlaceholderText("Название товара")
        inventoryFilterLayout.addWidget(self.productNameFilter, alignment=Qt.AlignmentFlag.AlignCenter)

        # Фильтрация по складу
        self.warehouseFilter = QComboBox()
        self.warehouseFilter.setFixedSize(620, 30)
        self.warehouseFilter.addItem("Все склады")

        warehouseList = []
        for warehouse in inventoryData:
            warehouseList.append(warehouse[1])
        warehouseList = list(set(warehouseList))

        self.warehouseFilter.addItems(warehouseList)
        self.warehouseFilter.currentTextChanged.connect(self.update_inventory_filters)
        inventoryFilterLayout.addWidget(self.warehouseFilter, alignment=Qt.AlignmentFlag.AlignCenter)

        inventoryLayout.addLayout(inventoryFilterLayout)
        inventoryLayout.addSpacing(10)

        # Layout для элементов управления количеством
        manipulateProductLayout = QVBoxLayout()

        manipulateProductLabel = QLabel("Управление количеством товаров")
        manipulateProductLabel.setAlignment(Qt.AlignmentFlag.AlignCenter)
        manipulateProductLayout.addWidget(manipulateProductLabel)

        # Поле выбора товара
        productSelectionLayout = QHBoxLayout()
        productSelectionLabel = QLabel('Товар: ')
        productSelectionLabel.setFixedWidth(110)

        productSelection = QComboBox()
        productSelection.setFixedWidth(400)
        productSelection.addItem('Выберите товар')

        productList = []
        for product in inventoryData:
            productList.append(product[0])
        productList = list(set(productList))
        productSelection.addItems(productList)

        productSelectionLayout.addWidget(productSelectionLabel)
        productSelectionLayout.addWidget(productSelection)

        manipulateProductLayout.addLayout(productSelectionLayout)

        # Поле выбора склада
        warehouseSelectionLayout = QHBoxLayout()
        warehouseSelectionLabel = QLabel('Склад: ')
        warehouseSelectionLabel.setFixedWidth(110)

        warehouseSelection = QComboBox()
        warehouseSelection.setFixedWidth(400)
        warehouseSelection.addItem('Выберите склад')


        warehouseSelection.addItems(warehouseList)

        warehouseSelectionLayout.addWidget(warehouseSelectionLabel)
        warehouseSelectionLayout.addWidget(warehouseSelection)

        manipulateProductLayout.addLayout(warehouseSelectionLayout)

        # Поле ввода количества товара
        productCountLayout = QHBoxLayout()
        productCountLabel = QLabel('Количество: ')
        productCountLabel.setFixedWidth(110)

        productCountLine = QLineEdit()
        productCountLine.setFixedWidth(400)
        productCountLine.setPlaceholderText("Количество товара")
        productCountLine.setValidator(QRegularExpressionValidator(QRegularExpression(r"^[1-9][0-9]*$")))

        productCountLayout.addWidget(productCountLabel)
        productCountLayout.addWidget(productCountLine)

        manipulateProductLayout.addLayout(productCountLayout)

        # Кнопки для управления количеством товара
        manipulateProductBtnLayout = QHBoxLayout()
        manipulateProductBtnLayout.addStretch()

        addProductBtn = QPushButton("Добавить")
        addProductBtn.setFixedWidth(170)
        manipulateProductBtnLayout.addWidget(addProductBtn)

        subtractProductBtn = QPushButton("Убавить")
        subtractProductBtn.setFixedWidth(170)
        manipulateProductBtnLayout.addWidget(subtractProductBtn)

        setQuantityBtn = QPushButton("Установить кол-во")
        setQuantityBtn.setFixedWidth(170)
        manipulateProductBtnLayout.addWidget(setQuantityBtn)

        manipulateProductBtnLayout.addStretch()
        manipulateProductLayout.addLayout(manipulateProductBtnLayout)

        manipulateProductLayout.addStretch()
        inventoryLayout.addLayout(manipulateProductLayout)
        contentLayout.addWidget(self.inventoryCard, alignment=Qt.AlignmentFlag.AlignCenter)

        # Далее


        contentLayout.addStretch()
        mainLayout.addWidget(scrollArea)

        """Навигационная панель"""
        self.navPanel = NavPanel(self)
        mainLayout.addWidget(self.navPanel)

        self.setLayout(mainLayout)

    def update_inventory_filters(self):
        self.inventoryFilterModel.productNameFilter = self.productNameFilter.text()
        self.inventoryFilterModel.warehouseFilter = self.warehouseFilter.currentText()
        self.inventoryFilterModel.invalidateFilter()