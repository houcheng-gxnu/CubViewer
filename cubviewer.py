#!/usr/bin/env python3
"""
Cube Viewer — VMD/Tachyon Cube 文件查看器 v1.0 (PyQt)
直接打开 .cub 文件，VMD 预览 + Tachyon 渲染，无需 Multiwfn。
后端引用自 fchk_orbital.py。
"""

import os
import sys
import glob
import subprocess
import socket
import time

from PyQt5.QtWidgets import (
    QApplication, QMainWindow, QWidget, QVBoxLayout, QHBoxLayout,
    QGroupBox, QLabel, QLineEdit, QPushButton, QRadioButton, QCheckBox,
    QComboBox, QTextEdit, QFileDialog, QMessageBox, QButtonGroup,
    QFrame, QGridLayout, QSlider, QTabWidget,
)
from PyQt5.QtCore import Qt, QThread, pyqtSignal
from PyQt5.QtGui import QFont, QColor, QTextCursor

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import fchk_orbital as backend


LIGHT_QSS = """
QMainWindow {
    background-color: #E4EAF2;
}

QWidget {
    font-family: "Segoe UI", "Microsoft YaHei", "Consolas", sans-serif;
    font-size: 9pt;
    color: #2C3E50;
}

QGroupBox {
    border: 1px solid #C8D6E5;
    border-radius: 6px;
    margin-top: 10px;
    padding-top: 8px;
    font-weight: bold;
    font-size: 9.5pt;
    color: #2C3E50;
    background-color: #FFFFFF;
}

QGroupBox::title {
    subcontrol-origin: margin;
    left: 12px;
    padding: 0 6px;
}

QTabWidget::pane {
    border: 1px solid #C8D6E5;
    border-radius: 4px;
    background-color: #FFFFFF;
    padding: 4px;
}

QTabBar::tab {
    background-color: #F1F5F9;
    border: 1px solid #CBD5E1;
    border-bottom: none;
    border-top-left-radius: 6px;
    border-top-right-radius: 6px;
    padding: 8px 12px;
    margin-right: 3px;
    min-width: 110px;
    color: #4A5568;
    font-weight: bold;
    font-size: 9pt;
}

QTabBar::tab:selected {
    background-color: #FFFFFF;
    color: #1565C0;
    border-bottom: 2px solid #1E88E5;
}

QTabBar::tab:hover:!selected {
    background-color: #E3F2FD;
    color: #1565C0;
}

QTabBar::tab:disabled {
    color: #94A3B8;
    background-color: #F1F5F9;
}

QPushButton {
    background-color: #E8ECF4;
    border: 1px solid #C8D6E5;
    border-radius: 4px;
    padding: 5px 14px;
    font-weight: bold;
    font-size: 9pt;
    color: #2C3E50;
}

QPushButton:hover {
    background-color: #D6DEEA;
    border-color: #1565C0;
}

QPushButton:pressed {
    background-color: #C8D6E5;
}

QPushButton#PrimaryBtn {
    background-color: #1565C0;
    color: #FFFFFF;
    border: 1px solid #0D47A1;
    font-size: 9.5pt;
    padding: 6px 18px;
}

QPushButton#PrimaryBtn:hover {
    background-color: #1E88E5;
}

QPushButton#RenderBtn {
    background-color: #2E7D32;
    color: #FFFFFF;
    border: 1px solid #1B5E20;
    font-size: 9.5pt;
    padding: 6px 18px;
}

QPushButton#RenderBtn:hover {
    background-color: #388E3C;
}

QPushButton#StopBtn {
    background-color: #C62828;
    color: #FFFFFF;
    border: 1px solid #B71C1C;
    font-size: 9.5pt;
    padding: 6px 18px;
}

QPushButton#StopBtn:hover {
    background-color: #E53935;
}

QPushButton#SmallBtn {
    padding: 3px 8px;
    font-size: 8.5pt;
    min-width: 35px;
}

QPushButton:disabled {
    background-color: #ECF0F5;
    color: #AAB5C0;
    border-color: #D5DDE5;
}

QLineEdit, QComboBox {
    border: 1px solid #C8D6E5;
    border-radius: 3px;
    padding: 3px 6px;
    background-color: #F8FAFC;
    font-size: 9pt;
}

QLineEdit:focus, QComboBox:focus {
    border-color: #1565C0;
    background-color: #FFFFFF;
}

QComboBox::drop-down {
    border: none;
    padding-right: 6px;
}

QComboBox QAbstractItemView {
    background-color: #FFFFFF;
    border: 1px solid #C8D6E5;
    selection-background-color: #E3F2FD;
    selection-color: #1565C0;
}

QSlider::groove:horizontal {
    border: 1px solid #C8D6E5;
    height: 6px;
    background: #E8ECF4;
    border-radius: 3px;
}

QSlider::handle:horizontal {
    background: #1565C0;
    border: 1px solid #0D47A1;
    width: 16px;
    margin: -5px 0;
    border-radius: 8px;
}

QSlider::handle:horizontal:hover {
    background: #1E88E5;
}

QSlider:disabled {
    background: transparent;
}

QCheckBox {
    spacing: 6px;
}

QCheckBox::indicator {
    width: 15px;
    height: 15px;
}

QRadioButton {
    spacing: 6px;
}

QRadioButton::indicator {
    width: 15px;
    height: 15px;
}

QTextEdit {
    border: 1px solid #C8D6E5;
    border-radius: 3px;
    background-color: #F8FAFC;
    font-family: "Consolas", "Courier New", monospace;
    font-size: 9pt;
    padding: 4px;
}

QLabel#TitleLabel {
    font-size: 13pt;
    font-weight: bold;
    color: #1565C0;
    letter-spacing: 2px;
}

QLabel#SubTitleLabel {
    font-size: 9pt;
    color: #78909C;
}

QLabel#ProgressLabel {
    font-size: 9pt;
    font-weight: bold;
    color: #1565C0;
    padding: 2px 6px;
    background-color: #E3F2FD;
    border-radius: 3px;
}

QLabel#HintLabel {
    font-size: 8.5pt;
    color: #90A4AE;
}
"""


class SciFiGroupBox(QGroupBox):
    def __init__(self, title, parent=None):
        super().__init__(title, parent)


class RenderWorker(QThread):
    log_signal = pyqtSignal(str)
    finished_signal = pyqtSignal(str)

    def __init__(self, port, render_dir, output_png, tachyon_exe,
                 resolution, style_name, shade_mode, trans_raster, threads):
        super().__init__()
        self.port = port
        self.render_dir = render_dir
        self.output_png = output_png
        self.tachyon_exe = tachyon_exe
        self.resolution = resolution
        self.style_name = style_name
        self.shade_mode = shade_mode
        self.trans_raster = trans_raster
        self.threads = threads

    def run(self):
        self.log_signal.emit(f"\nRendering current view (Style: {self.style_name})...")
        t0 = time.time()
        try:
            png = backend.render_current_view(
                self.port, self.render_dir, output_png=self.output_png,
                tachyon_exe=self.tachyon_exe, resolution=self.resolution,
                style_name=self.style_name, shade_mode=self.shade_mode,
                trans_raster=self.trans_raster, threads=self.threads,
            )
            dt = time.time() - t0
            if png:
                self.log_signal.emit(f"Render completed ({dt:.1f}s) -> {os.path.basename(png)}")
                self.finished_signal.emit(png)
            else:
                self.log_signal.emit(f"Render failed ({dt:.1f}s)")
                self.finished_signal.emit("")
        except Exception as e:
            self.log_signal.emit(f"Render error: {e}")
            self.finished_signal.emit("")


class CubeViewerApp(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Cube Viewer — VMD/Tachyon  [PyQt Edition]")
        self.resize(860, 700)
        self.setMinimumSize(780, 600)

        self.paths = backend.load_config()
        self.running = False
        self.vmd_port = None
        self.vmd_render_dir = None
        self.vmd_cube_path = None
        self.vmd_multi_cubes = None
        self._vmd_persist_sock = None
        self.current_iso = 0.05
        self.current_opacity = None
        self.iso_step = 0.005
        self.opacity_step = 0.05

        self._current_cubes = []

        self._setup_ui()
        self._apply_theme()

    def _setup_ui(self):
        central = QWidget()
        self.setCentralWidget(central)
        main_layout = QVBoxLayout(central)
        main_layout.setContentsMargins(12, 8, 12, 10)
        main_layout.setSpacing(6)

        title_label = QLabel("\u25c8  CUBE VIEWER  \u25c8")
        title_label.setObjectName("TitleLabel")
        title_label.setAlignment(Qt.AlignCenter)
        main_layout.addWidget(title_label)

        sub_label = QLabel("VMD + Tachyon  |  Direct Cube File Viewer")
        sub_label.setObjectName("SubTitleLabel")
        sub_label.setAlignment(Qt.AlignCenter)
        main_layout.addWidget(sub_label)

        self.tabs = QTabWidget()

        tab_setup = QWidget()
        tab_setup_layout = QVBoxLayout(tab_setup)
        tab_setup_layout.setContentsMargins(4, 4, 4, 4)
        tab_setup_layout.setSpacing(6)
        tab_setup_layout.addWidget(self._build_vmd_path_panel())
        tab_setup_layout.addWidget(self._build_input_panel())
        tab_setup_layout.addWidget(self._build_output_panel())
        tab_setup_layout.addStretch()
        self.tabs.addTab(tab_setup, "\U0001f4c1  Setup")

        tab_render = QWidget()
        tab_render_layout = QVBoxLayout(tab_render)
        tab_render_layout.setContentsMargins(4, 4, 4, 4)
        tab_render_layout.setSpacing(6)
        tab_render_layout.addWidget(self._build_render_params_panel())
        tab_render_layout.addStretch()
        self.tabs.addTab(tab_render, "\U0001f3a8  Render")

        tab_preview = QWidget()
        tab_preview_layout = QVBoxLayout(tab_preview)
        tab_preview_layout.setContentsMargins(4, 4, 4, 4)
        tab_preview_layout.setSpacing(6)
        tab_preview_layout.addWidget(self._build_buttons_panel())
        tab_preview_layout.addWidget(self._build_live_panel())
        tab_preview_layout.addStretch()
        self.tabs.addTab(tab_preview, "\u25b6\ufe0f  Preview")

        tab_tools = QWidget()
        tab_tools_layout = QVBoxLayout(tab_tools)
        tab_tools_layout.setContentsMargins(4, 4, 4, 4)
        tab_tools_layout.setSpacing(6)
        tab_tools_layout.addWidget(self._build_hydrogen_panel())
        tab_tools_layout.addWidget(self._build_draw_bond_panel())
        tab_tools_layout.addStretch()
        self.tabs.addTab(tab_tools, "\U0001f6e0\ufe0f  Tools")

        main_layout.addWidget(self.tabs, stretch=3)

        self.progress_label = QLabel("\u25c6  Ready")
        self.progress_label.setObjectName("ProgressLabel")
        main_layout.addWidget(self.progress_label)

        log_frame = QFrame()
        log_layout = QVBoxLayout(log_frame)
        log_layout.setContentsMargins(0, 0, 0, 0)

        self.log_text = QTextEdit()
        self.log_text.setReadOnly(True)
        self.log_text.setMinimumHeight(100)
        self.log_text.setMaximumHeight(160)
        log_layout.addWidget(self.log_text)

        main_layout.addWidget(log_frame)

    def _build_vmd_path_panel(self):
        grp = SciFiGroupBox("VMD PATH")
        layout = QHBoxLayout(grp)
        layout.setSpacing(6)

        layout.addWidget(QLabel("VMD:"))
        self.var_vmd = QLineEdit(self.paths["vmd"])
        self.var_vmd.setPlaceholderText("Path to vmd.exe")
        layout.addWidget(self.var_vmd, stretch=1)
        btn = QPushButton("Browse")
        btn.setObjectName("SmallBtn")
        btn.clicked.connect(self._browse_vmd)
        layout.addWidget(btn)

        return grp

    def _build_input_panel(self):
        grp = SciFiGroupBox("INPUT")
        layout = QHBoxLayout(grp)
        layout.setSpacing(6)

        self.mode_group = QButtonGroup(self)
        rb_folder = QRadioButton("Folder")
        rb_file = QRadioButton("Single File")
        self.mode_group.addButton(rb_folder, 0)
        self.mode_group.addButton(rb_file, 1)
        rb_file.setChecked(True)
        layout.addWidget(rb_folder)
        layout.addWidget(rb_file)

        self.var_path = QLineEdit()
        self.var_path.setPlaceholderText("Select .cub file or folder...")
        layout.addWidget(self.var_path, stretch=1)
        btn = QPushButton("Browse")
        btn.clicked.connect(self._browse_input)
        layout.addWidget(btn)

        return grp

    def _build_output_panel(self):
        grp = SciFiGroupBox("OUTPUT DIRECTORY")
        layout = QHBoxLayout(grp)
        layout.setSpacing(6)

        hint = QLabel("(default: same as input)")
        hint.setObjectName("HintLabel")
        layout.addWidget(hint)

        self.var_out = QLineEdit()
        self.var_out.setPlaceholderText("Output directory...")
        layout.addWidget(self.var_out, stretch=1)
        btn = QPushButton("Browse")
        btn.clicked.connect(self._browse_out)
        layout.addWidget(btn)

        return grp

    def _build_render_params_panel(self):
        grp = SciFiGroupBox("RENDER PARAMETERS")
        rlayout = QGridLayout(grp)
        rlayout.setVerticalSpacing(4)
        rlayout.setHorizontalSpacing(6)

        rlayout.addWidget(QLabel("Style:"), 0, 0)
        style_names = list(backend.STYLES.keys())
        style_display = [f"{n}  ({backend.STYLES[n]['desc']})" for n in style_names]
        self.var_style = QComboBox()
        self.var_style.addItems(style_display)
        self.var_style.setCurrentIndex(0)
        self.var_style.setMinimumWidth(320)
        rlayout.addWidget(self.var_style, 0, 1, 1, 4)

        rlayout.addWidget(QLabel("Resolution:"), 1, 0)
        self.var_res = QComboBox()
        self.var_res.addItems(["2000x1500", "1200x900", "3000x2250"])
        self.var_res.setCurrentIndex(0)
        self.var_res.setMaximumWidth(120)
        rlayout.addWidget(self.var_res, 1, 1)

        rlayout.addWidget(QLabel("Shading:"), 1, 2)
        shade_frame = QHBoxLayout()
        shade_frame.setSpacing(4)
        self.shade_group = QButtonGroup(self)
        rb_full = QRadioButton("Full")
        rb_medium = QRadioButton("Medium")
        self.shade_group.addButton(rb_full, 0)
        self.shade_group.addButton(rb_medium, 1)
        rb_full.setChecked(True)
        shade_frame.addWidget(rb_full)
        shade_frame.addWidget(rb_medium)
        rlayout.addLayout(shade_frame, 1, 3, 1, 2)

        tachy_frame = QHBoxLayout()
        tachy_frame.setSpacing(8)
        self.var_trans_raster = QCheckBox("-trans_raster3d")
        self.var_trans_raster.setChecked(True)
        tachy_frame.addWidget(self.var_trans_raster)
        tachy_frame.addWidget(QLabel("Threads:"))
        self.var_threads = QComboBox()
        self.var_threads.addItems(["1", "2", "4", "8", "16", "28"])
        self.var_threads.setCurrentIndex(2)
        self.var_threads.setMaximumWidth(60)
        tachy_frame.addWidget(self.var_threads)
        tachy_frame.addStretch()
        rlayout.addLayout(tachy_frame, 2, 0, 1, 5)

        for c in range(5):
            rlayout.setColumnStretch(c, 0)
        rlayout.setColumnStretch(1, 1)
        return grp

    def _build_buttons_panel(self):
        grp = SciFiGroupBox("ACTIONS")
        layout = QHBoxLayout(grp)
        layout.setSpacing(8)

        self.btn_preview = QPushButton("\u25c6  Preview (Single)")
        self.btn_preview.setObjectName("PrimaryBtn")
        self.btn_preview.clicked.connect(self._preview_single)
        layout.addWidget(self.btn_preview)

        self.btn_preview_multi = QPushButton("\u25c7  Preview (Multi)")
        self.btn_preview_multi.clicked.connect(self._preview_multi)
        layout.addWidget(self.btn_preview_multi)

        self.btn_render = QPushButton("\u25c6  Render Current View")
        self.btn_render.setObjectName("RenderBtn")
        self.btn_render.setEnabled(False)
        self.btn_render.clicked.connect(self._render_view)
        layout.addWidget(self.btn_render)

        layout.addStretch()
        return grp

    def _build_live_panel(self):
        grp = SciFiGroupBox("LIVE ADJUSTMENTS  (available after VMD opens)")
        layout = QGridLayout(grp)
        layout.setVerticalSpacing(6)
        layout.setHorizontalSpacing(8)

        layout.addWidget(QLabel("Isovalue:"), 0, 0)
        self.iso_slider = QSlider(Qt.Horizontal)
        self.iso_slider.setRange(5, 500)
        self.iso_slider.setValue(50)
        self.iso_slider.setEnabled(False)
        self.iso_slider.valueChanged.connect(self._on_iso_slider_changed)
        layout.addWidget(self.iso_slider, 0, 1)
        self.iso_value_label = QLabel("0.050")
        self.iso_value_label.setMinimumWidth(50)
        self.iso_value_label.setAlignment(Qt.AlignRight | Qt.AlignVCenter)
        layout.addWidget(self.iso_value_label, 0, 2)

        layout.addWidget(QLabel("Opacity:"), 1, 0)
        self.opacity_slider = QSlider(Qt.Horizontal)
        self.opacity_slider.setRange(5, 100)
        self.opacity_slider.setValue(75)
        self.opacity_slider.setEnabled(False)
        self.opacity_slider.valueChanged.connect(self._on_opacity_slider_changed)
        layout.addWidget(self.opacity_slider, 1, 1)
        self.opacity_value_label = QLabel("0.75")
        self.opacity_value_label.setMinimumWidth(50)
        self.opacity_value_label.setAlignment(Qt.AlignRight | Qt.AlignVCenter)
        layout.addWidget(self.opacity_value_label, 1, 2)

        layout.addWidget(QLabel("Iso Input:"), 2, 0)
        self.var_iso = QLineEdit("0.05")
        self.var_iso.setMaximumWidth(70)
        self.var_iso.textChanged.connect(self._on_iso_text_changed)
        layout.addWidget(self.var_iso, 2, 1)

        layout.setColumnStretch(1, 1)
        return grp

    def _build_hydrogen_panel(self):
        grp = SciFiGroupBox("HIDE HYDROGEN")
        layout = QHBoxLayout(grp)
        layout.setSpacing(8)

        self.btn_h_filter = QPushButton("Hide All Hydrogens")
        self.btn_h_filter.setEnabled(False)
        self.btn_h_filter.clicked.connect(self._toggle_h_filter)
        layout.addWidget(self.btn_h_filter)

        layout.addWidget(QLabel("Keep indices (comma separated):"))
        self.var_h_indices = QLineEdit()
        self.var_h_indices.setMaximumWidth(180)
        self.var_h_indices.setPlaceholderText("empty = hide all")
        layout.addWidget(self.var_h_indices)

        layout.addStretch()
        return grp

    def _build_draw_bond_panel(self):
        grp = SciFiGroupBox("DRAW DASHED LINE")
        layout = QGridLayout(grp)
        layout.setVerticalSpacing(4)
        layout.setHorizontalSpacing(6)

        row = 0
        layout.addWidget(QLabel("Atom 1:"), row, 0)
        self.var_bond_atom1 = QLineEdit("0")
        self.var_bond_atom1.setMaximumWidth(50)
        layout.addWidget(self.var_bond_atom1, row, 1)

        layout.addWidget(QLabel("Atom 2:"), row, 2)
        self.var_bond_atom2 = QLineEdit("1")
        self.var_bond_atom2.setMaximumWidth(50)
        layout.addWidget(self.var_bond_atom2, row, 3)

        layout.addWidget(QLabel("Color:"), row, 4)
        self.var_bond_color = QComboBox()
        self.var_bond_color.addItems(
            ["Gray", "Cyan", "Yellow", "Red", "Blue", "Green", "White", "Black"])
        self.var_bond_color.setCurrentIndex(0)
        self.var_bond_color.setMaximumWidth(80)
        layout.addWidget(self.var_bond_color, row, 5)

        row += 1
        layout.addWidget(QLabel("Type:"), row, 0)
        self.var_bond_type = QComboBox()
        self.var_bond_type.addItems(
            ["Dots", "Dashed(pymol)", "Cylinder", "Sphere", "Arrow(cone)", "Line"])
        self.var_bond_type.setCurrentIndex(0)
        self.var_bond_type.setMaximumWidth(110)
        layout.addWidget(self.var_bond_type, row, 1)

        layout.addWidget(QLabel("Material:"), row, 2)
        self.var_bond_mat = QComboBox()
        self.var_bond_mat.addItems(["50% Transparent", "Opaque", "Transparent"])
        self.var_bond_mat.setCurrentIndex(0)
        self.var_bond_mat.setMaximumWidth(130)
        layout.addWidget(self.var_bond_mat, row, 3)

        layout.addWidget(QLabel("Segments:"), row, 4)
        self.var_bond_nbars = QLineEdit("10")
        self.var_bond_nbars.setMaximumWidth(40)
        layout.addWidget(self.var_bond_nbars, row, 5)

        row += 1
        layout.addWidget(QLabel("Spacing:"), row, 0)
        self.var_bond_space = QLineEdit("1.2")
        self.var_bond_space.setMaximumWidth(50)
        layout.addWidget(self.var_bond_space, row, 1)

        layout.addWidget(QLabel("Radius:"), row, 2)
        self.var_bond_radius = QLineEdit("0.06")
        self.var_bond_radius.setMaximumWidth(50)
        layout.addWidget(self.var_bond_radius, row, 3)

        bond_btn_frame = QHBoxLayout()
        bond_btn_frame.setSpacing(4)
        self.btn_draw_bond = QPushButton("Draw Line")
        self.btn_draw_bond.setEnabled(False)
        self.btn_draw_bond.clicked.connect(self._draw_bond)
        bond_btn_frame.addWidget(self.btn_draw_bond)

        self.btn_undo_bond = QPushButton("Undo")
        self.btn_undo_bond.setEnabled(False)
        self.btn_undo_bond.setObjectName("SmallBtn")
        self.btn_undo_bond.clicked.connect(self._undo_bond)
        bond_btn_frame.addWidget(self.btn_undo_bond)

        self.btn_clear_bond = QPushButton("Clear All")
        self.btn_clear_bond.setEnabled(False)
        self.btn_clear_bond.setObjectName("SmallBtn")
        self.btn_clear_bond.clicked.connect(self._clear_bond)
        bond_btn_frame.addWidget(self.btn_clear_bond)

        layout.addLayout(bond_btn_frame, row, 4, 1, 2)

        for c in range(6):
            layout.setColumnStretch(c, 0)
        return grp

    def _apply_theme(self):
        self.setStyleSheet(LIGHT_QSS)

    def _append_log(self, msg):
        self.log_text.moveCursor(QTextCursor.End)
        self.log_text.insertPlainText(msg + "\n")
        self.log_text.moveCursor(QTextCursor.End)

    def _set_progress(self, msg):
        self.progress_label.setText(f"\u25c6  {msg}")

    def _get_style_name(self):
        val = self.var_style.currentText().strip()
        if val:
            return val.split("  ")[0].strip()
        return "sob-art"

    def _get_paths(self):
        vmd = self.var_vmd.text().strip()
        tachyon = os.path.join(os.path.dirname(vmd), "tachyon_WIN32.exe")
        return {
            "vmd": vmd,
            "tachyon": tachyon,
        }

    def _save_paths(self):
        vmd = self.var_vmd.text().strip()
        tachyon = os.path.join(os.path.dirname(vmd), "tachyon_WIN32.exe")
        backend.save_config(self.paths.get("multiwfn", ""), vmd, tachyon)

    def _get_params(self):
        try:
            iso = float(self.var_iso.text().strip())
        except ValueError:
            iso = 0.05
        style_name = self._get_style_name()
        try:
            res_str = self.var_res.currentText().strip()
            w, h = res_str.split("x")
            resolution = (int(w), int(h))
        except (ValueError, AttributeError):
            resolution = (2000, 1500)
        shade_id = self.shade_group.checkedId()
        shade_mode = "full" if shade_id == 0 else "medium"
        return iso, style_name, resolution, shade_mode

    def _browse_vmd(self):
        path, _ = QFileDialog.getOpenFileName(
            self, "Select VMD Executable", "", "Executable (*.exe)")
        if path:
            self.var_vmd.setText(path)

    def _browse_input(self):
        if self.mode_group.checkedId() == 0:
            path = QFileDialog.getExistingDirectory(self, "Select Input Folder")
        else:
            path, _ = QFileDialog.getOpenFileName(
                self, "Select Cube File", "",
                "Cube File (*.cub);;All Files (*.*)")
        if path:
            self.var_path.setText(path)

    def _browse_out(self):
        path = QFileDialog.getExistingDirectory(self, "Select Output Directory")
        if path:
            self.var_out.setText(path)

    def _preview_single(self):
        path = self.var_path.text().strip()
        if not path:
            QMessageBox.warning(self, "Warning",
                "Please select a .cub file or folder first")
            return

        out = self.var_out.text().strip() or (
            path if os.path.isdir(path) else os.path.dirname(path))

        cubes = sorted(glob.glob(os.path.join(out, "*.cub")) if os.path.isdir(path)
                       else [path] if path.endswith(".cub") else [])
        if not cubes:
            cubes = sorted(glob.glob(os.path.join(
                os.path.dirname(path), "*.cub"))) if os.path.isfile(path) else []
        if not cubes:
            QMessageBox.warning(self, "Warning",
                "No .cub files found.\nPlease select a .cub file or a folder containing .cub files.")
            return

        if len(cubes) == 1:
            self._do_preview(cubes[0])
            return

        from PyQt5.QtWidgets import QInputDialog
        cube_names = [os.path.basename(c) for c in cubes]
        item, ok = QInputDialog.getItem(
            self, "Select Cube File", "Choose cube file to preview:",
            cube_names, 0, False)
        if not ok or not item:
            return
        self._do_preview(cubes[cube_names.index(item)])

    def _do_preview(self, cube_path):
        self._close_persist_sock()
        iso, style_name, _, shade_mode = self._get_params()
        exe_paths = self._get_paths()

        if not os.path.exists(exe_paths["vmd"]):
            QMessageBox.warning(self, "Path Error",
                f"VMD not found:\n{exe_paths['vmd']}")
            return

        self.current_iso = iso
        self.current_opacity = None

        self._append_log(f"\nStarting VMD preview: {os.path.basename(cube_path)}")
        self._append_log(f"Style: {style_name}, Isovalue: {iso}")
        self._append_log("Adjust view in VMD, then click [Render Current View]")

        try:
            port, render_dir = backend.preview_cube(
                cube_path, isovalue=iso, style_name=style_name,
                vmd_exe=exe_paths["vmd"], shade_mode=shade_mode)
            if port:
                self.vmd_port = port
                self.vmd_render_dir = render_dir
                self.vmd_cube_path = cube_path
                self.vmd_multi_cubes = None
                self.btn_render.setEnabled(True)
                self.btn_draw_bond.setEnabled(True)
                self.btn_undo_bond.setEnabled(True)
                self.btn_clear_bond.setEnabled(True)
                self.btn_h_filter.setEnabled(True)
                self.iso_slider.setEnabled(True)
                self.iso_slider.blockSignals(True)
                self.iso_slider.setValue(int(iso * 1000))
                self.iso_slider.blockSignals(False)
                self.iso_value_label.setText(f"{iso:.3f}")
                self.opacity_slider.setEnabled(True)
                if self.current_opacity is None:
                    style = backend.STYES.get(style_name, backend.STYES["sob-art"])
                    self.current_opacity = style["surface_mat"][5]
                self.opacity_slider.blockSignals(True)
                self.opacity_slider.setValue(int(self.current_opacity * 100))
                self.opacity_slider.blockSignals(False)
                self.opacity_value_label.setText(f"{self.current_opacity:.2f}")
                self._append_log(f"VMD started (port {port}), waiting for operations...")
            else:
                self._append_log("VMD start failed")
        except Exception as e:
            self._append_log(f"VMD start error: {e}")

    def _preview_multi(self):
        path = self.var_path.text().strip()
        if not path:
            QMessageBox.warning(self, "Warning", "Please select a folder first")
            return

        out = self.var_out.text().strip() or path
        all_cubes = sorted(glob.glob(os.path.join(out, "*.cub")))

        if not all_cubes:
            QMessageBox.warning(self, "Warning",
                "No .cub files found in the directory")
            return

        from PyQt5.QtWidgets import QDialog, QListWidget, QDialogButtonBox

        if len(all_cubes) == 1:
            cubes = [(all_cubes[0], os.path.splitext(os.path.basename(all_cubes[0]))[0])]
        else:
            dlg = QDialog(self)
            dlg.setWindowTitle("Select cubes to preview")
            dlg.resize(500, 420)
            dlg_layout = QVBoxLayout(dlg)

            dlg_layout.addWidget(QLabel(
                "Select cubes to preview (multi-select with Ctrl or Shift):"))

            list_widget = QListWidget()
            list_widget.setSelectionMode(QListWidget.ExtendedSelection)
            for i, c in enumerate(all_cubes):
                list_widget.addItem(f"{os.path.basename(c)}")
                list_widget.item(i).setSelected(True)
            dlg_layout.addWidget(list_widget)

            btn_box = QDialogButtonBox(QDialogButtonBox.Ok | QDialogButtonBox.Cancel)
            btn_box.accepted.connect(dlg.accept)
            btn_box.rejected.connect(dlg.reject)
            dlg_layout.addWidget(btn_box)

            if dlg.exec_() != QDialog.Accepted:
                return

            selected = [all_cubes[i.row()] for i in list_widget.selectedIndexes()]
            if not selected:
                return
            cubes = [(c, os.path.splitext(os.path.basename(c))[0]) for c in selected]

        self._do_preview_multi(cubes)

    def _do_preview_multi(self, cubes):
        self._close_persist_sock()
        iso, style_name, _, shade_mode = self._get_params()
        exe_paths = self._get_paths()

        if not os.path.exists(exe_paths["vmd"]):
            QMessageBox.warning(self, "Path Error",
                f"VMD not found:\n{exe_paths['vmd']}")
            return

        h_str = self.var_h_indices.text().strip()
        if h_str:
            try:
                keep_h_indices = [int(x.strip()) for x in h_str.split(",") if x.strip()]
            except ValueError:
                keep_h_indices = []
        else:
            keep_h_indices = None

        self.current_iso = iso
        self.current_opacity = None

        self._append_log(f"\nStarting VMD multi-cube preview")
        self._append_log(f"Style: {style_name}, Isovalue: {iso}")

        try:
            port, render_dir, copied_cubes = backend.preview_multi_cubes(
                cubes, iso, style_name=style_name,
                vmd_exe=exe_paths["vmd"], shade_mode=shade_mode,
                keep_h_indices=keep_h_indices)
            if port:
                self.vmd_port = port
                self.vmd_render_dir = render_dir
                self.vmd_multi_cubes = copied_cubes
                self.vmd_cube_path = None
                self.btn_render.setEnabled(True)
                self.btn_draw_bond.setEnabled(True)
                self.btn_undo_bond.setEnabled(True)
                self.btn_clear_bond.setEnabled(True)
                self.btn_h_filter.setEnabled(True)
                self.iso_slider.setEnabled(True)
                self.iso_slider.blockSignals(True)
                self.iso_slider.setValue(int(iso * 1000))
                self.iso_slider.blockSignals(False)
                self.iso_value_label.setText(f"{iso:.3f}")
                self.opacity_slider.setEnabled(True)
                if self.current_opacity is None:
                    style = backend.STYES.get(style_name, backend.STYES["sob-art"])
                    self.current_opacity = style["surface_mat"][5]
                self.opacity_slider.blockSignals(True)
                self.opacity_slider.setValue(int(self.current_opacity * 100))
                self.opacity_slider.blockSignals(False)
                self.opacity_value_label.setText(f"{self.current_opacity:.2f}")
                self._append_log(f"VMD started (port {port}), waiting for operations...")
            else:
                self._append_log("VMD start failed")
        except Exception as e:
            self._append_log(f"VMD start error: {e}")

    def _render_view(self):
        if not self.vmd_port or not self.vmd_render_dir:
            QMessageBox.warning(self, "Warning",
                "Please click [Preview] to open VMD first")
            return

        out = self.var_out.text().strip()
        if out and not os.path.isdir(out):
            os.makedirs(out, exist_ok=True)

        _, style_name, resolution, shade_mode = self._get_params()
        exe_paths = self._get_paths()

        output_png = None
        if self.vmd_cube_path:
            cube_stem = os.path.splitext(os.path.basename(self.vmd_cube_path))[0]
            output_png = os.path.join(out, f"{cube_stem}.png") if out else None
        elif self.vmd_multi_cubes and self.vmd_multi_cubes[0][0]:
            stems = "_".join([os.path.splitext(os.path.basename(c))[0]
                              for c, _ in self.vmd_multi_cubes])
            output_png = os.path.join(out, f"{stems}_multi.png") if out else None

        trans_raster = self.var_trans_raster.isChecked()
        threads = int(self.var_threads.currentText())

        self.btn_render.setEnabled(False)
        self.render_worker = RenderWorker(
            self.vmd_port, self.vmd_render_dir, output_png,
            exe_paths["tachyon"], resolution, style_name,
            shade_mode, trans_raster, threads)
        self.render_worker.log_signal.connect(self._append_log)
        self.render_worker.finished_signal.connect(self._on_render_done)
        self.render_worker.start()

    def _on_render_done(self, png_path):
        self.btn_render.setEnabled(True)
        if png_path and os.path.exists(png_path):
            os.startfile(png_path)

    def _toggle_h_filter(self):
        if not self.vmd_port:
            self._append_log("Please click preview button to start VMD first")
            return

        current_text = self.btn_h_filter.text()
        if current_text == "Hide All Hydrogens":
            self.btn_h_filter.setText("Show All Hydrogens")
            h_str = self.var_h_indices.text().strip()
            if h_str:
                try:
                    keep_indices = [int(x.strip()) for x in h_str.split(",") if x.strip()]
                    idx_str = " ".join(map(str, keep_indices))
                    sel_str = f"not element H or (element H and index {idx_str})"
                except ValueError:
                    sel_str = "not element H"
            else:
                sel_str = "not element H"
            cmd = (
                f'foreach mid [molinfo list] {{'
                f'  mol modselect 0 $mid "{sel_str}"'
                f'}}'
            )
            self._send_vmd_cmd(cmd)
            self._append_log("[Hide H] Hid hydrogens for all molecules")
        else:
            self.btn_h_filter.setText("Hide All Hydrogens")
            cmd = 'foreach mid [molinfo list] { mol modselect 0 $mid all }'
            self._send_vmd_cmd(cmd)
            self._append_log("[Hide H] Restored hydrogens for all molecules")

    def _draw_bond(self):
        if not self.vmd_port:
            QMessageBox.warning(self, "Warning",
                "Please click [Preview] to open VMD first")
            return
        a1 = self.var_bond_atom1.text().strip()
        a2 = self.var_bond_atom2.text().strip()
        if not a1 or not a2:
            QMessageBox.warning(self, "Warning", "Please enter two atom indices")
            return

        bond_color_map = {
            "Black": "black", "Gray": "gray", "Cyan": "cyan", "Yellow": "yellow",
            "Red": "red", "Blue": "blue", "Green": "green", "White": "white"}
        bond_type_map = {
            "Dots": "dots", "Dashed(pymol)": "pymol",
            "Cylinder": "cylinder", "Sphere": "sphere",
            "Arrow(cone)": "cone", "Line": "line"}
        bond_mat_map = {
            "Opaque": "Opaque", "50% Transparent": "HalfTransparent",
            "Transparent": "Transparent"}

        color = bond_color_map.get(self.var_bond_color.currentText(), "gray")
        btype = bond_type_map.get(self.var_bond_type.currentText(), "dots")
        mat = bond_mat_map.get(self.var_bond_mat.currentText(), "HalfTransparent")
        nbars = self.var_bond_nbars.text().strip() or "10"
        space = self.var_bond_space.text().strip() or "1.2"
        radius = self.var_bond_radius.text().strip() or "0.06"

        if btype == "cylinder":
            cmd = (f"draw_bond -mol1 top -index1 {a1} -mol2 top -index2 {a2} "
                   f"-color {color} -h_type {btype} -h_radius {radius} -mat {mat}")
        else:
            cmd = (f"draw_bond -mol1 top -index1 {a1} -mol2 top -index2 {a2} "
                   f"-h_nbars {nbars} -h_space {space} -h_radius {radius} "
                   f"-color {color} -h_type {btype} -mat {mat}")
        resp = self._send_vmd_cmd(cmd)
        if resp and "ERROR" not in resp:
            self._append_log(f"[Draw Bond] Atom{a1}-{a2} {color} {btype} {mat}")
            self.btn_undo_bond.setEnabled(True)
        else:
            self._append_log("[Draw Bond] Failed")

    def _undo_bond(self):
        resp = self._send_vmd_cmd("draw_bond_undo")
        if resp and "ERROR" not in resp:
            self._append_log("[Bond] Undo")
        else:
            self._append_log("[Bond] Undo failed")

    def _clear_bond(self):
        resp = self._send_vmd_cmd("draw_bond_clear")
        if resp and "ERROR" not in resp:
            self._append_log("[Bond] Cleared all")
            self.btn_undo_bond.setEnabled(False)
        else:
            self._append_log("[Bond] Clear failed")

    def _send_vmd_cmd(self, cmd):
        if not self.vmd_port:
            return ""
        sock = getattr(self, '_vmd_persist_sock', None)
        if sock is None:
            try:
                sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
                sock.settimeout(5)
                sock.connect(("127.0.0.1", self.vmd_port))
                self._vmd_persist_sock = sock
            except Exception:
                return ""
        try:
            sock.sendall((cmd + "\n").encode("utf-8"))
            resp = b""
            sock.settimeout(0.3)
            try:
                while True:
                    chunk = sock.recv(4096)
                    if not chunk:
                        break
                    resp += chunk
                    if b"\n" in resp:
                        break
            except socket.timeout:
                pass
            sock.settimeout(5)
            return resp.decode("utf-8", errors="replace").strip()
        except Exception:
            self._close_persist_sock()
            return ""

    def _close_persist_sock(self):
        sock = getattr(self, '_vmd_persist_sock', None)
        if sock:
            try:
                sock.close()
            except Exception:
                pass
            self._vmd_persist_sock = None

    def _on_iso_slider_changed(self, val):
        if not self.vmd_port:
            return
        iso = val / 1000.0
        self.current_iso = iso
        self.iso_value_label.setText(f"{iso:.3f}")
        self.var_iso.blockSignals(True)
        self.var_iso.setText(f"{iso:.4g}")
        self.var_iso.blockSignals(False)
        cmd = f"mol modstyle 1 top Isosurface {iso} 0 0 0 1 1"
        self._send_vmd_cmd(cmd)
        cmd = f"mol modstyle 2 top Isosurface -{iso} 0 0 0 1 1"
        self._send_vmd_cmd(cmd)

    def _on_iso_text_changed(self, text):
        if not self.vmd_port:
            return
        try:
            iso = float(text.strip())
        except ValueError:
            return
        self.current_iso = iso
        self.iso_slider.blockSignals(True)
        self.iso_slider.setValue(int(iso * 1000))
        self.iso_slider.blockSignals(False)
        self.iso_value_label.setText(f"{iso:.3f}")
        cmd = f"mol modstyle 1 top Isosurface {iso} 0 0 0 1 1"
        self._send_vmd_cmd(cmd)
        cmd = f"mol modstyle 2 top Isosurface -{iso} 0 0 0 1 1"
        self._send_vmd_cmd(cmd)

    def _on_opacity_slider_changed(self, val):
        if not self.vmd_port:
            return
        op = val / 100.0
        self.current_opacity = op
        self.opacity_value_label.setText(f"{op:.2f}")
        for mat_name in ["_stl_a", "_stl_b"]:
            cmd = f"material change opacity {mat_name} {op}"
            self._send_vmd_cmd(cmd)

    def closeEvent(self, event):
        self._close_persist_sock()
        super().closeEvent(event)


def main():
    app = QApplication(sys.argv)
    app.setStyle("Fusion")
    window = CubeViewerApp()
    window.show()
    sys.exit(app.exec_())


if __name__ == "__main__":
    main()
