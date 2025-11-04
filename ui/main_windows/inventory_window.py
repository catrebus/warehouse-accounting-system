from PyQt6.QtCore import QSize, Qt, QRegularExpression, QSortFilterProxyModel
from PyQt6.QtGui import QColor, QRegularExpressionValidator
from PyQt6.QtWidgets import QLabel, QWidget, QWIDGETSIZE_MAX, QVBoxLayout, QStackedLayout, QHBoxLayout, QTableView, \
    QHeaderView, QFrame, QGraphicsDropShadowEffect, QScrollArea, QComboBox, QPushButton, QLineEdit, QMessageBox

from services.inventory_service import get_inventory, add_count
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

        # Поле выбора склада
        warehouseSelectionLayout = QHBoxLayout()
        warehouseSelectionLabel = QLabel('Склад: ')
        warehouseSelectionLabel.setFixedWidth(110)

        self.warehouseSelection = QComboBox()
        self.warehouseSelection.setFixedWidth(400)
        self.warehouseSelection.addItem('Выберите склад')

        self.warehouseSelection.addItems(warehouseList)

        warehouseSelectionLayout.addWidget(warehouseSelectionLabel)
        warehouseSelectionLayout.addWidget(self.warehouseSelection)

        manipulateProductLayout.addLayout(warehouseSelectionLayout)

        # Поле выбора товара
        productSelectionLayout = QHBoxLayout()
        productSelectionLabel = QLabel('Товар: ')
        productSelectionLabel.setFixedWidth(110)

        self.productSelection = QComboBox()
        self.productSelection.setFixedWidth(400)
        self.productSelection.addItem('Выберите товар')

        productList = []
        for product in inventoryData:
            productList.append(product[0])
        productList = list(set(productList))
        self.productSelection.addItems(productList)

        productSelectionLayout.addWidget(productSelectionLabel)
        productSelectionLayout.addWidget(self.productSelection)

        manipulateProductLayout.addLayout(productSelectionLayout)

        # Поле ввода количества товара
        productCountLayout = QHBoxLayout()
        productCountLabel = QLabel('Количество: ')
        productCountLabel.setFixedWidth(110)


        self.productCountLine = QLineEdit()
        self.productCountLine.setFixedWidth(400)
        self.productCountLine.setPlaceholderText("Количество товара")
        self.productCountLine.setMaxLength(10)
        self.productCountLine.setValidator(QRegularExpressionValidator(QRegularExpression(r"^[1-9][0-9]*$")))

        productCountLayout.addWidget(productCountLabel)
        productCountLayout.addWidget(self.productCountLine)

        manipulateProductLayout.addLayout(productCountLayout)

        # Кнопки для управления количеством товара
        manipulateProductBtnLayout = QHBoxLayout()
        manipulateProductBtnLayout.addStretch()

        addProductBtn = QPushButton("Добавить")
        addProductBtn.setFixedWidth(170)
        addProductBtn.clicked.connect(self.add_product_count)
        manipulateProductBtnLayout.addWidget(addProductBtn)

        subtractProductBtn = QPushButton("Отнять")
        subtractProductBtn.setFixedWidth(170)
        subtractProductBtn.clicked.connect(self.substract_product_count)
        manipulateProductBtnLayout.addWidget(subtractProductBtn)

        """setQuantityBtn = QPushButton("Установить кол-во")
        setQuantityBtn.setFixedWidth(170)
        manipulateProductBtnLayout.addWidget(setQuantityBtn)"""

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

    def add_product_count(self):
        if self.warehouseSelection.currentIndex() == 0:
            QMessageBox.warning(self, 'Ошибка', 'Выберите склад')
            return None

        if self.productSelection.currentIndex() == 0:
            QMessageBox.warning(self, 'Ошибка', 'Выберите товар')
            return None
        try:
            warehouse = self.warehouseSelection.currentText()
            product = self.productSelection.currentText()
            quantity = int(self.productCountLine.text())

            res = add_count(product, warehouse, quantity)
            if res['success']:
                QMessageBox.information(self, 'Успех', res['message'])
                self.update_inventory_table()
                self.productCountLine.clear()
                return None
            QMessageBox.warning(self, 'Ошбика', res['message'])

        except Exception as e:
            QMessageBox.warning(self, 'Ошибка', str(e))

    def substract_product_count(self):
        pass

    def update_inventory_table(self):
        newInventoryData = get_inventory(AppState.currentUser.warehouses)
        self.inventoryFilterModel.sourceModel().update_data(newInventoryData)
        self.inventoryFilterModel.invalidateFilter()