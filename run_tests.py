#!/usr/bin/env python
"""
Script para ejecutar todas las pruebas unitarias del proyecto

Uso:
    python run_tests.py              # Ejecutar todas las pruebas
    python run_tests.py verbose      # Modo verbose con más detalles
"""

import unittest
import sys
import os

# Agregar el directorio raíz al path
sys.path.insert(0, os.path.dirname(__file__))


def run_tests(verbosity=1):
    """
    Descubre y ejecuta todas las pruebas en el proyecto
    
    Args:
        verbosity: Nivel de detalle (1=normal, 2=verbose)
    """
    # Crear un test loader
    loader = unittest.TestLoader()
    
    # Descubrir todas las pruebas en los archivos test_*.py
    suite = loader.discover('.', pattern='test_*.py')
    
    # Crear un test runner
    runner = unittest.TextTestRunner(verbosity=verbosity)
    
    # Ejecutar las pruebas
    result = runner.run(suite)
    
    # Retornar código de salida basado en si pasaron todas las pruebas
    return 0 if result.wasSuccessful() else 1


if __name__ == '__main__':
    # Usar verbose si se pasa como argumento
    verbosity = 2 if 'verbose' in sys.argv else 1
    exit_code = run_tests(verbosity)
    sys.exit(exit_code)
