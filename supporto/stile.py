"""Stili e tema dell'applicazione Croce Rossa Italiana.
Riproduce l'estetica esatta dei mockup del PDF (pagine 4-14):
- Sfondo pulito (#FFFFFF / #FAFAFA)
- Titoli e intestazioni chiari con barra di stato / indicatori
- Pulsanti con contorno rosso / bordi arrotondati, testo rosso scuro (#C8102E / #B82832), hover con sfondo tenue
- Campi di input (QLineEdit, QDateEdit, QTimeEdit, QComboBox) con bordo sottile grigio (#B0B0B0), angoli arrotondati e padding
- Tabelle e liste alternate con intestazioni chiare e righe evidenziate
- Finestre con spaziatura e gerarchia ordinata
"""

FOGLIO_DI_STILE = """
/* Reset generale */
QWidget {
    font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, "Helvetica Neue", Arial, sans-serif;
    font-size: 13px;
    color: #2D3748;
    background-color: #FFFFFF;
}

/* Finestra principale e dialog */
QMainWindow, QDialog, QWidget[isWindow="true"] {
    background-color: #F8F9FA;
}

/* Titoli ed etichette */
QLabel {
    background: transparent;
}

QLabel[heading="true"] {
    font-size: 16px;
    font-weight: bold;
    color: #C8102E;
    padding-bottom: 4px;
}

QLabel[section="true"] {
    font-size: 14px;
    font-weight: 600;
    color: #1A202C;
    margin-top: 6px;
    margin-bottom: 2px;
}

/* Campi testo */
QLineEdit, QDateEdit, QTimeEdit, QComboBox {
    border: 1px solid #CBD5E0;
    border-radius: 4px;
    padding: 5px 8px;
    background-color: #FFFFFF;
    color: #2D3748;
    selection-background-color: #FED7D7;
    selection-color: #9B2C2C;
    min-height: 22px;
}

QLineEdit:focus, QDateEdit:focus, QTimeEdit:focus, QComboBox:focus {
    border: 1px solid #E53E3E;
    background-color: #FFFDFD;
}

QLineEdit:disabled, QComboBox:disabled {
    background-color: #EDF2F7;
    color: #A0AEC0;
    border-color: #E2E8F0;
}

/* ComboBox */
QComboBox::drop-down {
    subcontrol-origin: padding;
    subcontrol-position: top right;
    width: 24px;
    border-left: 1px solid #CBD5E0;
    border-top-right-radius: 4px;
    border-bottom-right-radius: 4px;
}

QComboBox QAbstractItemView {
    border: 1px solid #CBD5E0;
    background-color: #FFFFFF;
    selection-background-color: #FED7D7;
    selection-color: #9B2C2C;
    padding: 2px;
}

/* Pulsanti stile mockup (rettangolari arrotondati, bordo rosso/rosa tenue, testo rosso) */
QPushButton {
    border: 1.5px solid #E53E3E;
    border-radius: 6px;
    background-color: #FFF5F5;
    color: #C53030;
    font-weight: 600;
    padding: 6px 14px;
    min-height: 20px;
}

QPushButton:hover {
    background-color: #FED7D7;
    border-color: #C53030;
    color: #9B2C2C;
}

QPushButton:pressed {
    background-color: #FEB2B2;
    border-color: #9B2C2C;
}

QPushButton:disabled {
    border: 1.5px solid #E2E8F0;
    background-color: #F7FAFC;
    color: #CBD5E0;
}

/* Liste e visualizzazioni tabellari */
QListView, QListWidget, QTableView, QTableWidget {
    border: 1.5px solid #2D3748;
    background-color: #FFFFFF;
    gridline-color: #CBD5E0;
    font-size: 13px;
    color: #2D3748;
    selection-background-color: #FED7D7;
    selection-color: #742A2A;
}

QHeaderView::section {
    background-color: #D9D9D9;
    color: #1A202C;
    font-weight: bold;
    padding: 6px 8px;
    border: 1px solid #718096;
    border-top: none;
    font-size: 13px;
}

QTableWidget::item, QTableView::item {
    padding: 6px 8px;
    border-bottom: 1px solid #EDF2F7;
}

QTableWidget::item:selected, QTableView::item:selected {
    background-color: #FED7D7;
    color: #742A2A;
    font-weight: 500;
}

QListView::item, QListWidget::item {
    padding: 6px 8px;
    border-bottom: 1px solid #EDF2F7;
    border-radius: 2px;
}

QListView::item:hover, QListWidget::item:hover, QTableWidget::item:hover, QTableView::item:hover {
    background-color: #FFF5F5;
}

QListView::item:selected, QListWidget::item:selected {
    background-color: #FED7D7;
    color: #742A2A;
    font-weight: 500;
}

/* CheckBox */
QCheckBox {
    spacing: 6px;
}

QCheckBox::indicator {
    width: 16px;
    height: 16px;
    border: 1px solid #CBD5E0;
    border-radius: 3px;
    background: #FFFFFF;
}

QCheckBox::indicator:checked {
    background-color: #E53E3E;
    border-color: #C53030;
}

/* ScrollBar */
QScrollBar:vertical {
    border: none;
    background: #EDF2F7;
    width: 8px;
    margin: 0px;
    border-radius: 4px;
}

QScrollBar::handle:vertical {
    background: #CBD5E0;
    min-height: 20px;
    border-radius: 4px;
}

QScrollBar::handle:vertical:hover {
    background: #A0AEC0;
}

QLabel[error_banner="true"], .ErrorBanner {
    background-color: #FED7D7;
    color: #9B2C2C;
    border: 1px solid #FEB2B2;
    border-radius: 4px;
    padding: 8px 12px;
    font-size: 13px;
    font-weight: 500;
}
"""


def applica_tema(app):
    """Applica il tema grafico all'applicazione PyQt5."""
    app.setStyleSheet(FOGLIO_DI_STILE)


def crea_label_errore(parent=None) -> "QLabel":
    """Crea una QLabel stilizzata come banner di errore rosso, inizialmente nascosta."""
    from PyQt5.QtWidgets import QLabel
    lbl = QLabel(parent)
    lbl.setProperty("error_banner", "true")
    lbl.setWordWrap(True)
    lbl.hide()
    return lbl


def mostra_errore(label, testo: str) -> None:
    """Mostra un messaggio d'errore nel banner rosso."""
    if label is not None:
        label.setText(testo)
        label.show()


def nascondi_errore(label) -> None:
    """Nasconde il banner rosso di errore."""
    if label is not None:
        label.setText("")
        label.hide()

