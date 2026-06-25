"""
generar_dataset.py
==================
Script auxiliar para generar el dataset genérico de ejemplo.
Ejecutar UNA SOLA VEZ para crear el archivo CSV de práctica.

    python generar_dataset.py

Genera: datos/crudos/ventas_colombia_2022_2024.csv
  - 150.000 filas de transacciones de ventas
  - 12 columnas con variedad de tipos
  - ~8% duplicados, ~12% nulos en salario, ~10% nulos en departamento
  - Datos realistas de ciudades colombianas
"""

import pandas as pd
import numpy as np
import os

def main():
    np.random.seed(42)
    N = 150_000

    print("Generando dataset de ejemplo (150.000 filas)...")

    # ── Variables de dominio ──────────────────────────────────────────────────
    ciudades = [
        "Bogotá", "Medellín", "Cali", "Barranquilla", "Bucaramanga",
        "Cartagena", "Cúcuta", "Manizales", "Pereira", "Santa Marta"
    ]
    departamentos = [
        "Cundinamarca", "Antioquia", "Valle del Cauca", "Atlántico",
        "Santander", "Bolívar", "Norte de Santander", "Caldas",
        "Risaralda", "Magdalena"
    ]
    canales = ["Digital", "Presencial", "Telefónico", "Mayorista"]
    categorias = ["Electrónica", "Ropa y Calzado", "Alimentos", "Hogar", "Salud"]
    estados = ["Completada", "Cancelada", "Pendiente", "Devuelta"]

    # ── Crear pesos para distribución realista ────────────────────────────────
    pesos_ciudad = [0.25, 0.18, 0.14, 0.10, 0.07,
                    0.07, 0.06, 0.05, 0.05, 0.03]
    pesos_canal  = [0.40, 0.32, 0.18, 0.10]

    # ── Fechas continuas 2022–2024 ────────────────────────────────────────────
    fechas_inicio = pd.Timestamp("2022-01-01")
    fechas_fin    = pd.Timestamp("2024-12-31")
    dias_total    = (fechas_fin - fechas_inicio).days
    fechas = fechas_inicio + pd.to_timedelta(
        np.random.randint(0, dias_total, N), unit="D"
    )

    # ── Construir DataFrame base ──────────────────────────────────────────────
    ciudad_array = np.random.choice(ciudades, N, p=pesos_ciudad)
    # Mapear ciudad → departamento consistentemente
    mapa_cd = dict(zip(ciudades, departamentos))
    dep_array = np.array([mapa_cd[c] for c in ciudad_array])

    df = pd.DataFrame({
        "orden_id":       range(100001, 100001 + N),
        "fecha":          fechas,
        "cliente_id":     np.random.randint(1, 30001, N),
        "ciudad":         ciudad_array,
        "departamento":   dep_array,
        "canal_venta":    np.random.choice(canales, N, p=pesos_canal),
        "categoria":      np.random.choice(categorias, N),
        "precio_unitario": np.random.lognormal(mean=13.0, sigma=1.2, size=N).round(0),
        "cantidad":       np.random.randint(1, 15, N),
        "costo_unitario": None,   # Se calcula abajo
        "descuento_pct":  np.random.choice([0.0, 0.05, 0.10, 0.15, 0.20, None],
                                           N, p=[0.45, 0.20, 0.15, 0.10, 0.05, 0.05]),
        "estado_orden":   np.random.choice(estados, N, p=[0.75, 0.10, 0.10, 0.05]),
    })

    # ── Costo = 55–80% del precio ─────────────────────────────────────────────
    margen_base = np.random.uniform(0.20, 0.45, N)
    df["costo_unitario"] = (df["precio_unitario"] * (1 - margen_base)).round(0)

    # ── Introducir defectos intencionales ─────────────────────────────────────
    # 1. Nulos en precio_unitario (5%)
    idx_precio = np.random.choice(df.index, size=int(N * 0.05), replace=False)
    df.loc[idx_precio, "precio_unitario"] = np.nan

    # 2. Nulos en departamento (8%)
    idx_dep = np.random.choice(df.index, size=int(N * 0.08), replace=False)
    df.loc[idx_dep, "departamento"] = np.nan

    # 3. Nulos en costo_unitario (6%)
    idx_costo = np.random.choice(df.index, size=int(N * 0.06), replace=False)
    df.loc[idx_costo, "costo_unitario"] = np.nan

    # 4. Duplicados exactos (7% del total añadido al final)
    n_dup = int(N * 0.07)
    duplicados = df.sample(n=n_dup, random_state=7).copy()
    df = pd.concat([df, duplicados], ignore_index=True)

    # ── Guardar ───────────────────────────────────────────────────────────────
    os.makedirs("datos/crudos", exist_ok=True)
    ruta = "datos/crudos/ventas_colombia_2022_2024.csv"
    df.to_csv(ruta, index=False)

    print(f"\n✅ Dataset generado correctamente")
    print(f"   Ruta:      {ruta}")
    print(f"   Filas:     {len(df):,}")
    print(f"   Columnas:  {df.shape[1]}")
    print(f"   Tamaño:    {os.path.getsize(ruta)/1024**2:.1f} MB")
    print(f"\n   Distribución de defectos intencionales:")
    print(f"   - Duplicados:                ~{n_dup:,} filas")
    print(f"   - Nulos en precio_unitario:  ~{int(N*0.05):,} celdas")
    print(f"   - Nulos en departamento:     ~{int(N*0.08):,} celdas")
    print(f"   - Nulos en costo_unitario:   ~{int(N*0.06):,} celdas")
    print(f"   - Nulos en descuento_pct:    ~{int(N*0.05):,} celdas")
    print(f"\n   Próximo paso: python main.py")

if __name__ == "__main__":
    main()
