# Implementación LGA SnapShot Buttons

## Descripción
Sistema de botones personalizados para el viewer de Nuke que permite tomar snapshots y mostrar el último snapshot tomado mientras se mantiene presionado el botón.

## Archivos del Sistema

### 1. `LGA_ToolPack/init.py`
- **Función**: Registra el callback `OnViewerCreate` que se ejecuta cuando se crea un viewer
- **Importa**: `LGA_viewer_SnapShot_Buttons` para el sistema personalizado de botones

### 2. `LGA_ToolPack/LGA_viewer_SnapShot_Buttons.py`
- **Función**: Script principal que maneja la inserción de botones en el viewer
- **Características**:
  - Inserta dos botones en el viewer de Nuke
  - Primer botón (`Take_SnapShotButton`): Ejecuta la función `take_snapshot()`
  - Segundo botón (`Show_SnapShotButton`): Ejecuta la función `show_snapshot_hold()` con comportamiento hold
  - Usa iconos `snap_camera.png` para tomar y `sanp_picture.png` para mostrar
  - Importación única del módulo para mantener el estado entre llamadas

### 3. `LGA_ToolPack/LGA_viewer_SnapShot.py`
- **Función**: Contiene la lógica principal de snapshot
- **Características**:
  - Compatibilidad con PySide/PySide2
  - Verificaciones exhaustivas de canales válidos antes de procesar
  - Función `take_snapshot()` para capturar imagen del viewer
  - Función `show_snapshot_hold()` para mostrar snapshot con control manual
  - Función `get_viewer_info()` para obtener información del viewer activo con nodo conectado
  - Función `get_viewer_info_for_show()` para obtener información del viewer permitiendo trabajar sin nodo conectado
  - Integración con sistema RenderComplete para manejo de sonido
  - Sistema de numeración ascendente para snapshots únicos (evita problemas de cache)
  - Funciones auxiliares: `get_next_snapshot_number()`, `cleanup_old_snapshots()`, `get_latest_snapshot_path()`

## Funcionamiento del Sistema

### Flujo de Trabajo
1. **Inicialización**: Al abrir Nuke, `init.py` se carga automáticamente
2. **Creación de Viewer**: Se ejecuta el callback `OnViewerCreate()`
3. **Inserción de Botones**: `LGA_viewer_SnapShot_Buttons.launch()` busca el frameslider y agrega los botones
4. **Funcionalidad Activa**: Los botones ejecutan las funciones correspondientes

### Verificaciones de Seguridad
- **Viewer activo**: Verifica que hay un viewer disponible
- **Nodo válido**: Para `take_snapshot()` confirma que hay un nodo conectado al viewer
- **Canales válidos**: Verifica que el nodo tiene canales de color (RGB/RGBA) ANTES de cualquier procesamiento
- **Permisos de archivo**: Confirma acceso a carpeta temporal para guardar snapshots
- **Flexibilidad**: `show_snapshot_hold()` funciona con o sin nodo conectado al viewer

## Estructura de Clases

### Take_SnapShotButton
- **Función**: Botón para tomar snapshots
- **Icono**: `snap_camera.png`
- **Tooltip**: "Tomar SnapShot del viewer activo"
- **Comportamiento**: Ejecuta `take_snapshot()` al hacer clic
- **Requisito**: Necesita nodo conectado al viewer

### Show_SnapShotButton
- **Función**: Botón para mostrar snapshot con control manual
- **Icono**: `sanp_picture.png`
- **Tooltip**: "Mostrar SnapShot - Mantener presionado"
- **Comportamiento**: Ejecuta `show_snapshot_hold()` con eventos pressed/released
- **Flexibilidad**: Funciona con o sin nodo conectado al viewer
- **Importación**: Carga el módulo una sola vez para mantener estado entre llamadas

## Funciones Principales

### `take_snapshot()`
- **Verificaciones iniciales**: Viewer activo, nodo conectado, canales válidos (ANTES de RenderComplete)
- **Numeración única**: Genera snapshots con nombres `LGA_snapshot_N.jpg` donde N es ascendente
- **Proceso**: Crea nodo Write temporal, ejecuta render, guarda en carpeta temporal
- **Limpieza automática**: Elimina snapshots anteriores después del guardado exitoso
- **Salida**: Copia imagen al portapapeles y mantiene archivo temporal
- **Integración**: Maneja sistema RenderComplete si está disponible
- **Requisito**: Necesita nodo conectado al viewer con canales válidos

### `show_snapshot_hold(start)`
- **Función**: Muestra snapshot con control manual del usuario
- **start=True**: Busca el snapshot más reciente y lo muestra en viewer
- **start=False**: Elimina nodo Read temporal y restaura estado original
- **Estado**: Usa variable global para mantener información entre llamadas
- **Posicionamiento inteligente**: 
  - Con nodo conectado: Posiciona Read debajo del nodo existente
  - Sin nodo conectado: Posiciona Read arriba del viewer
- **Sin cache**: No necesita reload ya que cada snapshot tiene nombre único
- **Restauración**: Reconecta nodo original o desconecta viewer según estado inicial
- **Rendimiento**: Incluye `processEvents()` para evitar bloqueos de UI

### `get_viewer_info()`
- **Función**: Obtiene información del viewer activo con nodo conectado requerido
- **Retorna**: Tupla con (viewer, view_node, input_index, input_node)
- **Uso**: Para funciones que requieren nodo conectado como `take_snapshot()`
- **Manejo de errores**: Verificaciones robustas con debug prints

### `get_viewer_info_for_show()`
- **Función**: Obtiene información del viewer activo permitiendo trabajar sin nodo conectado
- **Retorna**: Tupla con (viewer, view_node, input_index, input_node) donde input_node puede ser None
- **Uso**: Para `show_snapshot_hold()` que puede funcionar sin nodo conectado
- **Flexibilidad**: Permite mostrar snapshots en viewers vacíos

### Funciones Auxiliares de Numeración

### `get_next_snapshot_number()`
- **Función**: Obtiene el siguiente número para snapshot verificando archivos existentes
- **Retorna**: Número entero siguiente al más alto encontrado
- **Patrón**: Busca archivos `LGA_snapshot_*.jpg` en carpeta temporal

### `cleanup_old_snapshots(current_number)`
- **Función**: Elimina snapshots con número menor al actual
- **Proceso**: Mantiene solo el snapshot más reciente para ahorrar espacio
- **Seguridad**: Manejo de errores en eliminación de archivos

### `get_latest_snapshot_path()`
- **Función**: Obtiene la ruta del snapshot con número más alto
- **Retorna**: Ruta completa del archivo o None si no encuentra ninguno
- **Uso**: Para `show_snapshot_hold()` al buscar el snapshot más reciente

## Implementación del Control Hold

El segundo botón usa eventos nativos de PySide2 para máxima responsividad:
- **pressed()**: Inicia la visualización del snapshot
- **released()**: Termina la visualización y restaura estado
- **Estado persistente**: Variable global mantiene información entre eventos
- **Módulo único**: Importación una sola vez evita reseteo de variables
- **Posicionamiento adaptativo**: Se adapta a viewers con o sin nodos conectados
- **Sistema único**: Cada snapshot tiene nombre único, evita problemas de cache

## Características Técnicas

### Manejo de Errores
- **Verificación de canales**: Previene errores de "has no valid channels"
- **Limpieza robusta**: Eliminación correcta de nodos temporales
- **Mensajes descriptivos**: Errores claros para debugging
- **Manejo de referencias**: Previene errores de "PythonObject not attached"
- **Verificación de estado**: Manejo seguro de viewers con/sin nodos conectados

### Optimización de Rendimiento
- **processEvents()**: Evita bloqueos de UI en puntos críticos
- **Importación única**: Módulo se carga una vez por botón
- **Estado global**: Mantiene información entre llamadas press/release
- **Limpieza automática**: Eliminación de nodos temporales y snapshots antiguos garantizada
- **Numeración inteligente**: Sistema ascendente evita conflictos y problemas de cache

### Integración con Sistemas
- **RenderComplete**: Manejo automático de sonido durante snapshot
- **Portapapeles**: Copia automática de imagen generada
- **Archivos temporales**: Gestión de snapshots en carpeta del sistema
- **Iconos**: Sistema de iconos personalizados para botones
- **Nuke API**: Uso correcto de `node["reload"].execute()` para recargar Read nodes

## Notas de Implementación
- Los botones se insertan buscando el widget con tooltip "frameslider range"
- Se limpian botones existentes antes de agregar los nuevos
- Debug prints disponibles para seguimiento de ejecución
- Restauración automática del estado del viewer en todos los casos
- Compatibilidad con versiones antiguas y nuevas de Nuke/PySide
- Soporte completo para viewers vacíos en función de mostrar snapshot

 