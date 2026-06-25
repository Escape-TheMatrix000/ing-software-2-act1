# Definición del Problema y Datos — [Nombre del Proyecto]

> **Instrucción:** Completa cada sección con la información real de tu equipo.
> Los campos en corchetes `[...]` son los que debes reemplazar.

---

## Equipo

| Integrante | Rol | Responsabilidad principal |
|------------|-----|---------------------------|
| [Nombre 1] | Arquitecto de Software | Estructura del repositorio, main.py |
| [Nombre 2] | Ingeniero ETL / Pandas | DataLoader, DataCleaner |
| [Nombre 3] | Especialista Visualización | (preparar para E2) |
| [Nombre 4] | QA / Documentación | Tests, README, docstrings |

---

## Dataset Seleccionado

| Atributo | Valor |
|----------|-------|
| **Nombre** | Ventas Colombia 2022–2024 (Dataset genérico de ejemplo) |
| **Fuente** | Generado localmente con `generar_dataset.py` |
| **URL** | N/A (generado para práctica) |
| **Filas** | 160.500 (con duplicados incluidos) |
| **Columnas** | 12 |
| **Período** | 2022-01-01 – 2024-12-31 |
| **Formato original** | CSV |
| **Tamaño en disco** | ~15 MB |
| **RAM al cargar** | ~85 MB (antes de optimización de tipos) |
| **RAM optimizado** | ~32 MB (después de casteo) |

### Descripción de columnas

| Columna | Tipo original | Tipo optimizado | Descripción | Nulos aprox. |
|---------|--------------|-----------------|-------------|--------------|
| `orden_id` | int64 | int32 | Identificador único de la orden | 0% |
| `fecha` | object | datetime64 | Fecha de la transacción | 0% |
| `cliente_id` | int64 | int16 | ID del cliente (1–30.000) | 0% |
| `ciudad` | object | category | Ciudad de la transacción | 0% |
| `departamento` | object | category | Departamento colombiano | ~8% |
| `canal_venta` | object | category | Canal: Digital/Presencial/Telefónico/Mayorista | 0% |
| `categoria` | object | category | Categoría del producto | 0% |
| `precio_unitario` | float64 | float32 | Precio por unidad en COP | ~5% |
| `cantidad` | int64 | int8 | Unidades vendidas (1–14) | 0% |
| `costo_unitario` | float64 | float32 | Costo del producto en COP | ~6% |
| `descuento_pct` | float64 | float32 | Descuento aplicado (0.0–0.20) | ~5% |
| `estado_orden` | object | category | Estado: Completada/Cancelada/Pendiente/Devuelta | 0% |

---

## Justificación de Selección

### Volumen (Big Data V1)
El dataset supera el mínimo requerido de 100.000 filas con **160.500 registros**.
Esto activa problemas reales de rendimiento: la diferencia entre código O(n) y O(n²)
es medible y visible con este volumen.

### Variedad (Big Data V2)
El dataset incluye variables de:
- **Tipo numérico continuo:** precio_unitario, costo_unitario, descuento_pct
- **Tipo numérico discreto:** cantidad, cliente_id, orden_id
- **Tipo categórico:** ciudad, departamento, canal_venta, categoria, estado_orden
- **Tipo temporal:** fecha (rango de 3 años)
- **Con defectos intencionales:** nulos en 4 columnas + duplicados (~7%)

### Velocidad (Big Data V3)
El pipeline procesa el dataset completo en menos de 10 segundos en hardware
estándar, permitiendo iterar rápidamente durante el desarrollo.

---

## Problema de Negocio

> **Reemplaza esta sección con el dominio de tu proyecto real**

Una empresa de comercio electrónico colombiana necesita entender el comportamiento
de sus ventas entre 2022 y 2024 para optimizar su estrategia de canales y regiones.

---

## Repositorio GitHub

- **URL:** https://github.com/[equipo]/[repositorio]
- **Rama principal:** main
- **Rama de desarrollo:** develop
