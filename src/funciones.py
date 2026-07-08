# =======================================================================
# IMPORTACIONES PARA LAS FUNCIONES
# =======================================================================

# Conexión con MySQL 
# -----------------------------------------------------------------------
import mysql.connector
from mysql.connector import Error

# Variables del entorno
# -----------------------------------------------------------------------
import os 
from dotenv import load_dotenv
load_dotenv()
password_sql = os.getenv("PASS_SQL")



# =======================================================================
# DECORADOR: Envolvemos las funciones
# =======================================================================

def requiere_conexion(funcion_original):
    def envoltura(conexion, *args, **kwargs):
        if conexion is None:
            print(f"Error: No hay conexión activa para ejecutar '{funcion_original.__name__}'")
            return None
        return funcion_original(conexion, *args, **kwargs)
    return envoltura



# =======================================================================
# FUNCIONES
# =======================================================================

# -----------------------------------------------------------------------
# Establece una conexión con el servidor MySQL local
# -----------------------------------------------------------------------
def conexion_mysql():

    try:
        # Usando el conector de la librería
        conexion = mysql.connector.connect(
            host = "127.0.0.1", 
            user= "root",
            password = password_sql,  # Usa la variable de contraseña del entorno local, no añadida en GitHub
            # Nota: Estamos creando una base de datos nueva, por lo que no se incluye
        )
        print("Conexión exitosa")
        return conexion
    
    # Maneja cualquier error relacionado con la base de datos que ocurra durante la conexión
    except Error as e:
        print (f"Ha ocurrido un error: {e}")


# -----------------------------------------------------------------------
# Crea una base de datos nueva si no existe
# -----------------------------------------------------------------------
@requiere_conexion
def crear_base_datos(conexion, nombre_bd):
    
    try:
        # Abre el cursor de forma segura usando un administrador de contexto para asegurar el cierre automático
        with conexion.cursor() as cursor:
            consulta = f"CREATE DATABASE IF NOT EXISTS {nombre_bd}"
            # Ejecuta la consulta de creación de la base de datos
            cursor.execute(consulta)
            print ("Consulta exitosa")

    # Captura cualquier error de ejecución de SQL
    except Error as e:
        print (f"Error al crear la base de datos: {e}")

# -----------------------------------------------------------------------
# Función para borrar la base de datos si es necesario
# -----------------------------------------------------------------------
@requiere_conexion
def borrar_base_datos(conexion, nombre_bd):

    try:
        # Solicita confirmación a usuario
        respuesta_usuario = input (f"La base de datos '{nombre_bd}' será borrada, ¿Estás seguro? (S/N):").upper()
        # Actúa solo en caso positivo
        if respuesta_usuario == "S":
            with conexion.cursor() as cursor:
                cursor.execute(f"DROP DATABASE IF EXISTS {nombre_bd}")
                conexion.commit()
                print(f"Base de datos {nombre_bd} eliminada correctamente")
        else:
            # Cualquier otra opción cancela el borrado
            print ("Operación cancelada")
    
    # Captura posibles errores en MYSQL
    except Error as e:
        print(f"Error al eliminar la base de datos: {e}")


# -----------------------------------------------------------------------
# Crea una tabla dentro de la base de datos designada si no existe
# -----------------------------------------------------------------------
@requiere_conexion
def crear_tabla_generica(conexion, nombre_bd, nombre_tabla, esquema_tabla):
    
    try:
        # Abre el cursor de forma segura usando un administrador de contexto para asegurar el cierre automático
        with conexion.cursor() as cursor:
            cursor.execute(f"USE {nombre_bd};")
            # Define la consulta SQL para la tabla genérica
            consulta = f''' CREATE TABLE IF NOT EXISTS {nombre_tabla} ({esquema_tabla});'''
            # Ejecuta la consulta de creación de la tabla
            cursor.execute(consulta)
            print ("Consulta de creación exitosa")
    
    # Captura cualquier error de ejecución de SQL
    except Error as e:
        print (f"Error al crear la tabla: {e}")


# -----------------------------------------------------------------------
# Función que puede borrar tablas si es necesario
# -----------------------------------------------------------------------
@requiere_conexion
def borrar_tabla(conexion, nombre_bd, nombre_tabla):

    try:

        # Comprueba si el usuario confirmó la operación
        respuesta_usuario = input(f"La tabla '{nombre_tabla}' será eliminada. ¿Estás seguro? (S/N):").upper()
        if respuesta_usuario == "S":
            # Abre el cursor de forma segura usando un administrador de contexto para asegurar el cierre automático
            with conexion.cursor() as cursor:
                # Selecciona la base de datos pasada como argumento
                cursor.execute(f"USE {nombre_bd};")
                # Define la consulta SQL para eliminar la tabla si existe
                consulta = f'''DROP TABLE IF EXISTS {nombre_tabla}'''
                # Ejecuta la consulta de eliminación de la tabla
                cursor.execute(consulta)
                conexion.commit()
                print("Tabla eliminada exitosamente")
        else: 
            print("Operación cancelada")

    # Captura cualquier error de ejecución de SQL
    except Error as e:
        print(f"Error al eliminar la tabla: {e}")


# -----------------------------------------------------------------------
# Inserta los datos de un DataFrame limpio en la tabla correspondiente
# -----------------------------------------------------------------------
@requiere_conexion
def insercion_datos(conexion, nombre_bd, nombre_tabla, df):
    
    try:
        # Convierte las filas del DataFrame a una lista de tuplas
        df_valores = df.values.tolist()
        
        # Generación dinámica de la consulta SQL basada en las columnas del DataFrame
        columnas = ", ".join(df.columns)
        marcadores = ", ".join(["%s"] * len(df.columns))
        
        consulta = f"INSERT INTO {nombre_tabla} ({columnas}) VALUES ({marcadores})"

        with conexion.cursor() as cursor:
            cursor.execute(f"USE {nombre_bd};")
            # Insertamos todos los registros
            cursor.executemany(consulta, df_valores)
            conexion.commit()
            print(f"Inserción exitosa: {len(df_valores)} registros añadidos en la tabla '{nombre_tabla}'.")

    # Captura errores de ejecución de SQL        
    except Error as e:
        print(f"Error al insertar datos en la tabla {nombre_tabla}: {e}")