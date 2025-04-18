"""
_______________________________________________________________

  LGA_NKS_CheckProjectVersions v1.5 - 2025 - Lega
  Chequea versiones de todos los proyectos abiertos en Hiero
_______________________________________________________________

"""

import hiero.core
import hiero.ui
import re
import os
import glob
import datetime
from PySide2.QtWidgets import QMainWindow, QVBoxLayout, QLabel, QPushButton, QGridLayout, QFrame, QTableWidget, QTableWidgetItem, QWidget, QApplication, QHBoxLayout
from PySide2.QtCore import Qt, QTimer
from PySide2.QtGui import QFont, QColor

# Configuración del temporizador (en minutos)
INTERVALO_TEMPORIZADOR = 5

# Variable global para almacenar el temporizador activo
temporizador_global = None
temporizador_id = "LGA_CheckProjects_Timer"

DEBUG = False

def debug_print(*message):
    if DEBUG:
        print(*message)

def extraer_version(ruta_disco):
    """Extrae el número de versión de la ruta del archivo en disco"""
    if not ruta_disco:
        return "No detectada"
    
    try:
        # Obtener el nombre del archivo (sin la ruta completa)
        nombre_archivo = os.path.basename(ruta_disco)
        
        # Quitar la extensión .hrox
        nombre_sin_extension = os.path.splitext(nombre_archivo)[0]
        
        # Buscar la parte que comienza con 'v' seguida de números al final del nombre
        resultado = re.search(r'(?:_|-)?(v\d+)$', nombre_sin_extension)
        if resultado:
            return resultado.group(1)  # Devuelve 'v###'
        
        # Si no encuentra 'v', buscar solo números al final después de un guion bajo o guion
        resultado = re.search(r'(?:_|-)?(\d+)$', nombre_sin_extension)
        if resultado:
            return 'v' + resultado.group(1)  # Añade 'v' a los números encontrados
        
        return "No detectada"
    except Exception as e:
        debug_print(f"Error al extraer versión: {str(e)}")
        return "Error"

def comparar_versiones(version1, version2):
    """Compara dos versiones en formato 'v###' y devuelve la mayor"""
    try:
        # Extraer solo los números de las versiones
        match1 = re.search(r'v?(\d+)', version1)
        match2 = re.search(r'v?(\d+)', version2)
        
        if not match1 or not match2:
            return version1  # Si no se pueden extraer números, devuelve la primera versión
            
        num1 = int(match1.group(1))
        num2 = int(match2.group(1))
        
        if num1 > num2:
            return version1
        else:
            return version2
    except Exception as e:
        debug_print(f"Error al comparar versiones {version1} y {version2}: {str(e)}")
        return version1  # En caso de error, devuelve la primera versión

def encontrar_version_mas_alta(ruta_actual):
    """Encuentra la ruta del archivo con la versión más alta en la misma carpeta"""
    if not ruta_actual or not os.path.exists(ruta_actual):
        return "No disponible"
    
    try:
        # Obtener la carpeta que contiene el archivo actual
        directorio = os.path.dirname(ruta_actual)
        
        # Obtener el nombre base del proyecto (sin versión ni extensión)
        nombre_archivo = os.path.basename(ruta_actual)
        
        # Extraer la parte base del nombre (antes de la versión)
        base_match = re.match(r'(.+?)(?:_|-)?v?\d+\.hrox$', nombre_archivo)
        if not base_match:
            base_match = re.match(r'(.+?)\.hrox$', nombre_archivo)
            if not base_match:
                return "No detectada"
        
        base_nombre = base_match.group(1)
        
        # Buscar todos los archivos .hrox en el directorio con el mismo nombre base
        patron_busqueda = os.path.join(directorio, f"{base_nombre}*v*.hrox")
        archivos = glob.glob(patron_busqueda)
        
        # Si no encuentra con el patrón v*.hrox, intentar con cualquier número
        if not archivos:
            patron_busqueda = os.path.join(directorio, f"{base_nombre}*[0-9]*.hrox")
            archivos = glob.glob(patron_busqueda)
        
        if not archivos:
            return "No hay otras versiones"
        
        # Extraer versiones de todos los archivos encontrados
        version_mas_alta = None
        archivo_mas_alto = None
        
        for archivo in archivos:
            version = extraer_version(archivo)
            if version == "No detectada" or version == "Error":
                continue
                
            if version_mas_alta is None:
                version_mas_alta = version
                archivo_mas_alto = archivo
            else:
                version_previa = version_mas_alta
                version_mas_alta = comparar_versiones(version_mas_alta, version)
                
                if version_mas_alta != version_previa:
                    archivo_mas_alto = archivo
        
        if version_mas_alta and archivo_mas_alto:
            # Devolver la ruta completa del archivo con la versión más alta
            return archivo_mas_alto
        else:
            return "No detectada"
            
    except Exception as e:
        debug_print(f"Error al buscar versión más alta: {str(e)}")
        return "Error"

def obtener_timestamp():
    """Devuelve una cadena formateada con la fecha y hora actual"""
    ahora = datetime.datetime.now()
    return ahora.strftime("%d/%m/%Y %H:%M:%S")

class ProyectosAbertosDialog(QMainWindow):
    def __init__(self, parent=None, proyectos_con_version_alta=None):
        super(ProyectosAbertosDialog, self).__init__(parent)
        self.setWindowTitle("Proyectos Abiertos")
        self.setMinimumSize(900, 200)  # Reducir la altura a la mitad
        
        # Establecer un nombre de objeto único para esta ventana
        self.setObjectName("LGA_ProyectosAbertosDialog")
        
        # Configurar banderas de ventana para permitir minimizar, maximizar y cerrar
        self.setWindowFlags(Qt.Window | Qt.WindowMinimizeButtonHint | Qt.WindowMaximizeButtonHint | Qt.WindowCloseButtonHint)
        
        # Hacer que la ventana se destruya completamente cuando se cierra
        self.setAttribute(Qt.WA_DeleteOnClose, True)
        
        # Conectar el evento de cierre para detener el temporizador
        self.destroyed.connect(self.on_destroyed)
        
        # Mostrar IDs de la ventana
        debug_print(f"ID de ventana nativo: {self.winId()}")
        debug_print(f"Nombre de objeto: {self.objectName()}")
        
        # Widget central y layout
        central_widget = QWidget()
        self.setCentralWidget(central_widget)
        layout = QVBoxLayout(central_widget)
        
        # Añadir título
        titulo = QLabel("Versiones de Proyectos Abiertos")
        titulo.setAlignment(Qt.AlignCenter)
        font = QFont()
        font.setBold(True)
        font.setPointSize(12)
        titulo.setFont(font)
        layout.addWidget(titulo)
        
        # Añadir información del temporizador
        self.label_timer = QLabel(f"Actualizando cada {INTERVALO_TEMPORIZADOR} minutos")
        self.label_timer.setAlignment(Qt.AlignCenter)
        layout.addWidget(self.label_timer)
        
        # Tabla para mostrar los datos
        self.tabla_proyectos = QTableWidget()
        self.tabla_proyectos.setColumnCount(3)
        self.tabla_proyectos.setHorizontalHeaderLabels([
            "Nombre del Proyecto", 
            "Ruta en Disco",
            "Versión Más Alta en Disco"
        ])
        self.tabla_proyectos.horizontalHeader().setStretchLastSection(True)
        self.tabla_proyectos.setColumnWidth(0, 200)  # Nombre del proyecto
        self.tabla_proyectos.setColumnWidth(1, 350)  # Ruta en disco
        
        layout.addWidget(self.tabla_proyectos)
        
        # Botones inferiores en layout horizontal
        botones_layout = QHBoxLayout()
        
        # Botón para actualizar
        boton_actualizar = QPushButton("Actualizar Ahora")
        boton_actualizar.clicked.connect(self.actualizar_proyectos)
        botones_layout.addWidget(boton_actualizar)
        
        # Botón para cerrar
        boton_cerrar = QPushButton("Cerrar")
        boton_cerrar.clicked.connect(self.close)
        botones_layout.addWidget(boton_cerrar)
        
        layout.addLayout(botones_layout)
        
        # Cargar proyectos o usar los datos proporcionados
        if proyectos_con_version_alta:
            self.actualizar_proyectos_con_datos(proyectos_con_version_alta)
        else:
            self.actualizar_proyectos()
    
    def on_destroyed(self):
        """Se llama cuando la ventana se destruye"""
        # Detener el temporizador si la ventana se cierra
        detener_temporizador()
    
    def actualizar_proyectos(self):
        """Actualiza la información de los proyectos abiertos en la tabla"""
        debug_print("Actualizando información de proyectos...")
        # Limpiar tabla existente
        self.tabla_proyectos.clearContents()
        self.tabla_proyectos.setRowCount(0)
        
        # Actualizar etiqueta de temporizador
        self.label_timer.setText(f"Actualizando cada {INTERVALO_TEMPORIZADOR} minutos. Última: {obtener_timestamp()}")
        
        # Llamar al método original de carga
        self.cargar_proyectos()
    
    def actualizar_proyectos_con_datos(self, proyectos_con_version_alta):
        """Actualiza la tabla con los datos proporcionados"""
        debug_print("Actualizando información de proyectos con datos preexistentes...")
        # Limpiar tabla existente
        self.tabla_proyectos.clearContents()
        self.tabla_proyectos.setRowCount(0)
        
        # Actualizar etiqueta de temporizador
        self.label_timer.setText(f"Actualizando cada {INTERVALO_TEMPORIZADOR} minutos. Última: {obtener_timestamp()}")
        
        # Configurar el número de filas para los proyectos con versión más alta
        self.tabla_proyectos.setRowCount(len(proyectos_con_version_alta))
        
        # Cargar datos directamente en la tabla
        for i, proyecto_data in enumerate(proyectos_con_version_alta):
            # Crear elementos de tabla
            item_nombre = QTableWidgetItem(proyecto_data['nombre'])
            item_ruta = QTableWidgetItem(proyecto_data['ruta_actual'])
            item_ruta_alta = QTableWidgetItem(proyecto_data['ruta_alta'])
            
            # Asignar a la tabla
            self.tabla_proyectos.setItem(i, 0, item_nombre)
            self.tabla_proyectos.setItem(i, 1, item_ruta)
            self.tabla_proyectos.setItem(i, 2, item_ruta_alta)
            
            debug_print(f"Añadido a tabla: {proyecto_data['nombre']}")
    
    def cargar_proyectos(self):
        """Carga la información de los proyectos abiertos en la tabla"""
        proyectos = hiero.core.projects()
        
        if not proyectos:
            self.close()  # Cerrar la ventana si no hay proyectos abiertos
            return
        
        # Filtrar proyectos que tienen una versión más alta disponible
        proyectos_con_version_alta = []
        
        for proyecto in proyectos:
            # Obtener nombre de la interfaz
            nombre_interfaz = proyecto.name()
            
            # Obtener ruta del disco
            ruta_disco = proyecto.path()
            
            # Extraer versión de la ruta en disco (para comparación)
            version_actual = extraer_version(ruta_disco)
            
            # Encontrar la ruta de la versión más alta en disco
            ruta_version_alta = encontrar_version_mas_alta(ruta_disco)
            
            # Verificar si tiene una versión más alta que la actual
            version_actual_num = -1
            version_alta_num = -1
            
            try:
                if version_actual != "No detectada" and version_actual != "Error":
                    match_actual = re.search(r'v?(\d+)', version_actual)
                    if match_actual:
                        version_actual_num = int(match_actual.group(1))
                
                if ruta_version_alta != "No detectada" and ruta_version_alta != "Error" and ruta_version_alta != "No disponible" and ruta_version_alta != "No hay otras versiones":
                    version_alta = extraer_version(ruta_version_alta)
                    if version_alta != "No detectada" and version_alta != "Error":
                        match_alta = re.search(r'v?(\d+)', version_alta)
                        if match_alta:
                            version_alta_num = int(match_alta.group(1))
            except Exception as e:
                debug_print(f"Error al comparar versiones: {str(e)}")
            
            # Solo incluir proyectos con versión más alta disponible
            if version_actual_num > 0 and version_alta_num > 0 and version_actual_num < version_alta_num:
                proyectos_con_version_alta.append({
                    'proyecto': proyecto,
                    'nombre': nombre_interfaz,
                    'ruta_actual': ruta_disco,
                    'ruta_alta': ruta_version_alta
                })
                debug_print(f"Proyecto {nombre_interfaz} - Versión actual: {version_actual}, Versión más alta: {version_alta}")
        
        # Si no hay proyectos con versión más alta, cerrar la ventana
        if not proyectos_con_version_alta:
            debug_print("No hay proyectos con versiones más altas disponibles. Cerrando ventana.")
            self.close()  # Cerrar la ventana si no hay proyectos con versiones más altas
            return
        
        # Cargar datos de proyectos con versión más alta
        self.actualizar_proyectos_con_datos(proyectos_con_version_alta)

def buscar_ventana_existente(nombre_objeto):
    """
    Busca si ya existe una ventana con el nombre de objeto especificado
    Devuelve la ventana si existe y está visible, None en caso contrario
    """
    for widget in QApplication.instance().allWidgets():
        if (widget.objectName() == nombre_objeto and 
            isinstance(widget, QMainWindow) and 
            widget.isVisible()):
            return widget
    return None

def detener_temporizador():
    """Detiene el temporizador global si existe"""
    global temporizador_global
    if temporizador_global is not None and temporizador_global.isActive():
        debug_print(f"Deteniendo temporizador con ID: {temporizador_id}")
        temporizador_global.stop()
        temporizador_global = None

def iniciar_temporizador():
    """Inicia o reinicia el temporizador global"""
    global temporizador_global, INTERVALO_TEMPORIZADOR
    
    # Detener temporizador existente si hay alguno
    detener_temporizador()
    
    # Crear un nuevo temporizador
    temporizador_global = QTimer()
    temporizador_global.setObjectName(temporizador_id)
    temporizador_global.timeout.connect(main)
    temporizador_global.start(INTERVALO_TEMPORIZADOR * 60 * 1000)  # Convertir minutos a milisegundos
    
    debug_print(f"Iniciado temporizador con ID: {temporizador_id}, intervalo: {INTERVALO_TEMPORIZADOR} minutos")

def actualizar_intervalo_temporizador(nuevo_intervalo):
    """Actualiza el intervalo del temporizador y lo reinicia"""
    global INTERVALO_TEMPORIZADOR
    
    # Actualizar la variable global
    INTERVALO_TEMPORIZADOR = nuevo_intervalo
    
    # Reiniciar el temporizador con el nuevo intervalo
    iniciar_temporizador()
    
    # Actualizar la etiqueta en la ventana si existe
    ventana_existente = buscar_ventana_existente("LGA_ProyectosAbertosDialog")
    if ventana_existente:
        ventana_existente.label_timer.setText(f"Actualizando cada {INTERVALO_TEMPORIZADOR} minutos")

def main():
    """Función principal que muestra el diálogo con los proyectos abiertos SOLO si hay versiones más altas"""
    # Verificar primero si hay proyectos abiertos
    proyectos = hiero.core.projects()
    if not proyectos or len(proyectos) == 0:
        debug_print("No hay proyectos abiertos. No se mostrará la ventana.")
        return
    
    # Verificar si hay proyectos con versiones más altas disponibles ANTES de abrir cualquier ventana
    proyectos_con_version_alta = []
    
    for proyecto in proyectos:
        nombre_interfaz = proyecto.name()
        ruta_disco = proyecto.path()
        version_actual = extraer_version(ruta_disco)
        ruta_version_alta = encontrar_version_mas_alta(ruta_disco)
        
        # Verificar si tiene una versión más alta que la actual
        version_actual_num = -1
        version_alta_num = -1
        
        try:
            if version_actual != "No detectada" and version_actual != "Error":
                match_actual = re.search(r'v?(\d+)', version_actual)
                if match_actual:
                    version_actual_num = int(match_actual.group(1))
            
            if ruta_version_alta != "No detectada" and ruta_version_alta != "Error" and ruta_version_alta != "No disponible" and ruta_version_alta != "No hay otras versiones":
                version_alta = extraer_version(ruta_version_alta)
                if version_alta != "No detectada" and version_alta != "Error":
                    match_alta = re.search(r'v?(\d+)', version_alta)
                    if match_alta:
                        version_alta_num = int(match_alta.group(1))
        except Exception as e:
            debug_print(f"Error al comparar versiones: {str(e)}")
        
        # Solo incluir proyectos con versión más alta disponible
        if version_actual_num > 0 and version_alta_num > 0 and version_actual_num < version_alta_num:
            proyectos_con_version_alta.append({
                'proyecto': proyecto,
                'nombre': nombre_interfaz,
                'ruta_actual': ruta_disco,
                'ruta_alta': ruta_version_alta
            })
    
    # Si no hay proyectos con versiones más altas, no abrir la ventana
    if not proyectos_con_version_alta:
        debug_print("No hay proyectos con versiones más altas disponibles. No se mostrará la ventana.")
        return
    
    # Verificar si ya existe una ventana abierta con el mismo nombre de objeto
    ventana_existente = buscar_ventana_existente("LGA_ProyectosAbertosDialog")
    
    if ventana_existente:
        # Si ya existe, mostrar su ID y activarla
        debug_print(f"Ya existe una ventana con ID: {ventana_existente.winId()}")
        debug_print(f"Usando ventana existente con nombre de objeto: {ventana_existente.objectName()}")
        
        # Actualizar los datos de la ventana existente
        ventana_existente.actualizar_proyectos_con_datos(proyectos_con_version_alta)
        
        # Activar la ventana existente (traerla al frente)
        ventana_existente.setWindowState(ventana_existente.windowState() & ~Qt.WindowMinimized | Qt.WindowActive)
        ventana_existente.activateWindow()
        ventana_existente.raise_()
    else:
        # Si no existe, crear una nueva ventana
        global ventana_proyectos
        ventana_proyectos = ProyectosAbertosDialog(hiero.ui.mainWindow(), proyectos_con_version_alta)
        ventana_proyectos.show()  # Usar show() en lugar de exec_() para modo no modal
    
    # Iniciar o reiniciar el temporizador
    iniciar_temporizador()

if __name__ == "__main__":
    main() 