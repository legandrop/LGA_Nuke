# Implementación LGA SnapShot Buttons

## Descripción
Sistema de botones personalizados para el viewer de Nuke que permite tomar snapshots, mostrar el último snapshot tomado, y probar efectos de hold.

## Archivos Modificados/Creados

### 1. `init.py`
- **Modificado**: Cambiado para usar nuestro sistema personalizado
- **Función**: Registra el callback `OnViewerCreate` que se ejecuta cuando se crea un viewer
- **Cambio principal**: Ahora importa `LGA_viewer_SnapShot_Buttons`

### 2. `LGA_viewer_SnapShot_Buttons.py`
- **Creado**: Script principal que maneja la inserción de botones en el viewer
- **Funcionalidades**:
  - Inserta tres botones en el viewer de Nuke
  - Primer botón: Ejecuta la función `take_snapshot()` de `LGA_viewer_SnapShot.py`
  - Segundo botón: Ejecuta la función `show_snapshot()` para mostrar el último snapshot
  - Tercer botón: Ejecuta la función `test_hold()` para probar efectos de hold (press/release)
  - Usa los mismos iconos que el script original (`snap_picture.png`, `snap_camera.png`)

### 3. `LGA_viewer_SnapShot.py`
- **Existente**: Script que contiene la lógica de snapshot
- **Modificado**: 
  - Corregidas las importaciones de PySide para compatibilidad
  - Función `main()` renombrada a `take_snapshot()` para mayor claridad
  - Agregada función `get_viewer_info()` para obtener información del viewer
  - Agregada función `show_snapshot()` para mostrar el último snapshot tomado
  - Agregada función `test_hold()` para crear/eliminar nodos NoOp con efecto hold
  - Mejorada la modularidad del código


## Cómo Funciona

1. **Al abrir Nuke**: El archivo `init.py` se carga automáticamente
2. **Al crear un Viewer**: Se ejecuta el callback `OnViewerCreate()`
3. **Inserción de botones**: `LGA_viewer_SnapShot_Buttons.launch()` busca el frameslider del viewer y agrega los botones
4. **Funcionalidad**: 
   - El primer botón ejecuta `LGA_viewer_SnapShot.take_snapshot()` para tomar el snapshot
   - El segundo botón ejecuta `LGA_viewer_SnapShot.show_snapshot()` para mostrar el último snapshot
   - El tercer botón ejecuta `LGA_viewer_SnapShot.test_hold()` para crear/eliminar nodos con efecto hold

## Estructura de Clases

### SnapShotButton
- Botón principal para tomar snapshots
- Icono: `snap_camera.png`
- Tooltip: "Tomar SnapShot del viewer activo"
- Acción: Ejecuta `LGA_viewer_SnapShot.take_snapshot()`

### SwitchButton (ahora ShowButton)
- Botón para mostrar el último snapshot
- Icono: `sanp_picture.png`
- Tooltip: "Mostrar ultimo SnapShot tomado"
- Acción: Ejecuta `LGA_viewer_SnapShot.show_snapshot()`

### HoldTestButton
- Botón para probar efectos de hold (press/release)
- Icono: `sanp_picture.png` (mismo que SwitchButton)
- Tooltip: "Test Hold Button - Mantener presionado"
- Acción: Ejecuta `LGA_viewer_SnapShot.test_hold()` con eventos pressed/released
- **Funcionalidad Hold**: Crea un nodo NoOp al presionar y lo elimina al soltar

## Funciones Principales

### `take_snapshot()`
- Toma un snapshot del viewer activo
- Guarda temporalmente en `temp/LGA_snapshot.jpg`
- Copia la imagen al portapapeles
- Maneja el sistema de sonido RenderComplete si está disponible

### `show_snapshot()`
- Verifica que existe el archivo `temp/LGA_snapshot.jpg`
- Crea un nodo Read temporal conectado al snapshot
- Muestra el snapshot en el viewer durante 1 segundo
- Restaura automáticamente el estado original del viewer

### `test_hold(start)`
- **start=True**: Crea un nodo NoOp con nombre "LGA_HOLD_TEST", color azul y label "HOLD TEST"
- **start=False**: Elimina el nodo NoOp si existe
- Proporciona feedback visual y en consola del estado del nodo
- Manejo robusto de errores con try/catch

### `get_viewer_info()`
- Función auxiliar que obtiene información del viewer activo
- Retorna tupla con (viewer, view_node, input_index, input_node)
- Maneja errores de forma robusta con debug prints

## Implementación del Efecto Hold

El tercer botón implementa un efecto de "hold" usando los signals `pressed()` y `released()` de PySide2:

```python
# Conectar eventos de press y release
self.addShortcutButton.pressed.connect(self.on_pressed)
self.addShortcutButton.released.connect(self.on_released)

def on_pressed(self):
    """Se ejecuta cuando se presiona el boton"""
    self.call_test_hold(start=True)

def on_released(self):
    """Se ejecuta cuando se suelta el boton"""
    self.call_test_hold(start=False)
```

## Notas Técnicas
- Los botones se insertan buscando el widget con tooltip "frameslider range"
- Se limpian botones existentes antes de agregar los nuevos
- Manejo de errores robusto con mensajes informativos
- Debug prints para seguimiento de la ejecución
- El segundo y tercer botón usan debug prints (sin nuke.message) para errores
- Restauración automática del estado del viewer después de mostrar el snapshot
- El efecto hold usa eventos nativos de PySide2 para máxima responsividad 