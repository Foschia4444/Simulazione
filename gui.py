# -*- coding: utf-8 -*-
from PyQt5 import QtCore, QtGui, QtWidgets
from PyQt5.Qt3DCore import QEntity, QTransform
from PyQt5.Qt3DExtras import Qt3DWindow, QPhongMaterial, QCuboidMesh, QCylinderMesh, QOrbitCameraController
from PyQt5.Qt3DRender import QCamera, QPointLight
from PyQt5.QtGui import QVector3D, QQuaternion
import sys
import threading
import queue
import time
import pyqtgraph as pg
from collections import deque
from math import sin, radians, pi
from main import start_simulation, run_server, run_client
import math

class Ui_MainWindow(object):
    def setupUi(self, MainWindow):
        MainWindow.setObjectName("MainWindow")
        MainWindow.resize(1782, 1016)
        sizePolicy = QtWidgets.QSizePolicy(QtWidgets.QSizePolicy.Fixed, QtWidgets.QSizePolicy.Fixed)
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(MainWindow.sizePolicy().hasHeightForWidth())
        MainWindow.setSizePolicy(sizePolicy)
        
        font = QtGui.QFont()
        font.setFamily("Times New Roman")
        font.setPointSize(10)
        font.setBold(True)
        font.setWeight(75)
        MainWindow.setFont(font)
        
        MainWindow.setStyleSheet("""
            QMainWindow {
                background-color: #444;
            }
            QDial {
                background-color: #2196F3;
                border: 8px solid #FFEB3B;
                border-radius: 50%;
            }
            QDial::handle {
                background-color: #4CAF50;
                border: 4px solid #388E3C;
                width: 35px;
                height: 35px;
                border-radius: 50%;
                margin-left: -17px;
                margin-top: -17px;
            }
        """)
        
        self.centralwidget = QtWidgets.QWidget(MainWindow)
        self.centralwidget.setObjectName("centralwidget")
        
        # Control Panel
        self.griglia = QtWidgets.QWidget(self.centralwidget)
        self.griglia.setGeometry(QtCore.QRect(290, 220, 761, 481))
        self.griglia.setStyleSheet("""
            QWidget {
                background-color: #333333;
                border: 3px solid #FFEB3B;
                border-radius: 10px;
                padding: 20px;
            }
            QLCDNumber {
                background-color: #222222;
                color: white;
                border: 2px solid #FFEB3B;
                border-radius: 5px;
                font-size: 20px;
                padding: 10px;
            }
        """)
        self.griglia.setObjectName("griglia")

        # 3D View Container (smaller size)
        self.three_d_container = QtWidgets.QWidget(self.centralwidget)
        self.three_d_container.setGeometry(QtCore.QRect(290, 720, 761, 250))
        self.three_d_container.setStyleSheet("background-color: #000000; border: 3px solid #FFEB3B; border-radius: 10px;")
        self.three_d_container.setObjectName("three_d_container")
        self.three_d_layout = QtWidgets.QVBoxLayout(self.three_d_container)
        self.three_d_layout.setContentsMargins(0, 0, 0, 0)
        self.three_d_layout.setSpacing(0)

        # Graphics Container
        self.graphics_container = QtWidgets.QWidget(self.centralwidget)
        self.graphics_container.setGeometry(QtCore.QRect(1060, 20, 700, 950))
        self.graphics_layout = QtWidgets.QVBoxLayout(self.graphics_container)
        self.graphics_container.setLayout(self.graphics_layout)
        
        # Plots
        self.plot1 = pg.PlotWidget(title="<span style='color: white; font-size: 12pt'>Velocità e Temperatura Lama</span>")
        self.plot1.setBackground('#333333')
        self.plot1.showGrid(x=True, y=True, alpha=0.3)
        self.plot1.setLabel('left', 'Valore', color='white')
        self.plot1.setLabel('bottom', 'Tempo (s)', color='white')
        self.plot1.getAxis('left').setPen('w')
        self.plot1.getAxis('bottom').setPen('w')
        
        self.plot2 = pg.PlotWidget(title="<span style='color: white; font-size: 12pt'>Temperature e Consumo</span>")
        self.plot2.setBackground('#333333')
        self.plot2.showGrid(x=True, y=True, alpha=0.3)
        self.plot2.setLabel('left', 'Valore', color='white')
        self.plot2.setLabel('bottom', 'Tempo (s)', color='white')
        self.plot2.getAxis('left').setPen('w')
        self.plot2.getAxis('bottom').setPen('w')
        
        self.graphics_layout.addWidget(self.plot1)
        self.graphics_layout.addWidget(self.plot2)

        # Buttons with specific styling
        self.pushButton_5 = QtWidgets.QPushButton(self.griglia)
        self.pushButton_5.setGeometry(QtCore.QRect(20, 90, 191, 51))
        font = QtGui.QFont()
        font.setFamily("Arial")
        font.setPointSize(16)
        font.setBold(True)
        self.pushButton_5.setFont(font)
        self.pushButton_5.setStyleSheet("""
            QPushButton {
                background-color: #4CAF50;
                color: white;
                border: 2px solid #388E3C;
                padding: 12px 25px;
                font-size: 16px;
                border-radius: 8px;
                font-weight: bold;
            }
            QPushButton:hover {
                background-color: #45a049;
            }
            QPushButton:pressed {
                background-color: #388E3C;
            }
        """)
        self.pushButton_5.setObjectName("pushButton_5")

        self.pushButton_6 = QtWidgets.QPushButton(self.griglia)
        self.pushButton_6.setGeometry(QtCore.QRect(20, 150, 191, 51))
        font = QtGui.QFont()
        font.setFamily("Arial")
        font.setPointSize(16)
        font.setBold(True)
        self.pushButton_6.setFont(font)
        self.pushButton_6.setStyleSheet("""
            QPushButton {
                background-color: #f44336;
                color: white;
                border: none;
                padding: 10px 20px;
                font-size: 16px;
                border-radius: 5px;
            }
            QPushButton:hover {
                background-color: #e53935;
            }
            QPushButton:pressed {
                background-color: #c62828;
            }
        """)
        self.pushButton_6.setObjectName("pushButton_6")

        self.pushButton_3 = QtWidgets.QPushButton(self.griglia)
        self.pushButton_3.setGeometry(QtCore.QRect(20, 320, 150, 150))  # Circular button
        font = QtGui.QFont()
        font.setFamily("Arial")
        font.setPointSize(13)
        font.setBold(True)
        self.pushButton_3.setFont(font)
        self.pushButton_3.setStyleSheet("""
            QPushButton {
                background-color: red;
                color: white;
                border: 3px solid black;
                border-radius: 50px;
                padding: 0;
            }
            QPushButton:hover {
                background-color: darkred;
            }
            QPushButton:pressed {
                background-color: black;
                border: 4px solid darkred;
            }
        """)
        self.pushButton_3.setObjectName("pushButton_3")
        self.pushButton_3.setObjectName("pushButton_3")

        self.pushButton_4 = QtWidgets.QPushButton(self.griglia)
        self.pushButton_4.setGeometry(QtCore.QRect(20, 220, 191, 61))
        font = QtGui.QFont()
        font.setFamily("Arial")
        font.setPointSize(16)
        font.setBold(True)
        self.pushButton_4.setFont(font)
        self.pushButton_4.setStyleSheet("""
            QPushButton {
                background-color: #2196F3;
                color: white;
                border: 2px solid #1E88E5;
                padding: 12px 25px;
                font-size: 16px;
                border-radius: 8px;
                font-weight: bold;
            }
            QPushButton:hover {
                background-color: #1976D2;
            }
            QPushButton:pressed {
                background-color: #1565C0;
            }
        """)
        self.pushButton_4.setObjectName("pushButton_4")

        # Status Label
        self.label = QtWidgets.QLabel(self.griglia)
        self.label.setGeometry(QtCore.QRect(270, 110, 461, 91))
        self.label.setStyleSheet("""
            QLabel {
                background-color: #f44336;
                color: white;
                padding: 10px;
                border-radius: 5px;
                font-size: 16px;
                text-align: center;
                font-weight: bold;
            }
        """)
        self.label.setObjectName("label")

        # LCD Display
        self.lcd_velocita = QtWidgets.QLCDNumber(self.griglia)
        self.lcd_velocita.setGeometry(QtCore.QRect(520, 260, 211, 171))
        self.lcd_velocita.setObjectName("lcd_velocita")

        # Title Label
        self.label_2 = QtWidgets.QLabel(self.griglia)
        self.label_2.setGeometry(QtCore.QRect(230, 0, 231, 71))
        self.label_2.setObjectName("label_2")

        # Speed Dial
        self.dial = QtWidgets.QDial(self.griglia)
        self.dial.setGeometry(QtCore.QRect(320, 280, 150, 150))
        self.dial.setMinimum(1)
        self.dial.setMaximum(100)
        self.dial.setObjectName("dial")
        
        MainWindow.setCentralWidget(self.centralwidget)
        self.menubar = QtWidgets.QMenuBar(MainWindow)
        self.menubar.setGeometry(QtCore.QRect(0, 0, 1782, 26))
        self.menubar.setObjectName("menubar")
        MainWindow.setMenuBar(self.menubar)
        self.statusbar = QtWidgets.QStatusBar(MainWindow)
        self.statusbar.setObjectName("statusbar")
        MainWindow.setStatusBar(self.statusbar)

        self.retranslateUi(MainWindow)
        QtCore.QMetaObject.connectSlotsByName(MainWindow)

    def retranslateUi(self, MainWindow):
        _translate = QtCore.QCoreApplication.translate
        MainWindow.setWindowTitle(_translate("MainWindow", "Segatrice CNC"))
        self.pushButton_5.setText(_translate("MainWindow", "ON/OFF macchina"))
        self.pushButton_6.setText(_translate("MainWindow", "ON/OFF lama"))
        self.pushButton_3.setText(_translate("MainWindow", "EMERGENCY"))
        self.pushButton_4.setText(_translate("MainWindow", "CAMBIO LAMA"))
        self.label.setText(_translate("MainWindow", "Macchina Spenta"))
        self.label_2.setText(_translate("MainWindow", "<html><head/><body><p><span style=\" font-size:12pt; font-weight:600; font-style:italic; color:#ffffff;\">SEGATRICE C.N.C.</span></p></body></html>"))

class SegatriceCNC(QtWidgets.QMainWindow):
    def __init__(self):
        super().__init__()
        self.ui = Ui_MainWindow()
        self.ui.setupUi(self)

        # Initialize simulation
        self.data_queue = queue.Queue()
        self.command_queue = queue.Queue()
        
        # State variables
        self.macchina_accesa = False
        self.lama_attiva = False
        self.emergenza = False
        self.current_speed = 0.0
        self.current_blade_angle = 30.0
        self.start_time = time.time()
        self.cutting_progress = 0.0
        self.blade_vibration = 0.0
        self.blade_rotation = 0.0
        self.blade_heat_factor = 0.0

        # Configure plots
        self.max_data_points = 200
        self.time_data = deque(maxlen=self.max_data_points)
        self.speed_data = deque(maxlen=self.max_data_points)
        self.blade_temp_data = deque(maxlen=self.max_data_points)
        self.machine_temp_data = deque(maxlen=self.max_data_points)
        self.consumption_data = deque(maxlen=self.max_data_points)
        self.coolant_temp_data = deque(maxlen=self.max_data_points)
        
        self.configure_dynamic_plots()
        self.setup_3d_scene()

        # Connect buttons
        self.ui.pushButton_5.clicked.connect(self.toggle_macchina)
        self.ui.pushButton_6.clicked.connect(self.toggle_lama)
        self.ui.pushButton_3.clicked.connect(self.emergenza_attiva)
        self.ui.pushButton_4.clicked.connect(self.cambio_lama)
        self.ui.dial.valueChanged.connect(self.aggiorna_velocita)

        # Initial state
        self.ui.dial.setEnabled(False)
        self.ui.dial.setValue(0)
        self.ui.lcd_velocita.display(0)

        # Start simulation
        self.simulation_thread = threading.Thread(target=start_simulation, args=(self.data_queue, self.command_queue))
        self.server_thread = threading.Thread(target=run_server)
        self.client_thread= threading.Thread(target=run_client)
        self.simulation_thread.daemon = True
        self.server_thread.daemon = True
        self.client_thread.daemon = True
        self.simulation_thread.start()
        self.server_thread.start()
        self.client_thread.start()
        # Timer for updates
        self.timer = QtCore.QTimer(self)
        self.timer.timeout.connect(self.leggi_coda)
        self.timer.start(100)

    def configure_dynamic_plots(self):
        colors = {
            'speed': '#00FF00',
            'blade_temp': '#FF0000',
            'machine_temp': '#FFFF00',
            'coolant_temp': '#00BFFF',
            'consumption': '#FFFFFF'
        }
        
        self.ui.plot1.clear()
        self.ui.plot1.addLegend()
        self.speed_curve = self.ui.plot1.plot(name="Velocità (m/s)", pen=pg.mkPen(colors['speed'], width=2))
        self.blade_temp_curve = self.ui.plot1.plot(name="Temp. Lama (°C)", pen=pg.mkPen(colors['blade_temp'], width=2))
        
        self.ui.plot2.clear()
        self.ui.plot2.addLegend()
        self.machine_temp_curve = self.ui.plot2.plot(name="Temp. Macchina (°C)", pen=pg.mkPen(colors['machine_temp'], width=2))
        self.coolant_temp_curve = self.ui.plot2.plot(name="Temp. Refrigerante (°C)", pen=pg.mkPen(colors['coolant_temp'], width=2))
        self.consumption_curve = self.ui.plot2.plot(name="Consumo (kW)", pen=pg.mkPen(colors['consumption'], width=2))

    def setup_3d_scene(self):
        # Create 3D window
        self.view = Qt3DWindow()
        self.container = self.createWindowContainer(self.view)
        self.ui.three_d_layout.addWidget(self.container)

        # Root entity
        self.root_entity = QEntity()

        # Camera setup - closer view
        self.camera = self.view.camera()
        self.camera.lens().setPerspectiveProjection(45.0, 16.0/9.0, 0.1, 1000.0)
        self.camera.setPosition(QVector3D(20, 30, 40))  # Adjusted for a better angle
        self.camera.setViewCenter(QVector3D(0, 0, 0))
        self.camera.setUpVector(QVector3D(0, 1, 0))

        # Camera controller
        cam_controller = QOrbitCameraController(self.root_entity)
        cam_controller.setCamera(self.camera)
        cam_controller.setLinearSpeed(50.0)
        cam_controller.setLookSpeed(180.0)

        # Lighting
        self.setup_lighting()

        # Machine base - properly connected to arm
        self.setup_machine_base()

        # Arm and blade - fixed positioning
        self.setup_arm_and_blade()

        # Material to cut with proper cutting animation
        self.setup_material_to_cut()

        # Set scene
        self.view.setRootEntity(self.root_entity)

    def setup_lighting(self):
        # Main light
        main_light_entity = QEntity(self.root_entity)
        main_light = QPointLight(main_light_entity)
        main_light.setColor(QtGui.QColor(255, 255, 255))
        main_light.setIntensity(0.8)
        main_light_transform = QTransform(main_light_entity)
        main_light_transform.setTranslation(QVector3D(30, 50, 30))
        main_light_entity.addComponent(main_light)
        main_light_entity.addComponent(main_light_transform)

        # Fill light
        fill_light_entity = QEntity(self.root_entity)
        fill_light = QPointLight(fill_light_entity)
        fill_light.setColor(QtGui.QColor(200, 200, 255))
        fill_light.setIntensity(0.3)
        fill_light_transform = QTransform(fill_light_entity)
        fill_light_transform.setTranslation(QVector3D(-30, 30, -30))
        fill_light_entity.addComponent(fill_light)
        fill_light_entity.addComponent(fill_light_transform)

    def setup_machine_base(self):
        # Base - larger and more realistic
        base_entity = QEntity(self.root_entity)
        base_mesh = QCuboidMesh()
        base_mesh.setXExtent(80.0)
        base_mesh.setYExtent(15.0)  # Thicker base
        base_mesh.setZExtent(50.0)
        base_material = QPhongMaterial()
        base_material.setDiffuse(QtGui.QColor(60, 60, 60))
        base_material.setShininess(50)
        base_transform = QTransform()
        base_transform.setTranslation(QVector3D(0, -7.5, 0))  # Adjusted for thicker base
        base_entity.addComponent(base_mesh)
        base_entity.addComponent(base_material)
        base_entity.addComponent(base_transform)

        # Table
        table_entity = QEntity(self.root_entity)
        table_mesh = QCuboidMesh()
        table_mesh.setXExtent(70.0)
        table_mesh.setYExtent(2.0)
        table_mesh.setZExtent(40.0)
        table_material = QPhongMaterial()
        table_material.setDiffuse(QtGui.QColor(120, 120, 120))
        table_material.setSpecular(QtGui.QColor(200, 200, 200))
        table_material.setShininess(100)
        table_transform = QTransform()
        table_transform.setTranslation(QVector3D(0, 0, 0))  # On top of base
        table_entity.addComponent(table_mesh)
        table_entity.addComponent(table_material)
        table_entity.addComponent(table_transform)

        # Column that connects base to arm
        column_entity = QEntity(self.root_entity)
        column_mesh = QCuboidMesh()
        column_mesh.setXExtent(15.0)
        column_mesh.setYExtent(40.0)  # Height of column
        column_mesh.setZExtent(15.0)
        column_material = QPhongMaterial()
        column_material.setDiffuse(QtGui.QColor(70, 70, 70))
        column_transform = QTransform()
        column_transform.setTranslation(QVector3D(-30, 20, 0))  # Positioned at back left
        column_entity.addComponent(column_mesh)
        column_entity.addComponent(column_material)
        column_entity.addComponent(column_transform)

    def setup_arm_and_blade(self):
        # Arm pivot point (connected to column)
        self.arm_pivot = QEntity(self.root_entity)
        pivot_mesh = QCylinderMesh()
        pivot_mesh.setRadius(3.0)
        pivot_mesh.setLength(10.0)
        pivot_material = QPhongMaterial()
        pivot_material.setDiffuse(QtGui.QColor(80, 80, 80))
        pivot_transform = QTransform()
        pivot_transform.setRotationX(90)
        pivot_transform.setTranslation(QVector3D(-30, 10, 0))  # Pivot point position
        self.arm_pivot.addComponent(pivot_mesh)
        self.arm_pivot.addComponent(pivot_material)
        self.arm_pivot.addComponent(pivot_transform)

        # Main arm (connected to pivot)
        self.arm_entity = QEntity(self.root_entity)
        arm_mesh = QCuboidMesh()
        arm_mesh.setXExtent(50.0)  # Length of the arm
        arm_mesh.setYExtent(8.0)   # Height of the arm
        arm_mesh.setZExtent(8.0)   # Width of the arm
        arm_material = QPhongMaterial()
        arm_material.setDiffuse(QtGui.QColor(200, 120, 50))
        arm_material.setSpecular(QtGui.QColor(255, 200, 150))
        arm_material.setShininess(80)
        self.arm_transform = QTransform()
        # Position the arm so its left end is at the pivot point (-30, 10, 0)
        # The arm's length is 50, so its center is at x = -30 + 25 = -5
        self.arm_transform.setTranslation(QVector3D(-5, 10, 0))
        self.arm_entity.addComponent(arm_mesh)
        self.arm_entity.addComponent(arm_material)
        self.arm_entity.addComponent(self.arm_transform)

        # Blade wheels
        self.setup_blade_wheels()

        # Blade
        self.setup_enhanced_blade()

    def setup_blade_wheels(self):
    # Top wheel (near the blade)
        wheel_top_entity = QEntity(self.arm_entity)
        wheel_top_mesh = QCylinderMesh()
        wheel_top_mesh.setRadius(6.0)
        wheel_top_mesh.setLength(2.0)
        wheel_top_mesh.setSlices(32)
        wheel_top_material = QPhongMaterial()
        wheel_top_material.setDiffuse(QtGui.QColor(150, 150, 150))
        wheel_top_material.setSpecular(QtGui.QColor(200, 200, 200))
        wheel_top_transform = QTransform()
        wheel_top_transform.setRotationX(90)
        wheel_top_transform.setTranslation(QVector3D(5.0, 0, 0))  # Align with blade at x = 5.0
        wheel_top_entity.addComponent(wheel_top_mesh)
        wheel_top_entity.addComponent(wheel_top_material)
        wheel_top_entity.addComponent(wheel_top_transform)

        # Bottom wheel (slightly to the left of the blade)
        wheel_bottom_entity = QEntity(self.arm_entity)
        wheel_bottom_mesh = QCylinderMesh()
        wheel_bottom_mesh.setRadius(6.0)
        wheel_bottom_mesh.setLength(2.0)
        wheel_bottom_mesh.setSlices(32)
        wheel_bottom_material = QPhongMaterial()
        wheel_bottom_material.setDiffuse(QtGui.QColor(150, 150, 150))
        wheel_bottom_transform = QTransform()
        wheel_bottom_transform.setRotationX(90)
        wheel_bottom_transform.setTranslation(QVector3D(-5.0, 0, 0))  # Slightly to the left of the blade
        wheel_bottom_entity.addComponent(wheel_bottom_mesh)
        wheel_bottom_entity.addComponent(wheel_bottom_material)
        wheel_bottom_entity.addComponent(wheel_bottom_transform)

    
    def setup_enhanced_blade(self):
        # Blade (between wheels)
        self.blade_entity = QEntity(self.arm_entity)
        blade_mesh = QCuboidMesh()
        blade_mesh.setXExtent(5.0)
        blade_mesh.setYExtent(0.5)
        blade_mesh.setZExtent(2.0)
        self.blade_material = QPhongMaterial()
        self.blade_material.setDiffuse(QtGui.QColor(180, 180, 180))
        self.blade_material.setSpecular(QtGui.QColor(255, 255, 255))
        self.blade_material.setShininess(120)
        self.blade_transform = QTransform()
        self.blade_transform.setTranslation(QVector3D(5.0, -20, 0))  # Centered over material
        self.blade_entity.addComponent(blade_mesh)
        self.blade_entity.addComponent(self.blade_material)
        self.blade_entity.addComponent(self.blade_transform)

        # Add blade guides
        guide_left = QEntity(self.arm_entity)
        guide_mesh = QCuboidMesh()
        guide_mesh.setXExtent(2.0)
        guide_mesh.setYExtent(10.0)
        guide_mesh.setZExtent(2.0)
        guide_material = QPhongMaterial()
        guide_material.setDiffuse(QtGui.QColor(200, 120, 50))
        guide_transform = QTransform()
        guide_transform.setTranslation(QVector3D(2.5, -15, 0))  # Adjusted to match blade (5.0 - 2.5)
        guide_left.addComponent(guide_mesh)
        guide_left.addComponent(guide_material)
        guide_left.addComponent(guide_transform)

        guide_right = QEntity(self.arm_entity)
        guide_transform = QTransform()
        guide_transform.setTranslation(QVector3D(7.5, -15, 0))  # Adjusted to match blade (5.0 + 2.5)
        guide_right.addComponent(guide_mesh)
        guide_right.addComponent(guide_material)
        guide_right.addComponent(guide_transform)
        
    def setup_material_to_cut(self):
        # Crea il pezzo iniziale
        self.create_new_material()

        # Remove the old material_entity and cut_part_entity
        self.material_entity = None
        self.cut_part_entity = None
    
    def create_new_material(self):
        # Material to cut - front part
        self.material_front_entity = QEntity(self.root_entity)
        material_front_mesh = QCuboidMesh()
        material_front_mesh.setXExtent(7.5)
        material_front_mesh.setYExtent(8.0)
        material_front_mesh.setZExtent(8.0)
        self.material_front_material = QPhongMaterial()
        self.material_front_material.setDiffuse(QtGui.QColor(200, 80, 80))
        self.material_front_material.setSpecular(QtGui.QColor(255, 150, 150))
        self.material_front_material.setShininess(60)
        self.material_front_transform = QTransform()
        self.material_front_transform.setTranslation(QVector3D(0, 4, -3.75))  # Centrato a z=-3.75 (avanti)
        self.material_front_entity.addComponent(material_front_mesh)
        self.material_front_entity.addComponent(self.material_front_material)
        self.material_front_entity.addComponent(self.material_front_transform)

        # Material to cut - back part
        self.material_back_entity = QEntity(self.root_entity)
        material_back_mesh = QCuboidMesh()
        material_back_mesh.setXExtent(7.5)
        material_back_mesh.setYExtent(8.0)
        material_back_mesh.setZExtent(8.0)
        self.material_back_material = QPhongMaterial()
        self.material_back_material.setDiffuse(QtGui.QColor(200, 80, 80))
        self.material_back_material.setSpecular(QtGui.QColor(255, 150, 150))
        self.material_back_material.setShininess(60)
        self.material_back_transform = QTransform()
        self.material_back_transform.setTranslation(QVector3D(0, 4, 3.75))  # Centrato a z=3.75 (dietro)
        self.material_back_entity.addComponent(material_back_mesh)
        self.material_back_entity.addComponent(self.material_back_material)
        self.material_back_entity.addComponent(self.material_back_transform)
        
    def remove_current_material(self):
        # Disattiva le entità correnti (le rimuove dalla scena)
        if hasattr(self, 'material_front_entity') and self.material_front_entity:
            self.material_front_entity.setEnabled(False)
        if hasattr(self, 'material_back_entity') and self.material_back_entity:
            self.material_back_entity.setEnabled(False)

    def toggle_macchina(self):
        if self.emergenza:
            return
            
        self.macchina_accesa = not self.macchina_accesa
        self.command_queue.put({"action": "toggle_machine"})
        
        if self.macchina_accesa:
            self.ui.label.setText("Macchina Accesa - Lama spenta")
            self.ui.label.setStyleSheet("QLabel { background-color: #4CAF50; color: white; }")
            self.ui.dial.setEnabled(True)
            self.ui.dial.setValue(1)
            self.ui.lcd_velocita.display(1)
        else:
            self.lama_attiva = False
            self.ui.label.setText("Macchina Spenta")
            self.ui.label.setStyleSheet("QLabel { background-color: #f44336; color: white; }")
            self.ui.dial.setEnabled(False)
            self.ui.lcd_velocita.display(0)
            self.ui.dial.setValue(0)

    def toggle_lama(self):
        if self.emergenza or not self.macchina_accesa:
            return
            
        self.lama_attiva = not self.lama_attiva
        self.command_queue.put({"action": "toggle_cutting"})
        self.ui.dial.setValue(1)
        self.ui.lcd_velocita.display(1)
        velocita = self.ui.dial.value()
        self.command_queue.put({"action": "set_speed", "speed": velocita})
        
        if self.lama_attiva:
            self.ui.label.setText("Macchina Accesa - Lama Attiva")
        else:
            self.ui.label.setText("Macchina Accesa - Lama spenta")

    def emergenza_attiva(self):
        if self.emergenza:
            self.emergenza = False
            self.macchina_accesa = True
            self.lama_attiva = False
            self.command_queue.put({"action": "emergency_solved"})
            self.ui.label.setText("Macchina Accesa - Lama spenta")
            self.ui.label.setStyleSheet("QLabel { background-color: #4CAF50; color: white; }")
            self.ui.dial.setEnabled(True)
            self.ui.dial.setValue(1)
            self.ui.lcd_velocita.display(1)
        else:
            self.emergenza = True
            self.macchina_accesa = False
            self.lama_attiva = False
            self.command_queue.put({"action": "emergency"})
            self.ui.label.setText("Emergenza")
            self.ui.label.setStyleSheet("QLabel { background-color: #ff9800; color: white; }")
            self.ui.dial.setEnabled(False)
            self.ui.lcd_velocita.display(0)
            self.ui.dial.setValue(0)

    def cambio_lama(self):
        if self.emergenza or self.macchina_accesa:
            return
            
        self.command_queue.put({"action": "replace_blade"})
        self.ui.label.setText("Cambio Lama in Corso")
        self.ui.label.setStyleSheet("QLabel { background-color: #2196F3; color: white; }")
        self.ui.dial.setEnabled(False)
        QtCore.QTimer.singleShot(2000, self.fine_cambio_lama)

    def fine_cambio_lama(self):
        if not self.macchina_accesa:
            self.macchina_accesa = not self.macchina_accesa
            self.command_queue.put({"action": "toggle_machine"})
            
        self.ui.label.setText("Macchina Accesa")
        self.ui.label.setStyleSheet("QLabel { background-color: #4CAF50; color: white; }")
        self.ui.dial.setEnabled(True)

    def aggiorna_velocita(self):
        if self.macchina_accesa:
            velocita = self.ui.dial.value()
            self.command_queue.put({"action": "set_speed", "speed": velocita})

    def leggi_coda(self):
        try:
            while not self.data_queue.empty():
                data = self.data_queue.get_nowait()
                current_time = time.time() - self.start_time
                
                # Update plot data
                self.update_plot_data(data, current_time)
                
                # Update 3D view
                self.update_3d_view(data)
                
        except queue.Empty:
            pass
        except Exception as e:
            print(f"Errore in leggi_coda: {e}")

    def update_plot_data(self, data, current_time):
        self.time_data.append(current_time)
        self.speed_data.append(data.get("speed", 0))
        self.blade_temp_data.append(data.get("blade_temp", 25))
        self.machine_temp_data.append(data.get("machine_temp", 25))
        self.consumption_data.append(data.get("consumption", 0))
        self.coolant_temp_data.append(data.get("coolant_temp", 20))
        
        self.speed_curve.setData(list(self.time_data), list(self.speed_data))
        self.blade_temp_curve.setData(list(self.time_data), list(self.blade_temp_data))
        self.machine_temp_curve.setData(list(self.time_data), list(self.machine_temp_data))
        self.consumption_curve.setData(list(self.time_data), list(self.consumption_data))
        self.coolant_temp_curve.setData(list(self.time_data), list(self.coolant_temp_data))
        
        self.current_speed = data.get("speed", 0)
        self.ui.lcd_velocita.display(round(self.current_speed, 2))

    def update_3d_view(self, data):
        self.current_blade_angle = data.get("blade_angle", self.current_blade_angle)
        self.current_blade_angle = min(30.0, max(-85.0, self.current_blade_angle))

        print(f"Current blade angle: {self.current_blade_angle}")

        # Arm transform
        pivot_point = QVector3D(-30, 10, 0)

        # Step 1: Compute the arm's new position after rotation
        arm_distance_from_pivot = 25.0  # Distance from pivot to arm's center (-5 - (-30))
        angle_rad = radians(self.current_blade_angle)
        arm_x = -30 + arm_distance_from_pivot * math.cos(angle_rad)
        arm_y = 10 + arm_distance_from_pivot * sin(angle_rad)
        arm_z = 0

        # Apply the arm's transform
        transform = QTransform()
        transform.setTranslation(QVector3D(arm_x, arm_y, arm_z))
        self.arm_transform.setMatrix(transform.matrix())

        # Compute the blade's Y position for cutting simulation
        arm_length = 50.0
        blade_y_offset = -2.0
        blade_tip_y = 10 + (arm_length * -sin(angle_rad)) + blade_y_offset

        print(f"angle_rad: {angle_rad}, sin(angle_rad): {sin(angle_rad)}, blade_tip_y: {blade_tip_y}")

        speed = data.get("speed", 0)
        blade_temp = data.get("blade_temp", 25)

        # Blade transform
        blade_transform = QTransform()
        # No inverse rotation needed since we're not rotating the arm entity directly
        blade_transform.setTranslation(QVector3D(5.0, -20, 0))  # Fixed position

        if self.lama_attiva and speed > 0:
            self.blade_vibration += speed * 0.1
            vibration = 0.3 * sin(self.blade_vibration)
            heat_factor = min(1.0, (blade_temp - 50) / 200.0)
            self.blade_heat_factor = heat_factor

            base_color = 180 - min(80, heat_factor * 80)
            glow_color = min(255, 180 + heat_factor * 75)
            r_diffuse = int(max(0, min(255, base_color + vibration * 20)))
            g_diffuse = int(max(0, min(255, base_color - heat_factor * 100)))
            b_diffuse = int(max(0, min(255, base_color - heat_factor * 100)))
            r_specular = int(max(0, min(255, glow_color)))
            g_specular = int(max(0, min(255, glow_color - heat_factor * 100)))
            b_specular = int(max(0, min(255, glow_color - heat_factor * 100)))
            self.blade_material.setDiffuse(QtGui.QColor(r_diffuse, g_diffuse, b_diffuse))
            self.blade_material.setSpecular(QtGui.QColor(r_specular, g_specular, b_specular))

            blade_transform.setTranslation(QVector3D(5.0, -20 + vibration, 0))
        else:
            self.blade_vibration = 0.0
            self.blade_material.setDiffuse(QtGui.QColor(180, 180, 180))
            self.blade_material.setSpecular(QtGui.QColor(255, 255, 255))
            blade_transform.setTranslation(QVector3D(5.0, -20, 0))

        self.blade_transform.setMatrix(blade_transform.matrix())

        if self.cutting_progress < 1.0:
            material_top_y = 8.0
            material_bottom_y = 0.0
            blade_z_center = blade_transform.translation().z()
            blade_z_extent = 2.0
            blade_z_min = blade_z_center - (blade_z_extent / 2)
            blade_z_max = blade_z_center + (blade_z_extent / 2)

            front_z_min = -7.75
            front_z_max = 0.25
            back_z_min = -0.25
            back_z_max = 7.75

            z_overlap = (blade_z_max >= front_z_min and blade_z_min <= front_z_max) or \
                        (blade_z_max >= back_z_min and blade_z_min <= back_z_max)

            if (blade_tip_y <= material_top_y and blade_tip_y >= material_bottom_y and
                self.lama_attiva and speed > 0 and z_overlap):
                cut_depth = (material_top_y - blade_tip_y) / (material_top_y - material_bottom_y)
                progress_increment = (speed * 0.001) * cut_depth
                self.cutting_progress += progress_increment
                self.cutting_progress = min(1.0, max(0.0, self.cutting_progress))
            else:
                self.cutting_progress = max(0.0, self.cutting_progress - 0.01)

        print(f"blade_tip_y: {blade_tip_y}, cutting_progress: {self.cutting_progress}, lama_attiva: {self.lama_attiva}, speed: {speed}")

        self.update_cut_visualization()
        
    def update_cut_visualization(self):
        if self.cutting_progress >= 1.0:
            self.remove_current_material()
            self.create_new_material()
            self.cutting_progress = 0.0
            self.current_blade_angle = 30.0
            # Reset arm position
            transform = QTransform()
            transform.setTranslation(QVector3D(-5, 10, 0))  # Initial arm position
            self.arm_transform.setMatrix(transform.matrix())
            self.blade_transform.setTranslation(QVector3D(5.0, -20, 0))
            print("Taglio completato: pezzo rimosso e nuovo pezzo creato")
        elif self.cutting_progress > 0.0:
            max_separation = 20.0
            separation = max_separation * self.cutting_progress
            self.material_front_transform.setTranslation(QVector3D(0, 4, -3.75 - separation))
            self.material_back_transform.setTranslation(QVector3D(0, 4, 3.75 + separation))
            print(f"Separating parts: front z={-3.75 - separation}, back z={3.75 + separation}, cutting_progress={self.cutting_progress}")
        else:
            self.material_front_transform.setTranslation(QVector3D(0, 4, -3.75))
            self.material_back_transform.setTranslation(QVector3D(0, 4, 3.75))
            print("Resetting parts position")

if __name__ == "__main__":
    app = QtWidgets.QApplication(sys.argv)
    window = SegatriceCNC()
    window.show()
    sys.exit(app.exec_())