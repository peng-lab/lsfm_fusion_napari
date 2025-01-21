from qtpy.QtWidgets import (
    QWidget,
    QVBoxLayout,
    QGridLayout,
    QLabel,
    QPushButton,
    QComboBox,
    QGroupBox,
)
import napari

from PyQt5 import QtGui

font = QtGui.QFont()
font.setFamily("Microsoft YaHei UI")
font.setPointSize(20)


class GuidedDialog(QWidget):
    def __init__(self, parent=None):
        super().__init__()
        self.viewer = parent.viewer
        self.parent = parent

        # check if at least 2 layers are present

        self.params = {}

        # self.method = None
        # self.amount = None
        # self.layer1 = None
        # self.direction1 = None
        # self.layer2 = None
        # self.direction2 = None
        # self.layer3 = None
        # self.direction3 = None
        # self.layer4 = None
        # self.direction4 = None

        self.init_ui()
        parent.logger.debug("GuidedDialog initialized")

    def init_ui(self):
        self.setFont(font)
        self.setLayout(QGridLayout())
        try:
            self.setStyleSheet(napari.qt.get_stylesheet(theme="dark"))
        except TypeError:
            self.setStyleSheet(napari.qt.get_stylesheet(theme_id="dark"))

        ### QObjects
        # Labels
        label_prompt_type = QLabel("Select the type of fusion:")
        label_prompt_amount = QLabel("Select the amount of images to fuse:")
        label_prompt_image1 = QLabel(
            "Select the first image from camera front:"
        )
        label_prompt_image2 = QLabel(
            "Select the second image from camera front:"
        )
        label_prompt_image3 = QLabel(
            "Select the first image from camera back:"
        )
        label_prompt_image4 = QLabel(
            "Select the second image from camera back:"
        )
        label_direction1 = QLabel("Direction:")
        label_direction2 = QLabel("Direction:")
        label_direction3 = QLabel("Direction:")
        label_direction3 = QLabel("Direction:")
        label_direction4 = QLabel("Direction:")
        self.label_display_direction2 = QLabel("Up")
        self.label_display_direction3 = QLabel("Down")
        self.label_display_direction3.setVisible(False)
        self.label_display_direction4 = QLabel("")

        # Buttons
        button_illumination = QPushButton("Illumination")
        button_detection = QPushButton("Detection")
        button_2 = QPushButton("2")
        button_2.setMinimumWidth(50)
        button_4 = QPushButton("4")
        button_4.setMinimumWidth(50)
        self.button_confirm_v1 = QPushButton("Confirm")
        self.button_confirm_v2 = QPushButton("Confirm")
        self.button_confirm_d1 = QPushButton("Confirm")
        self.button_apply_v2 = QPushButton("Apply")
        self.button_apply_d1 = QPushButton("Apply")
        self.button_apply_d2 = QPushButton("Apply")
        self.button_confirm_v1.setVisible(False)
        self.button_confirm_v2.setVisible(False)
        self.button_confirm_d1.setVisible(False)
        self.button_apply_v2.setVisible(False)
        self.button_apply_d1.setVisible(False)
        self.button_apply_d2.setVisible(False)
        button_cancel = QPushButton("Cancel")

        # Button connections
        button_illumination.clicked.connect(self.illu_on_click)
        button_detection.clicked.connect(self.det_on_click)
        button_2.clicked.connect(self.two_on_click)
        button_4.clicked.connect(self.four_on_click)
        self.button_confirm_v1.clicked.connect(self.confirm_v1_on_click)
        self.button_confirm_v2.clicked.connect(self.confirm_v2_on_click)
        self.button_confirm_d1.clicked.connect(self.confirm_d1_on_click)
        self.button_apply_v2.clicked.connect(self.apply_v2_on_click)
        self.button_apply_d1.clicked.connect(self.apply_d1_on_click)
        self.button_apply_d2.clicked.connect(self.apply_d2_on_click)
        button_cancel.clicked.connect(self.cancel_on_click)

        # Comboboxes
        self.combobox_image1 = QComboBox()
        self.combobox_image2 = QComboBox()
        self.combobox_image3 = QComboBox()
        self.combobox_image4 = QComboBox()
        self.combobox_direction1 = QComboBox()
        self.combobox_direction3 = QComboBox()
        self.combobox_direction3.setVisible(False)

        self.combobox_direction1.addItems(["Top", "Bottom", "Left", "Right"])

        # Groupboxes
        self.groupbox_type = QGroupBox("Fusion type")
        gb_type_layout = QGridLayout()
        gb_type_layout.addWidget(label_prompt_type, 0, 0)
        gb_type_layout.addWidget(button_illumination, 0, 1)
        gb_type_layout.addWidget(button_detection, 0, 2)
        self.groupbox_type.setLayout(gb_type_layout)

        self.groupbox_amount = QGroupBox("Amount of images")
        gb_amount_layout = QGridLayout()
        gb_amount_layout.addWidget(label_prompt_amount, 0, 0)
        gb_amount_layout.addWidget(button_2, 0, 1)
        gb_amount_layout.addWidget(button_4, 0, 2)
        self.groupbox_amount.setLayout(gb_amount_layout)
        self.groupbox_amount.setVisible(False)

        self.groupbox_image1 = QGroupBox("Image 1 (camera front)")
        gb_img1_layout = QGridLayout()
        gb_img1_layout.addWidget(label_prompt_image1, 0, 0)
        gb_img1_layout.addWidget(self.combobox_image1, 0, 1)
        gb_img1_layout.addWidget(label_direction1, 1, 0)
        gb_img1_layout.addWidget(self.combobox_direction1, 1, 1)
        self.groupbox_image1.setLayout(gb_img1_layout)
        self.groupbox_image1.setVisible(False)

        self.groupbox_image2 = QGroupBox("Image 2 (camera front)")
        gb_img2_layout = QGridLayout()
        gb_img2_layout.addWidget(label_prompt_image2, 0, 0)
        gb_img2_layout.addWidget(self.combobox_image2, 0, 1)
        gb_img2_layout.addWidget(label_direction2, 1, 0)
        gb_img2_layout.addWidget(self.label_display_direction2, 1, 1)
        self.groupbox_image2.setLayout(gb_img2_layout)
        self.groupbox_image2.setVisible(False)

        self.groupbox_image3 = QGroupBox("Image 1 (camera back)")
        gb_img3_layout = QGridLayout()
        gb_img3_layout.addWidget(label_prompt_image3, 0, 0)
        gb_img3_layout.addWidget(self.combobox_image3, 0, 1)
        gb_img3_layout.addWidget(label_direction3, 1, 0)
        gb_img3_layout.addWidget(self.combobox_direction3, 1, 1)
        gb_img3_layout.addWidget(self.label_display_direction3, 1, 1)
        self.groupbox_image3.setLayout(gb_img3_layout)
        self.groupbox_image3.setVisible(False)

        self.groupbox_image4 = QGroupBox("Image 2 (camera back)")
        gb_img4_layout = QGridLayout()
        gb_img4_layout.addWidget(label_prompt_image4, 0, 0)
        gb_img4_layout.addWidget(self.combobox_image4, 0, 1)
        gb_img4_layout.addWidget(label_direction4, 1, 0)
        gb_img4_layout.addWidget(self.label_display_direction4, 1, 1)
        self.groupbox_image4.setLayout(gb_img4_layout)
        self.groupbox_image4.setVisible(False)

        ### Layout
        layout = self.layout()
        layout.addWidget(self.groupbox_type, 0, 0, 1, -1)
        layout.addWidget(self.groupbox_amount, 1, 0, 1, -1)
        layout.addWidget(self.groupbox_image1, 2, 0, 1, -1)
        layout.addWidget(self.groupbox_image2, 3, 0, 1, -1)
        layout.addWidget(self.groupbox_image3, 4, 0, 1, -1)
        layout.addWidget(self.groupbox_image4, 5, 0, 1, -1)
        layout.addWidget(self.button_confirm_v1, 6, 0)
        layout.addWidget(self.button_confirm_v2, 6, 0)
        layout.addWidget(self.button_confirm_d1, 6, 0)
        layout.addWidget(self.button_apply_v2, 6, 0)
        layout.addWidget(self.button_apply_d1, 6, 0)
        layout.addWidget(self.button_apply_d2, 6, 0)
        layout.addWidget(button_cancel, 6, 1)

    def reset_ui(self):
        self.groupbox_type.setVisible(True)
        self.groupbox_amount.setVisible(False)
        self.groupbox_image1.setVisible(False)
        self.groupbox_image2.setVisible(False)
        self.groupbox_image3.setVisible(False)
        self.groupbox_image4.setVisible(False)
        self.button_confirm_v1.setVisible(False)
        self.button_confirm_v2.setVisible(False)
        self.button_confirm_d1.setVisible(False)
        self.button_apply_v2.setVisible(False)
        self.button_apply_d1.setVisible(False)
        self.button_apply_d2.setVisible(False)
        self.label_display_direction3.setVisible(False)
        self.combobox_direction3.setVisible(False)
        self.adjustSize()

    def illu_on_click(self):
        self.parent.logger.debug("Illumination button clicked")
        self.params["method"] = "illumination"
        # self.method = "illumination"
        self.params["amount"] = 2
        # self.amount = 2
        self.groupbox_type.setVisible(False)
        self.fill_layer_combobox(self.combobox_image1)
        self.groupbox_image1.setVisible(True)
        self.button_confirm_v1.setVisible(True)
        self.adjustSize()

    def det_on_click(self):
        self.parent.logger.debug("Detection button clicked")
        self.params["method"] = "detection"
        # self.method = "detection"
        self.groupbox_type.setVisible(False)
        self.groupbox_amount.setVisible(True)
        self.adjustSize()

    def two_on_click(self):
        # must be detection
        self.parent.logger.debug("Two images button clicked")
        self.params["amount"] = 2
        # self.amount = 2
        self.groupbox_amount.setVisible(False)
        self.fill_layer_combobox(self.combobox_image1)
        self.groupbox_image1.setVisible(True)
        self.button_confirm_v1.setVisible(True)
        self.label_display_direction3.setVisible(True)
        self.adjustSize()

    def four_on_click(self):
        # must be detection
        self.parent.logger.debug("Four images button clicked")
        # check if at least 4 layers are present
        self.params["amount"] = 4
        # self.amount = 4
        self.groupbox_amount.setVisible(False)
        self.fill_layer_combobox(self.combobox_image1)
        self.groupbox_image1.setVisible(True)
        self.button_confirm_v1.setVisible(True)
        self.combobox_direction3.setVisible(True)
        self.adjustSize()

    def confirm_v1_on_click(self):
        # always called
        self.parent.logger.debug("Confirm button v1 clicked")
        self.params["layer1"] = self.combobox_image1.currentText()
        self.params["direction1"] = self.combobox_direction1.currentText()
        self.groupbox_image1.setVisible(False)
        self.button_confirm_v1.setVisible(False)
        method = self.params["method"]
        amount = self.params["amount"]
        if method == "detection" and amount == 4:
            self.fill_layer_combobox(self.combobox_image2)
            self.set_direction_from_reference(
                self.label_display_direction2, self.params["direction1"]
            )
            self.set_direction_from_reference(
                self.combobox_direction3, self.params["direction1"]
            )
            self.groupbox_image2.setVisible(True)
            self.button_confirm_v2.setVisible(True)
        elif method == "illumination":
            self.fill_layer_combobox(self.combobox_image2)
            self.set_direction_from_reference(
                self.label_display_direction2, self.params["direction1"]
            )
            self.groupbox_image2.setVisible(True)
            self.button_apply_v2.setVisible(True)
        else:
            self.fill_layer_combobox(self.combobox_image3)
            self.set_direction_from_reference(
                self.label_display_direction3, self.params["direction1"]
            )
            self.groupbox_image3.setVisible(True)
            self.button_apply_d1.setVisible(True)
        self.adjustSize()

    def confirm_v2_on_click(self):
        # must be detection 4
        self.parent.logger.debug("Confirm button v2 clicked")
        self.params["layer2"] = self.combobox_image2.currentText()
        self.params["direction2"] = self.label_display_direction2.text()
        self.groupbox_image2.setVisible(False)
        self.button_confirm_v2.setVisible(False)
        self.fill_layer_combobox(self.combobox_image3)
        self.set_direction_from_reference(
            self.label_display_direction3, self.params["direction2"]
        )
        self.groupbox_image3.setVisible(True)
        self.button_confirm_d1.setVisible(True)
        self.adjustSize()

    def confirm_d1_on_click(self):
        # must be detection 4
        self.parent.logger.debug("Confirm button d1 clicked")
        self.params["layer3"] = self.combobox_image3.currentText()
        self.params["direction3"] = self.label_display_direction3.text()
        self.groupbox_image3.setVisible(False)
        self.button_confirm_d1.setVisible(False)
        self.fill_layer_combobox(self.combobox_image4)
        self.set_direction_from_reference(
            self.label_display_direction4, self.params["direction3"]
        )
        self.groupbox_image4.setVisible(True)
        self.button_apply_d2.setVisible(True)
        self.adjustSize()

    def apply_v2_on_click(self):
        # must be illumination
        self.parent.logger.debug("Apply button v2 clicked")
        self.params["layer2"] = self.combobox_image2.currentText()
        self.params["direction2"] = self.label_display_direction2.text()
        self.pass_input()

    def apply_d1_on_click(self):
        # must be detection 2
        self.parent.logger.debug("Apply button d1 clicked")
        self.params["layer3"] = self.combobox_image3.currentText()
        self.params["direction3"] = self.label_display_direction3.text()
        self.pass_input()

    def apply_d2_on_click(self):
        # must be detection 4
        self.parent.logger.debug("Apply button d2 clicked")
        self.params["layer4"] = self.combobox_image4.currentText()
        self.params["direction4"] = self.label_display_direction4.text()
        self.pass_input()

    def cancel_on_click(self):
        self.parent.logger.debug("Cancel button clicked")
        self.params = {}
        self.reset_ui()
        self.close()

    def fill_layer_combobox(self, combobox):
        combobox.clear()
        chosen_layers = [
            value
            for key, value in self.params.items()
            if key.startswith("layer")
        ]
        for layer in self.viewer.layers:
            if layer.name not in chosen_layers:
                combobox.addItem(layer.name)

    def set_direction_from_reference(self, element, reference):
        def get_opposite_direction(direction):
            if direction == "Top":
                return "Bottom"
            elif direction == "Bottom":
                return "Top"
            elif direction == "Left":
                return "Right"
            elif direction == "Right":
                return "Left"
            else:
                raise ValueError("Invalid direction")

        opposite = get_opposite_direction(reference)
        if isinstance(element, QComboBox):
            element.clear()
            element.addItems([reference, opposite])
        else:
            element.setText(opposite)

    def pass_input(self):
        self.parent.receive_input(self.params)
        self.parent.logger.debug("Input passed to main widget")
        self.params = {}
        self.reset_ui()
        self.close()
