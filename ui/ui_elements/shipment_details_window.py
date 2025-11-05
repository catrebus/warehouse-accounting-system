from PyQt6.QtCore import QSize, Qt
from PyQt6.QtGui import QIcon
from PyQt6.QtWidgets import QVBoxLayout, QDialog, QLabel, QTableView, QHeaderView, QPushButton

from services.shipments_service import get_shipment_details
from ui.ui_elements.table_model import TableModel


class ShipmentDetailsWindow(QDialog):
    """Диалоговое окно для создания пригласительного кода"""
    def __init__(self, shipmentId):
        super().__init__()

        self.shipmentId = shipmentId

        # Настройка параметров окна
        self.setWindowTitle("Содержание поставки")
        self.setWindowIcon(QIcon("assets/icons/app_icon.png"))
        self.setFixedSize(QSize(800, 400))

        # Главный layout
        mainLayout = QVBoxLayout()

        windowLabel = QLabel('Содержание поставки')
        windowLabel.setAlignment(Qt.AlignmentFlag.AlignCenter)
        mainLayout.addWidget(windowLabel, alignment=Qt.AlignmentFlag.AlignCenter)

        shipmentDetailsHeaders = ['Название товара', 'Количество']
        shipmentDetails = get_shipment_details(shipmentId)['data']
        self.suppliersModel = TableModel(shipmentDetails, shipmentDetailsHeaders)

        # Таблица для поставщиков
        shipmentDetailsTable = QTableView()
        shipmentDetailsTable.verticalHeader().setVisible(False)
        shipmentDetailsTable.setModel(self.suppliersModel)
        shipmentDetailsTable.resizeColumnsToContents()
        shipmentDetailsTable.setAlternatingRowColors(True)
        shipmentDetailsTable.setSelectionBehavior(shipmentDetailsTable.SelectionBehavior.SelectRows)
        shipmentDetailsTable.setFixedSize(700, 200)
        shipmentDetailsTable.horizontalHeader().setSectionResizeMode(QHeaderView.ResizeMode.Stretch)
        mainLayout.addWidget(shipmentDetailsTable, alignment=Qt.AlignmentFlag.AlignCenter)

        mainLayout.addStretch()

        exitBtn = QPushButton('Выход')
        exitBtn.setFixedSize(200,40)
        exitBtn.clicked.connect(self.close)
        mainLayout.addWidget(exitBtn, alignment=Qt.AlignmentFlag.AlignCenter)

        self.setLayout(mainLayout)

