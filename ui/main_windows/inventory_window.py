from PyQt6.QtCore import QSize, Qt, QRegularExpression, QSortFilterProxyModel
from PyQt6.QtGui import QColor, QRegularExpressionValidator
from PyQt6.QtWidgets import QLabel, QWidget, QWIDGETSIZE_MAX, QVBoxLayout, QStackedLayout, QHBoxLayout, QTableView, \
    QFrame, QGraphicsDropShadowEffect, QScrollArea, QComboBox, QPushButton, QLineEdit, QMessageBox, QHeaderView

from services.inventory_service import get_inventory, add_count, substract_count, get_all_products, \
    add_new_product_to_warehouse, del_product_from_warehouse, get_all_product_and_ids, add_product, del_product
from services.shipments_service import get_users_warehouses
from ui.base_window import BaseWindow
from ui.ui_elements.nav_panel import NavPanel
from ui.ui_elements.table_model import TableModel
from utils.app_state import AppState
from utils.export_to_excel import exportToExcel


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
        self.inventoryCard.setFixedSize(1000, 540)

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
        inventoryTable.setAlternatingRowColors(True)
        inventoryTable.setSelectionBehavior(inventoryTable.SelectionBehavior.SelectRows)
        inventoryTable.setFixedSize(616, 200)
        inventoryTable.setColumnWidth(0, 200)
        inventoryTable.setColumnWidth(1, 100)
        inventoryTable.setColumnWidth(2, 100)
        inventoryTable.setColumnWidth(3, 200)
        inventoryTable.horizontalHeader().setSectionsMovable(False)
        inventoryTable.horizontalHeader().setSectionResizeMode(QHeaderView.ResizeMode.Fixed)
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

        self.warehouseFilter.currentTextChanged.connect(self.update_inventory_filters)
        inventoryFilterLayout.addWidget(self.warehouseFilter, alignment=Qt.AlignmentFlag.AlignCenter)

        inventoryLayout.addLayout(inventoryFilterLayout)

        generateReport = QPushButton("Сгенерировать отчет")
        generateReport.clicked.connect(lambda: exportToExcel(inventoryModel))
        generateReport.setFixedSize(620, 30)
        inventoryLayout.addWidget(generateReport, alignment=Qt.AlignmentFlag.AlignCenter)

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
        self.load_warehouses_for_quantity_manupulation()
        self.warehouseSelection.currentTextChanged.connect(self.update_product_selection_data)

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

        self.update_product_selection_data()

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
            self.load_selectable_warehouses()
            toWarehouseLayout.addWidget(toWarehouseLabel)
            toWarehouseLayout.addWidget(self.toWarehouseSelection)

            newProductToWarehouseLayout.addLayout(toWarehouseLayout)

            newProductSelectionLayout = QHBoxLayout()
            newProductSelectionLabel = QLabel('Товар: ')
            newProductSelectionLabel.setFixedWidth(110)
            self.newProductSelection = QComboBox()
            self.update_new_product_selection_data()
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
        if AppState.currentUser.role == 1:
            # Подложка под элементы
            self.productCard = QFrame()
            self.productCard.setObjectName('cardLogin')
            self.productCard.setFixedSize(1000, 500)

            newProductLayout = QVBoxLayout(self.productCard)
            newProductLayout.setContentsMargins(15, 15, 15, 15)

            cardEffect = QGraphicsDropShadowEffect()
            cardEffect.setBlurRadius(30)
            cardEffect.setXOffset(0)
            cardEffect.setYOffset(4)
            cardEffect.setColor(QColor(0, 0, 0, 120))
            self.productCard.setGraphicsEffect(cardEffect)

            # Заголовок раздела
            newProductLabel = QLabel('Добавление и удаление товара из общего списка')
            newProductLabel.setAlignment(Qt.AlignmentFlag.AlignCenter)
            newProductLayout.addWidget(newProductLabel, alignment=Qt.AlignmentFlag.AlignCenter)
            newProductLayout.addSpacing(10)

            # Модель для таблицы товаров
            productsHeaders = ['Id','Название']
            productsData = get_all_product_and_ids()['data']
            self.productsModel = TableModel(productsData, productsHeaders)

            # Таблица для общего списка товаров
            productsTable = QTableView()
            productsTable.verticalHeader().setVisible(False)
            productsTable.setModel(self.productsModel)
            productsTable.setAlternatingRowColors(True)
            productsTable.setSelectionBehavior(productsTable.SelectionBehavior.SelectRows)
            productsTable.setFixedSize(516, 200)
            productsTable.setColumnWidth(0, 40)
            productsTable.setColumnWidth(1, 460)
            productsTable.horizontalHeader().setSectionResizeMode(QHeaderView.ResizeMode.Fixed)
            productsTable.horizontalHeader().setSectionsMovable(False)

            newProductLayout.addWidget(productsTable, alignment=Qt.AlignmentFlag.AlignCenter)
            newProductLayout.addSpacing(10)

            # Layout для действий с общим списком товаров
            actionWithProductsLayout = QVBoxLayout()

            # Добавление товара
            addProductToSystemLayout = QVBoxLayout() # Layout с элементами для добавления

            addProductToSystemLabel = QLabel('Добавление товара') # Заголовок элементов
            addProductToSystemLayout.addWidget(addProductToSystemLabel, alignment=Qt.AlignmentFlag.AlignCenter)

            newProductNameLayout = QHBoxLayout() # Layout для поля и подписи
            newProductNameLayout.addStretch()

            newProductNameLabel = QLabel('Имя нового товара: ') # Подпись поля
            newProductNameLabel.setFixedWidth(205)
            newProductNameLayout.addWidget(newProductNameLabel)

            self.newProductNameLine = QLineEdit() # Поле ввода названия нового товара
            self.newProductNameLine.setFixedWidth(220)
            self.newProductNameLine.setMaxLength(50)
            self.newProductNameLine.setPlaceholderText('Наименование товара')
            newProductNameLayout.addWidget(self.newProductNameLine)

            newProductNameLayout.addStretch()
            addProductToSystemLayout.addLayout(newProductNameLayout)

            addProductToSystemBtn = QPushButton('Добавить') # Кнопка добавления товара
            addProductToSystemBtn.setFixedWidth(180)
            addProductToSystemBtn.clicked.connect(self.add_product_to_database)
            addProductToSystemLayout.addWidget(addProductToSystemBtn, alignment=Qt.AlignmentFlag.AlignCenter)

            actionWithProductsLayout.addLayout(addProductToSystemLayout)
            actionWithProductsLayout.addSpacing(10)

            # Удаление товара
            delProductFromSystemLayout = QVBoxLayout() # Layout с элементами для удаления

            delProductFromSystemLabel = QLabel('Удаление товара') # Заголовок элементов удаления
            delProductFromSystemLayout.addWidget(delProductFromSystemLabel, alignment=Qt.AlignmentFlag.AlignCenter)

            delProductNameLayout = QHBoxLayout() # Layout для строки ввода и подписи
            delProductNameLayout.addStretch()

            delProductNameLabel = QLabel('Id удаляемого товара: ') # Подпись поля ввода id
            delProductNameLabel.setFixedWidth(205)
            delProductNameLayout.addWidget(delProductNameLabel)

            self.delProductIdLine = QLineEdit() # Поле ввода id
            self.delProductIdLine.setFixedWidth(220)
            self.delProductIdLine.setMaxLength(10)
            self.delProductIdLine.setValidator(QRegularExpressionValidator(QRegularExpression(r'^\d*$')))
            self.delProductIdLine.setPlaceholderText('Id товара')
            delProductNameLayout.addWidget(self.delProductIdLine)

            delProductNameLayout.addStretch()
            delProductFromSystemLayout.addLayout(delProductNameLayout)

            delProductFromSystemBtn = QPushButton('Удалить') # Кнопка удаления товара
            delProductFromSystemBtn.setFixedWidth(180)
            delProductFromSystemBtn.clicked.connect(self.del_product_from_database)
            delProductFromSystemLayout.addWidget(delProductFromSystemBtn, alignment=Qt.AlignmentFlag.AlignCenter)

            actionWithProductsLayout.addLayout(delProductFromSystemLayout)

            newProductLayout.addLayout(actionWithProductsLayout)

            newProductLayout.addStretch()
            contentLayout.addWidget(self.productCard, alignment=Qt.AlignmentFlag.AlignCenter)

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

    def load_selectable_warehouses(self):
        """Загрузка доступных пользователю складов для добавления товара на склад"""
        self.toWarehouseSelection.clear()
        self.toWarehouseSelection.addItem('Выберите склад')
        warehouses = get_users_warehouses()
        if warehouses['success']:
            for warehouseId, warehouseName in warehouses['data']:
                self.toWarehouseSelection.addItem(warehouseName, warehouseId)
            return None
        QMessageBox.warning(self, 'Ошибка', f'Ошибка в загрузке складов: {warehouses["data"]}')
        return None

    def load_warehouses_for_quantity_manupulation(self):
        warehouseList = []
        for warehouse in get_inventory(AppState.currentUser.warehouses):
            warehouseList.append(warehouse[1])
        warehouseList = list(set(warehouseList))

        self.warehouseSelection.clear()
        self.warehouseSelection.addItem('Выберите склад')
        self.warehouseSelection.addItems(warehouseList)

        self.warehouseFilter.clear()
        self.warehouseFilter.addItem("Все склады")
        self.warehouseFilter.addItems(warehouseList)

    def add_product_count(self):
        if self.warehouseSelection.currentIndex() == 0:
            QMessageBox.warning(self, 'Ошибка', 'Выберите склад')
            return None

        if self.productSelection.currentIndex() == 0:
            QMessageBox.warning(self, 'Ошибка', 'Выберите товар')
            return None

        if not self.productCountLine.text():
            QMessageBox.warning(self, 'Ошибка','Введите количество')
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

        if not self.productCountLine.text():
            QMessageBox.warning(self, 'Ошибка','Введите количество')
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

    def update_product_table(self):
        newProductData = get_all_product_and_ids()['data']
        self.productsModel.update_data(newProductData)

    def update_product_selection_data(self):
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

    def update_new_product_selection_data(self):
        self.newProductSelection.clear()
        self.newProductSelection.addItem('Выберите товар')
        self.newProductSelection.addItems(get_all_products()['data'])

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
                self.update_product_selection_data()
                self.load_warehouses_for_quantity_manupulation()
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
                self.update_product_selection_data()
                return None
            QMessageBox.warning(self, 'Ошибка', res['message'])
        except Exception as e:
            QMessageBox.warning(self, 'Ошибка', str(e))

    def add_product_to_database(self):

        newProductName = self.newProductNameLine.text().strip()
        if not newProductName:
            QMessageBox.warning(self, 'Ошибка', 'Введите имя нового товара')
            return None
        try:
            res = add_product(newProductName)

            if res['success']:
                QMessageBox.information(self, 'Успех', res['message'])
                self.update_product_table()
                self.update_new_product_selection_data()
                self.update_product_selection_data()
                self.newProductNameLine.clear()
                return None

            QMessageBox.warning(self, 'Ошибка', res['message'])
        except Exception as e:
            QMessageBox.warning(self, 'Ошибка', str(e))

    def del_product_from_database(self):

        delProductId = self.delProductIdLine.text().strip()
        if not delProductId:
            QMessageBox.warning(self, 'Ошибка', 'Введите Id удаляемого товара')
            return None
        try:
            delProductId = int(delProductId)
            res = del_product(delProductId)

            if res['success']:
                QMessageBox.information(self, 'Успех', res['message'])
                self.update_product_table()
                self.update_new_product_selection_data()
                self.update_product_selection_data()
                self.delProductIdLine.clear()
                return None

            QMessageBox.warning(self, 'Ошибка', res['message'])
        except Exception as e:
            QMessageBox.warning(self,'Ошибка', str(e))

    def refresh(self):
        self.update_inventory_table()
        self.update_product_selection_data()
        if self.user.role in [1,3]:
            self.load_selectable_warehouses()
            self.update_new_product_selection_data()
        if self.user.role == 1:
            self.update_product_table()

