# Cómo obtener Links de Imágenes y Frame Numbers de Review Attachments en ShotGrid

## Resumen
Este documento explica cómo obtener los links de descarga de imágenes de review y sus frame numbers asociados desde ShotGrid usando la API de Python.

## Estructura de Datos

### 1. Obtener Notas de una Versión
Para obtener las notas con attachments de una versión específica:

```python
def get_version_notes_debug(self, version_id):
    filters = [['note_links', 'in', {'type': 'Version', 'id': version_id}]]
    fields = [
        'id', 'content', 'user', 'created_at', 'updated_at', 'subject',
        'note_links', 'attachments', 'sg_status_list', 'sg_note_type',
        # ... otros campos
    ]
    return self.sg.find("Note", filters, fields)
```

**Campo clave:** `attachments` - contiene una lista de referencias a attachments

### 2. Estructura del Campo Attachments
El campo `attachments` en una nota contiene una lista de diccionarios con esta estructura:
```python
attachments: [
    {
        'id': 41634, 
        'name': 'annot_version_51150.16.png', 
        'type': 'Attachment'
    }
]
```

### 3. Extraer Frame Number del Nombre
El frame number está codificado en el nombre del archivo:
- **Patrón:** `annot_version_[VERSION_ID].[FRAME_NUMBER].png`
- **Ejemplo:** `annot_version_51150.16.png` → Frame 16

```python
def extract_frame_from_attachment_name(self, attachment_name):
    if ".png" in attachment_name:
        frame_match = re.search(r"\.(\d+)\.png$", attachment_name)
        if frame_match:
            return frame_match.group(1)
    return "Unknown"
```

### 4. Obtener Detalles Completos del Attachment
Para obtener el link de descarga, necesitas hacer una consulta adicional:

```python
def get_attachment_details(self, attachment_id):
    filters = [['id', 'is', attachment_id]]
    fields = [
        'id', 'code', 'description', 'this_file', 'image', 'sg_file_type',
        'created_at', 'updated_at', 'created_by', 'sg_status_list',
        'attachment_links', 'url', 'local_path'
    ]
    attachments = self.sg.find("Attachment", filters, fields)
    return attachments[0] if attachments else None
```

### 5. Extraer URL de Descarga
El link de descarga está en el campo `this_file`:

```python
def get_attachment_download_url(self, attachment_details):
    if attachment_details.get('this_file') and isinstance(attachment_details['this_file'], dict):
        return attachment_details['this_file'].get('url', 'No URL found')
    return "No URL found"
```

**Estructura del campo `this_file`:**
```python
this_file: {
    'url': 'https://sg-media-saopaulo.s3-accelerate.amazonaws.com/...', 
    'name': 'annot_version_51150.16.png', 
    'content_type': 'image/png', 
    'link_type': 'upload', 
    'type': 'Attachment', 
    'id': 41634
}
```

## Campos Importantes

### En las Notas (Note entity):
- **`attachments`** - Lista de referencias a attachments
- **`id`** - ID de la nota
- **`content`** - Contenido del comentario
- **`user`** - Usuario que creó la nota

### En los Attachments (Attachment entity):
- **`this_file`** - Diccionario con URL de descarga y metadatos
- **`image`** - URL del thumbnail/preview
- **`id`** - ID del attachment
- **`created_at`** - Fecha de creación
- **`created_by`** - Usuario que creó el attachment

## Proceso Completo

1. **Obtener notas de la versión** con el campo `attachments`
2. **Iterar sobre cada attachment** en las notas
3. **Extraer frame number** del nombre del archivo usando regex
4. **Obtener detalles completos** del attachment usando su ID
5. **Extraer URL de descarga** del campo `this_file['url']`

## Ejemplo de Uso

```python
# 1. Obtener notas con attachments
notes = sg_manager.get_version_notes_debug(version_id)

# 2. Procesar cada nota
for note in notes:
    if note.get('attachments'):
        for attachment_ref in note['attachments']:
            # 3. Extraer frame del nombre
            frame_number = extract_frame_from_attachment_name(attachment_ref['name'])
            
            # 4. Obtener detalles completos
            attachment_details = sg_manager.get_attachment_details(attachment_ref['id'])
            
            # 5. Extraer URL de descarga
            download_url = get_attachment_download_url(attachment_details)
            
            print(f"Frame: {frame_number}, URL: {download_url}")
```

## Resultado Final
- **Frame Number:** Extraído del nombre del archivo (ej: "16")
- **Download URL:** URL completa de AWS S3 para descargar la imagen PNG
- **Thumbnail URL:** URL del preview en el campo `image`

Esta información permite descargar las imágenes de review con sus frame numbers específicos para procesamiento posterior.
