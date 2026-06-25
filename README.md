# Proyecto Big Data — Ventas Colombia 2022–2024
### Entregable 1 | Ingeniería de Software II | Pipeline ETL

> Pipeline de ingesta, limpieza y auditoría de datos de ventas colombianas.
> Procesa 160.500 registros, resuelve defectos de calidad y reduce el uso
> de RAM en ~60% mediante casteo optimizado de tipos.

---

## Tabla de Contenidos
1. [Equipo](#equipo)
2. [Descripción del Proyecto](#descripción-del-proyecto)
3. [Estructura del Repositorio](#estructura-del-repositorio)
4. [Requisitos de Infraestructura](#requisitos-de-infraestructura)
5. [Instalación y Ejecución](#instalación-y-ejecución)
6. [Dataset](#dataset)
7. [Arquitectura del Sistema](#arquitectura-del-sistema)
8. [Resultados del Pipeline](#resultados-del-pipeline)

---

## Equipo

| Nombre | Rol |
|--------|-----|
| [Nombre 1] | Arquitecto de Software |
| [Nombre 2] | Ingeniero ETL / Pandas |
| [Nombre 3] | Especialista Visualización |
| [Nombre 4] | QA / Documentación |

---

## Descripción del Proyecto

Este proyecto implementa el **Entregable 1** del curso, que consiste en:

- Cargar un dataset real de más de 100.000 filas desde múltiples formatos (CSV, Parquet, JSON)
- Ejecutar una auditoría técnica de calidad (nulos, duplicados, tipos de dato)
- Limpiar el dataset aplicando estrategias justificadas por tipo de columna
- Optimizar el uso de RAM mediante casteo de tipos de dato
- Documentar todas las operaciones con logging profesional

---

## Estructura del Repositorio

```
proyecto-bigdata/
│
├── datos/
│   ├── crudos/                    ← Archivos originales (no modificar)
│   │   └── ventas_colombia_2022_2024.csv
│   └── procesados/                ← Salida del pipeline
│
├── src/
│   ├── __init__.py
│   ├── etl/
│   │   ├── __init__.py
│   │   ├── cargador.py            ← DataLoader: carga CSV/JSON/Parquet
│   │   └── limpiador.py           ← DataCleaner: limpia y optimiza RAM
│   ├── analisis/
│   │   └── __init__.py            ← (Módulos del E2 van aquí)
│   ├── viz/
│   │   └── __init__.py            ← (Módulos del E2 y E3 van aquí)
│   └── utils/
│       ├── __init__.py
│       └── performance.py         ← PipelineTimer: mide latencia
│
├── notebooks/
│   └── 01_exploracion.ipynb       ← EDA exploratoria (no es producción)
│
├── output/                        ← Resultados generados por el pipeline
├── logs/                          ← Registros de ejecución
├── docs/
│   ├── definicion_problema.md
│   └── formulacion_analitica.md
├── tests/
│
├── main.py                        ← EJECUTAR ESTE ARCHIVO
├── generar_dataset.py             ← Genera el CSV de ejemplo (solo una vez)
├── requirements.txt
└── README.md
```

---

## Requisitos de Infraestructura

### Hardware mínimo
- CPU: 2 núcleos
- RAM: 4 GB (el dataset ocupa ~32 MB optimizado)
- Almacenamiento: 500 MB libres

### Software
- Python: **3.10 o superior** (requerido para `X | Y` en type hints)
- pip: 22.0 o superior
- Git: 2.30 o superior

---

## Instalación y Ejecución

### Opción A — Entorno local

```bash
# 1. Clonar el repositorio
git clone https://github.com/[equipo]/[repo].git
cd [repo]

# 2. Crear entorno virtual (recomendado para aislar dependencias)
python -m venv .venv

# Activar el entorno virtual:
source .venv/bin/activate       # Linux / macOS
.venv\Scripts\activate          # Windows PowerShell

# 3. Instalar dependencias
pip install -r requirements.txt

# 4. Generar el dataset de ejemplo (solo la primera vez)
python generar_dataset.py

# 5. Ejecutar el pipeline
python main.py
```

### Opción B — Google Colab

```python
# Celda 1: Clonar e instalar
!git clone https://github.com/[equipo]/[repo].git
%cd [repo]
!pip install -r requirements.txt -q

# Celda 2: Generar el dataset
!python generar_dataset.py

# Celda 3: Ejecutar el pipeline
!python main.py
```

### Opción C — GitHub Codespaces

```bash
# El entorno se configura automáticamente.
# Solo ejecutar en la terminal integrada:
pip install -r requirements.txt
python generar_dataset.py
python main.py
```

### Verificar que funciona correctamente

El pipeline es exitoso si:
1. La consola muestra `✅ PIPELINE ETL COMPLETADO`
2. Existen archivos en `output/` (ventas_limpio.csv, reporte_ejecucion.json)
3. El archivo `logs/pipeline.log` contiene entradas INFO sin errores

---

## Dataset

| Atributo | Valor |
|----------|-------|
| Nombre | ventas_colombia_2022_2024.csv |
| Origen | Generado con `generar_dataset.py` para fines académicos |
| Filas | 160.500 (con duplicados intencionales) |
| Columnas | 12 |
| Período | 2022-01-01 – 2024-12-31 |
| Tamaño en disco | ~15 MB |
| RAM antes de optimización | ~85 MB |
| RAM después de optimización | ~32 MB |

**Defectos intencionales incluidos:**
- ~10.500 filas duplicadas exactas
- ~7.500 nulos en `precio_unitario`
- ~12.000 nulos en `departamento`
- ~9.000 nulos en `costo_unitario`
- ~7.500 nulos en `descuento_pct`

---

## Arquitectura del Sistema

```
[CSV en disco]
     │
     │  DataLoader.cargar()          ← Extracción
     ▼
[DataFrame crudo en RAM]
     │
     │  DataLoader.diagnosticar()    ← Auditoría
     ▼
[Reporte de calidad]
     │
     │  DataCleaner.limpiar()        ← Transformación
     │  → drop_duplicates()
     │  → fillna(mediana / 'Sin Datos')
     │  → optimizar_memoria()
     ▼
[DataFrame limpio y optimizado en RAM]
     │
     │  df.to_csv() / df.to_parquet()   ← Carga
     ▼
[output/ventas_limpio.csv + .parquet]
```

**Principio de diseño:** Cada módulo tiene una sola responsabilidad.
`DataLoader` solo carga. `DataCleaner` solo limpia. `main.py` solo orquesta.

---

## Resultados del Pipeline

| Métrica | Valor |
|---------|-------|
| Filas entrada | 160.500 |
| Filas limpias | ~149.000 |
| Nulos resueltos | ~36.000 |
| Reducción de RAM | ~60% |
| Latencia total | < 10 segundos |

Ver `output/reporte_ejecucion.json` para el reporte completo.
