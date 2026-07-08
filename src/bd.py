# =======================================================================
# CONFIGURACIÓN Y ESQUEMAS DE LA BASE DE DATOS
# =======================================================================

NOMBRE_BD = "hr_analytics"


# TABLA MAESTRA: DEPARTAMENTOS
# -----------------------------------------------------------------------
TABLA_DEPARTAMENTOS = "Departamentos"
ESQUEMA_DEPARTAMENTOS = '''
    DepartmentNumber INT PRIMARY KEY,
    DepartmentName VARCHAR(100) NOT NULL
'''

# TABLA MAESTRA: ROLES
# -----------------------------------------------------------------------
TABLA_ROLES = "Roles"
ESQUEMA_ROLES = '''
    JobRoleNumber INT PRIMARY KEY,
    JobRoleName VARCHAR(100) NOT NULL
'''

# TABLA MADRE: EMPLEADOS (DATOS PERSONALES)
# -----------------------------------------------------------------------
TABLA_PERSONALES = "empleados_personales"
ESQUEMA_PERSONALES = '''
    EmployeeNumber INT PRIMARY KEY,
    Age INT,
    Gender VARCHAR(20),
    MaritalStatus VARCHAR(20),
    Education INT,
    EducationField VARCHAR(50),
    DistanceFromHome INT
'''

# 4. TABLA HIJA: DATOS LABORALES
# -----------------------------------------------------------------------
TABLA_LABORALES = "empleados_laborales"
ESQUEMA_LABORALES = '''
    EmployeeNumber INT PRIMARY KEY,
    DepartmentNumber INT,
    JobRoleNumber INT,
    JobLevel INT,
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
    OverTime VARCHAR(10),
    FOREIGN KEY (EmployeeNumber) REFERENCES empleados_personales(EmployeeNumber) ON DELETE CASCADE
'''

# 6. TABLA HIJA: DATOS FINANCIEROS Y RENDIMIENTO
# -----------------------------------------------------------------------
TABLA_FINANCIEROS = "empleados_financieros"
ESQUEMA_FINANCIEROS = '''
    EmployeeNumber INT PRIMARY KEY,
    Attrition VARCHAR(10),
    MonthlyIncome INT,
    MonthlyRate INT,
    DailyRate INT,
    HourlyRate INT,
    PercentSalaryHike INT,
    StockOptionLevel INT,
    PerformanceRating INT,
    FOREIGN KEY (EmployeeNumber) REFERENCES empleados_personales(EmployeeNumber) ON DELETE CASCADE
'''