DARK_STYLE = """ 
QWidget {
    background-color: #1e1e1e;
    color: #ffffff;
    font-size: 14px;
}

QLabel {
    font-size: 16px;
    font-weight: bold;
}

QPushButton {
    background-color: #3a86ff;
    color: white;
    border-radius: 8px;
    padding: 8px;
    font-weight: bold;
}

QPushButton:hover {
    background-color: #5390ff;
}

QPushButton:pressed {
    background-color: #2a75f3;
}

QTableWidget {
    background-color: #2b2b2b;
    border: 1px solid #444;
    gridline-color: #444;
    selection-background-color: #3a86ff;
}

QHeaderView::section {
    background-color: #333333;
    color: white;
    padding: 5px;
    border: 1px solid #444;
    font-weight: bold;
}

QLineEdit,
QTextEdit,
QComboBox,
QTimeEdit {
    background-color: #2b2b2b;
    border: 1px solid #555;
    border-radius: 5px;
    padding: 5px;
    color: white;
}

QCheckBox {
    spacing: 10px;
}

"""