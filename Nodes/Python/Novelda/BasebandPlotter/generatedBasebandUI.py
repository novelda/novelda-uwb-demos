# -*- coding: utf-8 -*-

################################################################################
## Form generated from reading UI file 'basebandDesignerUINkGudo.ui'
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

class Ui_BasebandUIwin(object):
    def setupUi(self, BasebandUIwin):
        if not BasebandUIwin.objectName():
            BasebandUIwin.setObjectName(u"BasebandUIwin")
        BasebandUIwin.resize(1107, 782)
        self.centralwidget = QWidget(BasebandUIwin)
        self.centralwidget.setObjectName(u"centralwidget")
        self.firstMainVerticalLay = QVBoxLayout(self.centralwidget)
        self.firstMainVerticalLay.setObjectName(u"firstMainVerticalLay")
        self.firstMainVerticalLay.setContentsMargins(-1, 0, -1, 0)
        self.plotGridWidget = QWidget(self.centralwidget)
        self.plotGridWidget.setObjectName(u"plotGridWidget")
        sizePolicy = QSizePolicy(QSizePolicy.Policy.Preferred, QSizePolicy.Policy.Expanding)
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(98)
        sizePolicy.setHeightForWidth(self.plotGridWidget.sizePolicy().hasHeightForWidth())
        self.plotGridWidget.setSizePolicy(sizePolicy)
        self.plotGridLayout = QGridLayout(self.plotGridWidget)
        self.plotGridLayout.setSpacing(3)
        self.plotGridLayout.setObjectName(u"plotGridLayout")
        self.plotGridLayout.setContentsMargins(2, 0, 2, 0)

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
        sizePolicy2 = QSizePolicy(QSizePolicy.Policy.Maximum, QSizePolicy.Policy.Preferred)
        sizePolicy2.setHorizontalStretch(0)
        sizePolicy2.setVerticalStretch(0)
        sizePolicy2.setHeightForWidth(self.limitsAndResetVwidget.sizePolicy().hasHeightForWidth())
        self.limitsAndResetVwidget.setSizePolicy(sizePolicy2)
        self.verticalLayout_2 = QVBoxLayout(self.limitsAndResetVwidget)
        self.verticalLayout_2.setSpacing(0)
        self.verticalLayout_2.setObjectName(u"verticalLayout_2")
        self.verticalLayout_2.setContentsMargins(0, 0, 0, 10)
        self.rangeMaxHwidget = QWidget(self.limitsAndResetVwidget)
        self.rangeMaxHwidget.setObjectName(u"rangeMaxHwidget")
        self.rangeMaxHLay = QHBoxLayout(self.rangeMaxHwidget)
        self.rangeMaxHLay.setObjectName(u"rangeMaxHLay")
        self.rangeMaxHLay.setContentsMargins(-1, 0, -1, 0)
        self.rangeMaxLabel = QLabel(self.rangeMaxHwidget)
        self.rangeMaxLabel.setObjectName(u"rangeMaxLabel")
        sizePolicy3 = QSizePolicy(QSizePolicy.Policy.Preferred, QSizePolicy.Policy.Preferred)
        sizePolicy3.setHorizontalStretch(0)
        sizePolicy3.setVerticalStretch(0)
        sizePolicy3.setHeightForWidth(self.rangeMaxLabel.sizePolicy().hasHeightForWidth())
        self.rangeMaxLabel.setSizePolicy(sizePolicy3)
        self.rangeMaxLabel.setMinimumSize(QSize(63, 0))

        self.rangeMaxHLay.addWidget(self.rangeMaxLabel)

        self.rangeMaxLEdit = QLineEdit(self.rangeMaxHwidget)
        self.rangeMaxLEdit.setObjectName(u"rangeMaxLEdit")
        sizePolicy4 = QSizePolicy(QSizePolicy.Policy.Minimum, QSizePolicy.Policy.Fixed)
        sizePolicy4.setHorizontalStretch(0)
        sizePolicy4.setVerticalStretch(0)
        sizePolicy4.setHeightForWidth(self.rangeMaxLEdit.sizePolicy().hasHeightForWidth())
        self.rangeMaxLEdit.setSizePolicy(sizePolicy4)
        self.rangeMaxLEdit.setMaximumSize(QSize(100, 16777215))

        self.rangeMaxHLay.addWidget(self.rangeMaxLEdit)

        self.rangeMaxUnitLabel = QLabel(self.rangeMaxHwidget)
        self.rangeMaxUnitLabel.setObjectName(u"rangeMaxUnitLabel")

        self.rangeMaxHLay.addWidget(self.rangeMaxUnitLabel)

        self.horizontalSpacer = QSpacerItem(40, 20, QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Minimum)

        self.rangeMaxHLay.addItem(self.horizontalSpacer)


        self.verticalLayout_2.addWidget(self.rangeMaxHwidget)

        self.rangeMinHwidget = QWidget(self.limitsAndResetVwidget)
        self.rangeMinHwidget.setObjectName(u"rangeMinHwidget")
        self.rangeMinHLay = QHBoxLayout(self.rangeMinHwidget)
        self.rangeMinHLay.setObjectName(u"rangeMinHLay")
        self.rangeMinHLay.setContentsMargins(-1, 2, -1, 0)
        self.rangeMinLabel = QLabel(self.rangeMinHwidget)
        self.rangeMinLabel.setObjectName(u"rangeMinLabel")
        self.rangeMinLabel.setMinimumSize(QSize(63, 0))

        self.rangeMinHLay.addWidget(self.rangeMinLabel)

        self.rangeMinLEdit = QLineEdit(self.rangeMinHwidget)
        self.rangeMinLEdit.setObjectName(u"rangeMinLEdit")
        sizePolicy4.setHeightForWidth(self.rangeMinLEdit.sizePolicy().hasHeightForWidth())
        self.rangeMinLEdit.setSizePolicy(sizePolicy4)
        self.rangeMinLEdit.setMaximumSize(QSize(100, 16777215))

        self.rangeMinHLay.addWidget(self.rangeMinLEdit)

        self.rangeMinUnitLabel = QLabel(self.rangeMinHwidget)
        self.rangeMinUnitLabel.setObjectName(u"rangeMinUnitLabel")

        self.rangeMinHLay.addWidget(self.rangeMinUnitLabel)

        self.horizontalSpacer_2 = QSpacerItem(40, 20, QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Minimum)

        self.rangeMinHLay.addItem(self.horizontalSpacer_2)


        self.verticalLayout_2.addWidget(self.rangeMinHwidget)

        self.dopplerMaxHw = QWidget(self.limitsAndResetVwidget)
        self.dopplerMaxHw.setObjectName(u"dopplerMaxHw")
        self.dopplerMaxHlay = QHBoxLayout(self.dopplerMaxHw)
        self.dopplerMaxHlay.setObjectName(u"dopplerMaxHlay")
        self.dopplerMaxHlay.setContentsMargins(-1, 2, -1, 0)
        self.powerMaxLabel = QLabel(self.dopplerMaxHw)
        self.powerMaxLabel.setObjectName(u"powerMaxLabel")
        sizePolicy3.setHeightForWidth(self.powerMaxLabel.sizePolicy().hasHeightForWidth())
        self.powerMaxLabel.setSizePolicy(sizePolicy3)
        self.powerMaxLabel.setMinimumSize(QSize(63, 0))

        self.dopplerMaxHlay.addWidget(self.powerMaxLabel)

        self.powerMaxLEdit = QLineEdit(self.dopplerMaxHw)
        self.powerMaxLEdit.setObjectName(u"powerMaxLEdit")
        sizePolicy4.setHeightForWidth(self.powerMaxLEdit.sizePolicy().hasHeightForWidth())
        self.powerMaxLEdit.setSizePolicy(sizePolicy4)
        self.powerMaxLEdit.setMaximumSize(QSize(100, 16777215))

        self.dopplerMaxHlay.addWidget(self.powerMaxLEdit)

        self.horizontalSpacer_3 = QSpacerItem(40, 20, QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Minimum)

        self.dopplerMaxHlay.addItem(self.horizontalSpacer_3)


        self.verticalLayout_2.addWidget(self.dopplerMaxHw)

        self.powerMinHwidget = QWidget(self.limitsAndResetVwidget)
        self.powerMinHwidget.setObjectName(u"powerMinHwidget")
        self.powerMaxHlay = QHBoxLayout(self.powerMinHwidget)
        self.powerMaxHlay.setObjectName(u"powerMaxHlay")
        self.powerMaxHlay.setContentsMargins(-1, 2, -1, 0)
        self.powerMinLabel = QLabel(self.powerMinHwidget)
        self.powerMinLabel.setObjectName(u"powerMinLabel")
        sizePolicy3.setHeightForWidth(self.powerMinLabel.sizePolicy().hasHeightForWidth())
        self.powerMinLabel.setSizePolicy(sizePolicy3)
        self.powerMinLabel.setMinimumSize(QSize(63, 0))

        self.powerMaxHlay.addWidget(self.powerMinLabel)

        self.powerMinLEdit = QLineEdit(self.powerMinHwidget)
        self.powerMinLEdit.setObjectName(u"powerMinLEdit")
        sizePolicy4.setHeightForWidth(self.powerMinLEdit.sizePolicy().hasHeightForWidth())
        self.powerMinLEdit.setSizePolicy(sizePolicy4)
        self.powerMinLEdit.setMaximumSize(QSize(100, 16777215))

        self.powerMaxHlay.addWidget(self.powerMinLEdit)

        self.horizontalSpacer_4 = QSpacerItem(20, 20, QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Minimum)

        self.powerMaxHlay.addItem(self.horizontalSpacer_4)


        self.verticalLayout_2.addWidget(self.powerMinHwidget)


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
        sizePolicy4.setHeightForWidth(self.currFrameLEdit.sizePolicy().hasHeightForWidth())
        self.currFrameLEdit.setSizePolicy(sizePolicy4)
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

        self.linearScaleCheckbox = QCheckBox(self.parentWcurrframeResetBtn)
        self.linearScaleCheckbox.setObjectName(u"linearScaleCheckbox")

        self.firstCurrFrameResetVLay.addWidget(self.linearScaleCheckbox)

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

        BasebandUIwin.setCentralWidget(self.centralwidget)

        self.retranslateUi(BasebandUIwin)

        QMetaObject.connectSlotsByName(BasebandUIwin)
    # setupUi

    def retranslateUi(self, BasebandUIwin):
        BasebandUIwin.setWindowTitle(QCoreApplication.translate("BasebandUIwin", u"Baseband Plotter", None))
        self.logoLabel.setText(QCoreApplication.translate("BasebandUIwin", u"Logo", None))
        self.hotkeyLabel.setText(QCoreApplication.translate("BasebandUIwin", u"<html><head/><body><p>ShortcutKeys</p><p>MoreKeys</p></body></html>", None))
        self.liveOrPlaybackLabel.setText(QCoreApplication.translate("BasebandUIwin", u"Live", None))
        self.infoParamLabel.setText(QCoreApplication.translate("BasebandUIwin", u"infoParams", None))
        self.rangeMaxLabel.setText(QCoreApplication.translate("BasebandUIwin", u"Range max:", None))
        self.rangeMaxUnitLabel.setText(QCoreApplication.translate("BasebandUIwin", u"m", None))
        self.rangeMinLabel.setText(QCoreApplication.translate("BasebandUIwin", u"Range min:", None))
        self.rangeMinUnitLabel.setText(QCoreApplication.translate("BasebandUIwin", u"m", None))
        self.powerMaxLabel.setText(QCoreApplication.translate("BasebandUIwin", u"Power max:", None))
        self.powerMinLabel.setText(QCoreApplication.translate("BasebandUIwin", u"Power max:", None))
        self.currFrameTotBuffLabel1.setText(QCoreApplication.translate("BasebandUIwin", u"Current plot / total buffered", None))
        self.totalNumFramesBuffLabel.setText(QCoreApplication.translate("BasebandUIwin", u"/ total buff", None))
        self.resetLimitsBtn.setText(QCoreApplication.translate("BasebandUIwin", u"Reset Limits", None))
        self.linearScaleCheckbox.setText(QCoreApplication.translate("BasebandUIwin", u"Linear scale", None))
        self.seqNumTimeLabel.setText(QCoreApplication.translate("BasebandUIwin", u"SeqNumTime", None))
    # retranslateUi

