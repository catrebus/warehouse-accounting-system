from PyQt6.QtCore import QSize, Qt, QRegularExpression, QSortFilterProxyModel
from PyQt6.QtGui import QColor, QRegularExpressionValidator
from PyQt6.QtWidgets import QLabel, QWidget, QWIDGETSIZE_MAX, QVBoxLayout, QStackedLayout, QHBoxLayout, QTableView, \
    QHeaderView, QFrame, QGraphicsDropShadowEffect, QScrollArea, QComboBox, QPushButton, QLineEdit, QMessageBox

from services.inventory_service import get_inventory, add_count, substract_count, get_all_products, \
    add_new_product_to_warehouse, del_product_from_warehouse
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
        self.warehouseSelection.currentTextChanged.connect(self.updateProductSelectionData)

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

        self.updateProductSelectionData()

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

        manipulateProductBtnLayout.addStretch()
        manipulateProductLayout.addLayout(manipulateProductBtnLayout)

        manipulateProductLayout.addStretch()
        inventoryLayout.addLayout(manipulateProductLayout)
        contentLayout.addWidget(self.inventoryCard, alignment=Qt.AlignmentFlag.AlignCenter)
        contentLayout.addSpacing(30)

        # Добавление нового товара на склад
        if AppState.currentUser.role in [1,3]:

            self.newProductToWarehouseCard = QFrame()
            self.newProductToWarehouseCard.setObjectName('cardLogin')
            self.newProductToWarehouseCard.setFixedSize(1000, 160)

            newProductToWarehouseLayout = QVBoxLayout(self.newProductToWarehouseCard)
            newProductToWarehouseLayout.setContentsMargins(15, 15, 15, 15)

            cardEffect = QGraphicsDropShadowEffect()
            cardEffect.setBlurRadius(30)
            cardEffect.setXOffset(0)
            cardEffect.setYOffset(4)
            cardEffect.setColor(QColor(0, 0, 0, 120))
            self.newProductToWarehouseCard.setGraphicsEffect(cardEffect)

            # Заголовок добавления нового товара на склад
            newProductToWarehouseLabel = QLabel('Добавление и удаление товара со склада')
            newProductToWarehouseLabel.setAlignment(Qt.AlignmentFlag.AlignCenter)
            newProductToWarehouseLayout.addWidget(newProductToWarehouseLabel, alignment=Qt.AlignmentFlag.AlignCenter)
            newProductToWarehouseLayout.addSpacing(10)

            toWarehouseLayout = QHBoxLayout()
            toWarehouseLabel = QLabel('Склад: ')
            toWarehouseLabel.setFixedWidth(110)
            self.toWarehouseSelection = QComboBox()
            self.toWarehouseSelection.addItem('Выберите склад')
            self.toWarehouseSelection.addItems(warehouseList)
            toWarehouseLayout.addWidget(toWarehouseLabel)
            toWarehouseLayout.addWidget(self.toWarehouseSelection)

            newProductToWarehouseLayout.addLayout(toWarehouseLayout)

            newProductSelectionLayout = QHBoxLayout()
            newProductSelectionLabel = QLabel('Товар: ')
            newProductSelectionLabel.setFixedWidth(110)
            self.newProductSelection = QComboBox()
            self.newProductSelection.addItem('Выберите товар')
            self.newProductSelection.addItems(get_all_products()['data'])
            newProductSelectionLayout.addWidget(newProductSelectionLabel)
            newProductSelectionLayout.addWidget(self.newProductSelection)

            newProductToWarehouseLayout.addLayout(newProductSelectionLayout)

            delAddProductWarehouseBtns = QHBoxLayout()

            delAddProductWarehouseBtns.addStretch()
            addNewProductToWarehouseBtn = QPushButton('Добавить')
            addNewProductToWarehouseBtn.clicked.connect(self.add_new_product_to_warehouse)
            addNewProductToWarehouseBtn.setFixedWidth(170)
            delAddProductWarehouseBtns.addWidget(addNewProductToWarehouseBtn, alignment=Qt.AlignmentFlag.AlignCenter)

            deleteProductFromWarehouseBtn = QPushButton('Удалить')
            deleteProductFromWarehouseBtn.clicked.connect(self.del_product_from_warehouse)
            deleteProductFromWarehouseBtn.setFixedWidth(170)
            delAddProductWarehouseBtns.addWidget(deleteProductFromWarehouseBtn, alignment=Qt.AlignmentFlag.AlignCenter)
            delAddProductWarehouseBtns.addStretch()

            newProductToWarehouseLayout.addLayout(delAddProductWarehouseBtns)

            newProductToWarehouseLayout.addStretch()

            contentLayout.addWidget(self.newProductToWarehouseCard, alignment=Qt.AlignmentFlag.AlignCenter)
            contentLayout.addSpacing(30)

        # Добавление и удаление товара из общего списка
        """if AppState.currentUser.role == 1:
            self.newProductCard = QFrame()
            self.newProductCard.setObjectName('cardLogin')
            self.newProductCard.setFixedSize(1000, 500)

            newProductLayout = QVBoxLayout(self.newProductCard)
            newProductLayout.setContentsMargins(15, 15, 15, 15)

            cardEffect = QGraphicsDropShadowEffect()
            cardEffect.setBlurRadius(30)
            cardEffect.setXOffset(0)
            cardEffect.setYOffset(4)
            cardEffect.setColor(QColor(0, 0, 0, 120))
            self.newProductCard.setGraphicsEffect(cardEffect)

            newProductLabel = QLabel('Добавление и удаление товара из общего списка')
            newProductLabel.setAlignment(Qt.AlignmentFlag.AlignCenter)
            newProductLayout.addWidget(newProductLabel, alignment=Qt.AlignmentFlag.AlignCenter)
            newProductLayout.addSpacing(10)

            # Модель для таблицы хранящихся товаров
            productsHeaders = ['Название']
            productsData = get_all_products()['data']

            productsModel = TableModel(productsData, productsHeaders)


            # Таблица хранящихся товаров
            productsTable = QTableView()
            productsTable.verticalHeader().setVisible(False)
            productsTable.setModel(productsModel)
            productsTable.resizeColumnsToContents()
            productsTable.setAlternatingRowColors(True)
            productsTable.setSelectionBehavior(productsTable.SelectionBehavior.SelectRows)
            productsTable.setFixedSize(200, 200)
            productsTable.setColumnWidth(0, 200)

            newProductLayout.addWidget(productsTable, alignment=Qt.AlignmentFlag.AlignCenter)

            productNameLayout = QHBoxLayout()
            productNameLabel = QLabel('Название товара: ')

            productName = QLineEdit()

            contentLayout.addWidget(self.newProductCard, alignment=Qt.AlignmentFlag.AlignCenter)"""

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

            res = substract_count(product, warehouse, quantity)
            if res['success']:
                QMessageBox.information(self, 'Успех', res['message'])
                self.update_inventory_table()
                self.productCountLine.clear()
                return None
            QMessageBox.warning(self, 'Ошбика', res['message'])

        except Exception as e:
            QMessageBox.warning(self, 'Ошибка', str(e))

    def update_inventory_table(self):
        newInventoryData = get_inventory(AppState.currentUser.warehouses)
        self.inventoryFilterModel.sourceModel().update_data(newInventoryData)
        self.inventoryFilterModel.invalidateFilter()

    def updateProductSelectionData(self):
        self.productSelection.clear()
        if self.warehouseSelection.currentIndex() == 0:
            self.productSelection.addItem('Склад не выбран')
            return None

        self.productSelection.addItem('Выберите товар')
        inventoryData = get_inventory(AppState.currentUser.warehouses)

        productList = []
        for item in inventoryData:
            if item[1] == self.warehouseSelection.currentText():
                productList.append(item[0])
        productList = list(set(productList))
        self.productSelection.addItems(productList)

    def add_new_product_to_warehouse(self):
        if self.toWarehouseSelection.currentIndex() == 0:
            QMessageBox.warning(self, 'Ошибка','Выберите склад')
            return None
        if self.newProductSelection.currentIndex() == 0:
            QMessageBox.warning(self, "Ошибка", "Выберите товар")
            return None
        try:
            warehouse = self.toWarehouseSelection.currentText()
            product = self.newProductSelection.currentText()

            res = add_new_product_to_warehouse(product, warehouse)
            if res['success']:
                QMessageBox.information(self, 'Успех', res['message'])
                self.update_inventory_table()
                return None
            QMessageBox.warning(self, 'Ошибка', res['message'])
        except Exception as e:
            QMessageBox.warning(self, 'Ошибка', str(e))

    def del_product_from_warehouse(self):
        if self.toWarehouseSelection.currentIndex() == 0:
            QMessageBox.warning(self, 'Ошибка', 'Выберите склад')
            return None
        if self.newProductSelection.currentIndex() == 0:
            QMessageBox.warning(self, "Ошибка", "Выберите товар")
            return None
        try:
            warehouse = self.toWarehouseSelection.currentText()
            product = self.newProductSelection.currentText()

            res = del_product_from_warehouse(product, warehouse)
            if res['success']:
                QMessageBox.information(self, 'Успех', res['message'])
                self.update_inventory_table()
                return None
            QMessageBox.warning(self, 'Ошибка', res['message'])
        except Exception as e:
            QMessageBox.warning(self, 'Ошибка', str(e))