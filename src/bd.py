# =======================================================================
# CONFIGURACIÓN Y ESQUEMAS DE LA BASE DE DATOS
# =======================================================================

NOMBRE_BD = "hr_analytics"


# TABLA MAESTRA: DEPARTAMENTOS
# -----------------------------------------------------------------------
TABLA_DEPARTAMENTOS = "departamentos"
ESQUEMA_DEPARTAMENTOS = '''
    DepartmentNumber INT PRIMARY KEY,
    DepartmentName VARCHAR(100) NOT NULL
'''

# TABLA MAESTRA: ROLES
# -----------------------------------------------------------------------
TABLA_ROLES = "roles"
ESQUEMA_ROLES = '''
    JobRoleNumber INT PRIMARY KEY,
    JobRoleName VARCHAR(100) NOT NULL
'''

# TABLA MAESTRA: CAMPOS EDUCATIVOS
# -----------------------------------------------------------------------
TABLA_CAMPOS_EDUCATIVOS = "campos_educativos"
ESQUEMA_CAMPOS_EDUCATIVOS = '''
    EducationFieldNumber INT PRIMARY KEY,
    EducationFieldName VARCHAR(100) NOT NULL
'''

# TABLA MAESTRA: NIVEL EDUCATIVO
# -----------------------------------------------------------------------
TABLA_NIVEL_EDUCATIVO= "niveles_educacion"
ESQUEMA_EDUCATIVO = '''
    EducationNumber INT PRIMARY KEY,
    EducationName VARCHAR(50) NOT NULL
'''

# TABLA MADRE: EMPLEADOS (DATOS PERSONALES)
# -----------------------------------------------------------------------
TABLA_PERSONALES = "empleados_personales"
ESQUEMA_PERSONALES = '''
    EmployeeNumber INT PRIMARY KEY,
    EducationNumber INT,
    EducationFieldNumber INT,
    Attrition BOOLEAN,
    Age INT,
    Gender VARCHAR(20),
    MaritalStatus VARCHAR(20),
    DistanceFromHome INT,
    FOREIGN KEY (EducationFieldNumber) REFERENCES campos_educativos(EducationFieldNumber),
    FOREIGN KEY (EducationNumber) REFERENCES niveles_educacion(EducationNumber)
'''

# 4. TABLA HIJA: DATOS LABORALES
# -----------------------------------------------------------------------
TABLA_LABORALES = "empleados_laborales"
ESQUEMA_LABORALES = '''
    EmployeeNumber INT PRIMARY KEY,
    DepartmentNumber INT,
    JobRoleNumber INT,
    JobLevel INT,
    OverTime BOOLEAN,
    BusinessTravel VARCHAR(40),
    TotalWorkingYears INT,
    YearsAtCompany INT,
    YearsInCurrentRole INT,
    YearsSinceLastPromotion INT,
    YearsWithCurrManager INT,
    NumCompaniesWorked INT,
    TrainingTimesLastYear INT,
    FOREIGN KEY (EmployeeNumber) REFERENCES empleados_personales(EmployeeNumber) ON DELETE CASCADE,
    FOREIGN KEY (DepartmentNumber) REFERENCES departamentos(DepartmentNumber),
    FOREIGN KEY (JobRoleNumber) REFERENCES roles(JobRoleNumber)
'''

# 5. TABLA HIJA: ENCUESTAS Y SATISFACCIÓN
# -----------------------------------------------------------------------
TABLA_ENCUESTAS = "empleados_encuestas"
ESQUEMA_ENCUESTAS = '''
    EmployeeNumber INT PRIMARY KEY,
    EnvironmentSatisfaction INT,
    JobInvolvement INT,
    JobSatisfaction INT,
    RelationshipSatisfaction INT,
    WorkLifeBalance INT,
    FOREIGN KEY (EmployeeNumber) REFERENCES empleados_personales(EmployeeNumber) ON DELETE CASCADE
'''

# 6. TABLA HIJA: DATOS FINANCIEROS Y RENDIMIENTO
# -----------------------------------------------------------------------
TABLA_FINANCIEROS = "empleados_financieros"
ESQUEMA_FINANCIEROS = '''
    EmployeeNumber INT PRIMARY KEY,
    MonthlyIncome DECIMAL(10,2),
    MonthlyRate INT,
    DailyRate INT,
    HourlyRate INT,
    PercentSalaryHike INT,
    StockOptionLevel INT,
    PerformanceRating INT,
    FOREIGN KEY (EmployeeNumber) REFERENCES empleados_personales(EmployeeNumber) ON DELETE CASCADE
'''