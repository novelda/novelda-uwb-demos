
# --------------------

import os
from pathlib import Path
import json

import pyx7configuration as X7Config

from PySide6.QtWidgets import QMessageBox, QFileDialog
import PySide6.QtGui as QG
import PySide6.QtCore as QC

from PySide6.QtCore import QLocale
QLocale.setDefault(QLocale(QLocale.English, QLocale.UnitedStates))

from generated_pyx7gui import *

#----------------------
class PyX7GUI(Ui_MainWindow):

    def __init__(self):
        super().__init__()

        self.last_calc_x7config: X7Config.X7Configuration = None

    class AllTheFields:
        def __init__(self):
            self.fps = None
            self.max_range = None
            self.duty_cycle = None
            self.pulse_period = None
            self.antenna_gain = None
            self.number_of_chips = None
            self.tx_channel_sequence = None
            self.rx_mask_sequence = None

    def do_custom_setup(self, MainWindow, app):
        # double, int validators
        self.fpsLEdit.setValidator(QG.QDoubleValidator())
        self.maxRangeLEdit.setValidator(QG.QDoubleValidator())
        self.dutyCycleLEdit.setValidator(QG.QDoubleValidator())
        self.pulsePeriodLEdit.setValidator(QG.QIntValidator())
        self.antennaGainLEdit.setValidator(QG.QDoubleValidator())

        self.findFPSPulePeriodLEdit.setValidator(QG.QIntValidator(0, 1000000))

        # currently only support 1 chip
        self.numChipsLEdit.setText("1")
        self.numChipsLEdit.setReadOnly(True)

        tx_rx_validator = QC.QRegularExpression(r'^[\s*\d+\s*(?:,\s*\d+)\s]$')
        self.txChanLEdit.setValidator(QG.QRegularExpressionValidator(tx_rx_validator))
        self.rxMaskLEdit.setValidator(QG.QRegularExpressionValidator(tx_rx_validator))

        self.populate_preset_files()

        # on preset item click, load values
        self.comboBox.activated.connect(self.load_preset_file)

        # on button press, calculate chip config
        self.calcButton.setText("&Calculate Chip Config")
        self.saveFileButton.setText("&Save")
        self.exportChipButton.setText("&Export Chip Config")
        self.findFPSButton.setText("&Find FPS")

        self.calcButton.clicked.connect(self.calculate_chip_config)
        self.exportChipButton.clicked.connect(self.export_chip_config)

        self.fpsLEdit.setFocus()

        # save new preset file
        self.saveFileButton.clicked.connect(self.save_preset_file)

        # disable editing of output fields
        self.outputTextField.setReadOnly(True)
        self.findFPSoutputField.setReadOnly(True)

        self.set_custom_tab_order()
        self.set_logo_icon_images(MainWindow, app)

        # find valid fps from pulse period
        self.findFPSButton.clicked.connect(self.find_valid_fps_from_pulse_period)
    
    def export_chip_config(self):

        if self.last_calc_x7config is None:
            self.outputTextField.setPlainText("No calculated chip config to export")
            return
        
        x7config = self.last_calc_x7config

        if x7config is None:
            return

        chipConfig = x7config.get_chip_config()

        # default_name = "chip_config.json"
        # start_path = Path(__file__).resolve().parent
        file_name, _ = QFileDialog.getSaveFileName(
            self.centralwidget,
            "Save Chip Config",
            "",
            "JSON files (*.json);;All Files (*)"
        )
        if not file_name:
            return

        export_file = Path(file_name)
        if not export_file.suffix:
            export_file = export_file.with_suffix(".json")

        output_dict = {
            "RadarSource" : {
                "FPS" : str(x7config.fps()),
                "PulsePeriod" : str(chipConfig.pulse_period),
                "MframesPerPulse" : str(chipConfig.mframes_per_pulse),
                "PulsesPerIteration" : str(chipConfig.pulses_per_iteration),
                "IterationsPerFrame" : str(chipConfig.iterations_per_frame),
                "TxPower" : str(chipConfig.tx_power),
                "InterleavedFrames" : str(chipConfig.interleaved_frames),
                "TxChannelSequence" : "{" + ", ".join([str(x) + "u16" for x in chipConfig.tx_channel_sequence]) + "}",
                "RxMaskSequence" : "{" + ", ".join([str(x) + "u16" for x in chipConfig.rx_mask_sequence]) + "}"
            }

        }

        try:
            with open(export_file, "w") as f:
                json.dump(output_dict, f, indent=4)
        except Exception as e:
            self.outputTextField.setPlainText("Error exporting chip config to file, " + str(export_file) + ": " + str(e))
            return

        self.outputTextField.setPlainText("Chip config exported to: " + str(export_file))
    
    def find_valid_fps_from_pulse_period(self):
        try:
            pulse_period = int(self.findFPSPulePeriodLEdit.text())
        except Exception as e:
            self.findFPSoutputField.setPlainText("Error parsing pulse period, please check input value, Exception:\n " + str(e))
            return

        if pulse_period <= 0:
            self.findFPSoutputField.setPlainText("0 = automatic Pulse Period, please enter a positive integer value")
            return

        tempconfig = X7Config.X7Configuration(
            X7Config.X7UserConfiguration(4, 1, 4, 1, 1),
            X7Config.X7TxRxConfiguration([1], [1], 1)
        )

        try:
            valid_fps = tempconfig.find_valid_fps_list_from_pulse_period(pulse_period)

        except Exception as e:
            self.findFPSoutputField.setPlainText("Error finding valid FPS, please check input value, Exception:\n " + str(e))
            return

        # fps_str = ", ".join([str(fps) for fps in valid_fps])
        self.findFPSoutputField.setPlainText(f"Valid FPS for pulse period {pulse_period} is:\n{valid_fps}")

    def set_custom_tab_order(self):
        order = [
            self.saveFileNameLEdit,
            self.saveFileButton,
            self.fpsLEdit,
            self.dutyCycleLEdit,
            self.maxRangeLEdit,
            self.antennaGainLEdit,
            self.pulsePeriodLEdit,
            self.numChipsLEdit,
            self.txChanLEdit,
            self.rxMaskLEdit,
            self.calcButton,
            self.findFPSPulePeriodLEdit,
            self.findFPSButton,
            self.findFPSoutputField,
            self.outputTextField,
        ]

        for a, b in zip(order, order[1:]):
            QWidget.setTabOrder(a, b)
    
    def get_values_from_textfields(self):
        try:
            fps         = float(self.fpsLEdit.text())
            max_range   = float(self.maxRangeLEdit.text())
            duty_cycle  = float(self.dutyCycleLEdit.text())
            pulse_period = int(self.pulsePeriodLEdit.text())
            antenna_gain = float(self.antennaGainLEdit.text())
        except Exception as e:
            self.outputTextField.setPlainText("Error parsing X7UserConfiguration values, please check input, Exception:\n " + str(e))
            return None

        try:
            number_of_chips = int(self.numChipsLEdit.text())
            tx_channel_sequence = json.loads(self.txChanLEdit.text())
            rx_mask_sequence = json.loads(self.rxMaskLEdit.text())

            if len(tx_channel_sequence) != len(rx_mask_sequence):
                self.outputTextField.setPlainText("Error: Tx Channel Sequence and Rx Mask Sequence must have the same length")
                return None

        except Exception as e:
            self.outputTextField.setPlainText("Error parsing TxRx values, please check input, Exception:\n " + str(e))
            return None
        
        all_fields = self.AllTheFields()
        all_fields.fps = fps
        all_fields.max_range = max_range
        all_fields.duty_cycle = duty_cycle
        all_fields.pulse_period = pulse_period
        all_fields.antenna_gain = antenna_gain
        all_fields.number_of_chips = number_of_chips
        all_fields.tx_channel_sequence = tx_channel_sequence
        all_fields.rx_mask_sequence = rx_mask_sequence

        try:
            user_config = X7Config.X7UserConfiguration(
                fps         = fps,
                max_range   = max_range,
                duty_cycle  = duty_cycle,
                pulse_period = pulse_period,
                antenna_gain = antenna_gain
            )
        except Exception as e:
            self.outputTextField.setPlainText("Error creating user config, please check input values, Exception:\n " + str(e))
            return None
        try:
            txrx_config = X7Config.X7TxRxConfiguration(
                number_of_chips = number_of_chips,
                txChannelActiveVec = tx_channel_sequence,
                rxMaskActiveVec = rx_mask_sequence
            )
        except Exception as e:
            self.outputTextField.setPlainText("Error creating Tx/Rx config, please check input values, Exception:\n " + str(e))
            return None

        try:
            x7Config = X7Config.X7Configuration(
                user_config = user_config,
                txrx_config = txrx_config
            )
        except Exception as e:
            self.outputTextField.setPlainText("Error creating full X7 config, please check input values, Exception:\n " + str(e))
            return None
        
        return x7Config, all_fields

    def set_logo_icon_images(self, MainWindow, app):
        icon_fp = Path(__file__).resolve().parent.parent / "Resources" / "Images" / "cropped-NOVELDA-icon-192x192.png"
        icon = QIcon(str(icon_fp))
        MainWindow.setWindowIcon(icon)

        logo_img_fp = Path(__file__).resolve().parent.parent / "Resources" / "Images" / "Novelda_logo_hvit_150dpi.png"
        logo_img = QImage(str(logo_img_fp))

        self.logo_label = QLabel(parent=self.centralwidget)
        self.logo_label.setPixmap(QG.QPixmap.fromImage(logo_img).scaledToWidth(100, QC.Qt.SmoothTransformation))
        self.logo_label.move(14, 550)

        app.setStyle('Fusion')
        pal = QPalette()
        base_bg = QColor("#3A3E44")   # window/background
        alt_bg  = QColor("#787E85")   # alternate
        text_fg = QColor("#FFFFFF")   # text/fg
        field_bg = QColor("#252424")  # input fields

        pal.setColor(QPalette.Window, base_bg)
        pal.setColor(QPalette.Base, field_bg)
        pal.setColor(QPalette.AlternateBase, alt_bg)
        pal.setColor(QPalette.Button, base_bg)
        pal.setColor(QPalette.ToolTipBase, base_bg)

        pal.setColor(QPalette.WindowText, text_fg)
        pal.setColor(QPalette.Text, text_fg)
        pal.setColor(QPalette.ButtonText, text_fg)
        pal.setColor(QPalette.ToolTipText, text_fg)

        app.setPalette(pal)

    def save_preset_file(self):
        preset_dir = Path(__file__).resolve().parent / "Presets"
        if not os.path.exists(preset_dir):
            os.makedirs(preset_dir)

        preset_name = self.saveFileNameLEdit.text().strip()
        if preset_name == "":
            self.outputTextField.setPlainText("Please enter a valid preset name to save")
            return

        if not preset_name.endswith(".json"):
            preset_name += ".json"

        preset_file = preset_dir / preset_name
        if os.path.exists(preset_file):
            # ask for overwrite or cancel
            resp = QMessageBox.question(
                self.centralwidget,
                "Overwrite preset?",
                f"Preset '{preset_name}' already exists.\nDo you want to overwrite it?",
                QMessageBox.Yes | QMessageBox.No,
                QMessageBox.No
            )
            if resp != QMessageBox.Yes:
                self.outputTextField.setPlainText("Save canceled: file already exists.")
                return

        config, all_fields = self.get_values_from_textfields()
        if config is None:
            return

        preset = {
            "X7UserConfiguration" : {
                "FPS"          : all_fields.fps,
                "MaxRange"     : all_fields.max_range,
                "DutyCycle"    : all_fields.duty_cycle,
                "PulsePeriod"  : all_fields.pulse_period,
                "AntennaGain"  : all_fields.antenna_gain
            },
            "X7TxRxConfiguration" : {
                "NumberOfChips"      : all_fields.number_of_chips,
                "TxChannelSequence"  : all_fields.tx_channel_sequence,
                "RxMaskSequence"     : all_fields.rx_mask_sequence
            }
        }

        try:
            with open(preset_file, "w") as f:
                json.dump(preset, f, indent=4)
        except Exception as e:
            self.outputTextField.setPlainText("Error saving preset file, " + str(preset_file) + ": " + str(e))
            return

        self.outputTextField.setPlainText("Preset file saved: " + str(preset_file))

        self.populate_preset_files()
    
    def calculate_chip_config(self):

        x7config, _ = self.get_values_from_textfields()

        if x7config is None:
            return

        chipConfig = x7config.get_chip_config()

        self.outputTextField.setPlainText(str(chipConfig))
        self.last_calc_x7config = x7config


    def load_preset_file(self):

        if self.comboBox.currentText().strip() == "":
            return

        preset_dir = Path(__file__).resolve().parent / "Presets"
        preset_file = preset_dir / self.comboBox.currentText()
        if not os.path.exists(preset_file):
            print("Preset file does not exist: ", preset_file)
            return

        preset = None
        try:
            with open(preset_file, "r") as f:
                preset = json.load(f)
        except Exception as e:
            self.outputTextField.setPlainText("Error loading preset file, " + str(preset_file) + ": " + str(e))
            return

        # load values
        self.fpsLEdit.setText(str(preset["X7UserConfiguration"]["FPS"]))
        self.maxRangeLEdit.setText(str(preset["X7UserConfiguration"]["MaxRange"]))
        self.dutyCycleLEdit.setText(str(preset["X7UserConfiguration"]["DutyCycle"]))
        self.pulsePeriodLEdit.setText(str(preset["X7UserConfiguration"]["PulsePeriod"]))
        self.antennaGainLEdit.setText(str(preset["X7UserConfiguration"]["AntennaGain"]))

        self.numChipsLEdit.setText(str(preset["X7TxRxConfiguration"]["NumberOfChips"]))
        self.txChanLEdit.setText(str(preset["X7TxRxConfiguration"]["TxChannelSequence"]))
        self.rxMaskLEdit.setText(str(preset["X7TxRxConfiguration"]["RxMaskSequence"]))

    def populate_preset_files(self):
        preset_dir = Path(__file__).resolve().parent / "Presets"
        if not os.path.exists(preset_dir):
            os.makedirs(preset_dir)

        files = [f for f in os.listdir(preset_dir) if os.path.isfile(os.path.join(preset_dir, f)) and f.endswith(".json")]

        self.comboBox.clear()
        self.comboBox.addItems(files)

        self.load_preset_file()

if __name__ == "__main__":
    import sys

    app = QApplication(sys.argv)
    MainWindow = QMainWindow()
    ui = PyX7GUI()
    ui.setupUi(MainWindow)
    ui.do_custom_setup(MainWindow, app)
    MainWindow.show()
    sys.exit(app.exec())