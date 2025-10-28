# -*- coding: utf-8 -*-

################################################################################
## Form generated from reading UI file 'new_mainkzlaaC.ui'
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
from PySide6.QtWidgets import (QApplication, QCheckBox, QComboBox, QFrame,
    QHBoxLayout, QLabel, QLineEdit, QMainWindow,
    QPushButton, QSizePolicy, QSlider, QSpacerItem,
    QVBoxLayout, QWidget)

class Ui_MainWindow(object):
    def setupUi(self, MainWindow):
        if not MainWindow.objectName():
            MainWindow.setObjectName(u"MainWindow")
        MainWindow.resize(1681, 947)
        self.centralArea = QWidget(MainWindow)
        self.centralArea.setObjectName(u"centralArea")
        self.centralArea.setEnabled(True)
        sizePolicy = QSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Expanding)
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(self.centralArea.sizePolicy().hasHeightForWidth())
        self.centralArea.setSizePolicy(sizePolicy)
        self.verticalLayout = QVBoxLayout(self.centralArea)
        self.verticalLayout.setObjectName(u"verticalLayout")
        self.topPlotWidget = QHBoxLayout()
        self.topPlotWidget.setObjectName(u"topPlotWidget")
        self.topPlotWidget.setContentsMargins(-1, 0, 0, -1)
        self.topPlotBox = QWidget(self.centralArea)
        self.topPlotBox.setObjectName(u"topPlotBox")

        self.topPlotWidget.addWidget(self.topPlotBox)

        self.topRightPlot = QWidget(self.centralArea)
        self.topRightPlot.setObjectName(u"topRightPlot")

        self.topPlotWidget.addWidget(self.topRightPlot)


        self.verticalLayout.addLayout(self.topPlotWidget)

        self.horizontalLayout = QHBoxLayout()
        self.horizontalLayout.setObjectName(u"horizontalLayout")
        self.bottomLeftPlot = QWidget(self.centralArea)
        self.bottomLeftPlot.setObjectName(u"bottomLeftPlot")

        self.horizontalLayout.addWidget(self.bottomLeftPlot)

        self.bottomMiddlePlot = QWidget(self.centralArea)
        self.bottomMiddlePlot.setObjectName(u"bottomMiddlePlot")

        self.horizontalLayout.addWidget(self.bottomMiddlePlot)

        self.bottomRightPlot = QWidget(self.centralArea)
        self.bottomRightPlot.setObjectName(u"bottomRightPlot")

        self.horizontalLayout.addWidget(self.bottomRightPlot)


        self.verticalLayout.addLayout(self.horizontalLayout)

        self.controlsFirstVwidget = QWidget(self.centralArea)
        self.controlsFirstVwidget.setObjectName(u"controlsFirstVwidget")
        sizePolicy1 = QSizePolicy(QSizePolicy.Policy.Preferred, QSizePolicy.Policy.Preferred)
        sizePolicy1.setHorizontalStretch(98)
        sizePolicy1.setVerticalStretch(98)
        sizePolicy1.setHeightForWidth(self.controlsFirstVwidget.sizePolicy().hasHeightForWidth())
        self.controlsFirstVwidget.setSizePolicy(sizePolicy1)
        self.controlsFirstVlay = QHBoxLayout(self.controlsFirstVwidget)
        self.controlsFirstVlay.setObjectName(u"controlsFirstVlay")
        self.controlsFirstVlay.setContentsMargins(-1, 0, 9, 0)
        self.verticalLayout_3 = QVBoxLayout()
        self.verticalLayout_3.setObjectName(u"verticalLayout_3")
        self.verticalLayout_3.setContentsMargins(-1, 0, 5, -1)
        self.infoWidget = QVBoxLayout()
        self.infoWidget.setObjectName(u"infoWidget")
        self.infoWidget.setContentsMargins(5, 5, 5, 5)
        self.liveOrPlayInfoVwidget = QWidget(self.controlsFirstVwidget)
        self.liveOrPlayInfoVwidget.setObjectName(u"liveOrPlayInfoVwidget")
        self.liveOrPlayVLay = QVBoxLayout(self.liveOrPlayInfoVwidget)
        self.liveOrPlayVLay.setSpacing(5)
        self.liveOrPlayVLay.setObjectName(u"liveOrPlayVLay")
        self.liveOrPlayVLay.setContentsMargins(0, 0, 5, 5)
        self.hotkeyLabel = QLabel(self.liveOrPlayInfoVwidget)
        self.hotkeyLabel.setObjectName(u"hotkeyLabel")
        self.hotkeyLabel.setStyleSheet(u"color: #b1b7c0;\n"
"font-size: 10pt;")
        self.hotkeyLabel.setAlignment(Qt.AlignmentFlag.AlignLeading|Qt.AlignmentFlag.AlignLeft|Qt.AlignmentFlag.AlignTop)
        self.hotkeyLabel.setWordWrap(False)
        self.hotkeyLabel.setTextInteractionFlags(Qt.TextInteractionFlag.NoTextInteraction)

        self.liveOrPlayVLay.addWidget(self.hotkeyLabel)

        self.verticalSpacer_2 = QSpacerItem(20, 40, QSizePolicy.Policy.Minimum, QSizePolicy.Policy.Expanding)

        self.liveOrPlayVLay.addItem(self.verticalSpacer_2)


        self.infoWidget.addWidget(self.liveOrPlayInfoVwidget)


        self.verticalLayout_3.addLayout(self.infoWidget)

        self.logoLabel = QLabel(self.controlsFirstVwidget)
        self.logoLabel.setObjectName(u"logoLabel")
        self.logoLabel.setAlignment(Qt.AlignmentFlag.AlignBottom|Qt.AlignmentFlag.AlignLeading|Qt.AlignmentFlag.AlignLeft)

        self.verticalLayout_3.addWidget(self.logoLabel)


        self.controlsFirstVlay.addLayout(self.verticalLayout_3)

        self.vertLine0 = QFrame(self.controlsFirstVwidget)
        self.vertLine0.setObjectName(u"vertLine0")
        self.vertLine0.setFrameShadow(QFrame.Shadow.Plain)
        self.vertLine0.setFrameShape(QFrame.Shape.VLine)

        self.controlsFirstVlay.addWidget(self.vertLine0)

        self.sektorPlotSettingsVLayout = QVBoxLayout()
        self.sektorPlotSettingsVLayout.setObjectName(u"sektorPlotSettingsVLayout")
        self.sektorPlotSettingsVLayout.setContentsMargins(5, 0, 5, 0)
        self.SektorPlotLabel = QLabel(self.controlsFirstVwidget)
        self.SektorPlotLabel.setObjectName(u"SektorPlotLabel")
        sizePolicy2 = QSizePolicy(QSizePolicy.Policy.Preferred, QSizePolicy.Policy.Minimum)
        sizePolicy2.setHorizontalStretch(0)
        sizePolicy2.setVerticalStretch(0)
        sizePolicy2.setHeightForWidth(self.SektorPlotLabel.sizePolicy().hasHeightForWidth())
        self.SektorPlotLabel.setSizePolicy(sizePolicy2)
        self.SektorPlotLabel.setMinimumSize(QSize(0, 20))
        self.SektorPlotLabel.setMaximumSize(QSize(16777215, 20))
        self.SektorPlotLabel.setFrameShape(QFrame.Shape.NoFrame)
        self.SektorPlotLabel.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.SektorPlotLabel.setWordWrap(False)

        self.sektorPlotSettingsVLayout.addWidget(self.SektorPlotLabel)

        self.horizontalLine0 = QFrame(self.controlsFirstVwidget)
        self.horizontalLine0.setObjectName(u"horizontalLine0")
        self.horizontalLine0.setFrameShadow(QFrame.Shadow.Plain)
        self.horizontalLine0.setFrameShape(QFrame.Shape.HLine)

        self.sektorPlotSettingsVLayout.addWidget(self.horizontalLine0)

        self.trailBwdHLayout = QHBoxLayout()
        self.trailBwdHLayout.setObjectName(u"trailBwdHLayout")
        self.trailBwdHLayout.setContentsMargins(0, 0, -1, -1)
        self.trailBwdLabel = QLabel(self.controlsFirstVwidget)
        self.trailBwdLabel.setObjectName(u"trailBwdLabel")

        self.trailBwdHLayout.addWidget(self.trailBwdLabel)

        self.trailBwdLEdit = QLineEdit(self.controlsFirstVwidget)
        self.trailBwdLEdit.setObjectName(u"trailBwdLEdit")
        self.trailBwdLEdit.setMaximumSize(QSize(60, 16777215))

        self.trailBwdHLayout.addWidget(self.trailBwdLEdit)


        self.sektorPlotSettingsVLayout.addLayout(self.trailBwdHLayout)

        self.trailFwdHLayout = QHBoxLayout()
        self.trailFwdHLayout.setObjectName(u"trailFwdHLayout")
        self.trailFwdHLayout.setContentsMargins(0, 0, -1, -1)
        self.trailFwdLabel = QLabel(self.controlsFirstVwidget)
        self.trailFwdLabel.setObjectName(u"trailFwdLabel")

        self.trailFwdHLayout.addWidget(self.trailFwdLabel)

        self.trailFwdLEdit = QLineEdit(self.controlsFirstVwidget)
        self.trailFwdLEdit.setObjectName(u"trailFwdLEdit")
        self.trailFwdLEdit.setMaximumSize(QSize(60, 16777215))

        self.trailFwdHLayout.addWidget(self.trailFwdLEdit)


        self.sektorPlotSettingsVLayout.addLayout(self.trailFwdHLayout)

        self.invertTopPlotBtn = QPushButton(self.controlsFirstVwidget)
        self.invertTopPlotBtn.setObjectName(u"invertTopPlotBtn")
        sizePolicy3 = QSizePolicy(QSizePolicy.Policy.Maximum, QSizePolicy.Policy.Fixed)
        sizePolicy3.setHorizontalStretch(0)
        sizePolicy3.setVerticalStretch(0)
        sizePolicy3.setHeightForWidth(self.invertTopPlotBtn.sizePolicy().hasHeightForWidth())
        self.invertTopPlotBtn.setSizePolicy(sizePolicy3)
        self.invertTopPlotBtn.setMaximumSize(QSize(10000, 16777215))

        self.sektorPlotSettingsVLayout.addWidget(self.invertTopPlotBtn)

        self.horizontalLayout_2 = QHBoxLayout()
        self.horizontalLayout_2.setObjectName(u"horizontalLayout_2")
        self.horizontalLayout_2.setContentsMargins(-1, 10, -1, -1)
        self.horizontalSpacer_7 = QSpacerItem(40, 20, QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Minimum)

        self.horizontalLayout_2.addItem(self.horizontalSpacer_7)

        self.showFovLinesCheckBox = QCheckBox(self.controlsFirstVwidget)
        self.showFovLinesCheckBox.setObjectName(u"showFovLinesCheckBox")
        self.showFovLinesCheckBox.setChecked(True)

        self.horizontalLayout_2.addWidget(self.showFovLinesCheckBox)

        self.showXYcheckBox = QCheckBox(self.controlsFirstVwidget)
        self.showXYcheckBox.setObjectName(u"showXYcheckBox")
        self.showXYcheckBox.setChecked(True)

        self.horizontalLayout_2.addWidget(self.showXYcheckBox)

        self.horizontalSpacer_10 = QSpacerItem(40, 20, QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Minimum)

        self.horizontalLayout_2.addItem(self.horizontalSpacer_10)


        self.sektorPlotSettingsVLayout.addLayout(self.horizontalLayout_2)

        self.verticalSpacer_3 = QSpacerItem(20, 40, QSizePolicy.Policy.Minimum, QSizePolicy.Policy.Expanding)

        self.sektorPlotSettingsVLayout.addItem(self.verticalSpacer_3)


        self.controlsFirstVlay.addLayout(self.sektorPlotSettingsVLayout)

        self.vertLine1 = QFrame(self.controlsFirstVwidget)
        self.vertLine1.setObjectName(u"vertLine1")
        self.vertLine1.setFrameShadow(QFrame.Shadow.Plain)
        self.vertLine1.setFrameShape(QFrame.Shape.VLine)

        self.controlsFirstVlay.addWidget(self.vertLine1)

        self.PowerPlotSettingsVLayout = QVBoxLayout()
        self.PowerPlotSettingsVLayout.setObjectName(u"PowerPlotSettingsVLayout")
        self.PowerPlotSettingsVLayout.setContentsMargins(5, -1, 5, 0)
        self.PowerPlotLabel = QLabel(self.controlsFirstVwidget)
        self.PowerPlotLabel.setObjectName(u"PowerPlotLabel")
        sizePolicy2.setHeightForWidth(self.PowerPlotLabel.sizePolicy().hasHeightForWidth())
        self.PowerPlotLabel.setSizePolicy(sizePolicy2)
        self.PowerPlotLabel.setMinimumSize(QSize(0, 20))
        self.PowerPlotLabel.setMaximumSize(QSize(16777215, 20))
        self.PowerPlotLabel.setFrameShape(QFrame.Shape.NoFrame)
        self.PowerPlotLabel.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.PowerPlotLabel.setWordWrap(False)

        self.PowerPlotSettingsVLayout.addWidget(self.PowerPlotLabel)

        self.horizontalLine1 = QFrame(self.controlsFirstVwidget)
        self.horizontalLine1.setObjectName(u"horizontalLine1")
        self.horizontalLine1.setFrameShadow(QFrame.Shadow.Plain)
        self.horizontalLine1.setFrameShape(QFrame.Shape.HLine)

        self.PowerPlotSettingsVLayout.addWidget(self.horizontalLine1)

        self.horizontalLayout_5 = QHBoxLayout()
        self.horizontalLayout_5.setObjectName(u"horizontalLayout_5")

        self.PowerPlotSettingsVLayout.addLayout(self.horizontalLayout_5)

        self.rangeMaxHwidget = QWidget(self.controlsFirstVwidget)
        self.rangeMaxHwidget.setObjectName(u"rangeMaxHwidget")
        self.rangeMaxHLay_2 = QHBoxLayout(self.rangeMaxHwidget)
        self.rangeMaxHLay_2.setObjectName(u"rangeMaxHLay_2")
        self.rangeMaxHLay_2.setContentsMargins(0, 0, 0, 0)
        self.horizontalSpacer = QSpacerItem(40, 20, QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Minimum)

        self.rangeMaxHLay_2.addItem(self.horizontalSpacer)

        self.rangeMaxLabel = QLabel(self.rangeMaxHwidget)
        self.rangeMaxLabel.setObjectName(u"rangeMaxLabel")
        sizePolicy4 = QSizePolicy(QSizePolicy.Policy.Preferred, QSizePolicy.Policy.Preferred)
        sizePolicy4.setHorizontalStretch(0)
        sizePolicy4.setVerticalStretch(0)
        sizePolicy4.setHeightForWidth(self.rangeMaxLabel.sizePolicy().hasHeightForWidth())
        self.rangeMaxLabel.setSizePolicy(sizePolicy4)
        self.rangeMaxLabel.setMinimumSize(QSize(82, 0))
        self.rangeMaxLabel.setMaximumSize(QSize(82, 16777215))

        self.rangeMaxHLay_2.addWidget(self.rangeMaxLabel)

        self.rangeMaxLEdit = QLineEdit(self.rangeMaxHwidget)
        self.rangeMaxLEdit.setObjectName(u"rangeMaxLEdit")
        sizePolicy5 = QSizePolicy(QSizePolicy.Policy.Minimum, QSizePolicy.Policy.Fixed)
        sizePolicy5.setHorizontalStretch(0)
        sizePolicy5.setVerticalStretch(0)
        sizePolicy5.setHeightForWidth(self.rangeMaxLEdit.sizePolicy().hasHeightForWidth())
        self.rangeMaxLEdit.setSizePolicy(sizePolicy5)
        self.rangeMaxLEdit.setMaximumSize(QSize(100, 16777215))

        self.rangeMaxHLay_2.addWidget(self.rangeMaxLEdit)

        self.rangeMaxUnitLabel = QLabel(self.rangeMaxHwidget)
        self.rangeMaxUnitLabel.setObjectName(u"rangeMaxUnitLabel")
        self.rangeMaxUnitLabel.setMinimumSize(QSize(12, 0))
        self.rangeMaxUnitLabel.setMaximumSize(QSize(12, 16777215))

        self.rangeMaxHLay_2.addWidget(self.rangeMaxUnitLabel)

        self.horizontalSpacer_5 = QSpacerItem(40, 20, QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Minimum)

        self.rangeMaxHLay_2.addItem(self.horizontalSpacer_5)


        self.PowerPlotSettingsVLayout.addWidget(self.rangeMaxHwidget)

        self.rangeMinHwidget = QWidget(self.controlsFirstVwidget)
        self.rangeMinHwidget.setObjectName(u"rangeMinHwidget")
        self.rangeMinHLay_2 = QHBoxLayout(self.rangeMinHwidget)
        self.rangeMinHLay_2.setObjectName(u"rangeMinHLay_2")
        self.rangeMinHLay_2.setContentsMargins(0, 0, 0, 0)
        self.horizontalSpacer_6 = QSpacerItem(40, 20, QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Minimum)

        self.rangeMinHLay_2.addItem(self.horizontalSpacer_6)

        self.rangeMinLabel = QLabel(self.rangeMinHwidget)
        self.rangeMinLabel.setObjectName(u"rangeMinLabel")
        self.rangeMinLabel.setMinimumSize(QSize(82, 0))
        self.rangeMinLabel.setMaximumSize(QSize(82, 16777215))

        self.rangeMinHLay_2.addWidget(self.rangeMinLabel)

        self.rangeMinLEdit = QLineEdit(self.rangeMinHwidget)
        self.rangeMinLEdit.setObjectName(u"rangeMinLEdit")
        sizePolicy5.setHeightForWidth(self.rangeMinLEdit.sizePolicy().hasHeightForWidth())
        self.rangeMinLEdit.setSizePolicy(sizePolicy5)
        self.rangeMinLEdit.setMaximumSize(QSize(100, 16777215))

        self.rangeMinHLay_2.addWidget(self.rangeMinLEdit)

        self.rangeMinUnitLabel = QLabel(self.rangeMinHwidget)
        self.rangeMinUnitLabel.setObjectName(u"rangeMinUnitLabel")
        self.rangeMinUnitLabel.setMinimumSize(QSize(12, 0))
        self.rangeMinUnitLabel.setMaximumSize(QSize(12, 16777215))

        self.rangeMinHLay_2.addWidget(self.rangeMinUnitLabel)

        self.horizontalSpacer_2 = QSpacerItem(40, 20, QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Minimum)

        self.rangeMinHLay_2.addItem(self.horizontalSpacer_2)


        self.PowerPlotSettingsVLayout.addWidget(self.rangeMinHwidget)

        self.dopplerMaxHw = QWidget(self.controlsFirstVwidget)
        self.dopplerMaxHw.setObjectName(u"dopplerMaxHw")
        self.dopplerMaxHlay_2 = QHBoxLayout(self.dopplerMaxHw)
        self.dopplerMaxHlay_2.setObjectName(u"dopplerMaxHlay_2")
        self.dopplerMaxHlay_2.setContentsMargins(0, 0, 0, 0)
        self.horizontalSpacer_3 = QSpacerItem(40, 20, QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Minimum)

        self.dopplerMaxHlay_2.addItem(self.horizontalSpacer_3)

        self.powerMaxLabel = QLabel(self.dopplerMaxHw)
        self.powerMaxLabel.setObjectName(u"powerMaxLabel")
        sizePolicy4.setHeightForWidth(self.powerMaxLabel.sizePolicy().hasHeightForWidth())
        self.powerMaxLabel.setSizePolicy(sizePolicy4)
        self.powerMaxLabel.setMinimumSize(QSize(82, 0))
        self.powerMaxLabel.setMaximumSize(QSize(82, 16777215))

        self.dopplerMaxHlay_2.addWidget(self.powerMaxLabel)

        self.powerMaxLEdit = QLineEdit(self.dopplerMaxHw)
        self.powerMaxLEdit.setObjectName(u"powerMaxLEdit")
        sizePolicy5.setHeightForWidth(self.powerMaxLEdit.sizePolicy().hasHeightForWidth())
        self.powerMaxLEdit.setSizePolicy(sizePolicy5)
        self.powerMaxLEdit.setMaximumSize(QSize(100, 16777215))

        self.dopplerMaxHlay_2.addWidget(self.powerMaxLEdit)

        self.rangeMinUnitLabel_2 = QLabel(self.dopplerMaxHw)
        self.rangeMinUnitLabel_2.setObjectName(u"rangeMinUnitLabel_2")
        self.rangeMinUnitLabel_2.setMinimumSize(QSize(12, 0))
        self.rangeMinUnitLabel_2.setMaximumSize(QSize(12, 16777215))

        self.dopplerMaxHlay_2.addWidget(self.rangeMinUnitLabel_2)

        self.horizontalSpacer_8 = QSpacerItem(40, 20, QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Minimum)

        self.dopplerMaxHlay_2.addItem(self.horizontalSpacer_8)


        self.PowerPlotSettingsVLayout.addWidget(self.dopplerMaxHw)

        self.powerMinHwidget = QWidget(self.controlsFirstVwidget)
        self.powerMinHwidget.setObjectName(u"powerMinHwidget")
        self.powerMaxHlay_2 = QHBoxLayout(self.powerMinHwidget)
        self.powerMaxHlay_2.setObjectName(u"powerMaxHlay_2")
        self.powerMaxHlay_2.setContentsMargins(0, 0, 0, 0)
        self.horizontalSpacer_4 = QSpacerItem(40, 20, QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Minimum)

        self.powerMaxHlay_2.addItem(self.horizontalSpacer_4)

        self.powerMinLabel = QLabel(self.powerMinHwidget)
        self.powerMinLabel.setObjectName(u"powerMinLabel")
        sizePolicy4.setHeightForWidth(self.powerMinLabel.sizePolicy().hasHeightForWidth())
        self.powerMinLabel.setSizePolicy(sizePolicy4)
        self.powerMinLabel.setMinimumSize(QSize(82, 0))
        self.powerMinLabel.setMaximumSize(QSize(82, 16777215))

        self.powerMaxHlay_2.addWidget(self.powerMinLabel)

        self.powerMinLEdit = QLineEdit(self.powerMinHwidget)
        self.powerMinLEdit.setObjectName(u"powerMinLEdit")
        sizePolicy5.setHeightForWidth(self.powerMinLEdit.sizePolicy().hasHeightForWidth())
        self.powerMinLEdit.setSizePolicy(sizePolicy5)
        self.powerMinLEdit.setMaximumSize(QSize(100, 16777215))

        self.powerMaxHlay_2.addWidget(self.powerMinLEdit)

        self.rangeMinUnitLabel_3 = QLabel(self.powerMinHwidget)
        self.rangeMinUnitLabel_3.setObjectName(u"rangeMinUnitLabel_3")
        self.rangeMinUnitLabel_3.setMinimumSize(QSize(12, 0))
        self.rangeMinUnitLabel_3.setMaximumSize(QSize(12, 16777215))

        self.powerMaxHlay_2.addWidget(self.rangeMinUnitLabel_3)

        self.horizontalSpacer_9 = QSpacerItem(20, 20, QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Minimum)

        self.powerMaxHlay_2.addItem(self.horizontalSpacer_9)


        self.PowerPlotSettingsVLayout.addWidget(self.powerMinHwidget)

        self.verticalSpacer_4 = QSpacerItem(20, 40, QSizePolicy.Policy.Minimum, QSizePolicy.Policy.Expanding)

        self.PowerPlotSettingsVLayout.addItem(self.verticalSpacer_4)


        self.controlsFirstVlay.addLayout(self.PowerPlotSettingsVLayout)

        self.vertLine2 = QFrame(self.controlsFirstVwidget)
        self.vertLine2.setObjectName(u"vertLine2")
        self.vertLine2.setFrameShadow(QFrame.Shadow.Plain)
        self.vertLine2.setFrameShape(QFrame.Shape.VLine)

        self.controlsFirstVlay.addWidget(self.vertLine2)

        self.TimePlotSettingsVLayout = QVBoxLayout()
        self.TimePlotSettingsVLayout.setObjectName(u"TimePlotSettingsVLayout")
        self.TimePlotSettingsVLayout.setContentsMargins(5, -1, 5, -1)
        self.TimePlotSettingsLabel = QLabel(self.controlsFirstVwidget)
        self.TimePlotSettingsLabel.setObjectName(u"TimePlotSettingsLabel")
        sizePolicy2.setHeightForWidth(self.TimePlotSettingsLabel.sizePolicy().hasHeightForWidth())
        self.TimePlotSettingsLabel.setSizePolicy(sizePolicy2)
        self.TimePlotSettingsLabel.setMinimumSize(QSize(0, 20))
        self.TimePlotSettingsLabel.setMaximumSize(QSize(16777215, 20))
        self.TimePlotSettingsLabel.setFrameShape(QFrame.Shape.NoFrame)
        self.TimePlotSettingsLabel.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.TimePlotSettingsLabel.setWordWrap(False)

        self.TimePlotSettingsVLayout.addWidget(self.TimePlotSettingsLabel)

        self.horizontalLine2 = QFrame(self.controlsFirstVwidget)
        self.horizontalLine2.setObjectName(u"horizontalLine2")
        self.horizontalLine2.setFrameShadow(QFrame.Shadow.Plain)
        self.horizontalLine2.setFrameShape(QFrame.Shape.HLine)

        self.TimePlotSettingsVLayout.addWidget(self.horizontalLine2)

        self.horizontalLayout_4 = QHBoxLayout()
        self.horizontalLayout_4.setObjectName(u"horizontalLayout_4")
        self.label_2 = QLabel(self.controlsFirstVwidget)
        self.label_2.setObjectName(u"label_2")
        sizePolicy6 = QSizePolicy(QSizePolicy.Policy.Fixed, QSizePolicy.Policy.Preferred)
        sizePolicy6.setHorizontalStretch(0)
        sizePolicy6.setVerticalStretch(0)
        sizePolicy6.setHeightForWidth(self.label_2.sizePolicy().hasHeightForWidth())
        self.label_2.setSizePolicy(sizePolicy6)

        self.horizontalLayout_4.addWidget(self.label_2)

        self.choosePlotComboBox = QComboBox(self.controlsFirstVwidget)
        self.choosePlotComboBox.setObjectName(u"choosePlotComboBox")

        self.horizontalLayout_4.addWidget(self.choosePlotComboBox)


        self.TimePlotSettingsVLayout.addLayout(self.horizontalLayout_4)

        self.parentTimeZoom = QHBoxLayout()
        self.parentTimeZoom.setObjectName(u"parentTimeZoom")
        self.parentTimeZoom.setContentsMargins(-1, 0, -1, -1)
        self.label = QLabel(self.controlsFirstVwidget)
        self.label.setObjectName(u"label")

        self.parentTimeZoom.addWidget(self.label)

        self.timeScaleSlider = QSlider(self.controlsFirstVwidget)
        self.timeScaleSlider.setObjectName(u"timeScaleSlider")
        self.timeScaleSlider.setCursor(QCursor(Qt.CursorShape.ArrowCursor))
        self.timeScaleSlider.setMinimum(1)
        self.timeScaleSlider.setMaximum(300)
        self.timeScaleSlider.setOrientation(Qt.Orientation.Horizontal)

        self.parentTimeZoom.addWidget(self.timeScaleSlider)

        self.timeScaleLEdit = QLineEdit(self.controlsFirstVwidget)
        self.timeScaleLEdit.setObjectName(u"timeScaleLEdit")
        self.timeScaleLEdit.setMaximumSize(QSize(60, 16777215))

        self.parentTimeZoom.addWidget(self.timeScaleLEdit)


        self.TimePlotSettingsVLayout.addLayout(self.parentTimeZoom)

        self.resetLimitsBtn = QPushButton(self.controlsFirstVwidget)
        self.resetLimitsBtn.setObjectName(u"resetLimitsBtn")
        sizePolicy3.setHeightForWidth(self.resetLimitsBtn.sizePolicy().hasHeightForWidth())
        self.resetLimitsBtn.setSizePolicy(sizePolicy3)
        self.resetLimitsBtn.setMaximumSize(QSize(10000, 16777215))
        self.resetLimitsBtn.setFlat(False)

        self.TimePlotSettingsVLayout.addWidget(self.resetLimitsBtn)

        self.verticalSpacer_5 = QSpacerItem(20, 40, QSizePolicy.Policy.Minimum, QSizePolicy.Policy.Expanding)

        self.TimePlotSettingsVLayout.addItem(self.verticalSpacer_5)


        self.controlsFirstVlay.addLayout(self.TimePlotSettingsVLayout)

        self.vertLine3 = QFrame(self.controlsFirstVwidget)
        self.vertLine3.setObjectName(u"vertLine3")
        self.vertLine3.setFrameShadow(QFrame.Shadow.Plain)
        self.vertLine3.setFrameShape(QFrame.Shape.VLine)

        self.controlsFirstVlay.addWidget(self.vertLine3)

        self.generalSettingsVLayout = QVBoxLayout()
        self.generalSettingsVLayout.setObjectName(u"generalSettingsVLayout")
        self.generalSettingsVLayout.setContentsMargins(5, -1, -1, 0)
        self.currFrameTotBuffHw = QWidget(self.controlsFirstVwidget)
        self.currFrameTotBuffHw.setObjectName(u"currFrameTotBuffHw")
        self.currOutOfTotalHLay_2 = QHBoxLayout(self.currFrameTotBuffHw)
        self.currOutOfTotalHLay_2.setObjectName(u"currOutOfTotalHLay_2")
        self.currOutOfTotalHLay_2.setContentsMargins(-1, 0, -1, 0)
        self.currFrameTotBuffLabel1 = QLabel(self.currFrameTotBuffHw)
        self.currFrameTotBuffLabel1.setObjectName(u"currFrameTotBuffLabel1")

        self.currOutOfTotalHLay_2.addWidget(self.currFrameTotBuffLabel1)

        self.currFrameLEdit = QLineEdit(self.currFrameTotBuffHw)
        self.currFrameLEdit.setObjectName(u"currFrameLEdit")
        sizePolicy5.setHeightForWidth(self.currFrameLEdit.sizePolicy().hasHeightForWidth())
        self.currFrameLEdit.setSizePolicy(sizePolicy5)
        self.currFrameLEdit.setMaximumSize(QSize(80, 16777215))

        self.currOutOfTotalHLay_2.addWidget(self.currFrameLEdit)

        self.totalNumFramesBuffLabel = QLabel(self.currFrameTotBuffHw)
        self.totalNumFramesBuffLabel.setObjectName(u"totalNumFramesBuffLabel")

        self.currOutOfTotalHLay_2.addWidget(self.totalNumFramesBuffLabel)


        self.generalSettingsVLayout.addWidget(self.currFrameTotBuffHw)

        self.verticalSpacer = QSpacerItem(20, 40, QSizePolicy.Policy.Minimum, QSizePolicy.Policy.Expanding)

        self.generalSettingsVLayout.addItem(self.verticalSpacer)

        self.verticalLayout_2 = QVBoxLayout()
        self.verticalLayout_2.setObjectName(u"verticalLayout_2")
        self.liveOrPlaybackLabel = QLabel(self.controlsFirstVwidget)
        self.liveOrPlaybackLabel.setObjectName(u"liveOrPlaybackLabel")
        self.liveOrPlaybackLabel.setAlignment(Qt.AlignmentFlag.AlignRight|Qt.AlignmentFlag.AlignTrailing|Qt.AlignmentFlag.AlignVCenter)

        self.verticalLayout_2.addWidget(self.liveOrPlaybackLabel)

        self.infoParamLabel = QLabel(self.controlsFirstVwidget)
        self.infoParamLabel.setObjectName(u"infoParamLabel")
        self.infoParamLabel.setStyleSheet(u"color: #b1b7c0;\n"
"font-size: 10pt;")
        self.infoParamLabel.setAlignment(Qt.AlignmentFlag.AlignRight|Qt.AlignmentFlag.AlignTrailing|Qt.AlignmentFlag.AlignVCenter)

        self.verticalLayout_2.addWidget(self.infoParamLabel)


        self.generalSettingsVLayout.addLayout(self.verticalLayout_2)

        self.seqNumTimeLabel = QLabel(self.controlsFirstVwidget)
        self.seqNumTimeLabel.setObjectName(u"seqNumTimeLabel")
        self.seqNumTimeLabel.setStyleSheet(u"color: #b1b7c0;\n"
"font-size: 10pt;")
        self.seqNumTimeLabel.setAlignment(Qt.AlignmentFlag.AlignBottom|Qt.AlignmentFlag.AlignRight|Qt.AlignmentFlag.AlignTrailing)

        self.generalSettingsVLayout.addWidget(self.seqNumTimeLabel)

        self.horizontalLayout_3 = QHBoxLayout()
        self.horizontalLayout_3.setObjectName(u"horizontalLayout_3")
        self.horizontalLayout_3.setContentsMargins(-1, -1, 0, -1)

        self.generalSettingsVLayout.addLayout(self.horizontalLayout_3)


        self.controlsFirstVlay.addLayout(self.generalSettingsVLayout)


        self.verticalLayout.addWidget(self.controlsFirstVwidget)

        self.verticalLayout.setStretch(0, 6)
        self.verticalLayout.setStretch(1, 3)
        self.verticalLayout.setStretch(2, 1)
        MainWindow.setCentralWidget(self.centralArea)

        self.retranslateUi(MainWindow)

        QMetaObject.connectSlotsByName(MainWindow)
    # setupUi

    def retranslateUi(self, MainWindow):
        MainWindow.setWindowTitle(QCoreApplication.translate("MainWindow", u"Presence2D", None))
        self.hotkeyLabel.setText(QCoreApplication.translate("MainWindow", u"<html><head/><body><p>ShortcutKeys</p><p>MoreKeys</p></body></html>", None))
        self.logoLabel.setText(QCoreApplication.translate("MainWindow", u"Logo", None))
        self.SektorPlotLabel.setText(QCoreApplication.translate("MainWindow", u"Sector Plot Settings", None))
        self.trailBwdLabel.setText(QCoreApplication.translate("MainWindow", u"Past trail count", None))
        self.trailFwdLabel.setText(QCoreApplication.translate("MainWindow", u"Future trail count", None))
        self.invertTopPlotBtn.setText(QCoreApplication.translate("MainWindow", u"Invert Top View", None))
        self.showFovLinesCheckBox.setText(QCoreApplication.translate("MainWindow", u"FOV lines", None))
        self.showXYcheckBox.setText(QCoreApplication.translate("MainWindow", u"XY-Coordinates", None))
        self.PowerPlotLabel.setText(QCoreApplication.translate("MainWindow", u"Power Plot Settings", None))
        self.rangeMaxLabel.setText(QCoreApplication.translate("MainWindow", u"Range max:", None))
        self.rangeMaxUnitLabel.setText(QCoreApplication.translate("MainWindow", u"m", None))
        self.rangeMinLabel.setText(QCoreApplication.translate("MainWindow", u"Range min: ", None))
        self.rangeMinUnitLabel.setText(QCoreApplication.translate("MainWindow", u"m", None))
        self.powerMaxLabel.setText(QCoreApplication.translate("MainWindow", u"Power max:", None))
        self.rangeMinUnitLabel_2.setText("")
        self.powerMinLabel.setText(QCoreApplication.translate("MainWindow", u"Power min:", None))
        self.rangeMinUnitLabel_3.setText("")
        self.TimePlotSettingsLabel.setText(QCoreApplication.translate("MainWindow", u"Time Plots Settings", None))
        self.label_2.setText(QCoreApplication.translate("MainWindow", u"Choose plot view", None))
        self.label.setText(QCoreApplication.translate("MainWindow", u"History (s)", None))
        self.resetLimitsBtn.setText(QCoreApplication.translate("MainWindow", u"Reset Limits", None))
        self.currFrameTotBuffLabel1.setText(QCoreApplication.translate("MainWindow", u"Current plot / total buffered", None))
        self.totalNumFramesBuffLabel.setText(QCoreApplication.translate("MainWindow", u"/ total buff", None))
        self.liveOrPlaybackLabel.setText(QCoreApplication.translate("MainWindow", u"Live", None))
        self.infoParamLabel.setText(QCoreApplication.translate("MainWindow", u"infoParams", None))
        self.seqNumTimeLabel.setText(QCoreApplication.translate("MainWindow", u"SeqNumTime", None))
    # retranslateUi

