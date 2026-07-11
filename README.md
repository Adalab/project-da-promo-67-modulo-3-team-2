# 📊 HR Attrition Analysis

## 📌 Descripción

Este proyecto tiene como objetivo analizar los factores asociados a la rotación de empleados (*Employee Attrition*) mediante técnicas de análisis exploratorio de datos (EDA), estadística descriptiva y análisis de correlación.

A partir de un conjunto de datos de recursos humanos, se estudian variables demográficas, laborales, salariales y de satisfacción con el fin de identificar patrones que puedan ayudar a comprender qué características están relacionadas con el abandono de la empresa.

---

## 🛠️ Tecnologías utilizadas

* Python
* Jupyter Notebook
* Pandas
* NumPy
* Matplotlib
* Seaborn
* SciPy
* Git y GitHub
* MySQL

---

## 📂 Estructura del proyecto

```text
├── files/
│   └── hr_final.csv
│
├── notebooks/
│   ├── 01_Limpieza.ipynb
│   ├── 02_Analisis.ipynb
│   ├── 03_Correlacion.ipynb
│   └── 04_Resultados.ipynb
│
├── README.md
└── requirements.txt
```

### Descripción de los notebooks

**01_Limpieza.ipynb**

* Importación de datos.
* Limpieza y tratamiento de valores.
* Conversión de tipos de datos.
* Preparación del dataset final.

**02_Analisis.ipynb**

* Estadísticos descriptivos.
* Análisis de variables numéricas.
* Análisis de variables categóricas.
* Visualización de distribuciones.
* Detección de patrones y valores atípicos.

**03_Correlacion.ipynb**

* Matriz de correlación.
* Correlaciones entre variables numéricas.
* Interpretación de relaciones entre variables.

**04_Resultados.ipynb**

* Síntesis de los principales hallazgos.
* Interpretación de los resultados obtenidos.
* Conclusiones finales.

Automatización

El proyecto incluye un proceso ETL automatizado desarrollado en Python que permite:

* Extraer los datos originales.
* Aplicar automáticamente las transformaciones y limpieza realizadas durante el EDA.
* Crear la base de datos y las tablas en MySQL.
* Cargar el dataset limpio en la base de datos para su posterior consulta.

---

## ▶️ Cómo ejecutar el proyecto

1. Clonar este repositorio.

```bash
git clone https://github.com/Adalab/project-da-promo-67-modulo-3-team-2.git
```

2. Acceder al directorio del proyecto.

```bash
cd repositorio
```

3. Instalar las dependencias.

```bash
pip install -r requirements.txt
```

4. Abrir Jupyter Notebook.

```bash
jupyter notebook
```

5. Ejecutar los notebooks en orden:

* 01_EDA_transformación_limpieza
* 02_Analisis
* 03_Correlacion
* 04_Resultados

---

## 📈 Funcionalidades

Este proyecto permite:

* Explorar la estructura del conjunto de datos.
* Analizar variables numéricas y categóricas.
* Calcular estadísticas descriptivas.
* Representar gráficamente la distribución de las variables.
* Identificar posibles valores atípicos.
* Estudiar relaciones entre variables mediante correlaciones.
* Obtener conclusiones basadas en evidencia estadística.

---

## 📊 Ejemplo de análisis

Durante el análisis se incluyen:

* Estadísticos descriptivos.
* Histogramas.
* Boxplots.
* Gráficos de barras.
* Matrices de correlación.
* Interpretación de los resultados obtenidos.

---

## 🎯 Aprendizajes

Este proyecto ha permitido poner en práctica:

* Limpieza y preparación de datos.
* Análisis exploratorio (EDA).
* Estadística descriptiva.
* Interpretación de distribuciones.
* Análisis de correlación.
* Visualización de datos.
* Organización de proyectos con Git y GitHub.
* Comunicación de resultados mediante informes técnicos.

---

## 👥 Autoría

Proyecto realizado como parte del Bootcamp de Data Analytics.

Integrantes del equipo:

* Ana Daza
* Ángeles Toro
* Beatriz San José
* Teresa Díaz-Toledo
---

## 📄 Licencia

Proyecto desarrollado con fines educativos.
