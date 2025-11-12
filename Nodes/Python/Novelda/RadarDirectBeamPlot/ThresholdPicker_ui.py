# -*- coding: utf-8 -*-

################################################################################
## Form generated from reading UI file 'ThresholdPicker_designerrwayVn.ui'
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
from PySide6.QtWidgets import (QAbstractButton, QApplication, QDialog, QDialogButtonBox,
    QLabel, QLineEdit, QSizePolicy, QWidget)

class Ui_Dialog(object):
    def setupUi(self, Dialog):
        if not Dialog.objectName():
            Dialog.setObjectName(u"Dialog")
        Dialog.resize(373, 167)
        self.buttonBox = QDialogButtonBox(Dialog)
        self.buttonBox.setObjectName(u"buttonBox")
        self.buttonBox.setGeometry(QRect(10, 130, 341, 32))
        self.buttonBox.setOrientation(Qt.Orientation.Horizontal)
        self.buttonBox.setStandardButtons(QDialogButtonBox.StandardButton.Cancel|QDialogButtonBox.StandardButton.Ok)
        self.label = QLabel(Dialog)
        self.label.setObjectName(u"label")
        self.label.setGeometry(QRect(0, 10, 221, 31))
        self.threshAtRangesLEdit = QLineEdit(Dialog)
        self.threshAtRangesLEdit.setObjectName(u"threshAtRangesLEdit")
        self.threshAtRangesLEdit.setGeometry(QRect(0, 40, 361, 22))
        self.threshValuesLEdit = QLineEdit(Dialog)
        self.threshValuesLEdit.setObjectName(u"threshValuesLEdit")
        self.threshValuesLEdit.setGeometry(QRect(0, 90, 361, 22))
        self.label_2 = QLabel(Dialog)
        self.label_2.setObjectName(u"label_2")
        self.label_2.setGeometry(QRect(0, 60, 221, 31))

        self.retranslateUi(Dialog)
        self.buttonBox.accepted.connect(Dialog.accept)
        self.buttonBox.rejected.connect(Dialog.reject)

        QMetaObject.connectSlotsByName(Dialog)
    # setupUi

    def retranslateUi(self, Dialog):
        Dialog.setWindowTitle(QCoreApplication.translate("Dialog", u"Thresholds", None))
        self.label.setText(QCoreApplication.translate("Dialog", u"Threshold at ranges:", None))
        self.label_2.setText(QCoreApplication.translate("Dialog", u"Threshold values:", None))
    # retranslateUi

