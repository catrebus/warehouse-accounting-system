from PyQt6.QtCore import QSize, Qt, QRegularExpression
from PyQt6.QtGui import QColor, QRegularExpressionValidator
from PyQt6.QtWidgets import QLabel, QWidget, QWIDGETSIZE_MAX, QVBoxLayout, QStackedLayout, QScrollArea, QFrame, \
    QGraphicsDropShadowEffect, QTableView, QHeaderView, QHBoxLayout, QComboBox, QPushButton, QLineEdit, QMessageBox

from services.info_from_db import get_warehouses
from services.transfers_service import get_transfers_data, get_warehouses_data, add_new_warehouse
from ui.base_window import BaseWindow
from ui.ui_elements.create_new_transfer_window import CreateNewTransferWindow
from ui.ui_elements.nav_panel import NavPanel
from ui.ui_elements.table_model import TableModel
from ui.ui_elements.transfer_details import TransferDetailsWindow


class TransfersWindow(BaseWindow):

    # Характеристики окна
    widowTitle: str = 'Система складского учета - Перемещения'
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
        scrollArea.setHorizontalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAlwaysOff)

        # Заголовок
        titleLabel = QLabel("Перемещения")
        titleLabel.setFixedHeight(40)
        titleLabel.setAlignment(Qt.AlignmentFlag.AlignCenter)
        contentLayout.addWidget(titleLabel, alignment=Qt.AlignmentFlag.AlignTop)

        """Оформление транспортировки"""
        # Подложка под элементы
        self.newTransferCard = QFrame()
        self.newTransferCard.setObjectName('cardLogin')
        self.newTransferCard.setFixedSize(1000, 450)

        newTransferLayout = QVBoxLayout(self.newTransferCard)
        newTransferLayout.setContentsMargins(15, 15, 15, 15)

        cardEffect = QGraphicsDropShadowEffect()
        cardEffect.setBlurRadius(30)
        cardEffect.setXOffset(0)
        cardEffect.setYOffset(4)
        cardEffect.setColor(QColor(0, 0, 0, 120))
        self.newTransferCard.setGraphicsEffect(cardEffect)

        # Заголовок таблицы проведенных транспортировок
        transferTableLabel = QLabel('Перемещения товара')
        newTransferLayout.addWidget(transferTableLabel, alignment=Qt.AlignmentFlag.AlignCenter)
        newTransferLayout.addSpacing(10)


        transfersHeaders = ['Id', 'Отправитель', 'Получатель', 'Сотрудник', 'Дата']
        transfersData = get_transfers_data(self.user.warehouses)['data']
        self.transfersModel = TableModel(transfersData, transfersHeaders)

        # Таблица транспортировок
        self.transfersTable = QTableView()
        self.transfersTable.verticalHeader().setVisible(False)
        self.transfersTable.setModel(self.transfersModel)
        self.transfersTable.resizeColumnsToContents()
        self.transfersTable.setAlternatingRowColors(True)
        self.transfersTable.setSelectionBehavior(self.transfersTable.SelectionBehavior.SelectRows)
        self.transfersTable.setFixedSize(700, 200)
        self.transfersTable.horizontalHeader().setSectionResizeMode(QHeaderView.ResizeMode.Stretch)
        self.transfersTable.doubleClicked.connect(self.open_transfer_details)
        newTransferLayout.addWidget(self.transfersTable, alignment=Qt.AlignmentFlag.AlignCenter)
        newTransferLayout.addSpacing(10)

        # Оформление транспортировки
        newTransferLabel = QLabel('Оформление транспортировки')
        newTransferLayout.addWidget(newTransferLabel, alignment=Qt.AlignmentFlag.AlignCenter)
        newTransferLayout.addSpacing(10)

        fromWarehouseSelectionLayout = QHBoxLayout() # Строка выбора склада-отправителя
        fromWarehouseSelectionLayout.addStretch()

        fromWarehouseSelectionLabel = QLabel('Отправитель: ')
        fromWarehouseSelectionLabel.setFixedWidth(200)
        fromWarehouseSelectionLayout.addWidget(fromWarehouseSelectionLabel)

        self.fromWarehouseSelection = QComboBox()
        self.fromWarehouseSelection.setFixedWidth(200)
        self.load_from_warehouse()
        self.fromWarehouseSelection.currentTextChanged.connect(self.load_to_warehouse)
        fromWarehouseSelectionLayout.addWidget(self.fromWarehouseSelection)

        fromWarehouseSelectionLayout.addStretch()
        newTransferLayout.addLayout(fromWarehouseSelectionLayout)
        newTransferLayout.addSpacing(10)

        toWarehouseSelectionLayout = QHBoxLayout() # Строка выбора склада-получателя
        toWarehouseSelectionLayout.addStretch()

        toWarehouseSelectionLabel = QLabel('Получатель: ')
        toWarehouseSelectionLabel.setFixedWidth(200)
        toWarehouseSelectionLayout.addWidget(toWarehouseSelectionLabel)

        self.toWarehouseSelection = QComboBox()
        self.toWarehouseSelection.setFixedWidth(200)
        self.load_to_warehouse()
        toWarehouseSelectionLayout.addWidget(self.toWarehouseSelection)

        toWarehouseSelectionLayout.addStretch()
        newTransferLayout.addLayout(toWarehouseSelectionLayout)
        newTransferLayout.addSpacing(15)

        # Кнопка оформления транспортировки
        createTransferBtn = QPushButton('Оформить')
        createTransferBtn.clicked.connect(self.handle_create_new_transfer)
        createTransferBtn.setFixedWidth(300)
        newTransferLayout.addWidget(createTransferBtn, alignment=Qt.AlignmentFlag.AlignCenter)

        newTransferLayout.addStretch()
        contentLayout.addWidget(self.newTransferCard, alignment=Qt.AlignmentFlag.AlignCenter)
        contentLayout.addSpacing(30)

        """Добавление нового склада в бд"""
        if self.user.role in [1]:
            self.newWarehouseCard = QFrame()
            self.newWarehouseCard.setObjectName('cardLogin')
            self.newWarehouseCard.setFixedSize(1000, 500)

            newWarehouseLayout = QVBoxLayout(self.newWarehouseCard)
            newWarehouseLayout.setContentsMargins(15, 15, 15, 15)

            cardEffect = QGraphicsDropShadowEffect()
            cardEffect.setBlurRadius(30)
            cardEffect.setXOffset(0)
            cardEffect.setYOffset(4)
            cardEffect.setColor(QColor(0, 0, 0, 120))
            self.newWarehouseCard.setGraphicsEffect(cardEffect)

            # Заголовок элементов для добавления склада
            warehouseTableLabel = QLabel('Склады')
            newWarehouseLayout.addWidget(warehouseTableLabel, alignment=Qt.AlignmentFlag.AlignCenter)
            newWarehouseLayout.addSpacing(10)

            # Модель для таблицы складов
            warehousesHeaders = ['Id', 'Имя', 'Адрес', 'Площадь']
            warehousesData = get_warehouses_data()['data']
            self.warehousesModel = TableModel(warehousesData, warehousesHeaders)

            # Таблица для поставщиков
            warehousesTable = QTableView()
            warehousesTable.verticalHeader().setVisible(False)
            warehousesTable.setModel(self.warehousesModel)
            warehousesTable.resizeColumnsToContents()
            warehousesTable.setAlternatingRowColors(True)
            warehousesTable.setSelectionBehavior(warehousesTable.SelectionBehavior.SelectRows)
            warehousesTable.setFixedSize(700, 200)
            warehousesTable.setColumnWidth(0, 40)
            warehousesTable.setColumnWidth(1, 150)
            warehousesTable.setColumnWidth(2, 430)
            warehousesTable.setColumnWidth(3, 70)
            newWarehouseLayout.addWidget(warehousesTable, alignment=Qt.AlignmentFlag.AlignCenter)
            newWarehouseLayout.addSpacing(15)

            # Добавление нового склада
            newWarehouseLabel = QLabel('Добавление нового склада')
            newWarehouseLayout.addWidget(newWarehouseLabel, alignment=Qt.AlignmentFlag.AlignCenter)
            newWarehouseLayout.addSpacing(15)

            newWarehouseNameLayout = QHBoxLayout() # Строка ввода имени склада
            newWarehouseNameLayout.addStretch()

            newWarehouseNameLabel = QLabel('Название: ')
            newWarehouseNameLabel.setFixedWidth(200)
            self.newWarehouseNameLine = QLineEdit()
            self.newWarehouseNameLine.setFixedWidth(200)
            self.newWarehouseNameLine.setPlaceholderText('Название склада')
            self.newWarehouseNameLine.setMaxLength(255)

            newWarehouseNameLayout.addWidget(newWarehouseNameLabel, alignment=Qt.AlignmentFlag.AlignCenter)
            newWarehouseNameLayout.addWidget(self.newWarehouseNameLine, alignment=Qt.AlignmentFlag.AlignCenter)
            newWarehouseNameLayout.addStretch()
            newWarehouseLayout.addLayout(newWarehouseNameLayout)
            newWarehouseLayout.addSpacing(10)

            newWarehouseAddressLayout = QHBoxLayout()  # Строка ввода адреса склада
            newWarehouseAddressLayout.addStretch()

            newWarehouseAddressLabel = QLabel('Адрес: ')
            newWarehouseAddressLabel.setFixedWidth(200)
            self.newWarehouseAddressLine = QLineEdit()
            self.newWarehouseAddressLine.setFixedWidth(200)
            self.newWarehouseAddressLine.setPlaceholderText('Адрес склада')
            self.newWarehouseAddressLine.setMaxLength(255)

            newWarehouseAddressLayout.addWidget(newWarehouseAddressLabel, alignment=Qt.AlignmentFlag.AlignCenter)
            newWarehouseAddressLayout.addWidget(self.newWarehouseAddressLine, alignment=Qt.AlignmentFlag.AlignCenter)
            newWarehouseAddressLayout.addStretch()
            newWarehouseLayout.addLayout(newWarehouseAddressLayout)
            newWarehouseLayout.addSpacing(10)

            newWarehouseAreaLayout = QHBoxLayout()  # Строка ввода площади склада
            newWarehouseAreaLayout.addStretch()

            newWarehouseAreaLabel = QLabel('Площадь(м²): ')
            newWarehouseAreaLabel.setFixedWidth(200)
            self.newWarehouseAreaLine = QLineEdit()
            self.newWarehouseAreaLine.setFixedWidth(200)
            self.newWarehouseAreaLine.setPlaceholderText('Площадь склада')
            self.newWarehouseAreaLine.setValidator(QRegularExpressionValidator(QRegularExpression(r"^[1-9][0-9]*$")))
            self.newWarehouseAreaLine.setMaxLength(10)

            newWarehouseAreaLayout.addWidget(newWarehouseAreaLabel, alignment=Qt.AlignmentFlag.AlignCenter)
            newWarehouseAreaLayout.addWidget(self.newWarehouseAreaLine, alignment=Qt.AlignmentFlag.AlignCenter)
            newWarehouseAreaLayout.addStretch()
            newWarehouseLayout.addLayout(newWarehouseAreaLayout)
            newWarehouseLayout.addSpacing(15)

            # Кнопка добавления склада
            addNewWarehouseBtn = QPushButton('Добавить')
            addNewWarehouseBtn.clicked.connect(self.handle_add_new_warehouse)
            addNewWarehouseBtn.setFixedWidth(300)
            newWarehouseLayout.addWidget(addNewWarehouseBtn, alignment=Qt.AlignmentFlag.AlignCenter)

            newWarehouseLayout.addStretch()
            contentLayout.addWidget(self.newWarehouseCard, alignment=Qt.AlignmentFlag.AlignCenter)

        contentLayout.addStretch()
        mainLayout.addWidget(scrollArea)

        """Навигационная панель"""
        self.navPanel = NavPanel(self)
        mainLayout.addWidget(self.navPanel)


        self.setLayout(mainLayout)


    def open_transfer_details(self, index):
        """Открытие окна с содержимым транспортировки"""
        row = index.row()
        transferId = self.transfersTable.model().index(row, 0).data()

        dialog = TransferDetailsWindow(transferId)
        dialog.exec()

    def load_from_warehouse(self):
        self.fromWarehouseSelection.clear()
        self.fromWarehouseSelection.addItem('Выберите склад')
        warehouses = get_warehouses(self.user.warehouses)

        for warehouseId, warehouseName in warehouses:
            self.fromWarehouseSelection.addItem(warehouseName, warehouseId)
        return None

    def load_to_warehouse(self):
        self.toWarehouseSelection.clear()
        if self.fromWarehouseSelection.currentIndex() == 0:
            self.toWarehouseSelection.addItem('Выберите отправителя')
            return None
        self.toWarehouseSelection.addItem('Выберите склад')
        warehouses = get_warehouses()

        for warehouseId, warehouseName in warehouses:
            if warehouseId == self.fromWarehouseSelection.currentData():
                continue
            self.toWarehouseSelection.addItem(warehouseName, warehouseId)
        return None

    def handle_create_new_transfer(self):
        if self.fromWarehouseSelection.currentIndex() == 0:
            QMessageBox.warning(self, 'Ошибка', 'Выберите склад-отправитель')
            return None
        if self.toWarehouseSelection.currentIndex() == 0:
            QMessageBox.warning(self, 'Ошибка', 'Выберите склад-получатель')
            return None
        fromWarehouseId = self.fromWarehouseSelection.currentData()
        toWarehouseId = self.toWarehouseSelection.currentData()

        dialog = CreateNewTransferWindow(fromWarehouseId, toWarehouseId)
        dialog.exec()
        self.refresh()
        return None

    def handle_add_new_warehouse(self):
        newWarehouseName = self.newWarehouseNameLine.text().strip()
        newWarehouseAddress = self.newWarehouseAddressLine.text().strip()
        newWarehouseArea = self.newWarehouseAreaLine.text().strip()

        if not newWarehouseName:
            QMessageBox.warning(self, 'Ошибка', 'Заполните поле названия склада')
            return None
        if not newWarehouseAddress:
            QMessageBox.warning(self, 'Ошибка', 'Заполните поле адреса склада')
            return None
        if not newWarehouseArea:
            QMessageBox.warning(self, 'Ошибка', 'Заполните поле площади склада')
            return None

        result = add_new_warehouse(newWarehouseName,newWarehouseAddress, newWarehouseArea)
        if result['success']:
            QMessageBox.information(self, 'Успех', result['data'])
            self.refresh()
            return None
        QMessageBox.warning(self, 'Ошибка', result['data'])
        return None

    def update_transfers_table(self):
        newTransfersData = get_transfers_data(self.user.warehouses)['data']
        self.transfersModel.update_data(newTransfersData)

    def update_warehouses_table(self):
        newWarehousesData = get_warehouses_data()['data']
        self.warehousesModel.update_data(newWarehousesData)

    def refresh(self):
        self.update_transfers_table()
        self.load_from_warehouse()
        self.load_to_warehouse()
        if self.user.role == 1:
            self.update_warehouses_table()