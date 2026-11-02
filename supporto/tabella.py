"""Modulo helper per configurare QTableWidget con lo stile esatto dei mockup."""
from PyQt5.QtWidgets import QTableWidget, QHeaderView, QAbstractItemView, QTableWidgetItem
from PyQt5.QtCore import Qt


def crea_tabella(colonne: list[str], parent=None) -> QTableWidget:
    """Crea una QTableWidget configurata come nel mockup (selezione riga intera, colonne proporzionate)."""
    tabella = QTableWidget(parent)
    tabella.setColumnCount(len(colonne))
    tabella.setHorizontalHeaderLabels(colonne)
    tabella.setSelectionBehavior(QAbstractItemView.SelectRows)
    tabella.setSelectionMode(QAbstractItemView.SingleSelection)
    tabella.setEditTriggers(QAbstractItemView.NoEditTriggers)

    v_header = tabella.verticalHeader()
    if v_header is not None:
        v_header.setVisible(False)

    tabella.setShowGrid(True)

    h_header = tabella.horizontalHeader()
    if h_header is not None:
        h_header.setStretchLastSection(True)
        h_header.setSectionResizeMode(QHeaderView.Stretch)

    return tabella


def popola_riga(tabella: QTableWidget, riga_idx: int, valori: list[str]) -> None:
    """Inserisce una riga di celle non modificabili con testo centrato verticalmente."""
    align_center_left = 0x0080 | 0x0001  # Qt.AlignVCenter (128) | Qt.AlignLeft (1)
    for col_idx, val in enumerate(valori):
        item = QTableWidgetItem(val)
        item.setTextAlignment(align_center_left)
        tabella.setItem(riga_idx, col_idx, item)
