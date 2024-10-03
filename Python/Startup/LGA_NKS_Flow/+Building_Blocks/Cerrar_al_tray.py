import tkinter as tk
from PIL import Image
import os
import pystray


class Gui():

    def __init__(self):
        self.window = tk.Tk()
        self.image = Image.open(resource_path("LGA.ico")) 
         
        self.menu = (
            pystray.MenuItem('Show', self.show_window),
            pystray.MenuItem('Quit', self.quit_window)
            )
        self.window.protocol('WM_DELETE_WINDOW', self.withdraw_window)
        self.window.mainloop()


    def quit_window(self):
        self.icon.stop()
        self.window.destroy()


    def show_window(self):
        self.icon.stop()
        self.window.protocol('WM_DELETE_WINDOW', self.withdraw_window)
        self.window.after(0, self.window.deiconify)


    def withdraw_window(self):
        self.window.withdraw()
        self.icon = pystray.Icon("name", self.image, "title", self.menu)
        self.icon.run()

def resource_path(relative_path):
    """ Get absolute path to resource, works for dev and for PyInstaller """
    try:
        # PyInstaller creates a temp folder and stores path in _MEIPASS
        base_path = sys._MEIPASS
    except Exception:
        # Cuando no estamos usando PyInstaller, obten la ruta del directorio del script
        base_path = os.path.dirname(os.path.abspath(__file__))

    return os.path.join(base_path, relative_path)



if __name__ in '__main__':
    Gui()