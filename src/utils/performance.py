"""
src/utils/performance.py
========================
Monitor de rendimiento para el pipeline del Entregable 1.

Responsabilidad única: medir la latencia de cada operación del pipeline,
identificar cuellos de botella y documentar métricas de QoS (Quality of Service).

Autor: [Nombre del equipo]
Fecha: [Fecha]
"""

import time
import logging
from datetime import datetime

logger = logging.getLogger(__name__)


class PipelineTimer:
    """
    Cronómetro para pipelines de datos con reporte de métricas.

    Mide el tiempo de cada paso del pipeline, calcula el throughput
    (filas/segundo) e identifica automáticamente el cuello de botella.

    Attributes:
        nombre (str):  Nombre del pipeline para identificar en los logs.
        inicio (datetime): Momento de inicio del pipeline.
        marcas (dict): Diccionario de tiempos por paso.

    Example:
        >>> timer = PipelineTimer('pipeline_entregable1')
        >>> timer.iniciar()
        >>> df = loader.cargar()
        >>> timer.marcar('carga', n_registros=len(df))
        >>> df_limpio, _ = cleaner.limpiar(df)
        >>> timer.marcar('limpieza', n_registros=len(df_limpio))
        >>> metricas = timer.reporte()
    """

    def __init__(self, nombre: str) -> None:
        """
        Inicializa el PipelineTimer.

        Args:
            nombre (str): Nombre identificador del pipeline.
        """
        self.nombre = nombre
        self.inicio = None
        self.marcas = {}      # {nombre_paso: {'duracion': float, 'n_registros': int}}
        self.ultimo = None    # Tiempo del último .marcar() para calcular diferencias

    def iniciar(self) -> None:
        """
        Inicia el cronómetro del pipeline.

        Debe llamarse una vez antes del primer .marcar().
        """
        self.inicio = datetime.now()
        self.ultimo = time.perf_counter()  # Alta precisión
        logger.info(
            f'[{self.nombre}] Pipeline iniciado: '
            f'{self.inicio.strftime("%Y-%m-%d %H:%M:%S")}'
        )

    def marcar(self, nombre_paso: str, n_registros: int = 0) -> float:
        """
        Registra el tiempo transcurrido desde la última marca.

        Args:
            nombre_paso (str):  Etiqueta descriptiva del paso que terminó.
            n_registros (int):  Número de filas procesadas en este paso.
                                Permite calcular el throughput.

        Returns:
            float: Duración en segundos de este paso.

        Example:
            >>> timer.marcar('carga_datos', n_registros=len(df))
        """
        ahora     = time.perf_counter()
        duracion  = ahora - self.ultimo
        throughput = int(n_registros / duracion) if duracion > 0 else 0

        self.marcas[nombre_paso] = {
            'duracion':    round(duracion, 4),
            'n_registros': n_registros,
            'throughput':  throughput,
        }
        self.ultimo = ahora

        logger.info(
            f'  [{nombre_paso}]: {duracion:.3f}s | '
            f'{throughput:,} filas/s'
        )
        return duracion

    def reporte(self) -> dict:
        """
        Imprime el reporte completo de latencia e identifica el cuello de botella.

        Muestra una barra visual proporcional para facilitar la comparación.

        Returns:
            dict con 'pasos', 'total_seg', 'cuello_botella'.

        Example:
            >>> metricas = timer.reporte()
            >>> print(f"Cuello de botella: {metricas['cuello_botella']}")
        """
        if not self.marcas:
            logger.warning('PipelineTimer: no hay marcas registradas')
            return {}

        total  = sum(m['duracion'] for m in self.marcas.values())
        cuello = max(self.marcas, key=lambda k: self.marcas[k]['duracion'])

        print(f'\n{"="*60}')
        print(f'⏱️  REPORTE DE LATENCIA — {self.nombre}')
        print(f'{"="*60}')

        for paso, datos in self.marcas.items():
            pct   = datos['duracion'] / total * 100
            barra = '█' * int(pct / 4)  # Barra proporcional
            flag  = ' ← 🚨 CUELLO DE BOTELLA' if paso == cuello else ''
            print(
                f'  {paso:<22} {barra:<25} '
                f'{datos["duracion"]:.3f}s ({pct:.0f}%){flag}'
            )

        print(f'{"─"*60}')
        print(f'  TOTAL:          {total:.3f} segundos')
        print(f'  Inicio:         {self.inicio.strftime("%H:%M:%S")}')
        print(f'  Fin:            {datetime.now().strftime("%H:%M:%S")}')
        print(f'{"="*60}\n')

        logger.info(
            f'[{self.nombre}] Latencia total: {total:.3f}s | '
            f'Cuello: {cuello} ({self.marcas[cuello]["duracion"]:.3f}s)'
        )

        return {
            'pasos':          self.marcas,
            'total_seg':      round(total, 3),
            'cuello_botella': cuello,
        }
