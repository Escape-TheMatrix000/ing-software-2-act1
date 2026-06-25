"""
tests/test_cargador.py
======================
Pruebas básicas del módulo DataLoader.

Ejecutar con:
    python -m pytest tests/ -v
    # o simplemente:
    python tests/test_cargador.py
"""

import os
import sys
import unittest
import tempfile
import logging

import pandas as pd
import numpy as np

# Agregar el directorio raíz al path para importar src/
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from src.etl.cargador import DataLoader

# Silenciar logs durante los tests
logging.disable(logging.CRITICAL)


class TestDataLoaderInit(unittest.TestCase):
    """Pruebas de inicialización del DataLoader."""

    def test_extension_csv_detectada_correctamente(self):
        """El DataLoader debe detectar .csv como extensión válida."""
        loader = DataLoader('ruta/archivo.csv')
        self.assertEqual(loader.extension, '.csv')

    def test_extension_parquet_detectada_correctamente(self):
        """El DataLoader debe detectar .parquet como extensión válida."""
        loader = DataLoader('ruta/archivo.parquet')
        self.assertEqual(loader.extension, '.parquet')

    def test_extension_mayusculas_normalizada(self):
        """Las extensiones en mayúsculas deben normalizarse a minúsculas."""
        loader = DataLoader('ruta/archivo.CSV')
        self.assertEqual(loader.extension, '.csv')

    def test_formato_no_soportado_lanza_error(self):
        """Un formato no soportado (.xlsx) debe lanzar ValueError."""
        with self.assertRaises(ValueError):
            DataLoader('ruta/archivo.xlsx')


class TestDataLoaderCargar(unittest.TestCase):
    """Pruebas de carga de archivos."""

    def setUp(self):
        """Crear un DataFrame y CSV de prueba temporal."""
        self.df_prueba = pd.DataFrame({
            'id':       [1, 2, 3, 4, 5],
            'ciudad':   ['Bogotá', 'Medellín', 'Cali', 'Bogotá', 'Cali'],
            'monto':    [100.0, 200.0, 150.0, 300.0, 250.0],
            'activo':   [True, True, False, True, False],
        })
        # Crear archivo temporal
        self.tmp_dir    = tempfile.mkdtemp()
        self.ruta_csv   = os.path.join(self.tmp_dir, 'prueba.csv')
        self.ruta_parquet = os.path.join(self.tmp_dir, 'prueba.parquet')
        self.df_prueba.to_csv(self.ruta_csv, index=False)
        try:
            self.df_prueba.to_parquet(self.ruta_parquet, index=False)
            self.parquet_disponible = True
        except Exception:
            self.parquet_disponible = False

    def test_cargar_csv_exitoso(self):
        """Debe cargar un CSV válido y retornar un DataFrame."""
        loader = DataLoader(self.ruta_csv)
        df = loader.cargar()
        self.assertIsNotNone(df)
        self.assertIsInstance(df, pd.DataFrame)
        self.assertEqual(len(df), 5)

    def test_cargar_archivo_inexistente_retorna_none(self):
        """Cargar un archivo inexistente debe retornar None (no lanzar excepción)."""
        loader = DataLoader('ruta/inexistente.csv')
        df = loader.cargar()
        self.assertIsNone(df)

    def test_cargar_parquet_exitoso(self):
        """Debe cargar un Parquet válido si pyarrow está disponible."""
        if not self.parquet_disponible:
            self.skipTest('pyarrow no disponible')
        loader = DataLoader(self.ruta_parquet)
        df = loader.cargar()
        self.assertIsNotNone(df)
        self.assertEqual(len(df), 5)

    def test_columnas_preservadas(self):
        """Las columnas del CSV deben coincidir con las del DataFrame cargado."""
        loader = DataLoader(self.ruta_csv)
        df = loader.cargar()
        self.assertEqual(list(df.columns), ['id', 'ciudad', 'monto', 'activo'])


class TestDataLoaderDiagnosticar(unittest.TestCase):
    """Pruebas del método diagnosticar."""

    def setUp(self):
        """Crear un DataFrame con nulos y duplicados para diagnóstico."""
        self.df_con_defectos = pd.DataFrame({
            'col_a': [1, 2, None, 4, 1],   # 1 nulo, 1 duplicado (fila 0 y 4)
            'col_b': ['x', 'y', 'z', None, 'x'],
        })
        self.tmp_dir  = tempfile.mkdtemp()
        self.ruta_csv = os.path.join(self.tmp_dir, 'defectos.csv')
        self.df_con_defectos.to_csv(self.ruta_csv, index=False)
        self.loader   = DataLoader(self.ruta_csv)

    def test_diagnosticar_retorna_dict(self):
        """diagnosticar() debe retornar un diccionario con claves esperadas."""
        metricas = self.loader.diagnosticar(self.df_con_defectos)
        claves_esperadas = ['filas', 'columnas', 'nulos_total', 'pct_nulos', 'cumple_minimo']
        for clave in claves_esperadas:
            self.assertIn(clave, metricas)

    def test_detecta_nulos_correctamente(self):
        """diagnosticar() debe contar correctamente los valores nulos."""
        metricas = self.loader.diagnosticar(self.df_con_defectos)
        self.assertEqual(metricas['nulos_total'], 2)  # 1 en col_a + 1 en col_b

    def test_cumple_minimo_falso_para_dataset_pequeno(self):
        """Un dataset pequeño no debe cumplir el mínimo de 100.000 filas."""
        metricas = self.loader.diagnosticar(self.df_con_defectos)
        self.assertFalse(metricas['cumple_minimo'])


if __name__ == '__main__':
    # Habilitar logging para ver los mensajes durante los tests manuales
    logging.disable(logging.NOTSET)
    logging.basicConfig(level=logging.WARNING)

    loader = unittest.TestLoader()
    suite  = loader.loadTestsFromModule(sys.modules[__name__])
    runner = unittest.TextTestRunner(verbosity=2)
    result = runner.run(suite)
    sys.exit(0 if result.wasSuccessful() else 1)
