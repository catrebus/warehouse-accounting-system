from PyQt6.QtCore import QSize, QRegularExpression
from PyQt6.QtGui import QIcon, QRegularExpressionValidator
from PyQt6.QtWidgets import QVBoxLayout, QDialog, QPushButton, QTableWidget, QHBoxLayout, QComboBox, QLineEdit, \
    QHeaderView, QMessageBox

from services.shipments_service import get_available_products
from services.transfers_service import add_new_transfer


class CreateNewTransferWindow(QDialog):
    """Диалоговое окно для оформления перемещения"""
    def __init__(self, fromWarehouseId, toWarehouseId):
        super().__init__()

        self.fromWarehouseId = fromWarehouseId
        self.toWarehouseId = toWarehouseId

        # Получение всех продуктов, доступных на выбранном складе
        self.fromWarehouseProducts = get_available_products(self.fromWarehouseId)['data']
        self.toWarehouseProducts = get_available_products(self.toWarehouseId)['data']
        self.products =  list(set(self.fromWarehouseProducts) & set(self.toWarehouseProducts))

        # Настройка параметров окна
        self.setWindowTitle("Оформление транспортировки")
        self.setWindowIcon(QIcon("assets/icons/app_icon.png"))
        self.setFixedSize(QSize(800, 400))

        # Главный layout
        mainLayout = QVBoxLayout()

        # Таблица товаров
        self.table = QTableWidget(0, 3)
        self.table.setHorizontalHeaderLabels(["Товар", "Количество", ""])
        self.table.verticalHeader().setVisible(False)
        self.table.setColumnWidth(0, 500)
        self.table.setColumnWidth(1, 230)
        self.table.setColumnWidth(2, 30)

        header = self.table.horizontalHeader()
        header.setSectionResizeMode(0, QHeaderView.ResizeMode.Fixed)
        header.setSectionResizeMode(1, QHeaderView.ResizeMode.Fixed)

        # Дополнительно — отключает растягивание и ручное изменение мышкой
        header.setSectionsMovable(False)
        header.setSectionsClickable(False)

        mainLayout.addWidget(self.table)

        # Кнопка добавления строки
        addRowBtn = QPushButton("Добавить товар")
        addRowBtn.clicked.connect(self.add_row)
        mainLayout.addWidget(addRowBtn)

        mainLayout.addStretch()
        # Кнопки сохранения
        btnLayout = QHBoxLayout()
        saveBtn = QPushButton("Сохранить")
        cancelBtn = QPushButton("Отмена")
        saveBtn.clicked.connect(self.handle_save_btn)
        cancelBtn.clicked.connect(self.close)
        btnLayout.addWidget(saveBtn)
        btnLayout.addWidget(cancelBtn)
        mainLayout.addLayout(btnLayout)


        self.setLayout(mainLayout)

    def add_row(self):
        row = self.table.rowCount()
        self.table.insertRow(row)

        # ComboBox с товарами
        productCombo = QComboBox()
        productCombo.addItem('Выберите товар')
        for productId, productName in self.products:
            productCombo.addItem(productName, productId)
        self.table.setCellWidget(row, 0, productCombo)

        # Поле количества с валидатором
        qtyEdit = QLineEdit()
        qtyEdit.setValidator(QRegularExpressionValidator(QRegularExpression(r"^[1-9][0-9]*$")))
        qtyEdit.setMaxLength(10)
        self.table.setCellWidget(row, 1, qtyEdit)

        # Кнопка удаления строки
        removeBtn = QPushButton("✖")
        removeBtn.setFixedWidth(30)
        removeBtn.clicked.connect(lambda _, b=removeBtn: self.remove_row(b))
        self.table.setCellWidget(row, 2, removeBtn)

    def remove_row(self, button):
        for row in range(self.table.rowCount()):
            if self.table.cellWidget(row, 2) is button:
                self.table.removeRow(row)
                break

    def handle_save_btn(self):
        """Вернуть [(product_id, quantity), ...]"""
        result = []
        addedProducts = set()
        for row in range(self.table.rowCount()):
            productCombo = self.table.cellWidget(row, 0)
            qtyEdit = self.table.cellWidget(row, 1)

            if productCombo.currentIndex() == 0:
                QMessageBox.warning(self, 'Ошибка', 'Не во всех строках поставки выбран товар')
                return None
            if not qtyEdit.text():
                QMessageBox.warning(self, 'Ошибка', 'Не во всех строках поставки указано количество товара')
                return None

            pid = productCombo.currentData()
            qty = qtyEdit.text()
            if pid in addedProducts:
                QMessageBox.warning(self, 'Ошибка', 'Один и тот же товар был добавлен больше 1 раза')
                return None
            addedProducts.add(pid)

            result.append((pid, int(qty)))
        addingResult = add_new_transfer(self.fromWarehouseId, self.toWarehouseId, result)
        if addingResult['success']:
            QMessageBox.information(self, 'Успех', addingResult['data'])
            self.close()
            return None
        QMessageBox.warning(self, 'Ошибка', addingResult['data'])
        return None
