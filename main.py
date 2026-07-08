# Tratamiento de datos
# -----------------------------------------------------------------------
import pandas as pd 

# Conexión con archivo de funciones 
# -----------------------------------------------------------------------
import src.funciones as fn
import src.bd as bd

# Conexión con MySQL 
# -----------------------------------------------------------------------

# Variables del entorno
# -----------------------------------------------------------------------
import os 
from dotenv import load_dotenv
load_dotenv()
password_sql = os.getenv("PASS_SQL")


# =======================================================================
# SCRIPT PRINCIPAL DE CARGA (ETL - LOAD)
# =======================================================================

# -----------------------------------------------------------------------
# Carga inicial y división de datos
# -----------------------------------------------------------------------

print("Cargando datos originales de Recursos Humanos...")
df = pd.read_csv("src/files/hr_final.csv")

# Creación de tabla maestra de departamentos, educación y roles
# -----------------------------------------------------------------------
print("Convirtiendo columnas...")

depto_unicos = df["Department"].unique()

df_departamentos = pd.DataFrame({
    "DepartmentNumber": range(1, len(depto_unicos) + 1),
    "Department": depto_unicos  
})

roles_unicos = df["JobRole"].unique()

df_roles = pd.DataFrame({
    "JobRoleNumber": range(1, len(roles_unicos) + 1),
    "JobRole": roles_unicos
})

roles_unicos = df["EducationField"].unique()

df_educacion = pd.DataFrame({
    "EducationFieldNumber": range(1, len(roles_unicos) + 1),
    "EducationField": roles_unicos
})


# Diccionario con el significado de cada nivel educativo para creación de tabla
mapa_educacion = {
    1: 'Below College',
    2: 'College',
    3: 'Bachelor',
    4: 'Master',
    5: 'Doctor'
}

# Se define nuevo DF para insertar en MySQL
df_nivel_educativo = pd.DataFrame({
    "EducationNumber": list(mapa_educacion.keys()),
    "EducationName": list(mapa_educacion.values())
})

# Se realiza merge para que el df original tenga una nueva columna llamada 'DepartmentNumber', 'JobRoleNumber'
df_ampliado = pd.merge(df, df_departamentos, on="Department", how="left")
df_ampliado = pd.merge(df_ampliado, df_roles, on="JobRole", how="left")
df_ampliado = pd.merge(df_ampliado, df_educacion, on="EducationField", how="left")

# Se renombran las columnas de texto en la tabla para distinguir las nuevas columnas
df_departamentos.rename(columns={"Department": "DepartmentName"}, inplace=True)
df_roles.rename(columns={"JobRole": "JobRoleName"}, inplace=True)
df_educacion.rename(columns={"EducationField": "EducationFieldName"}, inplace=True)
df_ampliado = df_ampliado.rename(columns={"Education": "EducationNumber"})


# Se define los subconjuntos de columnas para división de datos en tablas
# -----------------------------------------------------------------------
print("Dividiendo columnas...")

columnas_personales = [
    "EmployeeNumber", "EducationNumber", "EducationFieldNumber", "Attrition", "Age", "Gender", 
    "MaritalStatus", "DistanceFromHome"]
columnas_laborales = [
    "EmployeeNumber", "DepartmentNumber", "JobRoleNumber", "JobLevel", "OverTime",
    "BusinessTravel", "TotalWorkingYears", "YearsAtCompany", "YearsInCurrentRole", 
    "YearsSinceLastPromotion", "YearsWithCurrManager", "NumCompaniesWorked", 
    "TrainingTimesLastYear"]
columnas_encuestas = [
    "EmployeeNumber", "EnvironmentSatisfaction", "JobInvolvement", "JobSatisfaction", 
    "RelationshipSatisfaction", "WorkLifeBalance"]
columnas_financieras = [
    "EmployeeNumber", "MonthlyIncome", "MonthlyRate", "DailyRate", 
    "HourlyRate", "PercentSalaryHike", "StockOptionLevel", "PerformanceRating"]

# Creamos los DataFrames independientes
# -----------------------------------------------------------------------
df_personales = df_ampliado[columnas_personales].copy()
df_laborales = df_ampliado[columnas_laborales].copy()
df_encuestas = df_ampliado[columnas_encuestas].copy()
df_financieros = df_ampliado[columnas_financieras].copy()


print("¡Todos los DataFrames han sido divididos y normalizados con éxito!")


# =======================================================================
# PIPELINE DE CARGA EN MYSQL 
# =======================================================================

print("\n--- Iniciando proceso de carga en MySQL ---")

# Paso 1: Establecer la conexión con el servidor local
conexion = fn.conexion_mysql()

# Paso 2: Crear la Base de Datos si no existe
fn.crear_base_datos(conexion, bd.NOMBRE_BD)

# Paso 3: Crear las tablas en el orden correcto de dependencias
print("\nCreando estructuras de tablas...")
# A) Primero las tablas maestras independientes
fn.crear_tabla_generica(conexion, bd.NOMBRE_BD, bd.TABLA_DEPARTAMENTOS, bd.ESQUEMA_DEPARTAMENTOS)
fn.crear_tabla_generica(conexion, bd.NOMBRE_BD, bd.TABLA_ROLES, bd.ESQUEMA_ROLES)
fn.crear_tabla_generica(conexion, bd.NOMBRE_BD, bd.TABLA_CAMPOS_EDUCATIVOS, bd.ESQUEMA_CAMPOS_EDUCATIVOS)
fn.crear_tabla_generica(conexion, bd.NOMBRE_BD, bd.TABLA_NIVEL_EDUCATIVO, bd.ESQUEMA_EDUCATIVO)
fn.crear_tabla_generica(conexion, bd.NOMBRE_BD, bd.TABLA_PERSONALES, bd.ESQUEMA_PERSONALES)

# B) Después las tablas hijas que llevan las Claves Foráneas
fn.crear_tabla_generica(conexion, bd.NOMBRE_BD, bd.TABLA_LABORALES, bd.ESQUEMA_LABORALES)
fn.crear_tabla_generica(conexion, bd.NOMBRE_BD, bd.TABLA_ENCUESTAS, bd.ESQUEMA_ENCUESTAS)
fn.crear_tabla_generica(conexion, bd.NOMBRE_BD, bd.TABLA_FINANCIEROS, bd.ESQUEMA_FINANCIEROS)


# Paso 4: Inserción de los datos desde los DataFrames limpios
print("\nVolcando datos en las tablas correspondientes...")
# A) Insertamos primero en las tablas maestras
fn.insercion_datos(conexion, bd.NOMBRE_BD, bd.TABLA_DEPARTAMENTOS, df_departamentos)
fn.insercion_datos(conexion, bd.NOMBRE_BD, bd.TABLA_ROLES, df_roles)
fn.insercion_datos(conexion, bd.NOMBRE_BD, bd.TABLA_CAMPOS_EDUCATIVOS, df_educacion)
fn.insercion_datos(conexion, bd.NOMBRE_BD, bd.TABLA_NIVEL_EDUCATIVO, df_nivel_educativo)
fn.insercion_datos(conexion, bd.NOMBRE_BD, bd.TABLA_PERSONALES, df_personales)


# B) Finalmente insertamos en las tablas dependientes
fn.insercion_datos(conexion, bd.NOMBRE_BD, bd.TABLA_LABORALES, df_laborales)
fn.insercion_datos(conexion, bd.NOMBRE_BD, bd.TABLA_ENCUESTAS, df_encuestas)
fn.insercion_datos(conexion, bd.NOMBRE_BD, bd.TABLA_FINANCIEROS, df_financieros)

print("\n--- ¡Proceso de carga finalizado con éxito! La base de datos ha sido completada. ---")