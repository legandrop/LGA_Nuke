# Python envia un mensaje a XYplorer
import ctypes
import ctypes.wintypes
import platform
import win32gui

def get_xy_hwnd(xy_class='ThunderRT6FormDC'):
    # Inicializa una variable para almacenar el handle de la ventana encontrada
    found_hwnd = None

    # Enumera todas las ventanas de nivel superior
    def enum_windows_callback(hwnd, extra):
        nonlocal found_hwnd  # Declara que vamos a usar una variable externa dentro de esta funcion anidada

        class_name = win32gui.GetClassName(hwnd)

        if class_name == xy_class:
            # Intenta obtener el numero de controles
            child_count = [0]  # Usa una lista como objeto mutable para almacenar el conteo

            def enum_child_windows_callback(hwnd_child, extra_child):
                child_count[0] += 1  # Incrementa el conteo
                return True  # Continua enumerando

            win32gui.EnumChildWindows(hwnd, enum_child_windows_callback, None)

            # Si se encontro un nombre de clase coincidente y el numero de subventanas es suficiente
            if child_count[0] >= 10:
                found_hwnd = hwnd  # Actualiza el handle de la ventana encontrada
                return False  # Detiene la enumeracion de ventanas de nivel superior

        return True  # Continua enumerando las ventanas de nivel superior

    # Enumera todas las ventanas de nivel superior y llama a la funcion callback
    try:
        win32gui.EnumWindows(enum_windows_callback, None)
    except Exception as e:
        return found_hwnd

    # Devuelve el handle de la ventana encontrada (si es que hay alguna)
    return found_hwnd

# Determina la arquitectura del sistema
if platform.architecture()[0] == '32bit':
    ULONG_PTR = ctypes.wintypes.ULONG
else:
    ULONG_PTR = ctypes.c_uint64

# Define la estructura COPYDATASTRUCT
class COPYDATASTRUCT(ctypes.Structure):
    _fields_ = [("dwData", ULONG_PTR),
                ("cbData", ctypes.wintypes.DWORD),
                ("lpData", ctypes.c_void_p)]

def Send_WM_COPYDATA(xyHwnd, message):
    if not xyHwnd:
        return None

    # Prepara los datos COPYDATASTRUCT
    cds = COPYDATASTRUCT()
    cds.dwData = 4194305  # Este es un valor de ejemplo, puede necesitar ajustarse segun tu aplicacion
    cds.cbData = len(message.encode('utf-16-le'))  # Calcula la longitud en bytes de UTF-16
    cds_data = ctypes.create_unicode_buffer(message)
    cds.lpData = ctypes.cast(ctypes.addressof(cds_data), ctypes.c_void_p)

    # Invoca SendMessageW
    user32 = ctypes.WinDLL('user32', use_last_error=True)
    result = user32.SendMessageW(xyHwnd, 74, 0, ctypes.byref(cds))

    return result

#############################################################################
# Ejemplo de uso
hwnd = get_xy_hwnd()  # Obtiene el handle de la ventana y lo imprime (necesitas un handle valido)
tag_command = "::tag 'Red', 'F:\\+Download Torrent';"  # Comando para etiquetar la carpeta
result = Send_WM_COPYDATA(hwnd, tag_command)
