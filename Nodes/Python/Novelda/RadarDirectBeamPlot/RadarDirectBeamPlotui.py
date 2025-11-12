# -*- coding: utf-8 -*-

################################################################################
## Form generated from reading UI file 'RadarDirectBeamDesignerfXuIew.ui'
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
from PySide6.QtWidgets import (QApplication, QCheckBox, QGridLayout, QHBoxLayout,
    QLabel, QLineEdit, QMainWindow, QPushButton,
    QSizePolicy, QSpacerItem, QVBoxLayout, QWidget)

class Ui_multiRangeDoppWin(object):
    def setupUi(self, multiRangeDoppWin):
        if not multiRangeDoppWin.objectName():
            multiRangeDoppWin.setObjectName(u"multiRangeDoppWin")
        multiRangeDoppWin.resize(1153, 858)
        self.centralwidget = QWidget(multiRangeDoppWin)
        self.centralwidget.setObjectName(u"centralwidget")
        self.firstMainVerticalLay = QVBoxLayout(self.centralwidget)
        self.firstMainVerticalLay.setSpacing(3)
        self.firstMainVerticalLay.setObjectName(u"firstMainVerticalLay")
        self.firstMainVerticalLay.setContentsMargins(0, 0, 0, 0)
        self.plotGridWidget = QWidget(self.centralwidget)
        self.plotGridWidget.setObjectName(u"plotGridWidget")
        sizePolicy = QSizePolicy(QSizePolicy.Policy.Preferred, QSizePolicy.Policy.Expanding)
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(98)
        sizePolicy.setHeightForWidth(self.plotGridWidget.sizePolicy().hasHeightForWidth())
        self.plotGridWidget.setSizePolicy(sizePolicy)
        self.plotGridLayout = QGridLayout(self.plotGridWidget)
        self.plotGridLayout.setSpacing(2)
        self.plotGridLayout.setObjectName(u"plotGridLayout")
        self.plotGridLayout.setContentsMargins(0, 0, 0, 0)

        self.firstMainVerticalLay.addWidget(self.plotGridWidget)

        self.controlsFirstVwidget = QWidget(self.centralwidget)
        self.controlsFirstVwidget.setObjectName(u"controlsFirstVwidget")
        sizePolicy1 = QSizePolicy(QSizePolicy.Policy.Preferred, QSizePolicy.Policy.Preferred)
        sizePolicy1.setHorizontalStretch(0)
        sizePolicy1.setVerticalStretch(5)
        sizePolicy1.setHeightForWidth(self.controlsFirstVwidget.sizePolicy().hasHeightForWidth())
        self.controlsFirstVwidget.setSizePolicy(sizePolicy1)
        self.controlsFirstVlay = QHBoxLayout(self.controlsFirstVwidget)
        self.controlsFirstVlay.setObjectName(u"controlsFirstVlay")
        self.controlsFirstVlay.setContentsMargins(-1, 0, -1, 0)
        self.logoLabel = QLabel(self.controlsFirstVwidget)
        self.logoLabel.setObjectName(u"logoLabel")

        self.controlsFirstVlay.addWidget(self.logoLabel)

        self.horizontalSpacer_5 = QSpacerItem(40, 20, QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Minimum)

        self.controlsFirstVlay.addItem(self.horizontalSpacer_5)

        self.hotkeyLabel = QLabel(self.controlsFirstVwidget)
        self.hotkeyLabel.setObjectName(u"hotkeyLabel")
        self.hotkeyLabel.setStyleSheet(u"color: #b1b7c0;\n"
"font-size: 10pt;")
        self.hotkeyLabel.setAlignment(Qt.AlignmentFlag.AlignLeading|Qt.AlignmentFlag.AlignLeft|Qt.AlignmentFlag.AlignTop)
        self.hotkeyLabel.setWordWrap(False)
        self.hotkeyLabel.setTextInteractionFlags(Qt.TextInteractionFlag.NoTextInteraction)

        self.controlsFirstVlay.addWidget(self.hotkeyLabel)

        self.horizontalSpacer_7 = QSpacerItem(40, 20, QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Minimum)

        self.controlsFirstVlay.addItem(self.horizontalSpacer_7)

        self.liveOrPlayInfoVwidget = QWidget(self.controlsFirstVwidget)
        self.liveOrPlayInfoVwidget.setObjectName(u"liveOrPlayInfoVwidget")
        self.liveOrPlayVLay = QVBoxLayout(self.liveOrPlayInfoVwidget)
        self.liveOrPlayVLay.setSpacing(5)
        self.liveOrPlayVLay.setObjectName(u"liveOrPlayVLay")
        self.liveOrPlayVLay.setContentsMargins(5, 0, 5, 5)
        self.liveOrPlaybackLabel = QLabel(self.liveOrPlayInfoVwidget)
        self.liveOrPlaybackLabel.setObjectName(u"liveOrPlaybackLabel")
        self.liveOrPlaybackLabel.setAlignment(Qt.AlignmentFlag.AlignLeading|Qt.AlignmentFlag.AlignLeft|Qt.AlignmentFlag.AlignTop)

        self.liveOrPlayVLay.addWidget(self.liveOrPlaybackLabel)

        self.infoParamLabel = QLabel(self.liveOrPlayInfoVwidget)
        self.infoParamLabel.setObjectName(u"infoParamLabel")
        self.infoParamLabel.setStyleSheet(u"color: #b1b7c0;\n"
"font-size: 10pt;")
        self.infoParamLabel.setAlignment(Qt.AlignmentFlag.AlignLeading|Qt.AlignmentFlag.AlignLeft|Qt.AlignmentFlag.AlignTop)

        self.liveOrPlayVLay.addWidget(self.infoParamLabel)

        self.verticalSpacer_2 = QSpacerItem(20, 40, QSizePolicy.Policy.Minimum, QSizePolicy.Policy.Expanding)

        self.liveOrPlayVLay.addItem(self.verticalSpacer_2)


        self.controlsFirstVlay.addWidget(self.liveOrPlayInfoVwidget)

        self.limitsAndResetVwidget = QWidget(self.controlsFirstVwidget)
        self.limitsAndResetVwidget.setObjectName(u"limitsAndResetVwidget")
        sizePolicy2 = QSizePolicy(QSizePolicy.Policy.Preferred, QSizePolicy.Policy.Preferred)
        sizePolicy2.setHorizontalStretch(0)
        sizePolicy2.setVerticalStretch(0)
        sizePolicy2.setHeightForWidth(self.limitsAndResetVwidget.sizePolicy().hasHeightForWidth())
        self.limitsAndResetVwidget.setSizePolicy(sizePolicy2)
        self.verticalLayout_2 = QVBoxLayout(self.limitsAndResetVwidget)
        self.verticalLayout_2.setSpacing(0)
        self.verticalLayout_2.setObjectName(u"verticalLayout_2")
        self.verticalLayout_2.setContentsMargins(0, 2, 0, 10)
        self.rangeMinHwidget = QWidget(self.limitsAndResetVwidget)
        self.rangeMinHwidget.setObjectName(u"rangeMinHwidget")
        self.rangeMinHLay = QHBoxLayout(self.rangeMinHwidget)
        self.rangeMinHLay.setObjectName(u"rangeMinHLay")
        self.rangeMinHLay.setContentsMargins(-1, 2, -1, 0)
        self.rangeMinLabel = QLabel(self.rangeMinHwidget)
        self.rangeMinLabel.setObjectName(u"rangeMinLabel")
        self.rangeMinLabel.setMinimumSize(QSize(70, 0))

        self.rangeMinHLay.addWidget(self.rangeMinLabel)

        self.rangeMinLEdit = QLineEdit(self.rangeMinHwidget)
        self.rangeMinLEdit.setObjectName(u"rangeMinLEdit")
        sizePolicy3 = QSizePolicy(QSizePolicy.Policy.Minimum, QSizePolicy.Policy.Fixed)
        sizePolicy3.setHorizontalStretch(0)
        sizePolicy3.setVerticalStretch(0)
        sizePolicy3.setHeightForWidth(self.rangeMinLEdit.sizePolicy().hasHeightForWidth())
        self.rangeMinLEdit.setSizePolicy(sizePolicy3)
        self.rangeMinLEdit.setMaximumSize(QSize(80, 16777215))

        self.rangeMinHLay.addWidget(self.rangeMinLEdit)

        self.rangeMaxLabel = QLabel(self.rangeMinHwidget)
        self.rangeMaxLabel.setObjectName(u"rangeMaxLabel")
        sizePolicy4 = QSizePolicy(QSizePolicy.Policy.Maximum, QSizePolicy.Policy.Preferred)
        sizePolicy4.setHorizontalStretch(0)
        sizePolicy4.setVerticalStretch(0)
        sizePolicy4.setHeightForWidth(self.rangeMaxLabel.sizePolicy().hasHeightForWidth())
        self.rangeMaxLabel.setSizePolicy(sizePolicy4)
        self.rangeMaxLabel.setMinimumSize(QSize(0, 0))

        self.rangeMinHLay.addWidget(self.rangeMaxLabel)

        self.rangeMaxLEdit = QLineEdit(self.rangeMinHwidget)
        self.rangeMaxLEdit.setObjectName(u"rangeMaxLEdit")
        sizePolicy3.setHeightForWidth(self.rangeMaxLEdit.sizePolicy().hasHeightForWidth())
        self.rangeMaxLEdit.setSizePolicy(sizePolicy3)
        self.rangeMaxLEdit.setMaximumSize(QSize(80, 16777215))

        self.rangeMinHLay.addWidget(self.rangeMaxLEdit)

        self.horizontalSpacer_2 = QSpacerItem(40, 20, QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Minimum)

        self.rangeMinHLay.addItem(self.horizontalSpacer_2)


        self.verticalLayout_2.addWidget(self.rangeMinHwidget)

        self.powerMinHwidget = QWidget(self.limitsAndResetVwidget)
        self.powerMinHwidget.setObjectName(u"powerMinHwidget")
        self.rangeMinHLay_2 = QHBoxLayout(self.powerMinHwidget)
        self.rangeMinHLay_2.setObjectName(u"rangeMinHLay_2")
        self.rangeMinHLay_2.setContentsMargins(-1, 2, -1, 0)
        self.powerMinLabel = QLabel(self.powerMinHwidget)
        self.powerMinLabel.setObjectName(u"powerMinLabel")
        self.powerMinLabel.setMinimumSize(QSize(70, 0))

        self.rangeMinHLay_2.addWidget(self.powerMinLabel)

        self.powerMinLEdit = QLineEdit(self.powerMinHwidget)
        self.powerMinLEdit.setObjectName(u"powerMinLEdit")
        sizePolicy3.setHeightForWidth(self.powerMinLEdit.sizePolicy().hasHeightForWidth())
        self.powerMinLEdit.setSizePolicy(sizePolicy3)
        self.powerMinLEdit.setMaximumSize(QSize(80, 16777215))

        self.rangeMinHLay_2.addWidget(self.powerMinLEdit)

        self.powerMaxLabel = QLabel(self.powerMinHwidget)
        self.powerMaxLabel.setObjectName(u"powerMaxLabel")
        sizePolicy4.setHeightForWidth(self.powerMaxLabel.sizePolicy().hasHeightForWidth())
        self.powerMaxLabel.setSizePolicy(sizePolicy4)
        self.powerMaxLabel.setMinimumSize(QSize(0, 0))

        self.rangeMinHLay_2.addWidget(self.powerMaxLabel)

        self.powerMaxLEdit = QLineEdit(self.powerMinHwidget)
        self.powerMaxLEdit.setObjectName(u"powerMaxLEdit")
        sizePolicy3.setHeightForWidth(self.powerMaxLEdit.sizePolicy().hasHeightForWidth())
        self.powerMaxLEdit.setSizePolicy(sizePolicy3)
        self.powerMaxLEdit.setMaximumSize(QSize(80, 16777215))

        self.rangeMinHLay_2.addWidget(self.powerMaxLEdit)

        self.horizontalSpacer_3 = QSpacerItem(40, 20, QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Minimum)

        self.rangeMinHLay_2.addItem(self.horizontalSpacer_3)


        self.verticalLayout_2.addWidget(self.powerMinHwidget)

        self.angleMinMaxHw = QWidget(self.limitsAndResetVwidget)
        self.angleMinMaxHw.setObjectName(u"angleMinMaxHw")
        self.angleMinMaxHl = QHBoxLayout(self.angleMinMaxHw)
        self.angleMinMaxHl.setObjectName(u"angleMinMaxHl")
        self.angleMinMaxHl.setContentsMargins(-1, 2, -1, 0)
        self.angleMinLabel = QLabel(self.angleMinMaxHw)
        self.angleMinLabel.setObjectName(u"angleMinLabel")
        self.angleMinLabel.setMinimumSize(QSize(70, 0))

        self.angleMinMaxHl.addWidget(self.angleMinLabel)

        self.angleMinLEdit = QLineEdit(self.angleMinMaxHw)
        self.angleMinLEdit.setObjectName(u"angleMinLEdit")
        sizePolicy3.setHeightForWidth(self.angleMinLEdit.sizePolicy().hasHeightForWidth())
        self.angleMinLEdit.setSizePolicy(sizePolicy3)
        self.angleMinLEdit.setMaximumSize(QSize(80, 16777215))

        self.angleMinMaxHl.addWidget(self.angleMinLEdit)

        self.angleMaxLabel = QLabel(self.angleMinMaxHw)
        self.angleMaxLabel.setObjectName(u"angleMaxLabel")
        sizePolicy4.setHeightForWidth(self.angleMaxLabel.sizePolicy().hasHeightForWidth())
        self.angleMaxLabel.setSizePolicy(sizePolicy4)
        self.angleMaxLabel.setMinimumSize(QSize(0, 0))

        self.angleMinMaxHl.addWidget(self.angleMaxLabel)

        self.angleMaxLEdit = QLineEdit(self.angleMinMaxHw)
        self.angleMaxLEdit.setObjectName(u"angleMaxLEdit")
        sizePolicy3.setHeightForWidth(self.angleMaxLEdit.sizePolicy().hasHeightForWidth())
        self.angleMaxLEdit.setSizePolicy(sizePolicy3)
        self.angleMaxLEdit.setMaximumSize(QSize(80, 16777215))

        self.angleMinMaxHl.addWidget(self.angleMaxLEdit)

        self.horizontalSpacer_4 = QSpacerItem(40, 20, QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Minimum)

        self.angleMinMaxHl.addItem(self.horizontalSpacer_4)


        self.verticalLayout_2.addWidget(self.angleMinMaxHw)

        self.slicesToPlotHw = QWidget(self.limitsAndResetVwidget)
        self.slicesToPlotHw.setObjectName(u"slicesToPlotHw")
        self.horizontalLayout = QHBoxLayout(self.slicesToPlotHw)
        self.horizontalLayout.setObjectName(u"horizontalLayout")
        self.anglePickBtn = QPushButton(self.slicesToPlotHw)
        self.anglePickBtn.setObjectName(u"anglePickBtn")

        self.horizontalLayout.addWidget(self.anglePickBtn)

        self.rangePickBtn = QPushButton(self.slicesToPlotHw)
        self.rangePickBtn.setObjectName(u"rangePickBtn")

        self.horizontalLayout.addWidget(self.rangePickBtn)

        self.threshPickBtn = QPushButton(self.slicesToPlotHw)
        self.threshPickBtn.setObjectName(u"threshPickBtn")

        self.horizontalLayout.addWidget(self.threshPickBtn)


        self.verticalLayout_2.addWidget(self.slicesToPlotHw)


        self.controlsFirstVlay.addWidget(self.limitsAndResetVwidget)

        self.parentWcurrframeResetBtn = QWidget(self.controlsFirstVwidget)
        self.parentWcurrframeResetBtn.setObjectName(u"parentWcurrframeResetBtn")
        self.firstCurrFrameResetVLay = QVBoxLayout(self.parentWcurrframeResetBtn)
        self.firstCurrFrameResetVLay.setObjectName(u"firstCurrFrameResetVLay")
        self.firstCurrFrameResetVLay.setContentsMargins(-1, 0, -1, 5)
        self.currFrameTotBuffHw = QWidget(self.parentWcurrframeResetBtn)
        self.currFrameTotBuffHw.setObjectName(u"currFrameTotBuffHw")
        self.currOutOfTotalHLay = QHBoxLayout(self.currFrameTotBuffHw)
        self.currOutOfTotalHLay.setObjectName(u"currOutOfTotalHLay")
        self.currOutOfTotalHLay.setContentsMargins(-1, 0, -1, 0)
        self.currFrameTotBuffLabel1 = QLabel(self.currFrameTotBuffHw)
        self.currFrameTotBuffLabel1.setObjectName(u"currFrameTotBuffLabel1")

        self.currOutOfTotalHLay.addWidget(self.currFrameTotBuffLabel1)

        self.currFrameLEdit = QLineEdit(self.currFrameTotBuffHw)
        self.currFrameLEdit.setObjectName(u"currFrameLEdit")
        sizePolicy3.setHeightForWidth(self.currFrameLEdit.sizePolicy().hasHeightForWidth())
        self.currFrameLEdit.setSizePolicy(sizePolicy3)
        self.currFrameLEdit.setMaximumSize(QSize(80, 16777215))

        self.currOutOfTotalHLay.addWidget(self.currFrameLEdit)

        self.totalNumFramesBuffLabel = QLabel(self.currFrameTotBuffHw)
        self.totalNumFramesBuffLabel.setObjectName(u"totalNumFramesBuffLabel")

        self.currOutOfTotalHLay.addWidget(self.totalNumFramesBuffLabel)


        self.firstCurrFrameResetVLay.addWidget(self.currFrameTotBuffHw)

        self.resetLimitsBtn = QPushButton(self.parentWcurrframeResetBtn)
        self.resetLimitsBtn.setObjectName(u"resetLimitsBtn")
        self.resetLimitsBtn.setMaximumSize(QSize(100, 16777215))

        self.firstCurrFrameResetVLay.addWidget(self.resetLimitsBtn)

        self.checkBoxesHw = QWidget(self.parentWcurrframeResetBtn)
        self.checkBoxesHw.setObjectName(u"checkBoxesHw")
        self.horizontalLayout_2 = QHBoxLayout(self.checkBoxesHw)
        self.horizontalLayout_2.setObjectName(u"horizontalLayout_2")
        self.checkBoxPizzaOrInterp = QCheckBox(self.checkBoxesHw)
        self.checkBoxPizzaOrInterp.setObjectName(u"checkBoxPizzaOrInterp")

        self.horizontalLayout_2.addWidget(self.checkBoxPizzaOrInterp)

        self.topDownCheckbox = QCheckBox(self.checkBoxesHw)
        self.topDownCheckbox.setObjectName(u"topDownCheckbox")

        self.horizontalLayout_2.addWidget(self.topDownCheckbox)


        self.firstCurrFrameResetVLay.addWidget(self.checkBoxesHw)

        self.verticalSpacer = QSpacerItem(20, 40, QSizePolicy.Policy.Minimum, QSizePolicy.Policy.Expanding)

        self.firstCurrFrameResetVLay.addItem(self.verticalSpacer)


        self.controlsFirstVlay.addWidget(self.parentWcurrframeResetBtn)

        self.seqNumTimeLabel = QLabel(self.controlsFirstVwidget)
        self.seqNumTimeLabel.setObjectName(u"seqNumTimeLabel")
        self.seqNumTimeLabel.setStyleSheet(u"color: #b1b7c0;\n"
"font-size: 10pt;")
        self.seqNumTimeLabel.setAlignment(Qt.AlignmentFlag.AlignLeading|Qt.AlignmentFlag.AlignLeft|Qt.AlignmentFlag.AlignTop)

        self.controlsFirstVlay.addWidget(self.seqNumTimeLabel)

        self.horizontalSpacer_6 = QSpacerItem(40, 20, QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Minimum)

        self.controlsFirstVlay.addItem(self.horizontalSpacer_6)


        self.firstMainVerticalLay.addWidget(self.controlsFirstVwidget)

        multiRangeDoppWin.setCentralWidget(self.centralwidget)

        self.retranslateUi(multiRangeDoppWin)

        QMetaObject.connectSlotsByName(multiRangeDoppWin)
    # setupUi

    def retranslateUi(self, multiRangeDoppWin):
        multiRangeDoppWin.setWindowTitle(QCoreApplication.translate("multiRangeDoppWin", u"Multi Range-Doppler Plotter", None))
        self.logoLabel.setText(QCoreApplication.translate("multiRangeDoppWin", u"Logo", None))
        self.hotkeyLabel.setText(QCoreApplication.translate("multiRangeDoppWin", u"<html><head/><body><p>ShortcutKeys</p><p>MoreKeys</p></body></html>", None))
        self.liveOrPlaybackLabel.setText(QCoreApplication.translate("multiRangeDoppWin", u"Live", None))
        self.infoParamLabel.setText(QCoreApplication.translate("multiRangeDoppWin", u"infoParams", None))
        self.rangeMinLabel.setText(QCoreApplication.translate("multiRangeDoppWin", u"Range min:", None))
        self.rangeMaxLabel.setText(QCoreApplication.translate("multiRangeDoppWin", u"max:", None))
        self.powerMinLabel.setText(QCoreApplication.translate("multiRangeDoppWin", u"Power min:", None))
        self.powerMaxLabel.setText(QCoreApplication.translate("multiRangeDoppWin", u"max:", None))
        self.angleMinLabel.setText(QCoreApplication.translate("multiRangeDoppWin", u"Angle min:", None))
        self.angleMaxLabel.setText(QCoreApplication.translate("multiRangeDoppWin", u"max:", None))
        self.anglePickBtn.setText(QCoreApplication.translate("multiRangeDoppWin", u"Angles to plot", None))
        self.rangePickBtn.setText(QCoreApplication.translate("multiRangeDoppWin", u"Ranges to plot", None))
        self.threshPickBtn.setText(QCoreApplication.translate("multiRangeDoppWin", u"Thresholds", None))
        self.currFrameTotBuffLabel1.setText(QCoreApplication.translate("multiRangeDoppWin", u"Current plot / total buffered", None))
        self.totalNumFramesBuffLabel.setText(QCoreApplication.translate("multiRangeDoppWin", u"/ total buff", None))
        self.resetLimitsBtn.setText(QCoreApplication.translate("multiRangeDoppWin", u"Reset Limits", None))
        self.checkBoxPizzaOrInterp.setText(QCoreApplication.translate("multiRangeDoppWin", u"Show Beam Sectors", None))
        self.topDownCheckbox.setText(QCoreApplication.translate("multiRangeDoppWin", u"Top Down View", None))
        self.seqNumTimeLabel.setText(QCoreApplication.translate("multiRangeDoppWin", u"SeqNumTime", None))
    # retranslateUi

