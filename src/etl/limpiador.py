"""
src/etl/limpiador.py
====================
Módulo de limpieza y optimización de datos para el Entregable 1.

Responsabilidad única: tomar un DataFrame crudo y devolver un DataFrame
limpio, optimizado en memoria, con todos los eventos documentados en logs.
NO carga archivos, NO genera gráficas, NO hace análisis de negocio.

Autor: [Nombre del equipo]
Fecha: [Fecha]
"""

import time
import logging

import pandas as pd
import numpy as np

logger = logging.getLogger(__name__)


# ─────────────────────────────────────────────────────────────────────────────
# FUNCIÓN UTILITARIA — Programación Estructurada (sin estado)
# Se usa en DataCleaner pero también puede llamarse directamente
# ─────────────────────────────────────────────────────────────────────────────

def optimizar_memoria(df: pd.DataFrame, verbose: bool = True) -> pd.DataFrame:
    """
    Optimiza los tipos de datos de un DataFrame para reducir el uso de RAM.

    Aplica las siguientes estrategias de forma automática:
      - int64/int32 → int8/int16/int32 según el rango real de valores.
      - float64 → float32 (precisión de 7 cifras, suficiente para negocio).
      - object con < 50% valores únicos → category (mucho más eficiente).

    Args:
        df (pd.DataFrame):  DataFrame a optimizar.
        verbose (bool):     Si True, registra el reporte en el log.

    Returns:
        pd.DataFrame: Copia del DataFrame con tipos de dato optimizados.

    Example:
        >>> df_opt = optimizar_memoria(df_crudo)
        >>> # Típicamente reduce 40-70% del uso de RAM
    """
    df_opt    = df.copy()
    mem_antes = df_opt.memory_usage(deep=True).sum() / 1024**2

    for col in df_opt.columns:
        tipo = df_opt[col].dtype

        # ── Enteros: reducir según rango real ──────────────────────────────
        if tipo in ['int64', 'int32']:
            col_min = df_opt[col].min()
            col_max = df_opt[col].max()

            if   col_min >= -128    and col_max <= 127:    df_opt[col] = df_opt[col].astype('int8')
            elif col_min >= -32768  and col_max <= 32767:  df_opt[col] = df_opt[col].astype('int16')
            elif tipo == 'int64':                           df_opt[col] = df_opt[col].astype('int32')

        # ── Decimales: reducir precisión ───────────────────────────────────
        elif tipo == 'float64':
            df_opt[col] = df_opt[col].astype('float32')

        # ── Texto con pocos valores únicos → category ──────────────────────
        elif tipo == 'object':
            n_unicos = df_opt[col].nunique()
            if n_unicos / len(df_opt) < 0.50:   # Menos del 50% son únicos
                df_opt[col] = df_opt[col].astype('category')

    mem_despues = df_opt.memory_usage(deep=True).sum() / 1024**2
    reduccion   = (1 - mem_despues / mem_antes) * 100

    if verbose:
        logger.info(
            f'Memoria optimizada: {mem_antes:.1f} MB → '
            f'{mem_despues:.1f} MB (−{reduccion:.0f}%)'
        )

    return df_opt


# ─────────────────────────────────────────────────────────────────────────────
# CLASE PRINCIPAL — Programación Orientada a Objetos (con estado)
# Tiene estado porque recuerda el nombre_proyecto y el logger entre llamadas
# ─────────────────────────────────────────────────────────────────────────────

class DataCleaner:
    """
    Limpiador de datos para el pipeline del Entregable 1.

    Aplica eliminación de duplicados, imputación de nulos según el tipo
    de cada columna, y optimización de tipos de dato. Documenta todas
    las decisiones mediante logging profesional.

    Attributes:
        nombre_proyecto (str): Nombre del proyecto para etiquetar logs.

    Example:
        >>> cleaner = DataCleaner(nombre_proyecto='ventas_colombia')
        >>> df_limpio, reporte = cleaner.limpiar(df_crudo)
        >>> print(f"Filas limpias: {reporte['filas_salida']:,}")
    """

    def __init__(self, nombre_proyecto: str = 'proyecto') -> None:
        """
        Inicializa el DataCleaner.

        Args:
            nombre_proyecto (str): Nombre para identificar los logs.
        """
        self.nombre_proyecto = nombre_proyecto
        self.logger = logging.getLogger(f'{nombre_proyecto}.DataCleaner')
        self.logger.info('DataCleaner inicializado')

    # ─────────────────────────────────────────────────────────────────────
    # MÉTODO PÚBLICO PRINCIPAL
    # ─────────────────────────────────────────────────────────────────────

    def limpiar(
        self,
        df: pd.DataFrame,
        estrategia_nulos: str = 'mediana',
        optimizar_ram: bool   = True,
    ) -> tuple[pd.DataFrame, dict]:
        """
        Limpia el DataFrame en tres pasos:
          1. Elimina duplicados exactos.
          2. Imputa valores nulos según el tipo de columna.
          3. (Opcional) Optimiza los tipos de dato para reducir RAM.

        Args:
            df (pd.DataFrame):         DataFrame crudo a limpiar.
            estrategia_nulos (str):    Estrategia para columnas numéricas:
                                         'mediana' → más robusta a outliers
                                         'media'   → más rápida pero sensible
                                         'eliminar'→ elimina filas con nulos
            optimizar_ram (bool):      Si True, aplica casteo de tipos al final.

        Returns:
            tuple[pd.DataFrame, dict]: (df_limpio, reporte_metricas)
              El reporte incluye: filas_entrada, filas_salida, filas_eliminadas,
              nulos_resueltos, ram_antes_mb, ram_despues_mb, pct_reduccion_ram,
              latencia_seg.

        Example:
            >>> df_limpio, reporte = cleaner.limpiar(df_crudo, 'mediana')
            >>> print(f"RAM reducida: {reporte['pct_reduccion_ram']}%")
        """
        self.logger.info('=== INICIO DE LIMPIEZA ===')
        t_inicio     = time.time()
        df_out       = df.copy()      # SIEMPRE trabajar sobre una copia
        filas_inicio = len(df_out)

        # ── PASO 1: ELIMINAR DUPLICADOS EXACTOS ───────────────────────────
        n_dup  = df_out.duplicated().sum()
        df_out = df_out.drop_duplicates()
        self.logger.info(f'Paso 1 — Duplicados eliminados: {n_dup:,} filas')

        # ── PASO 2: IMPUTAR VALORES NULOS ─────────────────────────────────
        nulos_resueltos = 0

        for col in df_out.columns:
            n_nulos = df_out[col].isna().sum()
            if n_nulos == 0:
                continue    # Sin nulos en esta columna — pasar a la siguiente

            tipo = df_out[col].dtype

            # Detect categorical-like columns (object, category, StringDtype, bool, datetime)
            is_numeric = pd.api.types.is_numeric_dtype(tipo)

            if not is_numeric:
                # Columnas no numéricas (texto, categoría, fecha): imputar con etiqueta neutral
                df_out[col] = df_out[col].fillna('Sin Datos')
                self.logger.info(
                    f'  {col}: {n_nulos:,} nulos → "Sin Datos" (no numérico)'
                )

            elif estrategia_nulos == 'eliminar':
                filas_antes = len(df_out)
                df_out      = df_out.dropna(subset=[col])
                filas_elim  = filas_antes - len(df_out)
                self.logger.info(
                    f'  {col}: {n_nulos:,} nulos → {filas_elim:,} filas eliminadas'
                )

            elif estrategia_nulos == 'media':
                valor = df_out[col].mean()
                df_out[col] = df_out[col].fillna(valor)
                self.logger.info(
                    f'  {col}: {n_nulos:,} nulos → media {valor:.2f}'
                )

            else:   # 'mediana' — opción por defecto, más robusta
                valor = df_out[col].median()
                df_out[col] = df_out[col].fillna(valor)
                self.logger.info(
                    f'  {col}: {n_nulos:,} nulos → mediana {valor:.2f}'
                )

            nulos_resueltos += n_nulos

        self.logger.info(
            f'Paso 2 — Nulos resueltos: {nulos_resueltos:,} valores'
        )

        # ── PASO 3: OPTIMIZAR TIPOS DE DATO (RAM) ─────────────────────────
        mem_antes   = df_out.memory_usage(deep=True).sum() / 1024**2
        if optimizar_ram:
            df_out = optimizar_memoria(df_out, verbose=True)
        mem_despues = df_out.memory_usage(deep=True).sum() / 1024**2

        # ── REPORTE FINAL ──────────────────────────────────────────────────
        duracion = time.time() - t_inicio

        reporte = {
            'filas_entrada':    filas_inicio,
            'filas_salida':     len(df_out),
            'filas_eliminadas': filas_inicio - len(df_out),
            'nulos_resueltos':  nulos_resueltos,
            'ram_antes_mb':     round(mem_antes, 2),
            'ram_despues_mb':   round(mem_despues, 2),
            'pct_reduccion_ram': round((1 - mem_despues / mem_antes) * 100, 1),
            'latencia_seg':     round(duracion, 3),
        }

        self.logger.info(
            f'=== FIN DE LIMPIEZA === | '
            f'{len(df_out):,} filas limpias | '
            f'RAM −{reporte["pct_reduccion_ram"]}% | '
            f'{duracion:.3f}s'
        )
        return df_out, reporte

    # ─────────────────────────────────────────────────────────────────────
    # MÉTODO DE VALIDACIÓN POST-LIMPIEZA
    # ─────────────────────────────────────────────────────────────────────

    def validar_limpieza(self, df: pd.DataFrame) -> bool:
        """
        Verifica que el DataFrame no tiene nulos ni duplicados.

        Útil para ejecutar después de limpiar y confirmar que el
        proceso fue exitoso antes de continuar el pipeline.

        Args:
            df (pd.DataFrame): DataFrame ya limpiado.

        Returns:
            bool: True si el DataFrame está completamente limpio.

        Example:
            >>> assert cleaner.validar_limpieza(df_limpio), "¡Aún hay datos sucios!"
        """
        nulos     = df.isna().sum().sum()
        dup       = df.duplicated().sum()
        es_limpio = (nulos == 0) and (dup == 0)

        if es_limpio:
            self.logger.info('Validación post-limpieza: ✅ DataFrame completamente limpio')
        else:
            self.logger.warning(
                f'Validación post-limpieza: ⚠️  '
                f'Nulos: {nulos:,} | Duplicados: {dup:,}'
            )

        return es_limpio
