"""
src/etl/cargador.py
===================
Módulo de carga universal de datos para el Entregable 1.

Responsabilidad única: leer un archivo de datos en cualquier formato
soportado (CSV, JSON, Parquet) y retornar un DataFrame de Pandas limpio
en cuanto a estructura. NO limpia datos, NO transforma, NO visualiza.

Autor: [Nombre del equipo]
Fecha: [Fecha]
"""

import os
import time
import logging

import pandas as pd

# Obtener el logger para este módulo
# Usa el nombre del módulo en la jerarquía: proyecto.etl.cargador
logger = logging.getLogger(__name__)


class DataLoader:
    """
    Cargador universal de datos para el pipeline del proyecto.

    Detecta automáticamente el formato del archivo por su extensión
    (.csv, .json, .parquet) y aplica la estrategia de lectura óptima
    para cada tipo. Registra todos los eventos con logging profesional.

    Attributes:
        ruta_archivo (str):    Ruta al archivo de datos a cargar.
        nombre_proyecto (str): Nombre del proyecto para identificar logs.
        extension (str):       Extensión detectada del archivo.

    Example:
        >>> loader = DataLoader('datos/crudos/ventas_colombia_2022_2024.csv')
        >>> df = loader.cargar()
        >>> metricas = loader.diagnosticar(df)
        >>> print(metricas['filas'])
    """

    # Formatos soportados por el cargador
    FORMATOS_SOPORTADOS = {'.csv', '.json', '.parquet'}

    def __init__(self, ruta_archivo: str, nombre_proyecto: str = 'proyecto') -> None:
        """
        Inicializa el DataLoader.

        Args:
            ruta_archivo (str):    Ruta absoluta o relativa al archivo de datos.
            nombre_proyecto (str): Nombre del proyecto para etiquetar los logs.

        Raises:
            ValueError: Si la extensión del archivo no está soportada.

        Example:
            >>> loader = DataLoader('datos/crudos/ventas.csv', 'ventas_colombia')
        """
        self.ruta_archivo    = ruta_archivo
        self.nombre_proyecto = nombre_proyecto

        # Detectar extensión automáticamente (en minúsculas para consistencia)
        # os.path.splitext('datos/ventas.CSV') → ('datos/ventas', '.CSV')
        _, self.extension = os.path.splitext(ruta_archivo)
        self.extension = self.extension.lower()

        if self.extension not in self.FORMATOS_SOPORTADOS:
            raise ValueError(
                f'Formato no soportado: "{self.extension}". '
                f'Formatos válidos: {self.FORMATOS_SOPORTADOS}'
            )

        logger.info(
            f'DataLoader inicializado | archivo: {ruta_archivo} | '
            f'formato detectado: {self.extension}'
        )

    # ─────────────────────────────────────────────────────────────────────────
    # MÉTODO PÚBLICO PRINCIPAL
    # ─────────────────────────────────────────────────────────────────────────

    def cargar(self) -> pd.DataFrame | None:
        """
        Carga el archivo detectando el formato automáticamente por extensión.

        Verifica la existencia del archivo antes de intentar leerlo.
        Delega a los métodos privados _cargar_csv / _cargar_json / _cargar_parquet.

        Returns:
            pd.DataFrame con los datos cargados, o None si ocurre un error.

        Example:
            >>> df = loader.cargar()
            >>> if df is not None:
            ...     print(f'{len(df):,} filas cargadas')
        """
        # Verificar que el archivo existe antes de intentar cargarlo
        if not os.path.exists(self.ruta_archivo):
            logger.error(f'Archivo no encontrado: {self.ruta_archivo}')
            return None

        # Seleccionar método de carga según la extensión detectada.
        # Usamos un diccionario en lugar de if/elif para facilitar
        # agregar nuevos formatos en el futuro (abierto para extensión).
        metodos_carga = {
            '.csv':     self._cargar_csv,
            '.json':    self._cargar_json,
            '.parquet': self._cargar_parquet,
        }

        return metodos_carga[self.extension]()

    # ─────────────────────────────────────────────────────────────────────────
    # MÉTODOS PRIVADOS — No llamar directamente desde fuera de la clase
    # El prefijo _ indica que son de uso interno
    # ─────────────────────────────────────────────────────────────────────────

    def _cargar_csv(self) -> pd.DataFrame | None:
        """
        Carga un archivo CSV con optimizaciones para archivos grandes.

        Usa low_memory=False para evitar advertencias de tipo mixto
        en columnas con datos heterogéneos (común en datos de negocio).

        Returns:
            pd.DataFrame con los datos del CSV, o None si falla.
        """
        try:
            logger.info(f'Iniciando lectura CSV: {self.ruta_archivo}')
            t_inicio = time.time()

            df = pd.read_csv(
                self.ruta_archivo,
                low_memory=False,       # Evita type inference por chunks
                encoding='utf-8',       # Encoding explícito para caracteres especiales
            )

            duracion = time.time() - t_inicio
            logger.info(
                f'CSV cargado exitosamente | '
                f'{len(df):,} filas × {df.shape[1]} columnas | '
                f'{duracion:.2f}s'
            )
            return df

        except pd.errors.EmptyDataError:
            logger.error(f'El archivo CSV está vacío: {self.ruta_archivo}')
            return None

        except pd.errors.ParserError as e:
            logger.error(f'Error al parsear CSV (archivo malformado): {e}')
            return None

        except UnicodeDecodeError:
            logger.warning('Encoding UTF-8 falló, intentando con latin-1...')
            try:
                df = pd.read_csv(self.ruta_archivo, low_memory=False, encoding='latin-1')
                logger.info(f'CSV cargado con encoding latin-1: {len(df):,} filas')
                return df
            except Exception as e:
                logger.error(f'No se pudo leer el archivo con ningún encoding: {e}')
                return None

        except Exception as e:
            logger.error(f'Error inesperado al cargar CSV: {e}')
            return None

    def _cargar_json(self) -> pd.DataFrame | None:
        """
        Carga un archivo JSON y normaliza la estructura si es necesario.

        Returns:
            pd.DataFrame con los datos del JSON, o None si falla.
        """
        try:
            logger.info(f'Iniciando lectura JSON: {self.ruta_archivo}')
            t_inicio = time.time()

            df = pd.read_json(self.ruta_archivo)

            duracion = time.time() - t_inicio
            logger.info(
                f'JSON cargado exitosamente | '
                f'{len(df):,} filas × {df.shape[1]} columnas | '
                f'{duracion:.2f}s'
            )
            return df

        except ValueError as e:
            # JSON malformado o estructura inesperada (muy frecuente con APIs)
            logger.error(f'JSON malformado o estructura inesperada: {e}')
            return None

        except Exception as e:
            logger.error(f'Error inesperado al cargar JSON: {e}')
            return None

    def _cargar_parquet(self) -> pd.DataFrame | None:
        """
        Carga un archivo Parquet — el formato más eficiente para Big Data.

        Parquet es columnar y comprimido: ocupa 3-5x menos que CSV y
        carga 5-10x más rápido. Los tipos de datos se preservan automáticamente.

        Returns:
            pd.DataFrame con los datos del Parquet, o None si falla.
        """
        try:
            logger.info(f'Iniciando lectura Parquet: {self.ruta_archivo}')
            t_inicio = time.time()

            df = pd.read_parquet(self.ruta_archivo)

            duracion = time.time() - t_inicio
            mem_mb   = df.memory_usage(deep=True).sum() / 1024**2

            logger.info(
                f'Parquet cargado exitosamente | '
                f'{len(df):,} filas × {df.shape[1]} columnas | '
                f'{mem_mb:.1f} MB en RAM | '
                f'{duracion:.3f}s'
            )
            return df

        except Exception as e:
            logger.error(f'Error al cargar Parquet: {e}')
            return None

    # ─────────────────────────────────────────────────────────────────────────
    # HERRAMIENTA DE AUDITORÍA
    # ─────────────────────────────────────────────────────────────────────────

    def diagnosticar(self, df: pd.DataFrame) -> dict:
        """
        Ejecuta las 3 herramientas de auditoría obligatorias:
          1. df.shape  → dimensiones
          2. df.head() → vista previa (en el log)
          3. df.info() → tipos y nulos

        Args:
            df (pd.DataFrame): El DataFrame a diagnosticar.

        Returns:
            dict con: filas, columnas, nulos_total, pct_nulos, cumple_minimo.

        Example:
            >>> metricas = loader.diagnosticar(df)
            >>> print(f"Cumple mínimo: {metricas['cumple_minimo']}")
        """
        logger.info('=== INICIO DE AUDITORÍA ===')

        # ── 1. DIMENSIONES ────────────────────────────────────────────────
        filas, columnas = df.shape
        logger.info(f'Dimensiones: {filas:,} filas × {columnas} columnas')

        # Validar mínimo de 100.000 filas requerido por el curso
        if filas < 100_000:
            logger.warning(
                f'ADVERTENCIA: Dataset con {filas:,} filas — '
                f'el mínimo requerido es 100.000'
            )

        # ── 2. TIPOS DE DATOS ─────────────────────────────────────────────
        tipos_conteo = df.dtypes.value_counts().to_dict()
        logger.info(f'Tipos de datos: {tipos_conteo}')

        # ── 3. VALORES NULOS ──────────────────────────────────────────────
        nulos_por_col = df.isnull().sum()
        nulos_total   = int(nulos_por_col.sum())
        pct_nulos     = round(nulos_total / (filas * columnas) * 100, 2)

        if nulos_total == 0:
            logger.info('Calidad de nulos: PERFECTA — sin valores faltantes')
        else:
            logger.warning(
                f'Valores nulos: {nulos_total:,} celdas ({pct_nulos}% del total)'
            )
            # Detalle por columna
            for col, n in nulos_por_col[nulos_por_col > 0].items():
                pct_col = round(n / filas * 100, 1)
                nivel   = 'CRÍTICO' if pct_col > 20 else ('MODERADO' if pct_col > 5 else 'LEVE')
                logger.warning(f'  [{nivel}] {col}: {n:,} nulos ({pct_col}%)')

        # ── 4. DUPLICADOS ─────────────────────────────────────────────────
        n_dup    = int(df.duplicated().sum())
        pct_dup  = round(n_dup / filas * 100, 2)
        if n_dup > 0:
            logger.warning(f'Filas duplicadas: {n_dup:,} ({pct_dup}%)')
        else:
            logger.info('Duplicados: ninguno detectado')

        logger.info('=== FIN DE AUDITORÍA ===')

        return {
            'filas':          filas,
            'columnas':       columnas,
            'nulos_total':    nulos_total,
            'pct_nulos':      pct_nulos,
            'duplicados':     n_dup,
            'pct_duplicados': pct_dup,
            'cumple_minimo':  filas >= 100_000,
        }
