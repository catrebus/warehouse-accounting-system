from PyQt6 import QtCore
from PyQt6.QtCore import QSize, Qt
from PyQt6.QtGui import QIcon
from PyQt6.QtWidgets import QVBoxLayout, QDialog, QLabel, QTableView, QHeaderView, QPushButton

from services.transfers_service import get_transfer_details
from ui.ui_elements.table_model import TableModel


class TransferDetailsWindow(QDialog):
    """Диалоговое окно для создания пригласительного кода"""
    def __init__(self, transferId):
        super().__init__()

        self.transferId = transferId

        # Настройка параметров окна
        self.setWindowTitle("Содержание транспортировки")
        self.setWindowIcon(QIcon("assets/icons/app_icon.png"))
        self.setFixedSize(QSize(800, 400))

        # Главный layout
        mainLayout = QVBoxLayout()

        windowLabel = QLabel('Содержание транспортировки')
        windowLabel.setAlignment(Qt.AlignmentFlag.AlignCenter)
        mainLayout.addWidget(windowLabel, alignment=Qt.AlignmentFlag.AlignCenter)

        transferDetailsHeaders = ['Название товара', 'Количество']
        transferDetails = get_transfer_details(transferId)['data']
        self.transferDetailsModel = TableModel(transferDetails, transferDetailsHeaders)

        # Таблица для поставщиков
        transferDetailsTable = QTableView()
        transferDetailsTable.verticalHeader().setVisible(False)
        transferDetailsTable.setModel(self.transferDetailsModel)
        transferDetailsTable.resizeColumnsToContents()
        transferDetailsTable.setAlternatingRowColors(True)
        transferDetailsTable.setSelectionBehavior(transferDetailsTable.SelectionBehavior.SelectRows)
        transferDetailsTable.setFixedSize(700, 200)
        transferDetailsTable.horizontalHeader().setSectionResizeMode(QHeaderView.ResizeMode.Stretch)
        mainLayout.addWidget(transferDetailsTable, alignment=Qt.AlignmentFlag.AlignCenter)

        mainLayout.addStretch()

        exitBtn = QPushButton('Выход')
        exitBtn.setFixedSize(200,40)
        exitBtn.clicked.connect(self.close)
        mainLayout.addWidget(exitBtn, alignment=Qt.AlignmentFlag.AlignCenter)
        exitBtn.setFocusPolicy(QtCore.Qt.FocusPolicy.NoFocus)

        self.setLayout(mainLayout)

