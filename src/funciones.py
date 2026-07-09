# =======================================================================
# IMPORTACIONES PARA LAS FUNCIONES
# =======================================================================

# Tratamiento de datos
# -----------------------------------------------------------------------
import pandas as pd 

# Imputación de nulos usando métodos avanzados estadísticos
# -----------------------------------------------------------------------
from sklearn.experimental import enable_iterative_imputer
from sklearn.impute import IterativeImputer

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
# FUNCIONES GESTIÓN DE NULOS
# =======================================================================

# -----------------------------------------------------------------------
# Función para gestión de nulos de las columnas categóricas
# -----------------------------------------------------------------------
def sustitucion_nulos_categoricas(df):
    # Copia del DF para evitar suscribir los datos en el original
    df = df.copy()
    # Selección de las columnas categóricas
    columnas_categoricas = df.select_dtypes(include='object').columns
    # Filtrado de las columnas con nulos
    columnas_con_nulos = [col for col in columnas_categoricas if df[col].isnull().sum() > 0]
    for columna in columnas_con_nulos:
        porcentaje_nulos = df[columna].isnull().sum()/df.shape[0]*100
        print(f"{columna}. Nulos antes = {df[columna].isnull().sum()} ({porcentaje_nulos:.1f}%)")

        # Búsqueda del valor dominante en la columna
        lista_valores = df[columna].value_counts()/df.shape[0]*100
        dominante = lista_valores.iloc[0]

        # Acción para valores por encima de 25% se imputa con la moda
        if porcentaje_nulos > 25:
            df[columna] = df[columna].fillna(lista_valores.index[0])
            print(f"{columna}. Nulos después = {df[columna].isnull().sum()}")

        # Por debajo de 25% se comprueba la dominancia
        else:
            print(f"{columna}. Dominante = {dominante:.1f}%")
            
            # Si la categoría dominante es inferior al 75% creamos una nueva categoría
            if dominante <= 75:
                df[columna] = df[columna].fillna('unknown')
                print(f"{columna}. Nulos después = {df[columna].isnull().sum()}")

            # Si la categoría dominante es superior al 75% se imputa con la moda    
            else:
                df[columna] = df[columna].fillna(lista_valores.index[0])
                print(f"{columna}. Nulos después = {df[columna].isnull().sum()}")

    return df


# -----------------------------------------------------------------------
# Función para gestión de nulos de las columnas booleanas
# -----------------------------------------------------------------------
def sustitucion_nulos_booleanas(df):
    # Copia del DF para evitar suscribir los datos en el original
    df = df.copy()
    # Selección de las columnas booleanas
    columnas_bool = df.select_dtypes(include='boolean').columns
    # Filtrado de columnas con nulos
    columnas_con_nulos = [col for col in columnas_bool if df[col].isnull().sum() > 0]

    for columna in columnas_con_nulos:
        moda = df[columna].mode()[0]
        print(f"{columna}: nulos antes = {df[columna].isnull().sum()}. Se sustituye con la moda: ({moda})")
        # Imputación con la moda
        df[columna] = df[columna].fillna(moda)

    return df


# -----------------------------------------------------------------------
# Función para gestión de nulos de las columnas numéricas
# -----------------------------------------------------------------------
def sustitucion_nulos_numericas(df):
    # Copia del DF para evitar suscribir los datos en el original
    df = df.copy()
    # Selección de las columnas numéricas
    columnas_numericas = df.select_dtypes(include=['number']).columns
    # Filtrado de columnas con nulos
    columnas_con_nulos = [col for col in columnas_numericas if df[col].isnull().sum() > 0]
    # Entrenamiento del imputador
    imputador = IterativeImputer(max_iter= 10, random_state= 42)
    valores_imputados = imputador.fit_transform(df[columnas_numericas])
    df_temp = pd.DataFrame(valores_imputados, columns=columnas_numericas, index=df.index)
    
    for columna in columnas_con_nulos:
        porcentaje_nulos = df[columna].isnull().sum()/df.shape[0]*100
        print(f"{columna}. Nulos antes = {df[columna].isnull().sum()} ({porcentaje_nulos:.1f}%)")

        # En nulos superiores a un 25% se sustituye con valores del imputador
        if porcentaje_nulos > 25:
            if str(df[columna].dtype) == 'Int64':
                df[columna] = round(df_temp[columna]).astype('Int64')
                print(f"{columna}. Nulos después = {df[columna].isnull().sum()}")
            else:
                df[columna] = df_temp[columna]
                print(f"{columna}. Nulos después = {df[columna].isnull().sum()}")

        # En nulos inferiores a un 25% se considera si hay sesgo entre media y mediana
        else:
            sesgo = df[columna].skew()
            mediana = df[columna].median()
            media = df[columna].mean() 
            print(f"{columna}. Sesgo = {sesgo:.2f}")

            # Para sesgos superiores a un 0.5 se imputa con la mediana
            if abs(sesgo) > 0.5:
                df[columna] = df[columna].fillna(round(mediana))
                print(f"{columna}. Nulos después = {df[columna].isnull().sum()}")
                
            # Para sesgos inferiores a un 0.5 se imputa con la media
            else:
                df[columna] = df[columna].fillna(round(media))
                print(f"{columna}. Nulos después = {df[columna].isnull().sum()}")

    return df


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
# FUNCIONES MySQL
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