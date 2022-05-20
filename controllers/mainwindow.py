from random import randint
import time
from pynput import keyboard
from PySide2.QtWidgets import QMainWindow, QHeaderView, QTableWidgetItem, QApplication
from views.Ui_main import Ui_MainWindow
from PySide2.QtCore import Slot

class MainWindow(QMainWindow):
    def __init__(self):
        super(MainWindow, self).__init__()

        self.ui = Ui_MainWindow()
        self.ui.setupUi(self)

        self.columnasTablas()
        self.interrupcion = False
        self.pausa = False
        self.continuar = True
        self.error = False
        self.boolEjecucion = False

        def pulsa(tecla):
            if tecla == keyboard.KeyCode.from_char('i') or tecla == keyboard.KeyCode.from_char('I'):
                if not self.pausa and self.boolEjecucion:
                    self.interrupcion = True
            elif tecla == keyboard.KeyCode.from_char('p') or tecla == keyboard.KeyCode.from_char('P'):
                if not self.pausa and self.boolEjecucion:
                    self.pausa = True
            elif tecla == keyboard.KeyCode.from_char('c') or tecla == keyboard.KeyCode.from_char('C'):
                if self.pausa and self.boolEjecucion:
                    self.continuar = False
            elif tecla == keyboard.KeyCode.from_char('e') or tecla == keyboard.KeyCode.from_char('E'):
                if not self.pausa and self.boolEjecucion:
                    self.error = True
                
        self.escuchador = keyboard.Listener(pulsa)
        self.escuchador.start()

        self.numeroProcesos = 0
        self.procesoActual = 1
        self.contadorProcesos = 0
        self.numeroEjecucion = 0
        self.tiempoTotal = 0
        self.listaRegistro = []
        self.listaEjecuccion = []
        self.listaTerminados = []
        self.listabloqueados = []

        self.ui.Empezar_pushButton.clicked.connect(self.empezar)
        self.ui.iniciar_pushButton.clicked.connect(self.iniciar)
    
    def llenarTablaRegistro(self):
        self.ui.captura_tableWidget.setRowCount(len(self.listaRegistro))

        for (index_row, row) in enumerate(self.listaRegistro):
            for(index_cell, cell) in enumerate(row):
                self.ui.captura_tableWidget.setItem(index_row,index_cell,QTableWidgetItem(str(cell)))
    
    def llenarTablaEjecucion(self):
        self.ui.ejecuccion_tableWidget.setRowCount(len(self.listaEjecuccion))

        for (index_row, row) in enumerate(self.listaEjecuccion):
            for(index_cell, cell) in enumerate(row):
                self.ui.ejecuccion_tableWidget.setItem(index_row,index_cell,QTableWidgetItem(str(cell)))

    def llenarTablaTerminados(self):
        self.ui.finalizados_tableWidget.setRowCount(len(self.listaTerminados))

        for (index_row, row) in enumerate(self.listaTerminados):
            for(index_cell, cell) in enumerate(row):
                self.ui.finalizados_tableWidget.setItem(index_row,index_cell,QTableWidgetItem(str(cell)))
    
    def llenarTablaBloqueados(self):
        self.ui.bloqueados_tableWidget.setRowCount(len(self.listabloqueados))

        for (index_row, row) in enumerate(self.listabloqueados):
            for(index_cell, cell) in enumerate(row):
                self.ui.bloqueados_tableWidget.setItem(index_row,index_cell,QTableWidgetItem(str(cell)))
    
    def columnasTablas(self):
        self.ui.captura_tableWidget.horizontalHeader().setSectionResizeMode(QHeaderView.ResizeToContents)
        self.ui.ejecuccion_tableWidget.horizontalHeader().setSectionResizeMode(QHeaderView.ResizeToContents)
        self.ui.finalizados_tableWidget.horizontalHeader().setSectionResizeMode(QHeaderView.ResizeToContents)
        self.ui.bloqueados_tableWidget.horizontalHeader().setSectionResizeMode(QHeaderView.ResizeToContents)
        
    def bloqueados(self):
        for proceso in reversed(self.listabloqueados):
            proceso[2] -= 1
            if proceso[2] == 0:
                proceso.pop(2)
                self.listaEjecuccion.append(self.listabloqueados.pop(self.listabloqueados.index(proceso)))
            self.llenarTablaBloqueados()
            self.llenarTablaEjecucion()
    
    def transicion(self):
        while len(self.listaEjecuccion) + len(self.listabloqueados) < 5 and len(self.listaRegistro):
            proceso = self.listaRegistro.pop(0)
            proceso.append(self.tiempoTotal)
            proceso.append(False)
            self.listaEjecuccion.append(proceso)
            self.llenarTablaRegistro()
            self.llenarTablaEjecucion()
    
    def calcular_tiempos(self, proceso):
        proceso.pop(4)
        proceso[3], proceso[4] = proceso[4], proceso[3]
        proceso.insert(4, self.tiempoTotal)
        proceso.insert(5, proceso[4] - proceso[3])
        proceso.insert(6, proceso[8] - proceso[3])
        proceso.insert(7, proceso[5] - proceso[7])
        proceso.pop()
        proceso.pop()
        return proceso
    
    def ejecucion(self):
        self.boolEjecucion = True
        while len(self.listaEjecuccion) or len(self.listabloqueados):
            self.transicion()
            self.interrupcion = False
            self.error = False
            if len(self.listaEjecuccion):
                proceso = self.listaEjecuccion.pop(0)
                if not proceso[5]:
                    if self.tiempoTotal == 0:
                        proceso.append(self.tiempoTotal)
                        proceso[5] = True
                    else:
                        proceso.append(self.tiempoTotal - 1)
                        proceso[5] = True
                self.llenarTablaEjecucion()
                self.ui.Id_label.setText(str(proceso[0]))
                self.ui.operacion_label.setText(proceso[1])
                self.ui.tiempo_label.setText(str(proceso[2]))
                i = 0
                j = proceso[3]
                while i <= proceso[3]:
                    self.bloqueados()
                    self.ui.transcurrido_lcdNumber.display(i)
                    self.ui.restante_lcdNumber.display(j)
                    self.ui.total_lcdNumber.display(self.tiempoTotal)
                    QApplication.processEvents()
                    time.sleep(1)
                    if self.pausa:
                        while self.continuar:
                            pass
                        self.pausa = False
                        self.continuar = True
                    elif self.interrupcion:
                        proceso[3] = j
                        proceso.insert(2, 9)
                        self.listabloqueados.append(proceso)
                        self.llenarTablaBloqueados()
                        self.ui.Id_label.setText("")
                        self.ui.operacion_label.setText("")
                        self.ui.tiempo_label.setText("")
                        self.ui.transcurrido_lcdNumber.display(0)
                        self.ui.restante_lcdNumber.display(0)
                        self.tiempoTotal += 1
                        break
                    elif self.error:
                        proceso.insert(2, "Error")
                        proceso[3] = proceso[3] - j
                        proceso = self.calcular_tiempos(proceso)
                        self.tiempoTotal += 1
                        break
                    if self.numeroEjecucion == 0 or i != 0:
                        self.tiempoTotal += 1
                    i += 1
                    j -= 1
                if not self.interrupcion and not self.error:
                    operacion = proceso[1].split()
                    resultado = 0
                    if operacion[1] == "+":
                        resultado = int(operacion[0]) + int(operacion[2])
                    elif operacion[1] == "-":
                        resultado = int(operacion[0]) - int(operacion[2])
                    elif operacion[1] == "*":
                        resultado = int(operacion[0]) * int(operacion[2])
                    elif operacion[1] == "/":
                        resultado = int(operacion[0]) / int(operacion[2])
                    else:
                        resultado = int(operacion[0]) % int(operacion[2])
                    proceso.insert(2, resultado)
                    proceso = self.calcular_tiempos(proceso)
                    proceso[4] -= 1
                    proceso[5] -= 1
                    proceso[7] -= 1
                if not self.interrupcion:
                    self.listaTerminados.append(proceso)
                    self.llenarTablaTerminados()
                    self.ui.Id_label.setText("")
                    self.ui.operacion_label.setText("")
                    self.ui.tiempo_label.setText("")
                    self.ui.transcurrido_lcdNumber.display(0)
                    self.ui.restante_lcdNumber.display(0)
                self.numeroEjecucion += 1
            else:
                self.bloqueados()
                QApplication.processEvents()
                time.sleep(1)
                self.tiempoTotal += 1
                self.ui.total_lcdNumber.display(self.tiempoTotal)

    @Slot()
    def empezar(self):
        procesos = self.ui.N_Procesos.value()
        if procesos > 0:
            self.ui.Empezar_pushButton.setEnabled(False)
            self.numeroProcesos = procesos
            self.agregar()

    def agregar(self):
        for i in range(self.numeroProcesos):
            random = randint(1, 5)
            if random == 1:
                signo = "+"
            elif random == 2:
                signo = "-"
            elif random == 3:
                signo = "*"
            elif random == 4:
                signo = "/"
            else:
                signo = "%"
            n2 = randint(1, 100)
            n1 = randint(0, 100)
            operacion = str(n1) + ' ' + signo + ' ' + str(n2)
            tiempo = randint(6, 16)
            restante = tiempo
            Id = i + 1
            if self.contadorProcesos < 5:
                self.contadorProcesos += 1
            else:
                self.contadorProcesos = 1
            self.listaRegistro.append([ Id, operacion, tiempo, restante])
            self.llenarTablaRegistro()
        self.ui.iniciar_pushButton.setEnabled(True)
    
    @Slot()
    def iniciar(self):
        self.ui.iniciar_pushButton.setEnabled(False)
        self.ui.N_Procesos.setEnabled(False)
        self.transicion()
        self.ejecucion()