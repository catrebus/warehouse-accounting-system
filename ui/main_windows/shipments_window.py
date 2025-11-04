from PyQt6.QtCore import QSize, Qt
from PyQt6.QtGui import QColor
from PyQt6.QtWidgets import QLabel, QWidget, QWIDGETSIZE_MAX, QVBoxLayout, QStackedLayout, QFrame, \
    QGraphicsDropShadowEffect, QHBoxLayout, QComboBox, QPushButton, QMessageBox, QScrollArea

from services.shipments_service import get_suppliers
from ui.base_window import BaseWindow
from ui.ui_elements.nav_panel import NavPanel
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
        self.newShipmentCard.setFixedSize(1000, 150)

        newShipmentLayout = QVBoxLayout(self.newShipmentCard)
        newShipmentLayout.setContentsMargins(15, 15, 15, 15)

        cardEffect = QGraphicsDropShadowEffect()
        cardEffect.setBlurRadius(30)
        cardEffect.setXOffset(0)
        cardEffect.setYOffset(4)
        cardEffect.setColor(QColor(0, 0, 0, 120))
        self.newShipmentCard.setGraphicsEffect(cardEffect)

        # Заголовок элементов создания поставки
        newShipmentLabel = QLabel('Создание поставки')
        newShipmentLayout.addWidget(newShipmentLabel, alignment=Qt.AlignmentFlag.AlignCenter)
        newShipmentLayout.addSpacing(10)

        # Строка выбора поставщика
        supplierSelectionLayout = QHBoxLayout()
        supplierSelectionLayout.addStretch()

        supplierSelectionLabel = QLabel('Поставщик: ')
        supplierSelectionLayout.addWidget(supplierSelectionLabel)

        self.supplierSelection = QComboBox()
        self.load_selectable_suppliers()
        supplierSelectionLayout.addWidget(self.supplierSelection)

        supplierSelectionLayout.addStretch()
        newShipmentLayout.addLayout(supplierSelectionLayout)
        newShipmentLayout.addSpacing(15)

        # Кнопка создания поставки
        createShipmentBtn = QPushButton('Создать')
        createShipmentBtn.setFixedWidth(300)
        newShipmentLayout.addWidget(createShipmentBtn, alignment=Qt.AlignmentFlag.AlignCenter)

        newShipmentLayout.addStretch()
        contentLayout.addWidget(self.newShipmentCard, alignment=Qt.AlignmentFlag.AlignCenter) # Добавление подложки с элементами создания поставки в окно
        contentLayout.addSpacing(30)

        """Добавление нового поставщика в бд"""
        if self.user.role in [1,3]:
            self.newSupplierCard = QFrame()
            self.newSupplierCard.setObjectName('cardLogin')
            self.newSupplierCard.setFixedSize(1000, 150)

            newSupplierLayout = QVBoxLayout(self.newSupplierCard)
            newSupplierLayout.setContentsMargins(15, 15, 15, 15)

            cardEffect = QGraphicsDropShadowEffect()
            cardEffect.setBlurRadius(30)
            cardEffect.setXOffset(0)
            cardEffect.setYOffset(4)
            cardEffect.setColor(QColor(0, 0, 0, 120))
            self.newSupplierCard.setGraphicsEffect(cardEffect)

            # Заголовок элементов для добавления поставщика
            newSupplierLabel = QLabel('Добавление поставщика')
            newSupplierLayout.addWidget(newSupplierLabel, alignment=Qt.AlignmentFlag.AlignCenter)
            newSupplierLayout.addSpacing(10)

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
        suppliers = get_suppliers()
        if suppliers['success']:
            for supplierId, supplierName in suppliers['data']:
                self.supplierSelection.addItem(supplierName, supplierId)
            return None
        QMessageBox.warning(self, 'Ошибка', f'Ошибка в загрузке поставщиков: {suppliers['data']}')
        return None

    def handle_create_new_shipment(self):
        """Обработка нажатия на кнопку создания поставки"""
        pass