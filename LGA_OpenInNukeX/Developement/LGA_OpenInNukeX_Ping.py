"""
____________________________________________________________

  LGA_OpenInNukeX v1.1 - 2024 - Lega Pugliese
  "ping.py" sends a ping to check if port 54325 is open
____________________________________________________________

"""

import socket

def ping_nukex():
    host = 'localhost'
    port = 54325  # El puerto donde NukeX escucha

    try:
        with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
            s.settimeout(10)  # Configurar un timeout para la conexion
            s.connect((host, port))  # Intentar establecer una conexion
            print("Connected to NukeX.")

            # Enviar un comando 'ping'
            s.sendall("ping".encode())
            print("Ping sent.")

            # Recibir respuesta
            response = s.recv(1024).decode()  # Esperar una respuesta
            print(f"Received response: {response}")

            if "pong" in response:
                print("NukeX is active and responding.")  # Confirmacion de que NukeX esta activo
            else:
                print("Received unexpected response.")  # La respuesta no es la esperada
    except socket.timeout:
        print("Error", "Connection to Nuke has expired.")
    except ConnectionRefusedError:
        print("Error", "Failed to connect to Nuke. Attempting to open NukeX with the file.")
    except ConnectionResetError:
        print("Error", "The connection was closed by the server.")

# Llamada a la funcion para verificar si NukeX esta abierto
ping_nukex()
