# Herramienta de Command & Control (C2) con Python

## 📄 Descripción General del Proyecto
Este repositorio contiene una herramienta de Command & Control (C2) desarrollada íntegramente en Python. El objetivo principal de este proyecto académico fue comprender los principios fundamentales de las comunicaciones persistentes y el control remoto de sistemas en un entorno de laboratorio controlado y ético. Está diseñada para la gestión de "implantes" (clientes) desde un servidor central.

## ✨ Características Implementadas
* **Comunicación Cliente-Servidor:** Utiliza sockets TCP/IP para establecer conexiones persistentes entre el servidor C2 y los implantes (clientes).
* **Ejecución Remota de Comandos:** Capacidad para enviar y ejecutar comandos del sistema operativo en el implante desde el servidor C2.
* **Exfiltración de Datos:** Funcionalidad para extraer archivos o información específica del implante al servidor C2.
* **Persistencia Básica:** Implementación de técnicas sencillas para mantener la conexión o reconexión del implante.
* **Cifrado Básico (Opcional - si lo implementaste):** Utiliza [AES/RSA/simple XOR] para asegurar la confidencialidad de las comunicaciones.

## 🚀 Tecnologías y Herramientas Utilizadas
* **Lenguaje de Programación:** Python 3.x
* **Librerías Python:**
    * `socket`
    * `subprocess`
    * `os`
    * `base64`
    * `Requests`
* **Sistemas Operativos de Prueba:** Linux (Kali/Ubuntu/Parrot OS), Windows.

## 🛠️ Cómo Funciona (Uso Básico)
1.  **Clonar el repositorio:**
    ```bash
    git clone [https://github.com/tu-usuario/Python-C2-Tool.git](https://github.com/tu-usuario/Python-C2-Tool.git)
    cd Python-C2-Tool
    ```
2.  **Configurar el Servidor C2:**
    * Editar `server.py` para establecer el puerto de escucha.
    * Ejecutar el servidor: `python3 server.py`
3.  **Configurar el Cliente (Implante):**
    * Editar `client.py` para apuntar a la IP y puerto del servidor C2.
    * Ejecutar el cliente en la máquina objetivo: `python3 client.py`
4.  **Interactuar:** Desde el servidor C2, podrás enviar comandos y recibir resultados de los implantes conectados.

## ⚠️ Aviso Importante (Disclaimer)
Este proyecto fue desarrollado con **fines exclusivamente educativos y de aprendizaje** en el ámbito de la ciberseguridad ofensiva. **No debe ser utilizado para actividades ilegales o maliciosas.** El autor no se hace responsable del mal uso que se le pueda dar a esta herramienta. Su propósito es ayudar a comprender el funcionamiento de las amenazas persistentes avanzadas (APT) y cómo protegerse de ellas.

## ✉️ Contacto
Zm0kSec
www.linkedin.com/in/benedicto-palma-verrdugo-094931301
