# Formulación Analítica — [Nombre del Proyecto]

> **Instrucción:** Completa con las hipótesis reales de tu equipo.
> Cada hipótesis debe tener métrica, segmento y umbral numérico.

---

## Dominio del Problema

Comercio electrónico / Ventas minoristas Colombia

---

## Hipótesis 1

**Enunciado:** El canal Digital tiene un ticket promedio al menos 20% superior
al canal Presencial en ciudades de más de 500.000 habitantes.

**Métrica clave:** Ticket promedio (precio_unitario × cantidad)

**Variable dependiente:** `precio_unitario * cantidad`

**Variable de segmentación:** `canal_venta`, `ciudad`

**Umbral de validación:** Diferencia ≥ 20%

**Columnas del dataset:** `precio_unitario`, `cantidad`, `canal_venta`, `ciudad`

---

## Hipótesis 2

**Enunciado:** El departamento de Antioquia concentra más del 15% del volumen
total de ventas de la categoría Electrónica.

**Métrica clave:** Participación porcentual en ventas de Electrónica

**Variable dependiente:** `orden_id` (conteo)

**Variable de segmentación:** `departamento`, `categoria`

**Umbral de validación:** Participación ≥ 15%

**Columnas del dataset:** `departamento`, `categoria`, `orden_id`

---

## Hipótesis 3

**Enunciado:** Las órdenes del cuarto trimestre (oct–dic) tienen una tasa de
cancelación superior al promedio anual en más de 5 puntos porcentuales.

**Métrica clave:** Tasa de cancelación (% de órdenes con estado "Cancelada")

**Variable dependiente:** `estado_orden`

**Variable de segmentación:** `fecha` (mes → trimestre)

**Umbral de validación:** Diferencia ≥ 5 puntos porcentuales

**Columnas del dataset:** `fecha`, `estado_orden`

---

## Caso de Uso Analítico Principal

**Actor:** Gerente Comercial

**Objetivo:** Identificar los canales y regiones con mayor potencial de crecimiento

**Flujo principal:**
1. Gerente ejecuta: `python main.py`
2. Sistema carga 160.500 registros desde `datos/crudos/`
3. Sistema limpia y valida la calidad de datos
4. Sistema calcula ticket promedio por canal y ciudad
5. Sistema calcula participación por departamento y categoría
6. Sistema calcula tasa de cancelación por trimestre
7. Sistema guarda resultados en `output/`
8. Gerente interpreta los resultados para ajustar estrategia comercial

**Postcondición:** Archivos limpios disponibles en `output/` para análisis del E2
