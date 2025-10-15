# -*- coding: utf-8 -*-

################################################################################
## Form generated from reading UI file 'add_plot_dialog_uiRTPYZD.ui'
##
## Created by: Qt User Interface Compiler version 6.9.2
##
## WARNING! All changes made in this file will be lost when recompiling UI file!
################################################################################

from PySide6.QtCore import (QCoreApplication, QDate, QDateTime, QLocale,
    QMetaObject, QObject, QPoint, QRect,
    QSize, QTime, QUrl, Qt)
from PySide6.QtGui import (QBrush, QColor, QConicalGradient, QCursor,
    QFont, QFontDatabase, QGradient, QIcon,
    QImage, QKeySequence, QLinearGradient, QPainter,
    QPalette, QPixmap, QRadialGradient, QTransform)
from PySide6.QtWidgets import (QAbstractItemView, QApplication, QDialog, QGroupBox,
    QHBoxLayout, QLabel, QLineEdit, QListWidget,
    QListWidgetItem, QPushButton, QSizePolicy, QSlider,
    QSpacerItem, QVBoxLayout, QWidget)

class Ui_Dialog(object):
    def setupUi(self, Dialog):
        if not Dialog.objectName():
            Dialog.setObjectName(u"Dialog")
        Dialog.resize(497, 408)
        self.currPlotList = QListWidget(Dialog)
        self.currPlotList.setObjectName(u"currPlotList")
        self.currPlotList.setGeometry(QRect(0, 210, 161, 192))
        self.currPlotList.setSelectionMode(QAbstractItemView.SelectionMode.ExtendedSelection)
        self.applyBtn = QPushButton(Dialog)
        self.applyBtn.setObjectName(u"applyBtn")
        self.applyBtn.setGeometry(QRect(170, 370, 91, 31))
        self.cancelBtn = QPushButton(Dialog)
        self.cancelBtn.setObjectName(u"cancelBtn")
        self.cancelBtn.setGeometry(QRect(270, 370, 91, 31))
        self.currPlotLabel = QLabel(Dialog)
        self.currPlotLabel.setObjectName(u"currPlotLabel")
        self.currPlotLabel.setGeometry(QRect(10, 190, 121, 16))
        self.removePlotBtn = QPushButton(Dialog)
        self.removePlotBtn.setObjectName(u"removePlotBtn")
        self.removePlotBtn.setGeometry(QRect(170, 210, 101, 24))
        self.addPlotGroupBox = QGroupBox(Dialog)
        self.addPlotGroupBox.setObjectName(u"addPlotGroupBox")
        self.addPlotGroupBox.setGeometry(QRect(0, 0, 481, 181))
        self.addPlotInfoLabel = QLabel(self.addPlotGroupBox)
        self.addPlotInfoLabel.setObjectName(u"addPlotInfoLabel")
        self.addPlotInfoLabel.setGeometry(QRect(10, 20, 261, 41))
        self.indexValFirstVw = QWidget(self.addPlotGroupBox)
        self.indexValFirstVw.setObjectName(u"indexValFirstVw")
        self.indexValFirstVw.setGeometry(QRect(10, 100, 251, 71))
        self.verticalLayout = QVBoxLayout(self.indexValFirstVw)
        self.verticalLayout.setSpacing(2)
        self.verticalLayout.setObjectName(u"verticalLayout")
        self.verticalLayout.setContentsMargins(2, 2, 2, 2)
        self.indexLineHw = QWidget(self.indexValFirstVw)
        self.indexLineHw.setObjectName(u"indexLineHw")
        self.horizontalLayout = QHBoxLayout(self.indexLineHw)
        self.horizontalLayout.setSpacing(2)
        self.horizontalLayout.setObjectName(u"horizontalLayout")
        self.horizontalLayout.setContentsMargins(-1, 2, -1, 2)
        self.indexLabel = QLabel(self.indexLineHw)
        self.indexLabel.setObjectName(u"indexLabel")
        self.indexLabel.setMinimumSize(QSize(38, 0))
        self.indexLabel.setMaximumSize(QSize(10000, 16777215))

        self.horizontalLayout.addWidget(self.indexLabel)

        self.indexLEdit = QLineEdit(self.indexLineHw)
        self.indexLEdit.setObjectName(u"indexLEdit")
        self.indexLEdit.setMaximumSize(QSize(80, 16777215))

        self.horizontalLayout.addWidget(self.indexLEdit)

        self.horizontalSpacer = QSpacerItem(40, 20, QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Minimum)

        self.horizontalLayout.addItem(self.horizontalSpacer)


        self.verticalLayout.addWidget(self.indexLineHw)

        self.valueLineHw = QWidget(self.indexValFirstVw)
        self.valueLineHw.setObjectName(u"valueLineHw")
        self.horizontalLayout_2 = QHBoxLayout(self.valueLineHw)
        self.horizontalLayout_2.setSpacing(2)
        self.horizontalLayout_2.setObjectName(u"horizontalLayout_2")
        self.horizontalLayout_2.setContentsMargins(-1, 2, -1, 2)
        self.label = QLabel(self.valueLineHw)
        self.label.setObjectName(u"label")
        self.label.setMinimumSize(QSize(38, 0))
        self.label.setMaximumSize(QSize(10000, 16777215))

        self.horizontalLayout_2.addWidget(self.label)

        self.valueLEdit = QLineEdit(self.valueLineHw)
        self.valueLEdit.setObjectName(u"valueLEdit")
        self.valueLEdit.setMaximumSize(QSize(100, 16777215))

        self.horizontalLayout_2.addWidget(self.valueLEdit)

        self.valueUnitLabel = QLabel(self.valueLineHw)
        self.valueUnitLabel.setObjectName(u"valueUnitLabel")

        self.horizontalLayout_2.addWidget(self.valueUnitLabel)

        self.horizontalSpacer_2 = QSpacerItem(40, 20, QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Minimum)

        self.horizontalLayout_2.addItem(self.horizontalSpacer_2)


        self.verticalLayout.addWidget(self.valueLineHw)

        self.verticalSpacer = QSpacerItem(20, 40, QSizePolicy.Policy.Minimum, QSizePolicy.Policy.Expanding)

        self.verticalLayout.addItem(self.verticalSpacer)

        self.indexSlider = QSlider(self.addPlotGroupBox)
        self.indexSlider.setObjectName(u"indexSlider")
        self.indexSlider.setGeometry(QRect(10, 70, 461, 22))
        self.indexSlider.setOrientation(Qt.Orientation.Horizontal)
        self.addPlotBtn = QPushButton(self.addPlotGroupBox)
        self.addPlotBtn.setObjectName(u"addPlotBtn")
        self.addPlotBtn.setGeometry(QRect(260, 100, 101, 41))
        self.plotParamGroupBox = QGroupBox(Dialog)
        self.plotParamGroupBox.setObjectName(u"plotParamGroupBox")
        self.plotParamGroupBox.setGeometry(QRect(280, 210, 201, 141))
        self.plotGridVw = QWidget(self.plotParamGroupBox)
        self.plotGridVw.setObjectName(u"plotGridVw")
        self.plotGridVw.setGeometry(QRect(9, 19, 224, 58))
        self.verticalLayout_2 = QVBoxLayout(self.plotGridVw)
        self.verticalLayout_2.setObjectName(u"verticalLayout_2")
        self.gridLabelLeditHw = QWidget(self.plotGridVw)
        self.gridLabelLeditHw.setObjectName(u"gridLabelLeditHw")
        self.horizontalLayout_3 = QHBoxLayout(self.gridLabelLeditHw)
        self.horizontalLayout_3.setObjectName(u"horizontalLayout_3")
        self.label_2 = QLabel(self.gridLabelLeditHw)
        self.label_2.setObjectName(u"label_2")
        self.label_2.setMaximumSize(QSize(120, 16777215))

        self.horizontalLayout_3.addWidget(self.label_2)

        self.gridColPerRowLEdit = QLineEdit(self.gridLabelLeditHw)
        self.gridColPerRowLEdit.setObjectName(u"gridColPerRowLEdit")
        self.gridColPerRowLEdit.setMaximumSize(QSize(40, 16777215))

        self.horizontalLayout_3.addWidget(self.gridColPerRowLEdit)

        self.horizontalSpacer_3 = QSpacerItem(40, 20, QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Minimum)

        self.horizontalLayout_3.addItem(self.horizontalSpacer_3)


        self.verticalLayout_2.addWidget(self.gridLabelLeditHw)


        self.retranslateUi(Dialog)

        QMetaObject.connectSlotsByName(Dialog)
    # setupUi

    def retranslateUi(self, Dialog):
        Dialog.setWindowTitle(QCoreApplication.translate("Dialog", u"Plots to show", None))
        self.applyBtn.setText(QCoreApplication.translate("Dialog", u"Apply", None))
        self.cancelBtn.setText(QCoreApplication.translate("Dialog", u"Cancel", None))
        self.currPlotLabel.setText(QCoreApplication.translate("Dialog", u"Currently Plotting:", None))
        self.removePlotBtn.setText(QCoreApplication.translate("Dialog", u"Remove Item(s)", None))
        self.addPlotGroupBox.setTitle(QCoreApplication.translate("Dialog", u"Add new plot", None))
        self.addPlotInfoLabel.setText(QCoreApplication.translate("Dialog", u"Make a list of [Dim] values to make plots for", None))
        self.indexLabel.setText(QCoreApplication.translate("Dialog", u"Index: ", None))
        self.label.setText(QCoreApplication.translate("Dialog", u"Value:", None))
        self.valueUnitLabel.setText(QCoreApplication.translate("Dialog", u"units", None))
        self.addPlotBtn.setText(QCoreApplication.translate("Dialog", u"Add Plot (Space)", None))
        self.plotParamGroupBox.setTitle(QCoreApplication.translate("Dialog", u"Plotting Grid", None))
        self.label_2.setText(QCoreApplication.translate("Dialog", u"Columns per Row: ", None))
        self.gridColPerRowLEdit.setText(QCoreApplication.translate("Dialog", u"3", None))
    # retranslateUi

