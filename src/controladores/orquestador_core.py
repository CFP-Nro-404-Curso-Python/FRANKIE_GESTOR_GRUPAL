import os
import sqlite3
from datetime import datetime
from infraestructura.conexion import ConexionDB



class OrquestadorCore:
    """
    Controlador del Módulo Core.
    Aplica las reglas de negocio y orquesta las acciones entre la Interfaz y la Infraestructura.
    """

    def ejecutar_backup(self) -> str:
        """
        Realiza una copia de seguridad en caliente (Hot Backup) de la base de datos.
        Devuelve un mensaje de éxito o de error para que la Vista lo muestre.
        """
        # 1. Calculamos las rutas relativas para que funcione en cualquier PC.
        ruta_base = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
        ruta_db_origen = os.path.join(ruta_base, 'db', 'frankie_gestor.db')
        carpeta_backups = os.path.join(ruta_base, 'db', 'backups')
        
        # Si la carpeta de backups no existe, la crea automáticamente.
        os.makedirs(carpeta_backups, exist_ok=True)
        
        # 2. Generamos un nombre único con fecha y hora para no pisar backups anteriores.
        fecha_str = datetime.now().strftime("%Y%m%d_%H%M%S")
        nombre_archivo = f'respaldo_frankie_{fecha_str}.db'
        ruta_db_destino = os.path.join(carpeta_backups, nombre_archivo)

        try:
            # 3. Lógica de Hot Backup nativa de SQLite (segura contra bloqueos).
            # Abrimos la conexión activa (Singleton).
            with ConexionDB() as db_origen:
                # Abrimos una conexión temporal solo para crear el archivo de destino
                db_destino = sqlite3.connect(ruta_db_destino)
                
                # La función .backup() copia los datos en caliente, incluso si el sistema está en uso.
                with db_destino:
                    db_origen.backup(db_destino)
                
                db_destino.close()
                
            return f"Backup exitoso.\nArchivo generado: {nombre_archivo}"
            
        except Exception as e:
            # Si algo falla, atrapamos el error y se lo mandamos a la Vista
            return f"Error crítico al generar backup: {e}"



# ===================================================================================
# ⚠️ ATENCIÓN ALICIA Y URIEL (CÓMO DEBEN ARMAR SUS CONTROLADORES):
# ===================================================================================
#
# Cuando creen orquestador_rrhh.py y orquestador_ventas.py, sigan estas reglas:
#
# 1. EL CONTROLADOR ES EL CEREBRO: La Vista (Tkinter) es tonta, solo hace clics.
#    El Repositorio (SQLite) es tonto, solo guarda datos. El Controlador es el único 
#    que piensa. Si hay que calcular un descuento o validar si un CUIT es correcto, 
#    SE HACE ACÁ.
#
# 2. CERO TKINTER: Está totalmente prohibido importar 'tkinter' o 'messagebox'
#    en esta carpeta. Fíjense que esta función devuelve un texto (str). Es la
#    interfaz (ui_panel.py) la que va a agarrar este texto y decidirá si lo muestra 
#    en un cartelito verde o rojo.
#
# 3. FLUJO DE TRABAJO: 
#    Vista captura clic -> Llama al Controlador -> Controlador hace los cálculos 
#    -> Controlador llama al Repositorio para guardar -> Devuelve respuesta a Vista.
# ===================================================================================