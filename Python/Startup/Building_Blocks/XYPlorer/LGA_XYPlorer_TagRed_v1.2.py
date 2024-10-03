import ctypes
import ctypes.wintypes
import platform

# Definiciones y estructuras necesarias para interactuar con la API de Windows
user32 = ctypes.windll.user32
EnumWindows = user32.EnumWindows
EnumWindowsProc = ctypes.WINFUNCTYPE(ctypes.wintypes.BOOL, ctypes.wintypes.HWND, ctypes.wintypes.LPARAM)
GetClassName = user32.GetClassNameW
EnumChildWindows = user32.EnumChildWindows
GetWindowTextLength = user32.GetWindowTextLengthW
GetWindowText = user32.GetWindowTextW

def get_xy_hwnd(xy_class='ThunderRT6FormDC'):
    found_hwnd = None

    def enum_windows_callback(hwnd, lParam):
        nonlocal found_hwnd
        class_name = ctypes.create_unicode_buffer(256)
        GetClassName(hwnd, class_name, 256)
        if class_name.value == xy_class:
            child_count = [0]

            def enum_child_windows_callback(hwnd_child, lParam_child):
                child_count[0] += 1
                return True

            EnumChildWindows(hwnd, EnumWindowsProc(enum_child_windows_callback), 0)

            if child_count[0] >= 10:
                found_hwnd = hwnd
                return False
        return True

    EnumWindows(EnumWindowsProc(enum_windows_callback), 0)
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

    cds = COPYDATASTRUCT()
    cds.dwData = 4194305
    cds.cbData = len(message.encode('utf-16-le'))
    cds_data = ctypes.create_unicode_buffer(message)
    cds.lpData = ctypes.cast(ctypes.addressof(cds_data), ctypes.c_void_p)

    user32 = ctypes.WinDLL('user32', use_last_error=True)
    result = user32.SendMessageW(xyHwnd, 74, 0, ctypes.byref(cds))

    return result

# Ejemplo de uso
hwnd = get_xy_hwnd()
tag_command = "::tag 'Red', 'F:\\+Download Torrent';"
result = Send_WM_COPYDATA(hwnd, tag_command)
