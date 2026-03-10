# JsonPRO
Json as sheetspreads editor

# JSON Pro - Spreadsheet-Style JSON Editor

A powerful desktop application that transforms JSON data into an intuitive spreadsheet interface. Edit, manage, and visualize JSON, CSV, and Excel files just like you would in Google Sheets or Excel, but with native JSON support.

![JSON Pro Screenshot](screenshot.png)

## Why JSON Pro?

Traditional JSON editors show you raw text. JSON Pro shows you **data**. Just like a spreadsheet program, you get:

- **Cells you can edit** - Double-click any value to change it
- **Rows and columns** - Add, delete, and rearrange like in Excel
- **Multiple sheets** - One file can have multiple data tables (subtabs)
- **Real-time filtering** - Search across all columns instantly
- **Drag-and-drop columns** - Reorganize your data visually

## Features

### 📊 Spreadsheet Interface
- **Editable Grid** - Double-click any cell to edit values
- **Row Operations** - Add, delete, copy, and paste entire rows
- **Column Management** - Add, delete, rename, and reorder columns
- **Sortable Headers** - Click any column header to sort data
- **Resizable Columns** - Drag column borders to adjust width
- **Column State Memory** - Remembers your column layout

### 📁 Multi-Format Support
- **JSON** - Opens any JSON structure (objects, arrays, nested data)
- **CSV** - Import and export with full editing capabilities
- **Excel** - Opens .xlsx/.xls files with multiple sheets as separate tabs

### 🗂️ Hierarchical Data View
- **Objects become rows** - JSON objects transform into table rows
- **Arrays become columns** - Array values spread across columns
- **Nested structures** - Complex JSON automatically flattened
- **Multiple sheets** - JSON objects with multiple keys become separate sheets

### 🔍 Smart Features
- **Live Search** - Filter data as you type
- **Copy/Paste Rows** - Duplicate rows with Ctrl+C/Ctrl+V
- **Column Renaming** - Change headers without affecting original data
- **Print Ready** - Print your data with custom headers and logo

## Installation

### Quick Install
```bash
# Clone the repository
git clone https://github.com/yourusername/json-pro.git
cd json-pro

# Install dependencies
pip install PyQt6 pandas openpyxl

# Run the application
python json_pro.py
```

### Requirements
```
PyQt6>=6.4.0      # GUI framework
pandas>=1.5.0     # Data manipulation
openpyxl>=3.0.0   # Excel support
```

## How It Works

### Opening Files
- **JSON** - Opens as spreadsheet(s). Each top-level key becomes a sheet tab
- **CSV** - Opens as a single sheet with columns
- **Excel** - Opens with all sheets preserved as separate tabs

### Editing Data
Just like a spreadsheet:
1. **Click a cell** to select it
2. **Double-click** to edit the value
3. **Press Enter** to save changes
4. **Use shortcuts** for quick operations

### Data Structure Examples

**Simple Array of Objects** → Single sheet with rows
```json
[
  {"name": "John", "age": 30},
  {"name": "Jane", "age": 25}
]
```

**Nested Objects** → Multiple sheets
```json
{
  "users": [...],
  "products": [...],
  "orders": [...]
}
```

## Keyboard Shortcuts

| Shortcut | Action | Like in Excel |
|----------|--------|---------------|
| Ctrl+N | New File | New workbook |
| Ctrl+O | Open File | Open workbook |
| Ctrl+S | Save | Save |
| Ctrl+P | Print | Print |
| Ctrl+C | Copy Row | Copy selected row |
| Ctrl+V | Paste Row | Paste as new row |
| Ctrl+Shift+A | Add Row | Insert row |
| Ctrl+Shift+D | Delete Row | Delete row |
| Ctrl+Alt+A | Add Column | Insert column |
| Ctrl+Alt+D | Delete Column | Delete column |
| Ctrl+Alt+R | Rename Column | Rename header |
| Ctrl+T | Add Subtab | New sheet |
| Ctrl+W | Delete Subtab | Delete sheet |
| Ctrl+R | Rename Subtab | Rename sheet |

## Use Cases

### 📱 Data Migration
Convert between JSON, CSV, and Excel formats without losing structure. Edit data in the familiar spreadsheet view before exporting.

### 📊 API Response Analysis
Open API JSON responses directly. Filter, sort, and explore data without writing code.

### 📝 Configuration Management
Edit complex JSON configuration files with confidence. See all options in a structured table format.

### 📈 Data Cleaning
Use the spreadsheet interface to clean and normalize data before importing into databases or other systems.

## Screenshots

*(Add screenshots showing:)*
- Main interface with multiple tabs
- Inline cell editing
- Search/filter functionality
- Print preview
- Multiple sheets view

## File Structure

```
json-pro/
├── json_pro.py          # Main application (single file!)
├── logo.png             # Application logo
├── app_icon.ico         # Window icon
├── jsonicon.png         # JSON file association icon
└── 2.png                # Secondary icon
```

## Tips & Tricks

- **Quick Filter** - Start typing in search box to filter rows instantly
- **Column Reorder** - Drag column headers to rearrange
- **Copy Multiple** - Select a row, copy, then paste to duplicate
- **Batch Edit** - Add new columns with default "-" values
- **Export Anywhere** - Save as JSON, CSV, or Excel from any format

## Contributing

Contributions are welcome! Whether it's:
- Bug fixes
- New features
- Documentation improvements
- Translation support

## License

MIT License - Use it freely in personal and commercial projects.

## Why "JSON Pro"?

Because it's the professional way to handle JSON data. Instead of wrestling with curly braces and brackets, you get a clean, intuitive spreadsheet interface that anyone can use. Perfect for developers, data analysts, and business users alike.

---

**JSON Pro - JSON editing, reimagined as spreadsheets.**
