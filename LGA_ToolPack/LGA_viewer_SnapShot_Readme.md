# Implementación LGA SnapShot Buttons

## Descripción
Sistema de botones personalizados para el viewer de Nuke que permite tomar snapshots y mostrar el último snapshot tomado mientras se mantiene presionado el botón.

## Archivos Modificados/Creados

### 1. `init.py`
- **Modificado**: Cambiado para usar nuestro sistema personalizado
- **Función**: Registra el callback `OnViewerCreate` que se ejecuta cuando se crea un viewer
- **Cambio principal**: Ahora importa `LGA_viewer_SnapShot_Buttons`

### 2. `LGA_viewer_SnapShot_Buttons.py`
- **Creado**: Script principal que maneja la inserción de botones en el viewer
- **Funcionalidades**:
  - Inserta dos botones en el viewer de Nuke
  - Primer botón (`Take_SnapShotButton`): Ejecuta la función `take_snapshot()` de `LGA_viewer_SnapShot.py`
  - Segundo botón (`Show_SnapShotButton`): Ejecuta la función `show_snapshot_hold()` para mostrar el snapshot mientras se mantiene presionado
  - Usa los iconos `snap_camera.png` para tomar y `sanp_picture.png` para mostrar

### 3. `LGA_viewer_SnapShot.py`
- **Existente**: Script que contiene la lógica de snapshot
- **Modificado**: 
  - Corregidas las importaciones de PySide para compatibilidad
  - Función `main()` renombrada a `take_snapshot()` para mayor claridad
  - Agregada función `get_viewer_info()` para obtener información del viewer
  - Función `show_snapshot()` mantiene el comportamiento original (1 segundo)
  - **Nueva función `show_snapshot_hold()`** para mostrar snapshot mientras se mantiene presionado el botón
  - **Eliminada función `test_hold()`** ya que era solo para investigación
  - Mejorada la modularidad del código

## Cómo Funciona

1. **Al abrir Nuke**: El archivo `init.py` se carga automáticamente
2. **Al crear un Viewer**: Se ejecuta el callback `OnViewerCreate()`
3. **Inserción de botones**: `LGA_viewer_SnapShot_Buttons.launch()` busca el frameslider del viewer y agrega los botones
4. **Funcionalidad**: 
   - El primer botón ejecuta `LGA_viewer_SnapShot.take_snapshot()` para tomar el snapshot
   - El segundo botón ejecuta `LGA_viewer_SnapShot.show_snapshot_hold()` para mostrar/ocultar el snapshot con efecto hold

## Estructura de Clases

### Take_SnapShotButton
- Botón principal para tomar snapshots
- Icono: `snap_camera.png`
- Tooltip: "Tomar SnapShot del viewer activo"
- Acción: Ejecuta `LGA_viewer_SnapShot.take_snapshot()` al hacer clic

### Show_SnapShotButton
- Botón para mostrar el snapshot con efecto hold
- Icono: `sanp_picture.png`
- Tooltip: "Mostrar SnapShot - Mantener presionado"
- Acción: Ejecuta `LGA_viewer_SnapShot.show_snapshot_hold()` con eventos pressed/released
- **Funcionalidad Hold**: Muestra el snapshot al presionar y lo oculta al soltar

## Funciones Principales

### `take_snapshot()`
- Toma un snapshot del viewer activo
- Guarda temporalmente en `temp/LGA_snapshot.jpg`
- Copia la imagen al portapapeles
- Maneja el sistema de sonido RenderComplete si está disponible

### `show_snapshot()`
- **Función original**: Muestra el snapshot durante 1 segundo automáticamente
- Verifica que existe el archivo `temp/LGA_snapshot.jpg`
- Crea un nodo Read temporal conectado al snapshot
- Restaura automáticamente el estado original del viewer

### `show_snapshot_hold(start)`
- **Nueva función**: Muestra el snapshot mientras se mantiene presionado el botón
- **start=True**: Crea un nodo Read temporal y muestra el snapshot en el viewer
- **start=False**: Elimina el nodo Read temporal y restaura el estado original
- Usa una variable global `_lga_snapshot_hold_state` para mantener el estado entre press/release
- Proporciona feedback visual y en consola del estado del snapshot
- Manejo robusto de errores con try/catch

### `get_viewer_info()`
- Función auxiliar que obtiene información del viewer activo
- Retorna tupla con (viewer, view_node, input_index, input_node)
- Maneja errores de forma robusta con debug prints

## Implementación del Efecto Hold

El segundo botón implementa un efecto de "hold" usando los signals `pressed()` y `released()` de PySide2:

```python
# Conectar eventos de press y release
self.addShortcutButton.pressed.connect(self.on_pressed)
self.addShortcutButton.released.connect(self.on_released)

def on_pressed(self):
    """Se ejecuta cuando se presiona el boton"""
    self.call_show_snapshot(start=True)

def on_released(self):
    """Se ejecuta cuando se suelta el boton"""
    self.call_show_snapshot(start=False)
```

## Cambios Realizados en v0.6

### Renombrado de Clases
- `SnapShotButton` → `Take_SnapShotButton`
- `SwitchButton` → `Show_SnapShotButton`
- **Eliminada**: `HoldTestButton` (ya no es necesaria)

### Nuevo Comportamiento del Botón Show
- **Antes**: Mostraba el snapshot durante 1 segundo al hacer clic
- **Ahora**: Muestra el snapshot mientras se mantiene presionado el botón
- **Implementación**: Usa eventos `pressed()` y `released()` para control total del usuario

### Funciones Eliminadas
- **`test_hold()`**: Eliminada ya que era solo para investigación y ejemplo

### Funciones Agregadas
- **`show_snapshot_hold(start)`**: Nueva función que maneja el comportamiento hold del snapshot

## Notas Técnicas
- Los botones se insertan buscando el widget con tooltip "frameslider range"
- Se limpian botones existentes antes de agregar los nuevos
- Manejo de errores robusto con mensajes informativos
- Debug prints para seguimiento de la ejecución
- El botón show usa debug prints (sin nuke.message) para errores
- Restauración automática del estado del viewer después de mostrar el snapshot
- El efecto hold usa eventos nativos de PySide2 para máxima responsividad
- Variable global `_lga_snapshot_hold_state` para mantener el estado entre press/release
- Solo dos botones en el viewer: Take y Show 