# Implementación LGA SnapShot Buttons

## Descripción
Sistema de botones personalizados para el viewer de Nuke que permite tomar snapshots y mostrar el último snapshot tomado mientras se mantiene presionado el botón.

## Archivos del Sistema

### 1. `init.py`
- **Función**: Registra el callback `OnViewerCreate` que se ejecuta cuando se crea un viewer
- **Importa**: `LGA_viewer_SnapShot_Buttons` para el sistema personalizado de botones

### 2. `LGA_viewer_SnapShot_Buttons.py`
- **Función**: Script principal que maneja la inserción de botones en el viewer
- **Características**:
  - Inserta dos botones en el viewer de Nuke
  - Primer botón (`Take_SnapShotButton`): Ejecuta la función `take_snapshot()`
  - Segundo botón (`Show_SnapShotButton`): Ejecuta la función `show_snapshot_hold()` con comportamiento hold
  - Usa iconos `snap_camera.png` para tomar y `sanp_picture.png` para mostrar
  - Importación única del módulo para mantener el estado entre llamadas

### 3. `LGA_viewer_SnapShot.py`
- **Función**: Contiene la lógica principal de snapshot
- **Características**:
  - Compatibilidad con PySide/PySide2
  - Verificaciones exhaustivas de canales válidos antes de procesar
  - Función `take_snapshot()` para capturar imagen del viewer
  - Función `show_snapshot()` para mostrar snapshot durante 1 segundo
  - Función `show_snapshot_hold()` para mostrar snapshot con control manual
  - Función `get_viewer_info()` para obtener información del viewer activo
  - Integración con sistema RenderComplete para manejo de sonido

## Funcionamiento del Sistema

### Flujo de Trabajo
1. **Inicialización**: Al abrir Nuke, `init.py` se carga automáticamente
2. **Creación de Viewer**: Se ejecuta el callback `OnViewerCreate()`
3. **Inserción de Botones**: `LGA_viewer_SnapShot_Buttons.launch()` busca el frameslider y agrega los botones
4. **Funcionalidad Activa**: Los botones ejecutan las funciones correspondientes

### Verificaciones de Seguridad
- **Viewer activo**: Verifica que hay un viewer disponible y conectado
- **Nodo válido**: Confirma que hay un nodo conectado al viewer
- **Canales válidos**: Verifica que el nodo tiene canales de color (RGB/RGBA) ANTES de cualquier procesamiento (incluyendo RenderComplete)
- **Permisos de archivo**: Confirma acceso a carpeta temporal para guardar snapshots

## Estructura de Clases

### Take_SnapShotButton
- **Función**: Botón para tomar snapshots
- **Icono**: `snap_camera.png`
- **Tooltip**: "Tomar SnapShot del viewer activo"
- **Comportamiento**: Ejecuta `take_snapshot()` al hacer clic

### Show_SnapShotButton
- **Función**: Botón para mostrar snapshot con control manual
- **Icono**: `sanp_picture.png`
- **Tooltip**: "Mostrar SnapShot - Mantener presionado"
- **Comportamiento**: Ejecuta `show_snapshot_hold()` con eventos pressed/released
- **Importación**: Carga el módulo una sola vez para mantener estado entre llamadas

## Funciones Principales

### `take_snapshot()`
- **Verificaciones iniciales**: Viewer activo, nodo conectado, canales válidos (ANTES de RenderComplete)
- **Proceso**: Crea nodo Write temporal, ejecuta render, guarda en carpeta temporal
- **Salida**: Copia imagen al portapapeles y mantiene archivo temporal
- **Integración**: Maneja sistema RenderComplete si está disponible

### `show_snapshot()`
- **Función**: Muestra snapshot durante 1 segundo automáticamente
- **Proceso**: Crea nodo Read temporal, conecta al viewer, usa QTimer para timing
- **Restauración**: Automática después del tiempo establecido

### `show_snapshot_hold(start)`
- **Función**: Muestra snapshot con control manual del usuario
- **start=True**: Crea nodo Read temporal y muestra snapshot en viewer
- **start=False**: Elimina nodo Read temporal y restaura estado original
- **Estado**: Usa variable global para mantener información entre llamadas
- **Rendimiento**: Incluye `processEvents()` para evitar bloqueos de UI

### `get_viewer_info()`
- **Función**: Obtiene información del viewer activo
- **Retorna**: Tupla con (viewer, view_node, input_index, input_node)
- **Manejo de errores**: Verificaciones robustas con debug prints

## Implementación del Control Hold

El segundo botón usa eventos nativos de PySide2 para máxima responsividad:
- **pressed()**: Inicia la visualización del snapshot
- **released()**: Termina la visualización y restaura estado
- **Estado persistente**: Variable global mantiene información entre eventos
- **Módulo único**: Importación una sola vez evita reseteo de variables

## Características Técnicas

### Manejo de Errores
- **Verificación de canales**: Previene errores de "has no valid channels"
- **Limpieza robusta**: Eliminación correcta de nodos temporales
- **Mensajes descriptivos**: Errores claros para debugging
- **Manejo de referencias**: Previene errores de "PythonObject not attached"

### Optimización de Rendimiento
- **processEvents()**: Evita bloqueos de UI en puntos críticos
- **Importación única**: Módulo se carga una vez por botón
- **Estado global**: Mantiene información entre llamadas press/release
- **Limpieza automática**: Eliminación de nodos temporales garantizada

### Integración con Sistemas
- **RenderComplete**: Manejo automático de sonido durante snapshot
- **Portapapeles**: Copia automática de imagen generada
- **Archivos temporales**: Gestión de snapshots en carpeta del sistema
- **Iconos**: Sistema de iconos personalizados para botones

## Notas de Implementación
- Los botones se insertan buscando el widget con tooltip "frameslider range"
- Se limpian botones existentes antes de agregar los nuevos
- Debug prints disponibles para seguimiento de ejecución
- Restauración automática del estado del viewer en todos los casos
- Compatibilidad con versiones antiguas y nuevas de Nuke/PySide

 