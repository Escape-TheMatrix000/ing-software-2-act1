"""
main.py
=======
Punto de entrada único del Pipeline ETL — Entregable 1.

Orquesta todos los módulos del sistema en secuencia:
  DataLoader → DataCleaner → Diagnóstico → Reporte

Ejecutar con:
    python main.py

El pipeline es completamente autónomo: no requiere intervención manual.
Los resultados se guardan en output/ y los logs en logs/pipeline.log.

Autor: [Nombre del equipo]
Fecha: [Fecha]
"""

import logging
import json
import sys
import os
from pathlib import Path

from src.etl.cargador   import DataLoader
from src.etl.limpiador  import DataCleaner
from src.utils.performance import PipelineTimer


# ─────────────────────────────────────────────────────────────────────────────
# CONFIGURACIÓN DE LOGGING
# ─────────────────────────────────────────────────────────────────────────────

def configurar_logging() -> None:
    """
    Configura el sistema de logging para toda la aplicación.

    Escribe en dos destinos simultáneamente:
      - logs/pipeline.log : registro permanente con timestamps
      - stdout            : salida visible en consola durante la ejecución
    """
    Path('logs').mkdir(exist_ok=True)

    logging.basicConfig(
        level=logging.INFO,
        format='%(asctime)s  %(name)-30s  %(levelname)-8s  %(message)s',
        datefmt='%Y-%m-%d %H:%M:%S',
        handlers=[
            logging.FileHandler(
                'logs/pipeline.log',
                encoding='utf-8',
                mode='a'   # append: no sobreescribe ejecuciones anteriores
            ),
            logging.StreamHandler(sys.stdout),
        ]
    )


# ─────────────────────────────────────────────────────────────────────────────
# FUNCIÓN PRINCIPAL
# ─────────────────────────────────────────────────────────────────────────────

def ejecutar_pipeline(
    ruta_datos: str = 'datos/crudos/ventas_colombia_2022_2024.csv',
    carpeta_salida: str = 'output/',
) -> dict:
    """
    Ejecuta el pipeline ETL completo del Entregable 1.

    Pasos:
      1. Carga de datos (Extract)
      2. Diagnóstico del dataset crudo
      3. Limpieza y optimización (Transform)
      4. Guardado del resultado limpio (Load)
      5. Generación del reporte de ejecución

    Args:
        ruta_datos (str):     Ruta al archivo de datos crudos.
        carpeta_salida (str): Carpeta donde guardar los resultados.

    Returns:
        dict con métricas de ejecución, calidad y rendimiento.
    """
    logger = logging.getLogger('pipeline.main')

    logger.info('=' * 65)
    logger.info('PIPELINE ETL — ENTREGABLE 1 — INICIANDO')
    logger.info('=' * 65)

    # Crear carpeta de salida si no existe
    Path(carpeta_salida).mkdir(parents=True, exist_ok=True)

    timer = PipelineTimer('entregable_1')
    timer.iniciar()

    reporte_final = {
        'exitoso':         False,
        'errores':         [],
        'metricas_calidad': {},
        'metricas_limpieza': {},
        'metricas_rendimiento': {},
    }

    # ── PASO 1: EXTRACCIÓN ────────────────────────────────────────────────────
    logger.info('─── PASO 1: CARGA DE DATOS ───')

    loader = DataLoader(ruta_datos, nombre_proyecto='ventas_colombia')
    df_crudo = loader.cargar()

    if df_crudo is None:
        logger.error('PIPELINE DETENIDO: no se pudo cargar el dataset')
        reporte_final['errores'].append('Fallo en carga del dataset')
        return reporte_final

    timer.marcar('carga_datos', n_registros=len(df_crudo))
    logger.info(f'Dataset cargado: {len(df_crudo):,} filas × {df_crudo.shape[1]} columnas')

    # ── PASO 2: DIAGNÓSTICO DEL DATASET CRUDO ────────────────────────────────
    logger.info('─── PASO 2: DIAGNÓSTICO DEL DATASET CRUDO ───')
    metricas_calidad = loader.diagnosticar(df_crudo)
    reporte_final['metricas_calidad'] = metricas_calidad
    timer.marcar('diagnostico')

    if not metricas_calidad['cumple_minimo']:
        logger.warning(
            f'El dataset tiene {metricas_calidad["filas"]:,} filas — '
            f'se requieren al menos 100.000'
        )

    # Mostrar vista previa del dataset crudo
    print('\n📊 VISTA PREVIA DEL DATASET CRUDO (primeras 5 filas):')
    print(df_crudo.head().to_string())
    print(f'\n📋 TIPOS DE DATO:')
    print(df_crudo.dtypes.to_string())

    # ── PASO 3: TRANSFORMACIÓN Y LIMPIEZA ────────────────────────────────────
    logger.info('─── PASO 3: LIMPIEZA Y OPTIMIZACIÓN ───')

    cleaner  = DataCleaner(nombre_proyecto='ventas_colombia')
    df_limpio, reporte_limpieza = cleaner.limpiar(
        df          = df_crudo,
        estrategia_nulos = 'mediana',    # Más robusta ante outliers
        optimizar_ram    = True,
    )

    reporte_final['metricas_limpieza'] = reporte_limpieza
    timer.marcar('limpieza', n_registros=len(df_limpio))

    # Validar que la limpieza fue exitosa
    es_limpio = cleaner.validar_limpieza(df_limpio)
    if not es_limpio:
        logger.warning('El DataFrame aún tiene datos sucios — revisar logs')
        reporte_final['errores'].append('Validación post-limpieza fallida')

    # ── PASO 4: CARGA (GUARDAR RESULTADOS) ───────────────────────────────────
    logger.info('─── PASO 4: GUARDAR DATASET LIMPIO ───')

    # Guardar como CSV (legible) y Parquet (eficiente para el E2)
    ruta_csv     = os.path.join(carpeta_salida, 'ventas_limpio.csv')
    ruta_parquet = os.path.join(carpeta_salida, 'ventas_limpio.parquet')

    df_limpio.to_csv(ruta_csv, index=False)
    logger.info(f'CSV guardado: {ruta_csv}')

    try:
        df_limpio.to_parquet(ruta_parquet, index=False)
        logger.info(f'Parquet guardado: {ruta_parquet}')
    except Exception as e:
        logger.warning(f'No se pudo guardar Parquet (instalar pyarrow): {e}')

    timer.marcar('guardar_resultados')

    # ── PASO 5: REPORTE DE RENDIMIENTO ───────────────────────────────────────
    logger.info('─── PASO 5: REPORTE DE RENDIMIENTO ───')
    metricas_render = timer.reporte()
    reporte_final['metricas_rendimiento'] = metricas_render
    reporte_final['exitoso'] = len(reporte_final['errores']) == 0

    # Guardar reporte completo en JSON
    ruta_reporte = os.path.join(carpeta_salida, 'reporte_ejecucion.json')
    with open(ruta_reporte, 'w', encoding='utf-8') as f:
        json.dump(reporte_final, f, indent=2, ensure_ascii=False, default=str)
    logger.info(f'Reporte guardado: {ruta_reporte}')

    # ── RESUMEN FINAL EN CONSOLA ──────────────────────────────────────────────
    print('\n' + '='*65)
    print('✅ PIPELINE ETL COMPLETADO')
    print('='*65)
    print(f'  Filas entrada:       {reporte_limpieza["filas_entrada"]:,}')
    print(f'  Filas limpias:       {reporte_limpieza["filas_salida"]:,}')
    print(f'  Filas eliminadas:    {reporte_limpieza["filas_eliminadas"]:,}')
    print(f'  Nulos resueltos:     {reporte_limpieza["nulos_resueltos"]:,}')
    print(f'  RAM reducida:        {reporte_limpieza["pct_reduccion_ram"]}%')
    print(f'  Latencia total:      {metricas_render.get("total_seg", "?")} s')
    print(f'  Errores:             {len(reporte_final["errores"])}')
    print(f'\n  Outputs en:          {carpeta_salida}')
    print(f'  Log en:              logs/pipeline.log')
    print('='*65)

    logger.info('PIPELINE ETL COMPLETADO EXITOSAMENTE')
    return reporte_final


# ─────────────────────────────────────────────────────────────────────────────
# PUNTO DE ENTRADA
# ─────────────────────────────────────────────────────────────────────────────

if __name__ == '__main__':
    configurar_logging()
    resultado = ejecutar_pipeline(
        ruta_datos     = 'datos/crudos/ventas_colombia_2022_2024.csv',
        carpeta_salida = 'output/',
    )
    sys.exit(0 if resultado['exitoso'] else 1)
