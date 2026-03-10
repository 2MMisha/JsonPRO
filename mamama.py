import sys
import json
import os
import pandas as pd
from PyQt6 import QtWidgets, QtGui, QtCore, QtPrintSupport

APP_NAME = "JSON Pro"
APP_COLORS = {
    "accent": "#ea8c2f",
    "gray": "#545454",
    "black": "#000000",
    "white": "#FFFFFF"
}
SUPPORTED_EXTENSIONS = ["*.json", "*.csv", "*.xlsx"]

class JsonEditorSubTab(QtWidgets.QWidget):
    def __init__(self, title, data):
        super().__init__()
        self.title = title
        self.data = data
        self.clipboard_data = []

        self.layout = QtWidgets.QVBoxLayout(self)
        self.search = QtWidgets.QLineEdit()
        self.search.setPlaceholderText(f"Search in {title}...")
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
        self.table.setEditTriggers(QtWidgets.QAbstractItemView.EditTrigger.DoubleClicked)
        self.table.setDragDropOverwriteMode(False)
        self.table.horizontalHeader().setSectionsMovable(True)
        self.table.horizontalHeader().setStretchLastSection(True)
        self.table.setCursor(QtGui.QCursor(QtCore.Qt.CursorShape.PointingHandCursor))

        self.layout.addWidget(self.table)

        self.search.textChanged.connect(self.proxy.setFilterFixedString)
        self.load_data()

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
                    try:
                        item[h] = json.loads(val)
                    except:
                        item[h] = val
                result.append(item)
        return result

    def to_dataframe(self):
        data = self.collect_data()
        return pd.DataFrame(data)

    def add_row(self):
        cols = self.model.columnCount()
        items = [QtGui.QStandardItem("-") for _ in range(cols)]
        for item in items:
            item.setEditable(True)
        self.model.appendRow(items)

    def delete_selected_row(self):
        indexes = self.table.selectionModel().selectedRows()
        for index in sorted(indexes, reverse=True):
            self.model.removeRow(index.row())

    def copy_selected(self):
        indexes = self.table.selectionModel().selectedRows()
        if indexes:
            row = indexes[0].row()
            self.clipboard_data = [self.model.item(row, col).text() for col in range(self.model.columnCount())]

    def paste_row(self):
        if not self.clipboard_data:
            return
        items = [QtGui.QStandardItem(text) for text in self.clipboard_data]
        for item in items:
            item.setEditable(True)
        self.model.appendRow(items)

class JsonEditorTab(QtWidgets.QTabWidget):
    def __init__(self, filename, content):
        super().__init__()
        self.filename = filename
        self.content = content
        self.subtabs = {}

        if isinstance(content, dict):
            for key, value in content.items():
                self.add_subtab(key, value)
        elif isinstance(content, list):
            self.add_subtab("root", content)

    def add_subtab(self, key, value):
        tab = JsonEditorSubTab(key, value)
        self.subtabs[key] = tab
        self.addTab(tab, key)

    def current_subtab(self):
        return self.currentWidget()

    def collect_all_data(self):
        result = {}
        for key, subtab in self.subtabs.items():
            result[key] = subtab.collect_data()
        return result

    def export_to_excel(self, path):
        with pd.ExcelWriter(path) as writer:
            for key, subtab in self.subtabs.items():
                df = subtab.to_dataframe()
                df.to_excel(writer, sheet_name=key, index=False)

    def export_to_csv(self, folder_path):
        for key, subtab in self.subtabs.items():
            df = subtab.to_dataframe()
            df.to_csv(os.path.join(folder_path, f"{key}.csv"), index=False)

    def print_preview(self):
        subtab = self.current_subtab()
        printer = QtPrintSupport.QPrinter()
        dialog = QtPrintSupport.QPrintDialog(printer)
        if dialog.exec():
            self.print_table(printer, subtab)

    def print_table(self, printer, subtab):
        doc = QtGui.QTextDocument()
        html = f"<h2 style='text-align:center;'>{os.path.basename(self.filename).upper()}</h2><table border='1' cellspacing='0' cellpadding='4'>"
        model = subtab.model
        headers = [model.headerData(i, QtCore.Qt.Orientation.Horizontal) for i in range(model.columnCount())]
        html += "<tr>" + "".join(f"<th>{h}</th>" for h in headers) + "</tr>"
        for row in range(model.rowCount()):
            html += "<tr>"
            for col in range(model.columnCount()):
                val = model.item(row, col).text()
                html += f"<td>{val}</td>"
            html += "</tr>"
        html += "</table><br><div style='text-align:center;'><img src='logo.png' height='64'/></div>"
        doc.setHtml(html)
        doc.print(printer)

class MainWindow(QtWidgets.QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle(APP_NAME)
        self.setWindowIcon(QtGui.QIcon("app_icon.ico"))
        self.resize(1280, 800)

        self.tabs = QtWidgets.QTabWidget()
        self.tabs.setTabsClosable(True)
        self.tabs.tabCloseRequested.connect(self.tabs.removeTab)
        self.setCentralWidget(self.tabs)

        self.init_menu()
        self.statusBar().showMessage("Welcome to JSON Pro")

    def init_menu(self):
        menubar = self.menuBar()

        file_menu = menubar.addMenu("File")
        file_menu.addAction("New", self.new_file)
        file_menu.addAction("Open", self.open_file)
        file_menu.addAction("Save", self.save_file)
        file_menu.addAction("Save As", self.save_as)
        file_menu.addAction("Export to Excel", self.export_excel)
        file_menu.addAction("Export to CSV", self.export_csv)
        file_menu.addSeparator()
        file_menu.addAction("Exit", self.close)

        edit_menu = menubar.addMenu("Edit")
        edit_menu.addAction("Add Row", self.add_row)
        edit_menu.addAction("Delete Row", self.delete_row)
        edit_menu.addAction("Copy Row", self.copy_row)
        edit_menu.addAction("Paste Row", self.paste_row)

        view_menu = menubar.addMenu("View")
        view_menu.addAction("Print Preview", self.print_current_tab)

        help_menu = menubar.addMenu("Help")
        about_action = QtGui.QAction("About", self)
        about_action.triggered.connect(self.show_about)
        help_menu.addAction(about_action)

    def show_about(self):
        msg = QtWidgets.QMessageBox(self)
        msg.setWindowTitle("About JSON Pro")
        msg.setText("<h2>JSON Pro</h2><p>Smart table editor for JSON / CSV / Excel</p>")
        msg.setIconPixmap(QtGui.QPixmap("logo.png").scaled(128, 128))
        msg.exec()

    def current_tab(self):
        return self.tabs.currentWidget()

    def current_subtab(self):
        tab = self.current_tab()
        return tab.current_subtab() if tab else None

    def new_file(self):
        tab = JsonEditorTab("untitled.json", {})
        self.tabs.addTab(tab, "Untitled")
        self.tabs.setCurrentWidget(tab)

    def open_file(self):
        path, _ = QtWidgets.QFileDialog.getOpenFileName(self, "Open File", "", "Files (*.json *.csv *.xlsx)")
        if not path:
            return
        ext = os.path.splitext(path)[1].lower()
        try:
            if ext == ".json":
                with open(path, 'r', encoding='utf-8') as f:
                    content = json.load(f)
            elif ext == ".csv":
                df = pd.read_csv(path)
                content = {"sheet": df.to_dict(orient='records')}
            elif ext == ".xlsx":
                xls = pd.read_excel(path, sheet_name=None)
                content = {k: df.to_dict(orient='records') for k, df in xls.items()}
            else:
                raise ValueError("Unsupported format")
            tab = JsonEditorTab(path, content)
            self.tabs.addTab(tab, os.path.basename(path))
            self.tabs.setCurrentWidget(tab)
        except Exception as e:
            QtWidgets.QMessageBox.critical(self, "Error", str(e))

    def save_file(self):
        tab = self.current_tab()
        if not tab:
            return
        try:
            with open(tab.filename, 'w', encoding='utf-8') as f:
                json.dump(tab.collect_all_data(), f, indent=2, ensure_ascii=False)
            self.statusBar().showMessage(f"Saved {tab.filename}", 2000)
        except:
            self.save_as()

    def save_as(self):
        tab = self.current_tab()
        if not tab:
            return
        path, _ = QtWidgets.QFileDialog.getSaveFileName(self, "Save As", "", "JSON Files (*.json)")
        if path:
            tab.filename = path
            self.save_file()
            self.tabs.setTabText(self.tabs.currentIndex(), os.path.basename(path))

    def export_excel(self):
        tab = self.current_tab()
        if not tab:
            return
        path, _ = QtWidgets.QFileDialog.getSaveFileName(self, "Export to Excel", "", "Excel Files (*.xlsx)")
        if path:
            tab.export_to_excel(path)

    def export_csv(self):
        tab = self.current_tab()
        if not tab:
            return
        folder = QtWidgets.QFileDialog.getExistingDirectory(self, "Select Folder to Export CSV")
        if folder:
            tab.export_to_csv(folder)

    def print_current_tab(self):
        tab = self.current_tab()
        if tab:
            tab.print_preview()

    def add_row(self):
        subtab = self.current_subtab()
        if subtab:
            subtab.add_row()

    def delete_row(self):
        subtab = self.current_subtab()
        if subtab:
            subtab.delete_selected_row()

    def copy_row(self):
        subtab = self.current_subtab()
        if subtab:
            subtab.copy_selected()

    def paste_row(self):
        subtab = self.current_subtab()
        if subtab:
            subtab.paste_row()

if __name__ == "__main__":
    app = QtWidgets.QApplication(sys.argv)
    app.setStyle("Fusion")
    app.setApplicationName(APP_NAME)
    window = MainWindow()
    window.show()
    sys.exit(app.exec())
