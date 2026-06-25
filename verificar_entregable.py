"""
verificar_entregable.py
=======================
Script de verificación automática del Entregable 1.

Comprueba que todos los requisitos técnicos están cumplidos
antes de la sesión de sustentación (Sesión 9).

Ejecutar con:
    python verificar_entregable.py
"""

import os
import sys


def verificar() -> tuple[list, list]:
    """
    Verifica todos los requisitos del Entregable 1.

    Returns:
        tuple[list, list]: (errores, advertencias)
    """
    errores      = []
    advertencias = []

    # ── ESTRUCTURA DEL REPOSITORIO ────────────────────────────────────────
    carpetas_requeridas = [
        'src/etl', 'src/analisis', 'src/viz', 'src/utils',
        'datos/crudos', 'datos/procesados', 'docs', 'logs', 'output', 'tests',
    ]
    for carpeta in carpetas_requeridas:
        if not os.path.isdir(carpeta):
            errores.append(f'Carpeta faltante: {carpeta}/')

    # ── ARCHIVOS CRÍTICOS ─────────────────────────────────────────────────
    archivos_criticos = [
        'main.py',
        'requirements.txt',
        'README.md',
        'src/__init__.py',
        'src/etl/__init__.py',
        'src/etl/cargador.py',
        'src/etl/limpiador.py',
        'src/utils/performance.py',
        'docs/definicion_problema.md',
        'docs/formulacion_analitica.md',
    ]
    for archivo in archivos_criticos:
        if not os.path.isfile(archivo):
            errores.append(f'Archivo faltante: {archivo}')

    # ── DATASET ───────────────────────────────────────────────────────────
    dataset_path = 'datos/crudos/ventas_colombia_2022_2024.csv'
    if not os.path.isfile(dataset_path):
        errores.append(
            f'Dataset no encontrado: {dataset_path}\n'
            f'  → Ejecuta primero: python generar_dataset.py'
        )
    else:
        # Verificar que tiene al menos 100.000 filas
        try:
            import pandas as pd
            # Contar filas sin cargar el archivo completo
            with open(dataset_path, 'r', encoding='utf-8') as f:
                n_filas = sum(1 for _ in f) - 1  # -1 por el encabezado
            if n_filas < 100_000:
                errores.append(
                    f'Dataset con solo {n_filas:,} filas — mínimo requerido: 100.000'
                )
            else:
                print(f'  ✅ Dataset: {n_filas:,} filas encontradas')
        except Exception as e:
            advertencias.append(f'No se pudo verificar el tamaño del dataset: {e}')

    # ── OUTPUTS GENERADOS ─────────────────────────────────────────────────
    # (Solo verifica si el pipeline se ejecutó al menos una vez)
    if not os.path.isfile('logs/pipeline.log'):
        advertencias.append(
            'logs/pipeline.log no existe — ejecuta python main.py primero'
        )
    if not os.path.isfile('output/reporte_ejecucion.json'):
        advertencias.append(
            'output/reporte_ejecucion.json no existe — ejecuta python main.py primero'
        )

    # ── DOCSTRINGS BÁSICOS ────────────────────────────────────────────────
    try:
        import ast
        for modulo in ['src/etl/cargador.py', 'src/etl/limpiador.py']:
            if os.path.isfile(modulo):
                with open(modulo, 'r', encoding='utf-8') as f:
                    tree = ast.parse(f.read())
                clases_sin_doc = []
                for node in ast.walk(tree):
                    if isinstance(node, (ast.ClassDef, ast.FunctionDef)):
                        if not (node.body and isinstance(node.body[0], ast.Expr)
                                and isinstance(node.body[0].value, ast.Constant)):
                            clases_sin_doc.append(node.name)
                if clases_sin_doc:
                    advertencias.append(
                        f'{modulo}: funciones/clases sin docstring: {clases_sin_doc}'
                    )
    except Exception:
        pass  # La verificación de docstrings es opcional

    return errores, advertencias


def main():
    print('\n' + '='*60)
    print('🔍 VERIFICACIÓN DEL ENTREGABLE 1')
    print('='*60)

    errores, advertencias = verificar()

    if advertencias:
        print(f'\n⚠️  ADVERTENCIAS ({len(advertencias)}):')
        for adv in advertencias:
            print(f'  ⚠  {adv}')

    if errores:
        print(f'\n❌ ERRORES — El entregable NO está listo ({len(errores)}):')
        for err in errores:
            print(f'  ❌ {err}')
        print('\n  Corrige los errores antes de la sustentación.')
        print('='*60 + '\n')
        sys.exit(1)
    else:
        print(f'\n✅ VERIFICACIÓN PASADA — Entregable 1 listo para sustentar')
        if advertencias:
            print(f'   (con {len(advertencias)} advertencia(s) menores)')
        print('='*60 + '\n')
        sys.exit(0)


if __name__ == '__main__':
    main()
