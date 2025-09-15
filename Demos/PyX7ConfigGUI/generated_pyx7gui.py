# -*- coding: utf-8 -*-

################################################################################
## Form generated from reading UI file 'X7ConfigUIhYEgvW.ui'
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
from PySide6.QtWidgets import (QApplication, QComboBox, QFrame, QGridLayout,
    QLabel, QLineEdit, QMainWindow, QPlainTextEdit,
    QPushButton, QSizePolicy, QWidget)

class Ui_MainWindow(object):
    def setupUi(self, MainWindow):
        if not MainWindow.objectName():
            MainWindow.setObjectName(u"MainWindow")
        MainWindow.resize(1055, 674)
        self.centralwidget = QWidget(MainWindow)
        self.centralwidget.setObjectName(u"centralwidget")
        self.frame = QFrame(self.centralwidget)
        self.frame.setObjectName(u"frame")
        self.frame.setGeometry(QRect(10, 250, 271, 221))
        self.frame.setFrameShape(QFrame.Shape.StyledPanel)
        self.frame.setFrameShadow(QFrame.Shadow.Plain)
        self.frame.setLineWidth(2)
        self.frame.setMidLineWidth(0)
        self.label = QLabel(self.frame)
        self.label.setObjectName(u"label")
        self.label.setGeometry(QRect(10, 0, 191, 31))
        font = QFont()
        font.setPointSize(14)
        self.label.setFont(font)
        self.gridLayoutWidget = QWidget(self.frame)
        self.gridLayoutWidget.setObjectName(u"gridLayoutWidget")
        self.gridLayoutWidget.setGeometry(QRect(10, 30, 251, 181))
        self.gridLayout = QGridLayout(self.gridLayoutWidget)
        self.gridLayout.setObjectName(u"gridLayout")
        self.gridLayout.setContentsMargins(0, 0, 0, 0)
        self.dutyCycleLEdit = QLineEdit(self.gridLayoutWidget)
        self.dutyCycleLEdit.setObjectName(u"dutyCycleLEdit")

        self.gridLayout.addWidget(self.dutyCycleLEdit, 1, 1, 1, 1)

        self.pulsePeriodLEdit = QLineEdit(self.gridLayoutWidget)
        self.pulsePeriodLEdit.setObjectName(u"pulsePeriodLEdit")

        self.gridLayout.addWidget(self.pulsePeriodLEdit, 4, 1, 1, 1)

        self.label_5 = QLabel(self.gridLayoutWidget)
        self.label_5.setObjectName(u"label_5")

        self.gridLayout.addWidget(self.label_5, 3, 0, 1, 1)

        self.label_6 = QLabel(self.gridLayoutWidget)
        self.label_6.setObjectName(u"label_6")

        self.gridLayout.addWidget(self.label_6, 4, 0, 1, 1)

        self.fpsLEdit = QLineEdit(self.gridLayoutWidget)
        self.fpsLEdit.setObjectName(u"fpsLEdit")

        self.gridLayout.addWidget(self.fpsLEdit, 0, 1, 1, 1)

        self.antennaGainLEdit = QLineEdit(self.gridLayoutWidget)
        self.antennaGainLEdit.setObjectName(u"antennaGainLEdit")

        self.gridLayout.addWidget(self.antennaGainLEdit, 3, 1, 1, 1)

        self.label_3 = QLabel(self.gridLayoutWidget)
        self.label_3.setObjectName(u"label_3")

        self.gridLayout.addWidget(self.label_3, 1, 0, 1, 1)

        self.label_2 = QLabel(self.gridLayoutWidget)
        self.label_2.setObjectName(u"label_2")

        self.gridLayout.addWidget(self.label_2, 0, 0, 1, 1)

        self.label_4 = QLabel(self.gridLayoutWidget)
        self.label_4.setObjectName(u"label_4")

        self.gridLayout.addWidget(self.label_4, 2, 0, 1, 1)

        self.maxRangeLEdit = QLineEdit(self.gridLayoutWidget)
        self.maxRangeLEdit.setObjectName(u"maxRangeLEdit")

        self.gridLayout.addWidget(self.maxRangeLEdit, 2, 1, 1, 1)

        self.calcButton = QPushButton(self.centralwidget)
        self.calcButton.setObjectName(u"calcButton")
        self.calcButton.setGeometry(QRect(10, 480, 131, 31))
        self.outputTextField = QPlainTextEdit(self.centralwidget)
        self.outputTextField.setObjectName(u"outputTextField")
        self.outputTextField.setGeometry(QRect(550, 250, 461, 221))
        self.frame_2 = QFrame(self.centralwidget)
        self.frame_2.setObjectName(u"frame_2")
        self.frame_2.setGeometry(QRect(280, 250, 251, 221))
        self.frame_2.setFrameShape(QFrame.Shape.StyledPanel)
        self.frame_2.setFrameShadow(QFrame.Shadow.Plain)
        self.frame_2.setLineWidth(2)
        self.frame_2.setMidLineWidth(0)
        self.label_7 = QLabel(self.frame_2)
        self.label_7.setObjectName(u"label_7")
        self.label_7.setGeometry(QRect(10, 0, 191, 31))
        self.label_7.setFont(font)
        self.gridLayoutWidget_2 = QWidget(self.frame_2)
        self.gridLayoutWidget_2.setObjectName(u"gridLayoutWidget_2")
        self.gridLayoutWidget_2.setGeometry(QRect(10, 30, 231, 181))
        self.gridLayout_2 = QGridLayout(self.gridLayoutWidget_2)
        self.gridLayout_2.setObjectName(u"gridLayout_2")
        self.gridLayout_2.setContentsMargins(0, 0, 0, 0)
        self.txChanLEdit = QLineEdit(self.gridLayoutWidget_2)
        self.txChanLEdit.setObjectName(u"txChanLEdit")

        self.gridLayout_2.addWidget(self.txChanLEdit, 1, 1, 1, 1)

        self.rxMaskLEdit = QLineEdit(self.gridLayoutWidget_2)
        self.rxMaskLEdit.setObjectName(u"rxMaskLEdit")

        self.gridLayout_2.addWidget(self.rxMaskLEdit, 2, 1, 1, 1)

        self.label_10 = QLabel(self.gridLayoutWidget_2)
        self.label_10.setObjectName(u"label_10")

        self.gridLayout_2.addWidget(self.label_10, 2, 0, 1, 1)

        self.label_9 = QLabel(self.gridLayoutWidget_2)
        self.label_9.setObjectName(u"label_9")

        self.gridLayout_2.addWidget(self.label_9, 0, 0, 1, 1)

        self.numChipsLEdit = QLineEdit(self.gridLayoutWidget_2)
        self.numChipsLEdit.setObjectName(u"numChipsLEdit")

        self.gridLayout_2.addWidget(self.numChipsLEdit, 0, 1, 1, 1)

        self.label_8 = QLabel(self.gridLayoutWidget_2)
        self.label_8.setObjectName(u"label_8")

        self.gridLayout_2.addWidget(self.label_8, 1, 0, 1, 1)

        self.frame_3 = QFrame(self.centralwidget)
        self.frame_3.setObjectName(u"frame_3")
        self.frame_3.setGeometry(QRect(10, 10, 471, 211))
        self.frame_3.setFrameShape(QFrame.Shape.StyledPanel)
        self.frame_3.setFrameShadow(QFrame.Shadow.Plain)
        self.frame_3.setLineWidth(2)
        self.label_11 = QLabel(self.frame_3)
        self.label_11.setObjectName(u"label_11")
        self.label_11.setGeometry(QRect(10, 10, 191, 31))
        self.label_11.setFont(font)
        self.gridLayoutWidget_3 = QWidget(self.frame_3)
        self.gridLayoutWidget_3.setObjectName(u"gridLayoutWidget_3")
        self.gridLayoutWidget_3.setGeometry(QRect(10, 40, 431, 46))
        self.gridLayout_3 = QGridLayout(self.gridLayoutWidget_3)
        self.gridLayout_3.setObjectName(u"gridLayout_3")
        self.gridLayout_3.setContentsMargins(0, 0, 0, 0)
        self.label_13 = QLabel(self.gridLayoutWidget_3)
        self.label_13.setObjectName(u"label_13")

        self.gridLayout_3.addWidget(self.label_13, 0, 0, 1, 1)

        self.comboBox = QComboBox(self.gridLayoutWidget_3)
        self.comboBox.setObjectName(u"comboBox")
        sizePolicy = QSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Fixed)
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(self.comboBox.sizePolicy().hasHeightForWidth())
        self.comboBox.setSizePolicy(sizePolicy)

        self.gridLayout_3.addWidget(self.comboBox, 0, 1, 1, 1)

        self.label_15 = QLabel(self.frame_3)
        self.label_15.setObjectName(u"label_15")
        self.label_15.setGeometry(QRect(10, 90, 311, 31))
        self.label_15.setFont(font)
        self.gridLayoutWidget_5 = QWidget(self.frame_3)
        self.gridLayoutWidget_5.setObjectName(u"gridLayoutWidget_5")
        self.gridLayoutWidget_5.setGeometry(QRect(10, 120, 431, 46))
        self.gridLayout_5 = QGridLayout(self.gridLayoutWidget_5)
        self.gridLayout_5.setObjectName(u"gridLayout_5")
        self.gridLayout_5.setContentsMargins(0, 0, 0, 0)
        self.label_16 = QLabel(self.gridLayoutWidget_5)
        self.label_16.setObjectName(u"label_16")

        self.gridLayout_5.addWidget(self.label_16, 0, 0, 1, 1)

        self.saveFileNameLEdit = QLineEdit(self.gridLayoutWidget_5)
        self.saveFileNameLEdit.setObjectName(u"saveFileNameLEdit")

        self.gridLayout_5.addWidget(self.saveFileNameLEdit, 0, 1, 1, 1)

        self.saveFileButton = QPushButton(self.frame_3)
        self.saveFileButton.setObjectName(u"saveFileButton")
        self.saveFileButton.setGeometry(QRect(10, 170, 131, 31))
        self.frame_4 = QFrame(self.centralwidget)
        self.frame_4.setObjectName(u"frame_4")
        self.frame_4.setGeometry(QRect(550, 10, 461, 211))
        self.frame_4.setFrameShape(QFrame.Shape.StyledPanel)
        self.frame_4.setFrameShadow(QFrame.Shadow.Plain)
        self.frame_4.setLineWidth(2)
        self.frame_4.setMidLineWidth(0)
        self.label_12 = QLabel(self.frame_4)
        self.label_12.setObjectName(u"label_12")
        self.label_12.setGeometry(QRect(10, 0, 331, 31))
        self.label_12.setFont(font)
        self.gridLayoutWidget_4 = QWidget(self.frame_4)
        self.gridLayoutWidget_4.setObjectName(u"gridLayoutWidget_4")
        self.gridLayoutWidget_4.setGeometry(QRect(10, 30, 171, 31))
        self.gridLayout_4 = QGridLayout(self.gridLayoutWidget_4)
        self.gridLayout_4.setObjectName(u"gridLayout_4")
        self.gridLayout_4.setContentsMargins(0, 0, 0, 0)
        self.label_17 = QLabel(self.gridLayoutWidget_4)
        self.label_17.setObjectName(u"label_17")

        self.gridLayout_4.addWidget(self.label_17, 0, 0, 1, 1)

        self.findFPSPulePeriodLEdit = QLineEdit(self.gridLayoutWidget_4)
        self.findFPSPulePeriodLEdit.setObjectName(u"findFPSPulePeriodLEdit")

        self.gridLayout_4.addWidget(self.findFPSPulePeriodLEdit, 0, 1, 1, 1)

        self.findFPSoutputField = QPlainTextEdit(self.frame_4)
        self.findFPSoutputField.setObjectName(u"findFPSoutputField")
        self.findFPSoutputField.setGeometry(QRect(10, 70, 441, 121))
        self.findFPSButton = QPushButton(self.frame_4)
        self.findFPSButton.setObjectName(u"findFPSButton")
        self.findFPSButton.setGeometry(QRect(190, 30, 131, 31))
        self.exportChipButton = QPushButton(self.centralwidget)
        self.exportChipButton.setObjectName(u"exportChipButton")
        self.exportChipButton.setGeometry(QRect(550, 480, 131, 31))
        MainWindow.setCentralWidget(self.centralwidget)

        self.retranslateUi(MainWindow)

        QMetaObject.connectSlotsByName(MainWindow)
    # setupUi

    def retranslateUi(self, MainWindow):
        MainWindow.setWindowTitle(QCoreApplication.translate("MainWindow", u"PyX7Configuration GUI", None))
        self.label.setText(QCoreApplication.translate("MainWindow", u"X7UserConfiguration", None))
        self.label_5.setText(QCoreApplication.translate("MainWindow", u"Antenna Gain", None))
        self.label_6.setText(QCoreApplication.translate("MainWindow", u"Pulse Period", None))
        self.label_3.setText(QCoreApplication.translate("MainWindow", u"Duty Cycle", None))
        self.label_2.setText(QCoreApplication.translate("MainWindow", u"FPS", None))
        self.label_4.setText(QCoreApplication.translate("MainWindow", u"Max Range", None))
        self.calcButton.setText(QCoreApplication.translate("MainWindow", u"Calculate Chip Config", None))
        self.outputTextField.setPlainText("")
        self.outputTextField.setPlaceholderText("")
        self.label_7.setText(QCoreApplication.translate("MainWindow", u"X7 TxRx Configuration", None))
        self.label_10.setText(QCoreApplication.translate("MainWindow", u"Rx Mask Sequence", None))
        self.label_9.setText(QCoreApplication.translate("MainWindow", u"Number of Chips", None))
        self.label_8.setText(QCoreApplication.translate("MainWindow", u"Tx Channel Sequence", None))
        self.label_11.setText(QCoreApplication.translate("MainWindow", u"From preset file", None))
        self.label_13.setText(QCoreApplication.translate("MainWindow", u"File Name", None))
        self.label_15.setText(QCoreApplication.translate("MainWindow", u"Save new preset from current values", None))
        self.label_16.setText(QCoreApplication.translate("MainWindow", u"File Name", None))
        self.saveFileNameLEdit.setPlaceholderText("")
        self.saveFileButton.setText(QCoreApplication.translate("MainWindow", u"Save", None))
        self.label_12.setText(QCoreApplication.translate("MainWindow", u"Find valid FPS list from Pulse Period", None))
        self.label_17.setText(QCoreApplication.translate("MainWindow", u"Pulse Period", None))
        self.findFPSoutputField.setPlainText("")
        self.findFPSoutputField.setPlaceholderText("")
        self.findFPSButton.setText(QCoreApplication.translate("MainWindow", u"Find FPS", None))
        self.exportChipButton.setText(QCoreApplication.translate("MainWindow", u"Export Chip Config", None))
    # retranslateUi

