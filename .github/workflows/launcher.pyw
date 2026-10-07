import os
import sys
import subprocess
import time
import webbrowser
import threading
import tkinter as tk
from tkinter import messagebox

# Configuración de rutas predeterminadas
XAMPP_PATH = r"C:\xampp"
PROJECT_PATH = os.path.dirname(os.path.abspath(__file__))
VENV_PYTHON = os.path.join(PROJECT_PATH, "venv", "Scripts", "python.exe")
RUN_SCRIPT = os.path.join(PROJECT_PATH, "run.py")

class AppLauncher:
    def __init__(self, root):
        self.root = root
        self.root.title("GroStop - Launcher")
        self.root.geometry("380x220")
        self.root.resizable(False, False)
        
        self.flask_process = None

        # Elementos de interfaz
        self.lbl_title = tk.Label(root, text="Panel de Control GroStop", font=("Segoe UI", 12, "bold"))
        self.lbl_title.pack(pady=10)

        self.lbl_status = tk.Label(root, text="Estado: Detenido", font=("Segoe UI", 10, "bold"), fg="#D32F2F")
        self.lbl_status.pack(pady=5)

        self.btn_start = tk.Button(
            root, 
            text="Iniciar Servidores y Aplicación", 
            font=("Segoe UI", 10), 
            bg="#2E7D32", 
            fg="white", 
            width=30, 
            height=2, 
            command=self.start_all_async
        )
        self.btn_start.pack(pady=8)

        self.btn_stop = tk.Button(
            root, 
            text="Detener Todo", 
            font=("Segoe UI", 10), 
            bg="#C62828", 
            fg="white", 
            width=30, 
            height=1, 
            command=self.stop_all
        )
        self.btn_stop.pack(pady=5)

    def start_all_async(self):
        threading.Thread(target=self.start_all, daemon=True).start()

    def start_all(self):
        self.btn_start.config(state="disabled")
        self.lbl_status.config(text="Estado: Iniciando Apache y MySQL...", fg="#ED6C02")
        
        # 1. Ejecución de scripts de arranque de XAMPP
        mysql_bat = os.path.join(XAMPP_PATH, "mysql_start.bat")
        apache_bat = os.path.join(XAMPP_PATH, "apache_start.bat")

        if os.path.exists(mysql_bat) and os.path.exists(apache_bat):
            subprocess.Popen([mysql_bat], creationflags=subprocess.CREATE_NO_WINDOW)
            subprocess.Popen([apache_bat], creationflags=subprocess.CREATE_NO_WINDOW)
            time.sleep(2)
        else:
            messagebox.showerror("Error", f"No se localizó XAMPP en la ruta: {XAMPP_PATH}")
            self.lbl_status.config(text="Estado: Error en XAMPP", fg="#D32F2F")
            self.btn_start.config(state="normal")
            return

        # 2. Inicialización del entorno virtual y aplicación Flask
        self.lbl_status.config(text="Estado: Arrancando servidor Flask...", fg="#ED6C02")
        if not os.path.exists(VENV_PYTHON):
            messagebox.showerror("Error", f"Entorno virtual no hallado en:\n{VENV_PYTHON}")
            self.lbl_status.config(text="Estado: Error en VENV", fg="#D32F2F")
            self.btn_start.config(state="normal")
            return

        self.flask_process = subprocess.Popen([VENV_PYTHON, RUN_SCRIPT], cwd=PROJECT_PATH)
        time.sleep(2)

        # 3. Apertura del cliente web
        webbrowser.open("http://127.0.0.1:5000/")
        self.lbl_status.config(text="Estado: En ejecución (http://127.0.0.1:5000/)", fg="#2E7D32")
        self.btn_start.config(state="normal")

    def stop_all(self):
        # Finalización del proceso Flask
        if self.flask_process:
            self.flask_process.terminate()
            self.flask_process = None

        # Detención de servicios XAMPP
        mysql_stop = os.path.join(XAMPP_PATH, "mysql_stop.bat")
        apache_stop = os.path.join(XAMPP_PATH, "apache_stop.bat")

        if os.path.exists(mysql_stop) and os.path.exists(apache_stop):
            subprocess.Popen([mysql_stop], creationflags=subprocess.CREATE_NO_WINDOW)
            subprocess.Popen([apache_stop], creationflags=subprocess.CREATE_NO_WINDOW)

        self.lbl_status.config(text="Estado: Detenido", fg="#D32F2F")

if __name__ == "__main__":
    root = tk.Tk()
    app = AppLauncher(root)
    root.mainloop()