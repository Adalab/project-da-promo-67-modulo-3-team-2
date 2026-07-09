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
# SCRIPT PRINCIPAL DE CARGA (ETL)
# =======================================================================

# -----------------------------------------------------------------------
# 1. EXTRACCIÓN (Extract)
# -----------------------------------------------------------------------
print("Cargando datos originales de Recursos Humanos...")
df = pd.read_csv("src/files/hr.csv")


# -----------------------------------------------------------------------
# 2. TRANSFORMACIÓN (Transform)
# -----------------------------------------------------------------------
print("Iniciando la transformación y limpieza de datos...")


# --- Bloque 1: Eliminación de columnas ---
print("Eliminando columnas sin valor de estudio...")

df.drop(columns=['EmployeeCount' , 'Over18', 'StandardHours'], inplace=True)


# --- Bloque 2: Borrado de duplicados ---
print("Borrando duplicados...")

df = df.drop_duplicates(keep='first')


# --- Bloque 3: Limpieza de textos ---
print("Corrigiendo estétitca del texto...")

df['JobRole'] = df['JobRole'].str.strip().str.title()
df['BusinessTravel'] = df['BusinessTravel'].str.replace("_", " ")
df['MaritalStatus'] = df['MaritalStatus'].replace('Marreid', 'Married')


# --- Bloque 4: Gestión de nulos ---
print("Tratando valores nulos con lógica de negocio...")

# Creamos el mapa de JobRole -> Department usando solo las filas donde Department NO sea nulo (.notna())
mapa_jobrole_dept = (
    df[df['Department'].notna()]
    .groupby('JobRole')['Department']
    .agg(lambda x: x.mode()[0])
    .to_dict()
)

# Creamos la máscara para localizar los NaN reales en la columna Department (.isna())
mascara_nan_dept = df['Department'].isna()

# Rellenamos los NaN de Department mapeando el JobRole correspondiente
df.loc[mascara_nan_dept, 'Department'] = df.loc[mascara_nan_dept, 'JobRole'].map(mapa_jobrole_dept)

# Gestión del resto de nulos a través de funciones
print("Pasando el dataset a las funciones de sustitución general...")

df_cat_limpio = fn.sustitucion_nulos_categoricas(df)
df_bool_limpio = fn.sustitucion_nulos_booleanas(df_cat_limpio)
df_limpio = fn.sustitucion_nulos_numericas(df_bool_limpio)


# --- Bloque 5: Corrección de tipos de datos ---
print("Tratando los tipos...")

df_limpio['Age'] = df_limpio['Age'].astype('Int64')
df_limpio['JobSatisfaction'] = df_limpio['JobSatisfaction'].astype('Int64')
df_limpio['TrainingTimesLastYear'] = df_limpio['TrainingTimesLastYear'].astype('Int64')
df_limpio['YearsWithCurrManager'] = df_limpio['YearsWithCurrManager'].astype('Int64')

# Mapeos a booleanos aplicados sobre df_limpio
df_limpio['Attrition'] = df_limpio['Attrition'].map({
    'Yes': True,
    'No': False
}).astype('boolean')

df_limpio['OverTime'] = df_limpio['OverTime'].map({
    'Yes': True, 
    'No': False
}).astype('boolean')


# --- Bloque 6: Preparación de datos para MySQL ---

# Creación de tabla maestra de departamentos, educación y roles
print("Convirtiendo columnas...")

depto_unicos = df_limpio["Department"].unique()

df_departamentos = pd.DataFrame({
    "DepartmentNumber": range(1, len(depto_unicos) + 1),
    "Department": depto_unicos  
})

roles_unicos = df_limpio["JobRole"].unique()

df_roles = pd.DataFrame({
    "JobRoleNumber": range(1, len(roles_unicos) + 1),
    "JobRole": roles_unicos
})

roles_unicos = df_limpio["EducationField"].unique()

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
df_ampliado = pd.merge(df_limpio, df_departamentos, on="Department", how="left")
df_ampliado = pd.merge(df_ampliado, df_roles, on="JobRole", how="left")
df_ampliado = pd.merge(df_ampliado, df_educacion, on="EducationField", how="left")

# Se renombran las columnas de texto en la tabla para distinguir las nuevas columnas
df_departamentos.rename(columns={"Department": "DepartmentName"}, inplace=True)
df_roles.rename(columns={"JobRole": "JobRoleName"}, inplace=True)
df_educacion.rename(columns={"EducationField": "EducationFieldName"}, inplace=True)
df_ampliado = df_ampliado.rename(columns={"Education": "EducationNumber"})


# Se define los subconjuntos de columnas para división de datos en tablas
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


# Se crean los DataFrames independientes
df_personales = df_ampliado[columnas_personales].copy()
df_laborales = df_ampliado[columnas_laborales].copy()
df_encuestas = df_ampliado[columnas_encuestas].copy()
df_financieros = df_ampliado[columnas_financieras].copy()


print("¡Todos los DataFrames han sido divididos y normalizados con éxito!")


# -----------------------------------------------------------------------
# 3. CARGA (Load)
# -----------------------------------------------------------------------

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