from pathlib import Path
import sys

from PySide6.QtCore import Qt
from PySide6.QtWidgets import (
    QApplication, QMainWindow, QPushButton, QDialog,
    QVBoxLayout, QHBoxLayout, QLabel, QLineEdit, QDialogButtonBox, QFileDialog
)

import PySide6.QtGui as QG

from MultiRangeDopplerPlotter.add_plot_dialog_ui import *
import numpy as np

class AddPlotDialog(QDialog, Ui_Dialog):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setupUi(self)
        self.applyBtn.clicked.connect(self.accept)
        self.cancelBtn.clicked.connect(self.reject)

        self.indexSlider.valueChanged.connect(self.index_changed)
        self.indexLEdit.textChanged.connect(self.index_changed_text)
        self.valueLEdit.textChanged.connect(self.value_changed_text)
        self.addPlotBtn.clicked.connect(self.add_current_index)
        self.removePlotBtn.clicked.connect(self.remove_selected_items)

        self.valueLEdit.setReadOnly(True)

        self.addPlotBtn.setShortcut(QG.QKeySequence(Qt.Key.Key_Space))

        self.removePlotBtn.setText("&Remove Selected")
        self.applyBtn.setText("&Apply")
        self.cancelBtn.setText("&Cancel")
        
        self.name_to_item_and_index: dict[str, (QListWidgetItem, int)] = {}
    
    def add_item_to_list(self, index: int):
        if index in self.name_to_item_and_index.values():
            return

        self.currPlotList.addItem(f"{self.curr_dim_name} = {self.curr_dim_values[index]:.4f} {self.curr_dim_unit}")
        newitem = self.currPlotList.item(self.currPlotList.count() - 1)
        self.name_to_item_and_index[newitem.text()] = (newitem, index)
    
    def initialize(self, dim_name: str, dim_unit: str, dim_values: list[float], selected_dim_indices: list[int], col_per_row: int):
        self.curr_dim_name = dim_name
        self.curr_dim_unit = dim_unit
        self.curr_dim_values: list[float] = dim_values.copy()
        self.chosen_dim_indices: list[int] = sorted(selected_dim_indices.copy())

        self.indexSlider.setMinimum(0)
        self.indexSlider.setMaximum(len(self.curr_dim_values) - 1)

        self.addPlotInfoLabel.setText(f"Make a list of {self.curr_dim_name} values to make plots for")
        self.valueUnitLabel.setText(f"({self.curr_dim_unit})")

        self.indexLEdit.setValidator(QG.QIntValidator(0, len(self.curr_dim_values) - 1, self))
        self.valueLEdit.setValidator(QG.QDoubleValidator(bottom=self.curr_dim_values[0], top=self.curr_dim_values[-1]))

        self.indexLEdit.setText("0")
        self.valueLEdit.setText(f"{self.curr_dim_values[0]:.4f}")

        self.gridColPerRowLEdit.setValidator(QG.QIntValidator(1, 15, self))
        self.gridColPerRowLEdit.setText(str(col_per_row))

        self.name_to_item_and_index.clear()
        self.currPlotList.clear()
        for idx in self.chosen_dim_indices:
            self.add_item_to_list(idx)
    
    def remove_selected_items(self):
        for item in self.currPlotList.selectedItems():
            if item.text() in self.name_to_item_and_index:
                _, idx = self.name_to_item_and_index[item.text()]
                if idx in self.chosen_dim_indices:
                    self.chosen_dim_indices.remove(idx)
                self.currPlotList.takeItem(self.currPlotList.row(item))
                del self.name_to_item_and_index[item.text()]
        
        # select next item if possible
        if self.currPlotList.count() > 0:
            self.currPlotList.setCurrentRow(0)
    
    def add_current_index(self):
        curr_idx = self.indexSlider.value()
        if curr_idx not in self.chosen_dim_indices:
            self.chosen_dim_indices.append(curr_idx)
            self.chosen_dim_indices.sort()
            # clear all and re-add
            self.currPlotList.clear()
            for idx in self.chosen_dim_indices:
                self.add_item_to_list(idx)
    
    def index_changed(self, value: int):
        self.indexLEdit.setText(str(value))
        self.valueLEdit.setText(f"{self.curr_dim_values[value]:.4f}")
        self.indexSlider.setValue(value)
    
    def index_changed_text(self, text: str):
        if text == "":
            return
        val = int(text)
        self.indexSlider.setValue(val)
    
    def value_changed_text(self, text: str):
        if text == "":
            return
        val = float(text)
        closest_idx = (np.abs(np.array(self.curr_dim_values) - val)).argmin()
        self.indexSlider.setValue(closest_idx)