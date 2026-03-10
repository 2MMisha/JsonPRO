import sys
import os
import json
import pandas as pd
from PyQt6 import QtWidgets, QtGui, QtCore, QtPrintSupport

APP_NAME = "JSON Pro"
APP_COLORS = {
    "accent": "#ea8c2f",
    "gray": "#545454",
    "black": "#000000"
}
MEDIA_FILES = {
    "logo": "logo.png",
    "icon": "app_icon.ico",
    "json_icon": "jsonicon.png",
    "secondary_icon": "2.png"
}

SUPPORTED_EXTENSIONS = ["*.json", "*.csv", "*.xlsx"]

class SubTab(QtWidgets.QWidget):
    def __init__(self, name, data):
        super().__init__()
        self.name = name
        self.data = data
        self.clipboard_data = []

        self.layout = QtWidgets.QVBoxLayout(self)

        self.search = QtWidgets.QLineEdit()
        self.search.setPlaceholderText(f"Search in {name}...")
        self.layout.addWidget(self.search)

        self.table = QtWidgets.QTableView()
        self.model = QtGui.QStandardItemModel()
        self.proxy = QtCore.QSortFilterProxyModel()
        self.proxy.setSourceModel(self.model)
        self.proxy.setFilterCaseSensitivity(QtCore.Qt.CaseSensitivity.CaseInsensitive)
        self.table.setModel(self.proxy)

        self.table.setSortingEnabled(True)
        self.table.setSelectionBehavior(QtWidgets.QAbstractItemView.SelectionBehavior.SelectRows)
        self.table.setSelectionMode(QtWidgets.QAbstractItemView.SelectionMode.SingleSelection)
        self.table.setEditTriggers(QtWidgets.QAbstractItemView.EditTrigger.DoubleClicked | QtWidgets.QAbstractItemView.EditTrigger.SelectedClicked)
        self.table.horizontalHeader().setSectionsMovable(True)
        self.table.horizontalHeader().setStretchLastSection(True)
        self.table.setCursor(QtGui.QCursor(QtCore.Qt.CursorShape.PointingHandCursor))
        self.table.horizontalHeader().sectionMoved.connect(self.save_header_state)
        self.table.horizontalHeader().sectionResized.connect(self.save_header_state)

        self.layout.addWidget(self.table)
        self.search.textChanged.connect(self.proxy.setFilterFixedString)

        self.load_data()
        self.load_header_state()

    def load_data(self):
        self.model.clear()
        if isinstance(self.data, list):
            if all(isinstance(item, dict) for item in self.data):
                headers = list({k for d in self.data for k in d.keys()})
                self.model.setHorizontalHeaderLabels(headers)
                for row_data in self.data:
                    row = [QtGui.QStandardItem(str(row_data.get(h, "-"))) for h in headers]
                    for item in row: item.setEditable(True)
                    self.model.appendRow(row)
            elif all(isinstance(item, str) for item in self.data):
                self.model.setHorizontalHeaderLabels(["Value"])
                for val in self.data:
                    item = QtGui.QStandardItem(val)
                    item.setEditable(True)
                    self.model.appendRow([item])

    def collect_data(self):
        headers = [self.model.headerData(i, QtCore.Qt.Orientation.Horizontal) for i in range(self.model.columnCount())]
        result = []
        for row in range(self.model.rowCount()):
            if headers == ["Value"]:
                result.append(self.model.item(row, 0).text())
            else:
                item = {}
                for col, h in enumerate(headers):
                    val = self.model.item(row, col).text()
                    # Пытаемся парсить числовые значения, иначе строка
                    try:
                        val_parsed = json.loads(val)
                    except:
                        val_parsed = val
                    item[h] = val_parsed
                result.append(item)
        return result

    def save_header_state(self):
        # Сохраняем порядок и размеры колонок в Qt settings или в атрибут
        header = self.table.horizontalHeader()
        self._header_state = {
            "order": [header.logicalIndex(i) for i in range(header.count())],
            "sizes": [header.sectionSize(i) for i in range(header.count())],
        }

    def load_header_state(self):
        if hasattr(self, "_header_state"):
            header = self.table.horizontalHeader()
            order = self._header_state.get("order", [])
            sizes = self._header_state.get("sizes", [])
            for visual_index, logical_index in enumerate(order):
                header.moveSection(header.visualIndex(logical_index), visual_index)
            for i, size in enumerate(sizes):
                header.resizeSection(i, size)


class JsonEditor(QtWidgets.QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle(APP_NAME)
        self.resize(1100, 700)
        self.setWindowIcon(QtGui.QIcon(MEDIA_FILES["icon"]))

        self.file_paths = {}  # индекс вкладки -> путь файла
        self.subtabs = {}     # индекс вкладки -> {название подвкладки: SubTab}

        self.clipboard_data = []

        self.tabs = QtWidgets.QTabWidget()
        self.tabs.setTabsClosable(True)
        self.tabs.tabCloseRequested.connect(self.close_tab)
        self.setCentralWidget(self.tabs)

        self.status = QtWidgets.QStatusBar()
        self.setStatusBar(self.status)

        self.create_menus()
        self.create_shortcuts()

    def create_menus(self):
        menubar = self.menuBar()

        file_menu = menubar.addMenu("File")
        new_action = QtGui.QAction("New", self)
        new_action.setShortcut("Ctrl+N")
        new_action.triggered.connect(self.new_file)
        file_menu.addAction(new_action)

        open_action = QtGui.QAction("Open", self)
        open_action.setShortcut("Ctrl+O")
        open_action.triggered.connect(self.open_file)
        file_menu.addAction(open_action)

        save_action = QtGui.QAction("Save", self)
        save_action.setShortcut("Ctrl+S")
        save_action.triggered.connect(self.save_file)
        file_menu.addAction(save_action)

        save_as_action = QtGui.QAction("Save As", self)
        save_as_action.triggered.connect(self.save_file_as)
        file_menu.addAction(save_as_action)

        export_excel_action = QtGui.QAction("Export to Excel", self)
        export_excel_action.triggered.connect(self.export_excel)
        file_menu.addAction(export_excel_action)

        export_csv_action = QtGui.QAction("Export to CSV", self)
        export_csv_action.triggered.connect(self.export_csv)
        file_menu.addAction(export_csv_action)

        file_menu.addSeparator()

        print_action = QtGui.QAction("Print", self)
        print_action.setShortcut("Ctrl+P")
        print_action.triggered.connect(self.print_all)
        file_menu.addAction(print_action)

        file_menu.addSeparator()

        exit_action = QtGui.QAction("Exit", self)
        exit_action.triggered.connect(self.close)
        file_menu.addAction(exit_action)

        edit_menu = menubar.addMenu("Edit")
        add_row_action = QtGui.QAction("Add Row", self)
        add_row_action.setShortcut("Ctrl+Shift+A")
        add_row_action.triggered.connect(self.add_row)
        edit_menu.addAction(add_row_action)

        delete_row_action = QtGui.QAction("Delete Row", self)
        delete_row_action.setShortcut("Ctrl+Shift+D")
        delete_row_action.triggered.connect(self.delete_row)
        edit_menu.addAction(delete_row_action)

        add_col_action = QtGui.QAction("Add Column", self)
        add_col_action.setShortcut("Ctrl+Alt+A")
        add_col_action.triggered.connect(self.add_column)
        edit_menu.addAction(add_col_action)

        delete_col_action = QtGui.QAction("Delete Column", self)
        delete_col_action.setShortcut("Ctrl+Alt+D")
        delete_col_action.triggered.connect(self.delete_column)
        edit_menu.addAction(delete_col_action)

        rename_col_action = QtGui.QAction("Rename Column", self)
        rename_col_action.setShortcut("Ctrl+Alt+R")
        rename_col_action.triggered.connect(self.rename_column)
        edit_menu.addAction(rename_col_action)

        edit_menu.addSeparator()

        add_subtab_action = QtGui.QAction("Add Subtab", self)
        add_subtab_action.setShortcut("Ctrl+T")
        add_subtab_action.triggered.connect(self.add_subtab)
        edit_menu.addAction(add_subtab_action)

        delete_subtab_action = QtGui.QAction("Delete Subtab", self)
        delete_subtab_action.setShortcut("Ctrl+W")
        delete_subtab_action.triggered.connect(self.delete_subtab)
        edit_menu.addAction(delete_subtab_action)

        rename_subtab_action = QtGui.QAction("Rename Subtab", self)
        rename_subtab_action.setShortcut("Ctrl+R")
        rename_subtab_action.triggered.connect(self.rename_subtab)
        edit_menu.addAction(rename_subtab_action)

        help_menu = menubar.addMenu("Help")
        about_action = QtGui.QAction("About", self)
        about_action.triggered.connect(self.show_about)
        help_menu.addAction(about_action)

    def create_shortcuts(self):
        QtGui.QShortcut(QtGui.QKeySequence("Ctrl+C"), self, self.copy_row)
        QtGui.QShortcut(QtGui.QKeySequence("Ctrl+V"), self, self.paste_row)
    def current_subtab(self):
        main_index = self.tabs.currentIndex()
        if main_index == -1:
            return None
        tab_widget = self.tabs.widget(main_index)
        # Если подвкладки — это QTabWidget
        if isinstance(tab_widget, QtWidgets.QTabWidget):
            sub_index = tab_widget.currentIndex()
            if sub_index == -1:
                return None
            return tab_widget.widget(sub_index)
        # Иначе один SubTab сразу
        elif isinstance(tab_widget, SubTab):
            return tab_widget
        return None

    def new_file(self):
        # Новый пустой таб с пустой подвкладкой
        subtab = SubTab("Sheet1", [])
        tab_widget = QtWidgets.QTabWidget()
        tab_widget.addTab(subtab, "Sheet1")
        index = self.tabs.addTab(tab_widget, "Untitled")
        self.tabs.setCurrentIndex(index)
        self.file_paths[index] = None
        self.subtabs[index] = {"Sheet1": subtab}

    def open_file(self):
        path, _ = QtWidgets.QFileDialog.getOpenFileName(self, "Open file", "", "JSON Files (*.json);;CSV Files (*.csv);;Excel Files (*.xlsx *.xls)")
        if not path:
            return
        try:
            ext = os.path.splitext(path)[1].lower()
            if ext == ".json":
                with open(path, "r", encoding="utf-8") as f:
                    data = json.load(f)
                self.open_json_data(data, os.path.basename(path))
            elif ext == ".csv":
                df = pd.read_csv(path)
                data = df.to_dict(orient='records')
                self.open_simple_data(data, os.path.basename(path))
            elif ext in [".xlsx", ".xls"]:
                xls = pd.ExcelFile(path)
                # Для Excel создаём QTabWidget с листами
                tab_widget = QtWidgets.QTabWidget()
                subtabs_dict = {}
                for sheet in xls.sheet_names:
                    df = xls.parse(sheet)
                    data = df.to_dict(orient='records')
                    subtab = SubTab(sheet, data)
                    tab_widget.addTab(subtab, sheet)
                    subtabs_dict[sheet] = subtab
                index = self.tabs.addTab(tab_widget, os.path.basename(path))
                self.tabs.setCurrentIndex(index)
                self.file_paths[index] = path
                self.subtabs[index] = subtabs_dict
            else:
                QtWidgets.QMessageBox.warning(self, "Unsupported format", "File format not supported")
                return
        except Exception as e:
            QtWidgets.QMessageBox.critical(self, "Error opening file", str(e))

    def open_json_data(self, data, filename):
        if isinstance(data, dict):
            # Если есть несколько ключей с листами — подвкладки
            tab_widget = QtWidgets.QTabWidget()
            subtabs_dict = {}
            for key, val in data.items():
                subtab = SubTab(key, val)
                tab_widget.addTab(subtab, key)
                subtabs_dict[key] = subtab
            index = self.tabs.addTab(tab_widget, filename)
            self.tabs.setCurrentIndex(index)
            self.file_paths[index] = filename
            self.subtabs[index] = subtabs_dict
        elif isinstance(data, list):
            # Просто список объектов — один субтаб
            subtab = SubTab("Sheet1", data)
            tab_widget = QtWidgets.QTabWidget()
            tab_widget.addTab(subtab, "Sheet1")
            index = self.tabs.addTab(tab_widget, filename)
            self.tabs.setCurrentIndex(index)
            self.file_paths[index] = filename
            self.subtabs[index] = {"Sheet1": subtab}
        else:
            QtWidgets.QMessageBox.warning(self, "Invalid JSON", "Unsupported JSON structure")

    def open_simple_data(self, data, filename):
        subtab = SubTab("Sheet1", data)
        tab_widget = QtWidgets.QTabWidget()
        tab_widget.addTab(subtab, "Sheet1")
        index = self.tabs.addTab(tab_widget, filename)
        self.tabs.setCurrentIndex(index)
        self.file_paths[index] = filename
        self.subtabs[index] = {"Sheet1": subtab}

    def save_file(self):
        index = self.tabs.currentIndex()
        if index == -1:
            return
        path = self.file_paths.get(index)
        if not path:
            self.save_file_as()
        else:
            self._save_to_path(index, path)

    def save_file_as(self):
        index = self.tabs.currentIndex()
        if index == -1:
            return
        path, _ = QtWidgets.QFileDialog.getSaveFileName(self, "Save As", "", "JSON Files (*.json);;CSV Files (*.csv);;Excel Files (*.xlsx)")
        if not path:
            return
        self.file_paths[index] = path
        self._save_to_path(index, path)
        self.tabs.setTabText(index, os.path.basename(path))

    def _save_to_path(self, index, path):
        ext = os.path.splitext(path)[1].lower()
        subtabs_dict = self.subtabs.get(index)
        if not subtabs_dict:
            QtWidgets.QMessageBox.warning(self, "No data", "No data to save")
            return
        try:
            if ext == ".json":
                data_to_save = {}
                for key, subtab in subtabs_dict.items():
                    data_to_save[key] = subtab.collect_data()
                with open(path, "w", encoding="utf-8") as f:
                    json.dump(data_to_save, f, indent=4, ensure_ascii=False)
            elif ext == ".csv":
                # Сохраняем первую подвкладку в CSV
                first_subtab = next(iter(subtabs_dict.values()))
                df = pd.DataFrame(first_subtab.collect_data())
                df.to_csv(path, index=False)
            elif ext in [".xlsx", ".xls"]:
                with pd.ExcelWriter(path) as writer:
                    for key, subtab in subtabs_dict.items():
                        df = pd.DataFrame(subtab.collect_data())
                        df.to_excel(writer, sheet_name=key, index=False)
            else:
                QtWidgets.QMessageBox.warning(self, "Unsupported format", "Unsupported save format")
                return
            self.status.showMessage(f"Saved {path}", 4000)
        except Exception as e:
            QtWidgets.QMessageBox.critical(self, "Error saving file", str(e))

    def export_excel(self):
        index = self.tabs.currentIndex()
        if index == -1:
            return
        path, _ = QtWidgets.QFileDialog.getSaveFileName(self, "Export to Excel", "", "Excel Files (*.xlsx)")
        if not path:
            return
        if not path.endswith(".xlsx"):
            path += ".xlsx"
        self._save_to_path(index, path)

    def export_csv(self):
        index = self.tabs.currentIndex()
        if index == -1:
            return
        path, _ = QtWidgets.QFileDialog.getSaveFileName(self, "Export to CSV", "", "CSV Files (*.csv)")
        if not path:
            return
        if not path.endswith(".csv"):
            path += ".csv"
        self._save_to_path(index, path)

    def print_all(self):
        index = self.tabs.currentIndex()
        if index == -1:
            return
        subtabs_dict = self.subtabs.get(index)
        if not subtabs_dict:
            return

        printer = QtPrintSupport.QPrinter()
        preview = QtPrintSupport.QPrintPreviewDialog(printer, self)
        preview.paintRequested.connect(lambda p=printer: self.handle_print(p, index))
        preview.exec()

    def handle_print(self, printer, index):
        subtabs_dict = self.subtabs.get(index)
        painter = QtGui.QPainter(printer)

        for i, (key, subtab) in enumerate(subtabs_dict.items()):
            if i > 0:
                printer.newPage()

            rect = painter.viewport()
            font = painter.font()
            font.setPointSize(16)
            painter.setFont(font)

            # Верхний колонтитул — название подвкладки (ключ) и в скобках название файла
            title = f"{key} ({self.file_paths.get(index, 'Untitled')})"
            painter.drawText(rect, QtCore.Qt.AlignmentFlag.AlignTop | QtCore.Qt.AlignmentFlag.AlignHCenter, title)

            # Логотип побольше снизу
            logo = QtGui.QPixmap(MEDIA_FILES["logo"])
            if not logo.isNull():
                scaled_logo = logo.scaledToWidth(100, QtCore.Qt.TransformationMode.SmoothTransformation)
                bottom_rect = QtCore.QRect(rect.left(), rect.bottom() - scaled_logo.height() - 10, scaled_logo.width(), scaled_logo.height())
                painter.drawPixmap(bottom_rect, scaled_logo)

            # Отрисовка таблицы в виде текста
            headers = [subtab.model.headerData(c, QtCore.Qt.Orientation.Horizontal) for c in range(subtab.model.columnCount())]
            rows = []
            for r in range(subtab.model.rowCount()):
                row_items = []
                for c in range(subtab.model.columnCount()):
                    item = subtab.model.item(r, c)
                    row_items.append(item.text() if item else "")
                rows.append(row_items)

            y_offset = 40
            line_height = 20
            painter.setFont(QtGui.QFont("Arial", 10))

            # Рисуем заголовки
            x = 10
            for h in headers:
                painter.drawText(x, y_offset, str(h))
                x += 100
            y_offset += line_height

            # Рисуем строки
            for row in rows:
                x = 10
                for cell in row:
                    painter.drawText(x, y_offset, str(cell))
                    x += 100
                y_offset += line_height

        painter.end()

    # Методы для редактирования таблицы

    def add_row(self):
        subtab = self.current_subtab()
        if not subtab:
            QtWidgets.QMessageBox.warning(self, "Warning", "No active subtab to add a row.")
            return
        row_position = subtab.model.rowCount()
        subtab.model.insertRow(row_position)
        for col in range(subtab.model.columnCount()):
            subtab.model.setItem(row_position, col, QtGui.QStandardItem("-"))

    def delete_row(self):
        subtab = self.current_subtab()
        if not subtab:
            QtWidgets.QMessageBox.warning(self, "Warning", "No active subtab to delete a row.")
            return
        selected = subtab.table.selectionModel().selectedRows()
        if not selected:
            QtWidgets.QMessageBox.warning(self, "Warning", "No row selected.")
            return
        for index in sorted(selected, reverse=True):
            subtab.model.removeRow(index.row())

    def add_column(self):
        subtab = self.current_subtab()
        if not subtab:
            QtWidgets.QMessageBox.warning(self, "Warning", "No active subtab to add a column.")
            return
        col_count = subtab.model.columnCount()
        subtab.model.setHorizontalHeaderItem(col_count, QtGui.QStandardItem("New Column"))
        for row in range(subtab.model.rowCount()):
            subtab.model.setItem(row, col_count, QtGui.QStandardItem("-"))

    def delete_column(self):
        subtab = self.current_subtab()
        if not subtab:
            QtWidgets.QMessageBox.warning(self, "Warning", "No active subtab to delete a column.")
            return
        col = subtab.table.currentIndex().column()
        if col == -1:
            QtWidgets.QMessageBox.warning(self, "Warning", "No column selected.")
            return
        subtab.model.removeColumn(col)

    def rename_column(self):
        subtab = self.current_subtab()
        if not subtab:
            QtWidgets.QMessageBox.warning(self, "Warning", "No active subtab to rename a column.")
            return
        col = subtab.table.currentIndex().column()
        if col == -1:
            QtWidgets.QMessageBox.warning(self, "Warning", "No column selected.")
            return
        old_name = subtab.model.headerData(col, QtCore.Qt.Orientation.Horizontal)
        text, ok = QtWidgets.QInputDialog.getText(self, "Rename Column", f"Old name: {old_name}\nNew name:")
        if ok and text:
            subtab.model.setHeaderData(col, QtCore.Qt.Orientation.Horizontal, text)

    def add_subtab(self):
        index = self.tabs.currentIndex()
        if index == -1:
            QtWidgets.QMessageBox.warning(self, "Warning", "No main tab open to add a subtab.")
            return
        tab_widget = self.tabs.widget(index)
        if not isinstance(tab_widget, QtWidgets.QTabWidget):
            QtWidgets.QMessageBox.warning(self, "Warning", "Current tab does not support subtabs.")
            return
        text, ok = QtWidgets.QInputDialog.getText(self, "Add Subtab", "Subtab name:")
        if ok and text:
            new_subtab = SubTab(text, [])
            tab_widget.addTab(new_subtab, text)
            self.subtabs[index][text] = new_subtab

    def delete_subtab(self):
        index = self.tabs.currentIndex()
        if index == -1:
            QtWidgets.QMessageBox.warning(self, "Warning", "No main tab open to delete a subtab.")
            return
        tab_widget = self.tabs.widget(index)
        if not isinstance(tab_widget, QtWidgets.QTabWidget):
            QtWidgets.QMessageBox.warning(self, "Warning", "Current tab does not support subtabs.")
            return
        subtab_index = tab_widget.currentIndex()
        if subtab_index == -1:
            QtWidgets.QMessageBox.warning(self, "Warning", "No subtab selected.")
            return
        subtab_name = tab_widget.tabText(subtab_index)
        tab_widget.removeTab(subtab_index)
        if subtab_name in self.subtabs[index]:
            del self.subtabs[index][subtab_name]

    def rename_subtab(self):
        index = self.tabs.currentIndex()
        if index == -1:
            QtWidgets.QMessageBox.warning(self, "Warning", "No main tab open to rename a subtab.")
            return
        tab_widget = self.tabs.widget(index)
        if not isinstance(tab_widget, QtWidgets.QTabWidget):
            QtWidgets.QMessageBox.warning(self, "Warning", "Current tab does not support subtabs.")
            return
        subtab_index = tab_widget.currentIndex()
        if subtab_index == -1:
            QtWidgets.QMessageBox.warning(self, "Warning", "No subtab selected.")
            return
        old_name = tab_widget.tabText(subtab_index)
        text, ok = QtWidgets.QInputDialog.getText(self, "Rename Subtab", f"Old name: {old_name}\nNew name:")
        if ok and text:
            tab_widget.setTabText(subtab_index, text)
            self.subtabs[self.tabs.currentIndex()][text] = self.subtabs[self.tabs.currentIndex()].pop(old_name)

    def copy_row(self):
        subtab = self.current_subtab()
        if not subtab:
            return
        selected = subtab.table.selectionModel().selectedRows()
        if not selected:
            return
        row = selected[0].row()
        self.clipboard_data = []
        for col in range(subtab.model.columnCount()):
            item = subtab.model.item(row, col)
            self.clipboard_data.append(item.text() if item else "")

    def paste_row(self):
        subtab = self.current_subtab()
        if not subtab:
            return
        if not hasattr(self, 'clipboard_data') or not self.clipboard_data:
            return
        row_position = subtab.model.rowCount()
        subtab.model.insertRow(row_position)
        for col, text in enumerate(self.clipboard_data):
            subtab.model.setItem(row_position, col, QtGui.QStandardItem(text))

    def close_tab(self, index):
        if index in self.file_paths:
            del self.file_paths[index]
        if index in self.subtabs:
            del self.subtabs[index]
        self.tabs.removeTab(index)

    def show_about(self):
        dlg = QtWidgets.QDialog(self)
        dlg.setWindowTitle(f"About {APP_NAME}")
        dlg.resize(400, 300)
        layout = QtWidgets.QVBoxLayout(dlg)

        logo_label = QtWidgets.QLabel()
        pix = QtGui.QPixmap(MEDIA_FILES["logo"])
        if not pix.isNull():
            logo_label.setPixmap(pix.scaled(150, 150, QtCore.Qt.AspectRatioMode.KeepAspectRatio, QtCore.Qt.TransformationMode.SmoothTransformation))
        logo_label.setAlignment(QtCore.Qt.AlignmentFlag.AlignCenter)
        layout.addWidget(logo_label)

        text = QtWidgets.QLabel(f"{APP_NAME} — JSON/CSV/Excel редактор с вкладками, фильтрацией и печатью.")
        text.setWordWrap(True)
        text.setAlignment(QtCore.Qt.AlignmentFlag.AlignCenter)
        layout.addWidget(text)

        btn = QtWidgets.QPushButton("Close")
        btn.clicked.connect(dlg.close)
        layout.addWidget(btn)

        dlg.exec()

def main():
    app = QtWidgets.QApplication(sys.argv)
    app.setStyle("Fusion")

    palette = QtGui.QPalette()
    palette.setColor(QtGui.QPalette.ColorRole.Window, QtGui.QColor("#FFFFFF"))
    palette.setColor(QtGui.QPalette.ColorRole.WindowText, QtGui.QColor(APP_COLORS["black"]))
    palette.setColor(QtGui.QPalette.ColorRole.Base, QtGui.QColor("#FFFFFF"))
    palette.setColor(QtGui.QPalette.ColorRole.AlternateBase, QtGui.QColor("#f0f0f0"))
    palette.setColor(QtGui.QPalette.ColorRole.ToolTipBase, QtGui.QColor(APP_COLORS["black"]))
    palette.setColor(QtGui.QPalette.ColorRole.ToolTipText, QtGui.QColor(APP_COLORS["black"]))
    palette.setColor(QtGui.QPalette.ColorRole.Text, QtGui.QColor(APP_COLORS["black"]))
    palette.setColor(QtGui.QPalette.ColorRole.Button, QtGui.QColor("#FFFFFF"))
    palette.setColor(QtGui.QPalette.ColorRole.ButtonText, QtGui.QColor(APP_COLORS["accent"]))
    palette.setColor(QtGui.QPalette.ColorRole.Highlight, QtGui.QColor(APP_COLORS["accent"]))
    palette.setColor(QtGui.QPalette.ColorRole.HighlightedText, QtGui.QColor("#FFFFFF"))
    app.setPalette(palette)

    window = JsonEditor()
    window.show()
    sys.exit(app.exec())

if __name__ == "__main__":
    main()