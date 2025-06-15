# Implementación LGA SnapShot Buttons

## Descripción
Sistema de botones personalizados para el viewer de Nuke que permite tomar snapshots y funcionalidades adicionales.

## Archivos Modificados/Creados

### 1. `init.py`
- **Modificado**: Cambiado para usar nuestro sistema personalizado
- **Función**: Registra el callback `OnViewerCreate` que se ejecuta cuando se crea un viewer
- **Cambio principal**: Ahora importa `LGA_viewer_SnapShot_Buttons`

### 2. `LGA_viewer_SnapShot_Buttons.py`
- **Creado**: Script principal que maneja la inserción de botones en el viewer
- **Funcionalidades**:
  - Inserta dos botones en el viewer de Nuke
  - Primer botón: Ejecuta la función `main()` de `LGA_viewer_SnapShot.py`
  - Segundo botón: Funcionalidad futura (placeholder)
  - Usa los mismos iconos que el script original (`snap_picture.png`, `snap_camera.png`)

### 3. `LGA_viewer_SnapShot.py`
- **Existente**: Script que contiene la lógica de snapshot
- **Modificado**: Corregidas las importaciones de PySide para compatibilidad
- **Función**: Toma un snapshot del viewer activo y lo copia al portapapeles


## Cómo Funciona

1. **Al abrir Nuke**: El archivo `init.py` se carga automáticamente
2. **Al crear un Viewer**: Se ejecuta el callback `OnViewerCreate()`
3. **Inserción de botones**: `LGA_viewer_SnapShot_Buttons.launch()` busca el frameslider del viewer y agrega los botones
4. **Funcionalidad**: El primer botón ejecuta `LGA_viewer_SnapShot.main()` para tomar el snapshot

## Estructura de Clases

### SnapShotButton
- Botón principal para tomar snapshots
- Icono: `snap_picture.png`
- Tooltip: "Tomar SnapShot del viewer activo"
- Acción: Ejecuta `LGA_viewer_SnapShot.main()`

### SwitchButton
- Botón secundario (funcionalidad futura)
- Icono: `snap_camera.png`
- Tooltip: "Cambiar viewer (funcionalidad futura)"
- Acción: Placeholder para futuras implementaciones


## Notas Técnicas
- Los botones se insertan buscando el widget con tooltip "frameslider range"
- Se limpian botones existentes antes de agregar los nuevos
- Manejo de errores robusto con mensajes informativos
- Debug prints para seguimiento de la ejecución 