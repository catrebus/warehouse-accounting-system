from PyQt6.QtCore import QSize, Qt, QRegularExpression
from PyQt6.QtGui import QColor, QRegularExpressionValidator
from PyQt6.QtWidgets import QLabel, QWidget, QWIDGETSIZE_MAX, QVBoxLayout, QStackedLayout, QFrame, \
    QGraphicsDropShadowEffect, QHBoxLayout, QComboBox, QPushButton, QMessageBox, QScrollArea, QTableView, QHeaderView, \
    QLineEdit, QDialog

from services.shipments_service import get_suppliers_name, get_suppliers_data, get_shipments_data, get_users_warehouses
from ui.base_window import BaseWindow
from ui.ui_elements.create_new_shipment_window import CreateNewShipmentWindow
from ui.ui_elements.nav_panel import NavPanel
from ui.ui_elements.shipment_details_window import ShipmentDetailsWindow
from ui.ui_elements.table_model import TableModel
from utils.app_state import AppState


class ShipmentsWindow(BaseWindow):

    # Характеристики окна
    widowTitle: str = 'Система складского учета - Поставки'
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
        contentLayout.setContentsMargins(80, 10, 0, 10)
        contentLayout.setSpacing(0)

        scrollArea = QScrollArea()
        scrollArea.setWidgetResizable(True)
        scrollArea.setWidget(contentWidget)

        # Заголовок вкладки
        titleLabel = QLabel("Поставки")
        titleLabel.setFixedHeight(40)
        titleLabel.setAlignment(Qt.AlignmentFlag.AlignCenter)
        contentLayout.addWidget(titleLabel, alignment=Qt.AlignmentFlag.AlignTop)

        """Создание поставки"""
        # Подложка под элементы
        self.newShipmentCard = QFrame()
        self.newShipmentCard.setObjectName('cardLogin')
        self.newShipmentCard.setFixedSize(1000, 450)

        newShipmentLayout = QVBoxLayout(self.newShipmentCard)
        newShipmentLayout.setContentsMargins(15, 15, 15, 15)

        cardEffect = QGraphicsDropShadowEffect()
        cardEffect.setBlurRadius(30)
        cardEffect.setXOffset(0)
        cardEffect.setYOffset(4)
        cardEffect.setColor(QColor(0, 0, 0, 120))
        self.newShipmentCard.setGraphicsEffect(cardEffect)

        # Заголовок таблицы принятых поставок
        shipmentTableLabel = QLabel('Принятые поставки')
        newShipmentLayout.addWidget(shipmentTableLabel, alignment=Qt.AlignmentFlag.AlignCenter)
        newShipmentLayout.addSpacing(10)

        shipmentsHeaders = ['Id', 'Поставщик', 'Сотрудник', 'Склад', 'Дата']
        shipmentsData = get_shipments_data(self.user.warehouses)['data']
        self.shipmentsModel = TableModel(shipmentsData, shipmentsHeaders)

        # Таблица поставок
        self.shipmentsTable = QTableView()
        self.shipmentsTable.verticalHeader().setVisible(False)
        self.shipmentsTable.setModel(self.shipmentsModel)
        self.shipmentsTable.resizeColumnsToContents()
        self.shipmentsTable.setAlternatingRowColors(True)
        self.shipmentsTable.setSelectionBehavior(self.shipmentsTable.SelectionBehavior.SelectRows)
        self.shipmentsTable.setFixedSize(700, 200)
        self.shipmentsTable.horizontalHeader().setSectionResizeMode(QHeaderView.ResizeMode.Stretch)
        self.shipmentsTable.doubleClicked.connect(self.open_shipment_details)
        newShipmentLayout.addWidget(self.shipmentsTable, alignment=Qt.AlignmentFlag.AlignCenter)
        newShipmentLayout.addSpacing(10)

        # Заголовок элементов создания поставки
        newShipmentLabel = QLabel('Создание поставки')
        newShipmentLayout.addWidget(newShipmentLabel, alignment=Qt.AlignmentFlag.AlignCenter)
        newShipmentLayout.addSpacing(10)

        # Строка выбора поставщика
        supplierSelectionLayout = QHBoxLayout()
        supplierSelectionLayout.addStretch()

        supplierSelectionLabel = QLabel('Поставщик: ')
        supplierSelectionLabel.setFixedWidth(200)
        supplierSelectionLayout.addWidget(supplierSelectionLabel)

        self.supplierSelection = QComboBox()
        self.supplierSelection.setFixedWidth(200)
        self.load_selectable_suppliers()
        supplierSelectionLayout.addWidget(self.supplierSelection)

        supplierSelectionLayout.addStretch()
        newShipmentLayout.addLayout(supplierSelectionLayout)
        newShipmentLayout.addSpacing(10)

        warehouseSelectionLayout = QHBoxLayout()
        warehouseSelectionLayout.addStretch()

        warehouseSelectionLabel = QLabel('Склад: ')
        warehouseSelectionLabel.setFixedWidth(200)
        warehouseSelectionLayout.addWidget(warehouseSelectionLabel)

        self.warehouseSelection = QComboBox()
        self.warehouseSelection.setFixedWidth(200)
        self.load_selectable_warehouses()
        warehouseSelectionLayout.addWidget(self.warehouseSelection)

        warehouseSelectionLayout.addStretch()
        newShipmentLayout.addLayout(warehouseSelectionLayout)
        newShipmentLayout.addSpacing(15)


        # Кнопка создания поставки
        createShipmentBtn = QPushButton('Создать')
        createShipmentBtn.clicked.connect(self.handle_create_new_shipment)
        createShipmentBtn.setFixedWidth(300)
        newShipmentLayout.addWidget(createShipmentBtn, alignment=Qt.AlignmentFlag.AlignCenter)

        newShipmentLayout.addStretch()
        contentLayout.addWidget(self.newShipmentCard, alignment=Qt.AlignmentFlag.AlignCenter) # Добавление подложки с элементами создания поставки в окно
        contentLayout.addSpacing(30)

        """Добавление нового поставщика в бд"""
        if self.user.role in [1,3]:
            self.newSupplierCard = QFrame()
            self.newSupplierCard.setObjectName('cardLogin')
            self.newSupplierCard.setFixedSize(1000, 450)

            newSupplierLayout = QVBoxLayout(self.newSupplierCard)
            newSupplierLayout.setContentsMargins(15, 15, 15, 15)

            cardEffect = QGraphicsDropShadowEffect()
            cardEffect.setBlurRadius(30)
            cardEffect.setXOffset(0)
            cardEffect.setYOffset(4)
            cardEffect.setColor(QColor(0, 0, 0, 120))
            self.newSupplierCard.setGraphicsEffect(cardEffect)

            # Заголовок элементов для добавления поставщика
            newSupplierLabel = QLabel('Поставщики')
            newSupplierLayout.addWidget(newSupplierLabel, alignment=Qt.AlignmentFlag.AlignCenter)
            newSupplierLayout.addSpacing(10)

            # Модель для таблицы поставщиков
            suppliersHeaders = ['Имя', 'Номер телефона', 'Почта']
            suppliersData = get_suppliers_data()['data']
            self.suppliersModel = TableModel(suppliersData, suppliersHeaders)

            # Таблица для поставщиков
            suppliersTable = QTableView()
            suppliersTable.verticalHeader().setVisible(False)
            suppliersTable.setModel(self.suppliersModel)
            suppliersTable.resizeColumnsToContents()
            suppliersTable.setAlternatingRowColors(True)
            suppliersTable.setSelectionBehavior(suppliersTable.SelectionBehavior.SelectRows)
            suppliersTable.setFixedSize(700, 200)
            suppliersTable.horizontalHeader().setSectionResizeMode(QHeaderView.ResizeMode.Stretch)
            newSupplierLayout.addWidget(suppliersTable, alignment=Qt.AlignmentFlag.AlignCenter)
            newSupplierLayout.addSpacing(15)

            suppliersTableLabel = QLabel('Добавление нового поставщика')
            newSupplierLayout.addWidget(suppliersTableLabel, alignment=Qt.AlignmentFlag.AlignCenter)
            newSupplierLayout.addSpacing(15)

            # Поля ввода данных о новом поставщике
            newSupplierNameLayout = QHBoxLayout() # Имя поставщика
            newSupplierNameLayout.addStretch()

            newSupplierNameLabel = QLabel('Имя: ')
            newSupplierNameLabel.setFixedWidth(150)
            newSupplierNameLine = QLineEdit()
            newSupplierNameLine.setFixedWidth(250)
            newSupplierNameLine.setPlaceholderText('Имя нового поставщика')
            newSupplierNameLine.setMaxLength(45)

            newSupplierNameLayout.addWidget(newSupplierNameLabel, alignment=Qt.AlignmentFlag.AlignCenter)
            newSupplierNameLayout.addWidget(newSupplierNameLine, alignment=Qt.AlignmentFlag.AlignCenter)
            newSupplierNameLayout.addStretch()
            newSupplierLayout.addLayout(newSupplierNameLayout)

            newSupplierPhoneLayout = QHBoxLayout() # Номер телефона поставщика
            newSupplierPhoneLayout.addStretch()

            newSupplierPhoneLabel = QLabel('Номер телефона: ')
            newSupplierPhoneLabel.setFixedWidth(150)
            newSupplierPhoneLine = QLineEdit()
            newSupplierPhoneLine.setFixedWidth(250)
            newSupplierPhoneLine.setPlaceholderText('Телефон нового поставщика')
            newSupplierPhoneLine.setMaxLength(20)
            newSupplierPhoneLine.setValidator(QRegularExpressionValidator(QRegularExpression(r'^\d*$')))

            newSupplierPhoneLayout.addWidget(newSupplierPhoneLabel, alignment=Qt.AlignmentFlag.AlignCenter)
            newSupplierPhoneLayout.addWidget(newSupplierPhoneLine, alignment=Qt.AlignmentFlag.AlignCenter)
            newSupplierPhoneLayout.addStretch()
            newSupplierLayout.addLayout(newSupplierPhoneLayout)

            newSupplierEmailLayout = QHBoxLayout() # Email поставщика
            newSupplierEmailLayout.addStretch()

            newSupplierEmailLabel = QLabel('Почта: ')
            newSupplierEmailLabel.setFixedWidth(150)
            newSupplierEmailLine = QLineEdit()
            newSupplierEmailLine.setFixedWidth(250)
            newSupplierEmailLine.setPlaceholderText('Электронная почта')
            newSupplierEmailLine.setMaxLength(45)

            newSupplierEmailLayout.addWidget(newSupplierEmailLabel, alignment=Qt.AlignmentFlag.AlignCenter)
            newSupplierEmailLayout.addWidget(newSupplierEmailLine, alignment=Qt.AlignmentFlag.AlignCenter)
            newSupplierEmailLayout.addStretch()
            newSupplierLayout.addLayout(newSupplierEmailLayout)
            newSupplierLayout.addSpacing(15)

            addNewSupplierBtn = QPushButton('Добавить')
            addNewSupplierBtn.clicked.connect(self.handle_add_new_supplier)
            addNewSupplierBtn.setFixedWidth(200)
            newSupplierLayout.addWidget(addNewSupplierBtn, alignment=Qt.AlignmentFlag.AlignCenter)

            newSupplierLayout.addStretch()
            contentLayout.addWidget(self.newSupplierCard, alignment=Qt.AlignmentFlag.AlignCenter)

        contentLayout.addStretch()
        mainLayout.addWidget(scrollArea)

        """Навигационная панель"""
        self.navPanel = NavPanel(self)
        mainLayout.addWidget(self.navPanel)


        self.setLayout(mainLayout)

    def load_selectable_suppliers(self):
        """Загрузка поставщиков из бд в список для создания поставки"""
        self.supplierSelection.clear()
        self.supplierSelection.addItem('Выберите поставщика')
        suppliers = get_suppliers_name()
        if suppliers['success']:
            for supplierId, supplierName in suppliers['data']:
                self.supplierSelection.addItem(supplierName, supplierId)
            return None
        QMessageBox.warning(self, 'Ошибка', f'Ошибка в загрузке поставщиков: {suppliers['data']}')
        return None

    def load_selectable_warehouses(self):
        """Загрузка доступных пользователю складов в список для создания поставки"""
        self.warehouseSelection.clear()
        self.warehouseSelection.addItem('Выберите склад')
        warehouses = get_users_warehouses()
        if warehouses['success']:
            for warehouseId, warehouseName in warehouses['data']:
                self.warehouseSelection.addItem(warehouseName, warehouseId)
            return None
        QMessageBox.warning(self, 'Ошибка', f'Ошибка в загрузке складов: {warehouses["data"]}')
        return None

    def open_shipment_details(self, index):
        """Открытие окна с содержанием поставки"""
        row = index.row()
        shipmentId = self.shipmentsTable.model().index(row, 0).data()

        dialog = ShipmentDetailsWindow(shipmentId)
        dialog.exec()

    def handle_create_new_shipment(self):
        """Обработка нажатия на кнопку создания поставки"""
        if self.supplierSelection.currentIndex() == 0:
            QMessageBox.warning(self, 'Ошибка', 'Выберите поставщика')
            return None
        if self.warehouseSelection.currentIndex() == 0:
            QMessageBox.warning(self, 'Ошибка', 'Выберите склад')
            return None
        supplierId = self.supplierSelection.currentData()
        warehouseId = self.warehouseSelection.currentData()
        dialog = CreateNewShipmentWindow(supplierId, warehouseId)
        dialog.exec()
        self.update_shipments_table()
        return None

    def update_shipments_table(self):
        """Обновление таблицы поставок"""
        newShipmentsData = get_shipments_data(self.user.warehouses)['data']
        self.shipmentsModel.update_data(newShipmentsData)

    def handle_add_new_supplier(self):
        """Обработка нажатия на кнопку добавления поставщика"""
        pass

    def update_suppliers_table(self):
        """Обновление таблицы с поставщиками"""
        newSuppliersData = get_suppliers_data()['data']
        self.shipmentsModel.update_data(newSuppliersData)