# -*- coding: utf-8 -*-

import queue
import threading
from PyQt5 import QtCore, QtGui, QtWidgets
from simulazionecoda import start_simulation  # Importa la funzione di avvio dal file simulazioneCoda

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
            QDial::handle:hover {
                background-color: #388E3C;
            }
            QDial::sub-page {
                background: #BBDEFB;
                border-radius: 50%;
            }
            QDial::add-page {
                background: #E3F2FD;
                border-radius: 50%;
            }
        """)
        self.centralwidget = QtWidgets.QWidget(MainWindow)
        self.centralwidget.setObjectName("centralwidget")
        
        self.griglia = QtWidgets.QWidget(self.centralwidget)
        self.griglia.setGeometry(QtCore.QRect(290, 220, 761, 481))
        self.griglia.setStyleSheet("""
            QWidget {
                background-color: #333333;
                border: 3px solid #FFEB3B;
                border-radius: 10px;
                padding: 20px;
                font-family: Arial;
            }
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

        self.pushButton_5 = QtWidgets.QPushButton(self.griglia)
        self.pushButton_5.setGeometry(QtCore.QRect(20, 90, 191, 51))
        font = QtGui.QFont()
        font.setFamily("Arial")
        font.setPointSize(16)
        font.setBold(True)
        self.pushButton_5.setFont(font)
        self.pushButton_5.setObjectName("pushButton_5")

        self.pushButton_6 = QtWidgets.QPushButton(self.griglia)
        self.pushButton_6.setGeometry(QtCore.QRect(20, 150, 191, 51))
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
        self.pushButton_3.setGeometry(QtCore.QRect(20, 320, 181, 101))
        font = QtGui.QFont()
        font.setFamily("Arial")
        font.setPointSize(16)
        font.setBold(True)
        self.pushButton_3.setFont(font)
        self.pushButton_3.setStyleSheet("""
            QPushButton {
                background-color: red;
                color: white;
                border: 4px solid black;
                border-radius: 30px;
                padding: 15px;
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

        self.lcd_velocita = QtWidgets.QLCDNumber(self.griglia)
        self.lcd_velocita.setGeometry(QtCore.QRect(520, 260, 211, 171))
        self.lcd_velocita.setObjectName("lcd_velocita")

        self.label_2 = QtWidgets.QLabel(self.griglia)
        self.label_2.setGeometry(QtCore.QRect(230, 0, 231, 71))
        self.label_2.setObjectName("label_2")

        self.dial = QtWidgets.QDial(self.griglia)
        self.dial.setGeometry(QtCore.QRect(320, 280, 150, 150))
        self.dial.setMinimum(1)
        self.dial.setMaximum(100)
        self.dial.setValue(1)
        self.dial.setNotchesVisible(True)  # Mostra tacche per feedback visivo
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

        # Variabili di stato
        self.macchina_accesa = False
        self.lama_attiva = False
        self.emergenza = False

        # Coda condivisa per inviare comandi alla simulazione
        self.coda = queue.Queue()

        # Avvia la simulazione in un thread separato
        self.sim_thread = threading.Thread(target=start_simulation, args=(self.coda,), daemon=True)
        self.sim_thread.start()

        # Collegamento segnali
        self.ui.pushButton_5.clicked.connect(self.toggle_macchina)
        self.ui.pushButton_6.clicked.connect(self.toggle_lama)
        self.ui.pushButton_3.clicked.connect(self.emergenza_attiva)
        self.ui.pushButton_4.clicked.connect(self.cambio_lama)
        self.ui.dial.valueChanged.connect(self.aggiorna_velocita)

        # Stato iniziale
        self.ui.dial.setEnabled(False)
        self.ui.lcd_velocita.display(0)

    def toggle_macchina(self):
        if self.emergenza:
            return
        
        self.macchina_accesa = not self.macchina_accesa
        if self.macchina_accesa:
            self.ui.label.setText("Macchina Accesa - Lama Spenta")
            self.ui.label.setStyleSheet("QLabel { background-color: #4CAF50; color: white; padding: 10px; border-radius: 5px; font-size: 16px; text-align: center; font-weight: bold; }")
            self.ui.dial.setEnabled(True)
            velocita = self.ui.dial.value()
            self.ui.lcd_velocita.display(velocita)  # Mostra il valore del dial
            self.coda.put(("macchina_accesa", velocita))
        else:
            self.lama_attiva = False
            self.ui.label.setText("Macchina Spenta")
            self.ui.label.setStyleSheet("QLabel { background-color: #f44336; color: white; padding: 10px; border-radius: 5px; font-size: 16px; text-align: center; font-weight: bold; }")
            self.ui.dial.setEnabled(False)
            self.ui.lcd_velocita.display(0)
            self.coda.put(("macchina_spenta", 0))

    def toggle_lama(self):
        if self.emergenza or not self.macchina_accesa:
            return
        
        self.lama_attiva = not self.lama_attiva
        if self.lama_attiva:
            self.ui.label.setText("Macchina Accesa - Lama Attiva")
            self.ui.label.setStyleSheet("QLabel { background-color: #4CAF50; color: white; padding: 10px; border-radius: 5px; font-size: 16px; text-align: center; font-weight: bold; }")
            self.coda.put(("lama_attiva", None))
        else:
            self.ui.label.setText("Macchina Accesa - Lama Spenta")
            self.ui.label.setStyleSheet("QLabel { background-color: #4CAF50; color: white; padding: 10px; border-radius: 5px; font-size: 16px; text-align: center; font-weight: bold; }")
            self.coda.put(("lama_spenta", None))

    def emergenza_attiva(self):
        self.emergenza = True
        self.macchina_accesa = False
        self.lama_attiva = False
        self.ui.label.setText("Emergenza")
        self.ui.label.setStyleSheet("QLabel { background-color: #ff9800; color: white; padding: 10px; border-radius: 5px; font-size: 16px; text-align: center; font-weight: bold; }")
        self.ui.dial.setEnabled(False)
        self.ui.lcd_velocita.display(0)
        self.coda.put(("macchina_spenta", 0))
        self.emergenza = False

    def cambio_lama(self):
        if self.emergenza or not self.macchina_accesa:
            return
        
        self.ui.label.setText("Cambio Lama in Corso")
        self.ui.label.setStyleSheet("QLabel { background-color: #2196F3; color: white; padding: 10px; border-radius: 5px; font-size: 16px; text-align: center; font-weight: bold; }")
        self.ui.dial.setEnabled(False)
        self.coda.put(("cambio_lama", None))
        QtCore.QTimer.singleShot(2000, self.fine_cambio_lama)

    def fine_cambio_lama(self):
        if self.macchina_accesa:
            self.ui.label.setText("Macchina Accesa - Lama Spenta" if not self.lama_attiva else "Macchina Accesa - Lama Attiva")
            self.ui.label.setStyleSheet("QLabel { background-color: #4CAF50; color: white; padding: 10px; border-radius: 5px; font-size: 16px; text-align: center; font-weight: bold; }")
            self.ui.dial.setEnabled(True)
            velocita = self.ui.dial.value()
            self.ui.lcd_velocita.display(velocita)  # Mostra il valore del dial
            self.coda.put(("velocita", velocita))

    def aggiorna_velocita(self, value):
        if self.macchina_accesa:
            velocita = self.ui.dial.value()
            self.ui.lcd_velocita.display(velocita)  # Aggiorna l'LCD immediatamente
            self.coda.put(("velocita", velocita))

if __name__ == "__main__":
    import sys
    app = QtWidgets.QApplication(sys.argv)
    window = SegatriceCNC()
    window.show()
    sys.exit(app.exec_())