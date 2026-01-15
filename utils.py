"""
Utilitaires pour la gestion des chemins (compatible exe)
"""

import sys
import os
from pathlib import Path

def get_base_path():
    """
    Retourne le chemin du dossier de l'application
    
    Fonctionne en mode :
    - Script normal : retourne le dossier contenant le script
    - EXE PyInstaller : retourne le dossier contenant l'exe
    
    Returns:
        Path: Chemin absolu du dossier de base
    """
    if getattr(sys, 'frozen', False):
        # Mode exe (PyInstaller)
        # sys.executable pointe vers l'exe
        return Path(sys.executable).parent
    else:
        # Mode script normal
        # __file__ pointe vers ce fichier utils.py
        return Path(__file__).parent

# Chemin de base global
BASE_PATH = get_base_path()
