import logging
import warnings
from pathlib import Path
import os

from qtpy.QtWidgets import (
    QPushButton,
    QWidget,
    QLabel,
    QComboBox,
    QCheckBox,
    QLineEdit,
    QGroupBox,
    QGridLayout,
    QVBoxLayout,
    QScrollArea,
    QDialog,
    QFileDialog,
)
from qtpy.QtCore import Qt

import napari
from leonardo_toolset import FUSE_illu, FUSE_det

from ._dialog import GuidedDialog
from ._writer import save_dialog, write_tiff


class FusionWidget(QWidget):
    """Main widget for the plugin."""

    def __init__(self, viewer: napari.viewer.Viewer):
        super().__init__()
        self.viewer = viewer
        self.logger: logging.Logger
        self._initialize_logger()

        self.logger.debug("Initializing FusionWidget")

        self.guided_dialog = GuidedDialog(self)
        self.image_config_is_valid = False

        self._initialize_ui()

        self.inputs = [
            [
                self.label_illu2,
                self.label_illumination2,
                self.label_direction2,
                self.label_selected_direction2,
            ],
            [
                self.label_illu3,
                self.label_illumination3,
                self.label_direction3,
                self.label_selected_direction3,
            ],
            [
                self.label_illu4,
                self.label_illumination4,
                self.label_direction4,
                self.label_selected_direction4,
            ],
        ]

        def wrapper(self, func, event):
            self.guided_dialog.close()
            self.logger.debug("Exiting")
            return func(event)

        with warnings.catch_warnings():
            warnings.simplefilter("ignore")
            func = self.viewer.window._qt_window.closeEvent
            self.viewer.window._qt_window.closeEvent = lambda event: wrapper(
                self, func, event
            )

        self.viewer.layers.events.removed.connect(self._mark_invalid_layer_label)
        def connect_rename(event):
            event.value.events.name.connect(self._update_layer_label)
        self.viewer.layers.events.inserted.connect(connect_rename)
        def write_old_name_to_metadata(event):
            event.value.metadata["old_name"] = event.value.name
        self.viewer.layers.events.inserted.connect(write_old_name_to_metadata)
        for layer in self.viewer.layers:
            layer.metadata["old_name"] = layer.name
            layer.events.name.connect(self._update_layer_label)

        self.logger.debug("FusionWidget initialized")
        self.logger.info("Ready to use")

    def _initialize_logger(self):
        self.logger = logging.getLogger(__name__)
        self.logger.setLevel(logging.DEBUG)
        self.logger.propagate = False
        for handler in self.logger.handlers:
            self.logger.removeHandler(handler)
        handler = logging.StreamHandler()
        handler.setLevel(logging.DEBUG)
        handler.setFormatter(
            logging.Formatter(
                fmt="%(asctime)s - %(levelname)s - %(message)s",
                datefmt="%Y-%m-%d %H:%M:%S",
            )
        )
        self.logger.addHandler(handler)

    def _initialize_ui(self):
        self.logger.debug("Initializing UI")

        ### QObjects
        # objects that can be updated are attributes of the class
        # for ease of access

        # QLabels
        title = QLabel("<h1>LSFM Fusion</h1>")
        title.setAlignment(Qt.AlignCenter)
        title.setMaximumHeight(100)
        self.method = QLabel("")
        self.amount = QLabel("")
        label_illumination1 = QLabel("illumination 1:")
        self.label_illumination2 = QLabel("illumination 2:")
        self.label_illumination3 = QLabel("illumination 3:")
        self.label_illumination4 = QLabel("illumination 4:")
        self.label_illu1 = QLabel() # TODO: handle long layer names
        self.label_illu2 = QLabel()
        self.label_illu3 = QLabel()
        self.label_illu4 = QLabel()
        label_direction1 = QLabel("Direction:")
        self.label_direction2 = QLabel("Direction:")
        self.label_direction3 = QLabel("Direction:")
        self.label_direction4 = QLabel("Direction:")
        self.label_selected_direction1 = QLabel()
        self.label_selected_direction2 = QLabel()
        self.label_selected_direction3 = QLabel()
        self.label_selected_direction4 = QLabel()
        label_resample_ratio = QLabel("Resample ratio:")
        label_window_size = QLabel("Window size:")
        label_gf_kernel_size = QLabel("GF kernel size:")
        label_req_segmentation = QLabel("Require segmentation:")
        label_req_registration = QLabel("Require registration:")
        self.label_lateral_resolution = QLabel("Lateral resolution:")
        self.label_lateral_resolution.setVisible(False)
        self.label_axial_resolution = QLabel("Axial resolution:")
        self.label_axial_resolution.setVisible(False)
        label_req_flip_illu = QLabel("Require flipping along illumination:")
        label_req_flip_det = QLabel("Require flipping along detection:")
        label_keep_tmp = QLabel("Keep temporary files:")
        path = Path(__file__).parent.parent.parent / "intermediates"
        os.makedirs(path, exist_ok=True)
        self.label_tmp_path = QLabel(str(path))
        self.label_tmp_path.setWordWrap(True)
        self.label_tmp_path.setMaximumWidth(350)

        # QPushButtons
        btn_input = QPushButton("Input")
        btn_path = QPushButton("Set temp path")
        btn_process = QPushButton("Process")
        btn_save = QPushButton("Save")

        btn_input.clicked.connect(self.guided_dialog.show)
        btn_path.clicked.connect(self.get_path)
        btn_process.clicked.connect(self._process_on_click)
        btn_save.clicked.connect(self._save_on_click)

        # QCheckBoxes
        self.checkbox_req_segmentation = QCheckBox()
        self.checkbox_req_registration = QCheckBox()
        self.checkbox_req_registration.stateChanged.connect(
            self._toggle_registration
        )
        self.checkbox_req_flip_illu = QCheckBox()
        self.checkbox_req_flip_det = QCheckBox()
        self.checkbox_keep_tmp = QCheckBox()

        # QLineEdits
        self.lineedit_resample_ratio = QLineEdit()
        self.lineedit_window_size_Y = QLineEdit()
        self.lineedit_window_size_X = QLineEdit()
        self.lineedit_gf_kernel_size = QLineEdit()
        self.lineedit_lateral_resolution = QLineEdit()
        self.lineedit_lateral_resolution.setVisible(False)
        self.lineedit_axial_resolution = QLineEdit()
        self.lineedit_axial_resolution.setVisible(False)

        self.lineedit_resample_ratio.setText("2")
        self.lineedit_window_size_Y.setText("59")
        self.lineedit_window_size_X.setText("5")
        self.lineedit_gf_kernel_size.setText("49")
        self.lineedit_lateral_resolution.setText("1")
        self.lineedit_axial_resolution.setText("1")

        self.input_box = QGroupBox("Input")
        input_layout = QGridLayout()
        input_layout.addWidget(self.method, 0, 0)
        input_layout.addWidget(self.amount, 0, 1)
        input_layout.addWidget(label_illumination1, 1, 0)
        input_layout.addWidget(self.label_illu1, 1, 1)
        input_layout.addWidget(label_direction1, 2, 0)
        input_layout.addWidget(self.label_selected_direction1, 2, 1)
        input_layout.addWidget(self.label_illumination2, 3, 0)
        input_layout.addWidget(self.label_illu2, 3, 1)
        input_layout.addWidget(self.label_direction2, 4, 0)
        input_layout.addWidget(self.label_selected_direction2, 4, 1)
        input_layout.addWidget(self.label_illumination3, 5, 0)
        input_layout.addWidget(self.label_illu3, 5, 1)
        input_layout.addWidget(self.label_direction3, 6, 0)
        input_layout.addWidget(self.label_selected_direction3, 6, 1)
        input_layout.addWidget(self.label_illumination4, 7, 0)
        input_layout.addWidget(self.label_illu4, 7, 1)
        input_layout.addWidget(self.label_direction4, 8, 0)
        input_layout.addWidget(self.label_selected_direction4, 8, 1)
        self.input_box.setLayout(input_layout)
        self.input_box.setVisible(False)

        parameters = QGroupBox("Parameters")
        parameters_layout = QGridLayout()
        parameters_layout.addWidget(label_resample_ratio, 0, 0, 1, 2)
        parameters_layout.addWidget(self.lineedit_resample_ratio, 0, 2)
        parameters_layout.addWidget(label_window_size, 1, 0)
        parameters_layout.addWidget(self.lineedit_window_size_Y, 1, 1)
        parameters_layout.addWidget(self.lineedit_window_size_X, 1, 2)
        parameters_layout.addWidget(label_gf_kernel_size, 2, 0, 1, 2)
        parameters_layout.addWidget(self.lineedit_gf_kernel_size, 2, 2)
        parameters_layout.addWidget(label_req_segmentation, 3, 0, 1, 2)
        parameters_layout.addWidget(self.checkbox_req_segmentation, 3, 2)
        parameters_layout.addWidget(label_req_registration, 4, 0, 1, 2)
        parameters_layout.addWidget(self.checkbox_req_registration, 4, 2)
        parameters_layout.addWidget(self.label_lateral_resolution, 5, 0, 1, 2)
        parameters_layout.addWidget(self.lineedit_lateral_resolution, 5, 2)
        parameters_layout.addWidget(self.label_axial_resolution, 6, 0, 1, 2)
        parameters_layout.addWidget(self.lineedit_axial_resolution, 6, 2)
        parameters_layout.addWidget(label_req_flip_illu, 7, 0, 1, 2)
        parameters_layout.addWidget(self.checkbox_req_flip_illu, 7, 2)
        parameters_layout.addWidget(label_req_flip_det, 8, 0, 1, 2)
        parameters_layout.addWidget(self.checkbox_req_flip_det, 8, 2)
        parameters_layout.addWidget(label_keep_tmp, 9, 0, 1, 2)
        parameters_layout.addWidget(self.checkbox_keep_tmp, 9, 2)
        parameters.setLayout(parameters_layout)

        ### Layout
        layout = QGridLayout()
        layout.addWidget(title, 0, 0, 1, -1)
        layout.addWidget(btn_input, 1, 0)
        layout.addWidget(btn_path, 1, 1)
        layout.addWidget(self.input_box, 2, 0, 1, -1)
        # layout.addWidget(input1, 1, 0, 1, -1)
        # layout.addWidget(input2, 2, 0, 1, -1)
        layout.addWidget(parameters, 3, 0, 1, -1)
        layout.addWidget(self.label_tmp_path, 4, 0, 1, -1)
        layout.addWidget(btn_process, 5, 0)
        layout.addWidget(btn_save, 5, 1)

        widget = QWidget()
        widget.setLayout(layout)

        scroll_area = QScrollArea()
        scroll_area.setWidget(widget)
        scroll_area.setWidgetResizable(True)

        self.setLayout(QVBoxLayout())
        self.layout().addWidget(scroll_area)
        self.setMinimumWidth(330)

    def _update_layer_label(self, event):
        new_name = event.source.name
        old_name = event.source.metadata.get("old_name", None)
        event.source.metadata["old_name"] = new_name
        labels = [
            self.label_illu1,
            self.label_illu2,
            self.label_illu3,
            self.label_illu4,
        ]
        for label in labels:
            if label.text() == old_name:
                label.setText(new_name)
                self.logger.debug(f"Layer name updated: {old_name} -> {new_name}")
                break

    def _mark_invalid_layer_label(self, event):
        layername = event.value.name
        labels = [
            self.label_illu1,
            self.label_illu2,
            self.label_illu3,
            self.label_illu4,
        ]
        for label in labels:
            if label.text() == layername:
                label.setStyleSheet("color: red")
                self.logger.warning(f"Layer invalidated: {layername}")
                self.image_config_is_valid = False
                break

    def get_path(self):
        path = QFileDialog.getExistingDirectory(self, "Select Directory")
        self.label_tmp_path.setText(path)

    def _toggle_registration(self, event):
        if event == Qt.Checked:
            self.label_lateral_resolution.setVisible(True)
            self.label_axial_resolution.setVisible(True)
            self.lineedit_lateral_resolution.setVisible(True)
            self.lineedit_axial_resolution.setVisible(True)
        else:
            self.label_lateral_resolution.setVisible(False)
            self.label_axial_resolution.setVisible(False)
            self.lineedit_lateral_resolution.setVisible(False)
            self.lineedit_axial_resolution.setVisible(False)

    def _set_input_visible(self, numbers, visible):
        if isinstance(numbers, int):
            numbers = [numbers]
        indices = [x - 2 for x in numbers]
        inputs = [self.inputs[index] for index in indices]
        elements = [element for sublist in inputs for element in sublist]
        for element in elements:
            element.setVisible(visible)

    def receive_input(self, params):
        self.logger.debug("Parsing input")
        self.logger.debug(f"Parameters: {params}")

        self.method.setText(params["method"])
        self.amount.setText(str(params["amount"]))
        self.label_illu1.setStyleSheet("")
        self.label_illu2.setStyleSheet("")
        self.label_illu3.setStyleSheet("")
        self.label_illu4.setStyleSheet("")
        
        self.label_illu1.setText(params["layer1"])
        self.label_selected_direction1.setText(params["direction1"])

        if params["method"] == "detection":
            # detection
            self.amount.setVisible(True)
            self.label_illu3.setText(params["layer3"])
            self.label_selected_direction3.setText(params["direction3"])
            self._set_input_visible(3, True)
            if params["amount"] == 2:
                # detection with 2 images
                self._set_input_visible([2,4], False)
            else:
                # detection with 4 images
                self.label_illu2.setText(params["layer2"])
                self.label_selected_direction2.setText(params["direction2"])
                self.label_illu4.setText(params["layer4"])
                self.label_selected_direction4.setText(params["direction4"])
                self._set_input_visible([2,4], True)
        else:
            # illumination (2 images)
            self.amount.setVisible(False)
            self.label_illu2.setText(params["layer2"])
            self.label_selected_direction2.setText(params["direction2"])
            self._set_input_visible(2, True)
            self._set_input_visible([3,4], False)

        self.image_config_is_valid = True
        self.input_box.setVisible(True)

    def _save_on_click(self):
        self.logger.debug("Save button clicked")
        layernames = [
            layer.name
            for layer in self.viewer.layers
            if type(layer) == napari.layers.Image
        ]
        layernames.reverse()
        if not layernames:
            self.logger.info("No layers available")
            return
        if len(layernames) == 1:
            self.logger.info("Only one layer available")
            layername = layernames[0]
        else:
            self.logger.info("Multiple layers available")
            dialog = LayerSelection(layernames)
            index = dialog.exec_()
            if index == -1:
                self.logger.info("No layer selected")
                return
            layername = layernames[index]
        self.logger.debug(f"Selected layer: {layername}")
        data = self.viewer.layers[self.viewer.layers.index(layername)].data
        self.logger.debug(f"Data shape: {data.shape}")
        self.logger.debug(f"Data dtype: {data.dtype}")
        filepath = save_dialog(self)
        if filepath == ".tiff" or filepath == ".tif":
            self.logger.info("No file selected")
            return
        self.logger.debug(f"Filepath: {filepath}")
        write_tiff(filepath, data)
        self.logger.info("Data saved")

    def _process_on_click(self):
        params = self._get_parameters()
        if params is None:
            return
        exclude_keys = {'image1', 'image2', 'image3', 'image4'}

        filtered_dict = {k: v for k, v in params.items() if k not in exclude_keys}
        self.logger.debug(filtered_dict)
        
        if params["method"] == "illumination":
            model = FUSE_illu()
        else:
            model = FUSE_det()

        output_image = model.train_from_params(params)
        self.viewer.add_image(output_image) # set name of layer

    def _get_parameters(self):
        self.logger.debug("Compiling parameters")
        if not self.input_box.isVisible():
            self.logger.error("Input not set")
            return None
        
        if not self.image_config_is_valid:
            self.logger.error("Invalid image configuration")
            return None
        
        params = {}

        method = self.method.text()
        params["method"] = method
        if method == "detection":
            amount = int(self.amount.text())
        else:
            amount = 2
        params["amount"] = amount
        image1_name = self.label_illu1.text()
        params["image1"] = self.viewer.layers[image1_name].data
        params["direction1"] = self.label_selected_direction1.text()

        if method == "illumination" or amount == 4:
            image2_name = self.label_illu2.text()
            params["image2"] = self.viewer.layers[image2_name].data
            params["direction2"] = self.label_selected_direction2.text()

        if method == "detection":
            image3_name = self.label_illu3.text()
            params["image3"] = self.viewer.layers[image3_name].data
            params["direction3"] = self.label_selected_direction3.text()
            if amount == 4:
                image4_name = self.label_illu4.text()
                params["image4"] = self.viewer.layers[image4_name].data
                params["direction4"] = self.label_selected_direction4.text()

        try:
            params["resample_ratio"] = int(self.lineedit_resample_ratio.text())
        except ValueError:
            self.logger.error("Invalid resample ratio")
            return
        if not (1 <= params["resample_ratio"] <= 5):
            self.logger.error("Resample ratio must be between 1 and 5")
            return
        try:
            params["window_size"] = (
                int(self.lineedit_window_size_Y.text()),
                int(self.lineedit_window_size_X.text()),
            )
        except ValueError:
            self.logger.error("Invalid window size")
            return
        if not (
            9 <= params["window_size"][0] <= 89
            and 3 <= params["window_size"][1] <= 29
        ):
            self.logger.error("Window size must be between 3x9 and 29x89")
            return
        try:
            params["GF_kernel_size"] = int(self.lineedit_gf_kernel_size.text())
        except ValueError:
            self.logger.error("Invalid GF kernel size")
            return
        if not (29 <= params["GF_kernel_size"] <= 89):
            self.logger.error("GF kernel size must be between 29 and 89")
            return
        params["require_segmentation"] = (
            self.checkbox_req_segmentation.isChecked()
        )
        params["require_registration"] = (
            self.checkbox_req_registration.isChecked()
        )
        if params["require_registration"]:
            try:
                params["lateral_resolution"] = float(
                    self.lineedit_lateral_resolution.text()
                )
            except ValueError:
                self.logger.error("Invalid lateral resolution")
                return
            try:
                params["axial_resolution"] = float(
                    self.lineedit_axial_resolution.text()
                )
            except ValueError:
                self.logger.error("Invalid axial resolution")
                return
        params["require_flip_illu"] = self.checkbox_req_flip_illu.isChecked()
        params["require_flip_det"] = self.checkbox_req_flip_det.isChecked()
        params["keep_intermediates"] = self.checkbox_keep_tmp.isChecked()
        params["tmp_path"] = self.label_tmp_path.text()
        self.logger.debug(f"Parameters: {params.keys()}")
        return params


class LayerSelection(QDialog):
    def __init__(self, layernames: list[str]):
        super().__init__()
        self.setWindowTitle("Select Layer to save as TIFF")
        self.combobox = QComboBox()
        self.combobox.addItems(layernames)
        btn_select = QPushButton("Select")
        btn_select.clicked.connect(self.accept)
        layout = QVBoxLayout()
        layout.addWidget(self.combobox)
        layout.addWidget(btn_select)
        self.setLayout(layout)
        self.setMinimumSize(250, 100)

    def accept(self):
        self.done(self.combobox.currentIndex())

    def reject(self):
        self.done(-1)
